"""
Qdrant-backed vector store.

Uses Qdrant's local file-based mode — no server process or Docker needed.
Data is persisted to a directory on disk and survives restarts.

Qdrant concepts used here:
  Collection  — like a table; holds all points for one topic.
  Point       — one stored item: a vector + a payload (metadata dict).
  Payload     — arbitrary JSON attached to a point (title, content, etc.).
  Upsert      — insert or update; same point ID overwrites the old one.
  Scroll      — paginated scan of all points (used for listing documents).
"""

from typing import Any, Dict, List, Optional

from rank_bm25 import BM25Okapi
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

# Every document goes into this single Qdrant collection.
_COLLECTION = "chargeback_docs"


class VectorStore:
    """
    Wrapper around a Qdrant local collection that stores document embeddings
    and supports semantic similarity search.

    The collection is created lazily on the first call to add_document(),
    because the vector size (number of dimensions) is only known at that point.

    Usage:
        store = VectorStore()
        store.add_document("id1", "Title", "Content text", [0.1, 0.2, ...])
        results = store.search([0.1, 0.2, ...], top_k=3)
    """

    def __init__(self, persist_path: str = "./qdrant_data"):
        """
        Initialise the vector store and connect to the local Qdrant instance.

        Args:
            persist_path (str): Path to the directory where Qdrant stores its
                                files. Created automatically if it does not
                                exist. Defaults to './qdrant_data'.
        """
        # QdrantClient(path=...) runs in embedded local mode — no server needed.
        self.client = QdrantClient(path=persist_path)
        # Flag to avoid redundant collection-existence checks on every write.
        self._collection_ready = False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_collection(self, vector_size: int) -> None:
        """
        Create the Qdrant collection on first use if it does not already exist.

        Called automatically by add_document() before the first upsert.
        Skips creation if the collection already exists (e.g. from a previous
        run loaded from disk).

        Args:
            vector_size (int): Number of dimensions in each embedding vector.
                               Must match the output size of the embedding model
                               (384 for BAAI/bge-small-en-v1.5).
        """
        if self._collection_ready:
            return

        existing = [c.name for c in self.client.get_collections().collections]
        if _COLLECTION not in existing:
            self.client.create_collection(
                collection_name=_COLLECTION,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE,  # score = cosine similarity (0–1)
                ),
            )

        self._collection_ready = True

    def _str_id_to_int(self, doc_id: str) -> int:
        """
        Convert a string document ID to an unsigned 64-bit integer.

        Qdrant point IDs must be unsigned 64-bit integers or UUIDs.
        This method derives a stable numeric ID from the string doc_id so
        that the same title always maps to the same Qdrant point ID,
        enabling safe upserts (overwrite instead of duplicate).

        Uses MD5 rather than Python's built-in hash() — str hashing is
        randomly seeded per process (PYTHONHASHSEED) unless explicitly
        fixed, so hash() gives a DIFFERENT integer for the same string on
        every process restart. That silently turned every re-run of
        load_encyclopedia.py into duplicate inserts instead of upserts.

        Args:
            doc_id (str): The string document ID (e.g. 'a1b2c3d4').

        Returns:
            int: A stable positive integer derived from doc_id,
                 guaranteed to fit in 63 bits.
        """
        import hashlib
        return int(hashlib.md5(doc_id.encode()).hexdigest(), 16) % (2 ** 63)

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def add_document(
        self,
        doc_id: str,
        title: str,
        content: str,
        embedding: List[float],
        summary: str = "",
        section: str = "",
        network: str = "",
        reason_code: str = "",
        document_type: str = "",
        keywords: Optional[List[str]] = None,
    ) -> None:
        """
        Insert a new document or overwrite an existing one in Qdrant.

        Uses Qdrant's upsert operation which is idempotent — if a point with
        the same doc_id already exists, it is fully replaced. This makes it
        safe to re-index the same document multiple times without creating
        duplicates.

        The document text and title are stored as a 'payload' alongside the
        vector so they can be retrieved in search results without a second
        lookup.

        Args:
            doc_id  (str):         Unique identifier for this document.
                                   Must be deterministic (same title → same ID)
                                   to allow safe re-indexing.
            title   (str):         Human-readable document name shown in results.
            content (str):         Full text of the document that was embedded.
            embedding (List[float]): Vector representation of the content,
                                   produced by the FastEmbed model.
                                   Length must match the collection's vector size.

        Returns:
            None
        """
        self._ensure_collection(len(embedding))

        self.client.upsert(
            collection_name=_COLLECTION,
            points=[
                PointStruct(
                    id=self._str_id_to_int(doc_id),
                    vector=embedding,
                    payload={
                        "doc_id":        doc_id,
                        "title":         title,
                        "content":       content,
                        "summary":       summary,
                        "section":       section,
                        "network":       network,
                        "reason_code":   reason_code,
                        "document_type": document_type,
                        "keywords":      keywords or [],
                    },
                )
            ],
        )

    def clear(self) -> None:
        """
        Delete the entire Qdrant collection including all documents and vectors.

        This operation is irreversible. After calling clear(), the knowledge
        base is empty and documents must be re-indexed from scratch.

        Returns:
            None
        """
        try:
            self.client.delete_collection(_COLLECTION)
        except Exception:
            pass
        self._collection_ready = False

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def search(self, query_embedding: List[float], top_k: int = 3) -> List[Dict]:
        """
        Find the top-k most semantically similar documents for a query vector.

        Uses Qdrant's query_points API (recommended over the older search()
        method for local file-persistence mode). Qdrant computes cosine
        similarity between the query vector and every stored document vector,
        then returns the closest matches sorted by score descending.

        A score of 1.0 means identical meaning; 0.0 means completely unrelated.
        In practice, scores above 0.70 indicate a strong match for this domain.

        Args:
            query_embedding (List[float]): Vector representation of the user's
                                           query, produced by the same FastEmbed
                                           model used during indexing.
            top_k (int): Maximum number of results to return. Defaults to 3.

        Returns:
            List[Dict]: List of matching documents, each containing:
                        - id      (str):   Document identifier.
                        - title   (str):   Document title.
                        - content (str):   Full document text.
                        - score   (float): Cosine similarity score (0.0–1.0).
                        Sorted by score descending (best match first).
        """
        result = self.client.query_points(
            collection_name=_COLLECTION,
            query=query_embedding,
            limit=top_k,
            with_payload=True,
        )
        return [
            {
                "id":            hit.payload["doc_id"],
                "title":         hit.payload["title"],
                "content":       hit.payload["content"],
                "summary":       hit.payload.get("summary", ""),
                "section":       hit.payload.get("section", ""),
                "network":       hit.payload.get("network", ""),
                "reason_code":   hit.payload.get("reason_code", ""),
                "score":         round(hit.score, 4),
            }
            for hit in result.points
        ]

    def filter_by_payload(self, filters: Dict[str, Any], limit: int = 50) -> List[Dict]:
        """
        Return documents whose payload fields match ALL given key=value pairs.
        Uses Qdrant's native field-condition filtering — no full-collection scan.

        Args:
            filters: e.g. {"section": "04_Visa"} or {"network": "Mastercard"}.
            limit:   Maximum number of results (default 50).

        Returns:
            List[Dict]: Matching documents with id, title, content, score=1.0.
        """
        conditions = [
            FieldCondition(key=k, match=MatchValue(value=v))
            for k, v in filters.items()
        ]
        try:
            points, _ = self.client.scroll(
                collection_name=_COLLECTION,
                scroll_filter=Filter(must=conditions),
                limit=limit,
                with_payload=True,
                with_vectors=False,
            )
        except Exception:
            return []
        return [
            {
                "id":            p.payload["doc_id"],
                "title":         p.payload["title"],
                "content":       p.payload["content"],
                "summary":       p.payload.get("summary", ""),
                "section":       p.payload.get("section", ""),
                "network":       p.payload.get("network", ""),
                "reason_code":   p.payload.get("reason_code", ""),
                "score":         1.0,
            }
            for p in points
        ]

    def hybrid_search(
        self,
        query: str,
        query_embedding: List[float],
        top_k: int = 8,
        bm25_weight: float = 0.3,
    ) -> List[Dict]:
        """
        Fuse BM25 keyword scores with vector similarity via reciprocal rank
        fusion (RRF). BM25 helps surface documents that contain the exact
        reason-code string or network name even when the embedding space
        treats them as near-synonyms of unrelated tokens.

        Args:
            query:           Raw text query for BM25 tokenisation.
            query_embedding: Pre-computed vector for the same query.
            top_k:           Number of fused results to return.
            bm25_weight:     Weight for BM25 in the RRF score (0-1).
                             Vector weight = 1 - bm25_weight.

        Returns:
            List[Dict]: Top-k results sorted by fused score descending.
        """
        # Fetch a wider candidate pool for re-ranking.
        candidate_limit = max(top_k * 5, 50)
        try:
            vec_results = self.search(query_embedding, top_k=candidate_limit)
        except Exception:
            return []
        if not vec_results:
            return []

        # Build BM25 index over the candidate set only (not the full corpus).
        tokens = query.lower().split()
        corpus = [r["content"].lower().split() for r in vec_results]
        bm25   = BM25Okapi(corpus)
        bm25_scores = bm25.get_scores(tokens)

        # Normalize BM25 scores to [0, 1].
        bm25_max = max(bm25_scores) if max(bm25_scores) > 0 else 1.0
        bm25_norm = [s / bm25_max for s in bm25_scores]

        # Reciprocal rank fusion: fuse vector rank + BM25 score.
        vec_weight = 1.0 - bm25_weight
        fused = []
        for rank, (doc, bm25_s) in enumerate(zip(vec_results, bm25_norm)):
            rrf   = vec_weight / (rank + 1) + bm25_weight * bm25_s
            fused.append({**doc, "score": round(rrf, 4)})

        fused.sort(key=lambda x: x["score"], reverse=True)
        return fused[:top_k]

    def filter_by_title(self, keywords: List[str]) -> List[Dict]:
        """
        Return all documents whose title contains any of the given keywords
        (case-insensitive). Used for network-specific list queries where
        semantic search alone may miss lower-ranked but relevant documents.

        Args:
            keywords: List of strings to match against document titles.

        Returns:
            List[Dict]: Matching documents with id, title, content, score=1.0.
        """
        try:
            points, _ = self.client.scroll(
                collection_name=_COLLECTION,
                limit=1000,
                with_payload=True,
                with_vectors=False,
            )
        except Exception:
            return []
        lower_kws = [k.lower() for k in keywords]
        return [
            {
                "id":          p.payload["doc_id"],
                "title":       p.payload["title"],
                "content":     p.payload["content"],
                "summary":     p.payload.get("summary", ""),
                "section":     p.payload.get("section", ""),
                "network":     p.payload.get("network", ""),
                "reason_code": p.payload.get("reason_code", ""),
                "score":       1.0,
            }
            for p in points
            if any(kw in p.payload.get("title", "").lower() for kw in lower_kws)
        ]

    def list_documents(self) -> List[Dict]:
        """
        Return a lightweight list of all documents currently in the knowledge base.

        Uses Qdrant's scroll API to page through all stored points without
        loading their vectors into memory, keeping this operation fast and
        memory-efficient regardless of collection size.

        Returns:
            List[Dict]: List of document summaries, each containing:
                        - id    (str): Document identifier.
                        - title (str): Document title.
                        Returns an empty list if the collection is empty.
        """
        points, _ = self.client.scroll(
            collection_name=_COLLECTION,
            limit=1000,
            with_payload=["doc_id", "title"],  # fetch only metadata, not content
            with_vectors=False,                 # skip vectors to save memory
        )
        return [
            {"id": p.payload["doc_id"], "title": p.payload["title"]}
            for p in points
        ]

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """
        Return the total number of documents currently stored in Qdrant.

        Used to check whether the knowledge base is empty before attempting
        a search. Returns 0 if the collection does not exist yet or if
        Qdrant returns None for points_count (which can happen in local mode
        before any documents are indexed).

        Returns:
            int: Number of documents in the collection, or 0 if empty/missing.
        """
        try:
            info = self.client.get_collection(_COLLECTION)
            return info.points_count or 0   # points_count can be None in local mode
        except Exception:
            return 0
