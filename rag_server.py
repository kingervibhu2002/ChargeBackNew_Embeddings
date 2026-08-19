"""
MCP RAG Server

Exposes three tools that any MCP-compatible client (Claude, etc.) can call:
  - add_document   : embed and index a document into Qdrant
  - search         : retrieve top-k most relevant documents for a query
  - list_documents : list every indexed document's title and ID

The server speaks the MCP stdio protocol. It is spawned automatically as a
subprocess by rag_client.py and test_search.py — you do not run it directly.

Architecture:
  Client (rag_client.py)
    → spawns this process via stdio
    → calls tools by name
    → this server embeds text with FastEmbed and queries Qdrant
    → returns results as JSON strings
"""

import hashlib
import json
import sys

from fastembed import TextEmbedding
from mcp.server.fastmcp import FastMCP

from vector_store import VectorStore

# ---------------------------------------------------------------------------
# Singletons — loaded once at server startup, shared across all tool calls
# ---------------------------------------------------------------------------

mcp = FastMCP("rag-server")

# BAAI/bge-small-en-v1.5:
#   - 130 MB download (cached after first run)
#   - Produces 384-dimensional embeddings
#   - Uses ONNX runtime — no PyTorch dependency
#
# Startup diagnostics go to stderr, not stdout — stdout is reserved for the
# MCP JSON-RPC protocol stream. A stray stdout print() here gets read by the
# client as a malformed protocol message ("Failed to parse JSONRPC message").
_EMBED_MODEL = "BAAI/bge-small-en-v1.5"
print(f"[rag_server] Loading embedding model '{_EMBED_MODEL}' …", file=sys.stderr, flush=True)
_model = TextEmbedding(_EMBED_MODEL)
print("[rag_server] Model ready.", file=sys.stderr, flush=True)

_store = VectorStore(persist_path="./qdrant_data")


# ---------------------------------------------------------------------------
# Private helper functions
# ---------------------------------------------------------------------------

def _embed(text: str) -> list[float]:
    """
    Convert a plain text string into a 384-dimensional embedding vector.

    Uses the FastEmbed TextEmbedding model loaded at server startup.
    The embed() method returns a generator; next() extracts the single result
    and tolist() converts the numpy array to a plain Python list of floats.

    This function is called for both indexing (documents) and searching
    (queries) so that both live in the same vector space, making cosine
    similarity scores meaningful.

    Args:
        text (str): Any plain text string to be embedded.

    Returns:
        list[float]: A list of 384 floating-point numbers representing
                     the semantic meaning of the input text.
    """
    return next(_model.embed([text])).tolist()


def _doc_id(title: str) -> str:
    """
    Generate a stable, deterministic 8-character document ID from a title.

    Uses MD5 hashing to ensure the same title always produces the same ID
    across different Python processes and runs. This is critical for Qdrant
    upsert behaviour — if we used Python's built-in hash(), the ID would
    change every run (Python randomises hash seeds), causing duplicate entries.

    Args:
        title (str): The document title to hash.

    Returns:
        str: An 8-character hexadecimal string (e.g. 'a1b2c3d4').
             Derived from the first 8 characters of the MD5 digest.
    """
    return hashlib.md5(title.encode()).hexdigest()[:8]


# ---------------------------------------------------------------------------
# MCP Tool definitions
# ---------------------------------------------------------------------------

@mcp.tool()
def add_document(
    title: str,
    content: str,
    summary: str = "",
    section: str = "",
    network: str = "",
    reason_code: str = "",
    document_type: str = "",
    keywords: str = "",
) -> str:
    """
    Add a new document (or update an existing one) in the RAG knowledge base.

    Workflow:
      1. Generate a deterministic ID from the title using MD5.
      2. Embed the content text into a 384-dim vector using FastEmbed.
      3. Upsert the vector + payload into Qdrant (overwrites if ID exists).

    Args:
        title         (str): Short, descriptive name for the document.
        content       (str): Full text content of the document to be embedded.
        summary       (str): Optional short overview paragraph (~2-3 sentences).
        section       (str): Encyclopedia section folder, e.g. '04_Visa'.
        network       (str): Card network this doc covers, e.g. 'Visa'.
        reason_code   (str): Reason code if doc is code-specific, e.g. '13.1'.
        document_type (str): Doc category, e.g. 'reason_code', 'policy', 'guide'.
        keywords      (str): Comma-separated keywords for BM25 boosting.

    Returns:
        str: Confirmation with document title, ID, and total doc count.
    """
    doc_id    = _doc_id(title)
    embedding = _embed(content)
    kw_list   = [k.strip() for k in keywords.split(",") if k.strip()] if keywords else []
    _store.add_document(
        doc_id, title, content, embedding,
        summary=summary,
        section=section,
        network=network,
        reason_code=reason_code,
        document_type=document_type,
        keywords=kw_list,
    )
    return f"Indexed '{title}' → id={doc_id}  (total docs: {len(_store)})"


@mcp.tool()
def search(query: str, top_k: int = 3) -> str:
    """
    Retrieve the most relevant documents for a natural-language query.

    Workflow:
      1. Check that the knowledge base is not empty.
      2. Embed the query text into a 384-dim vector using FastEmbed.
      3. Ask Qdrant to find the top-k vectors closest to the query vector.
      4. Return the matching documents with their similarity scores as JSON.

    The similarity score ranges from 0.0 (unrelated) to 1.0 (identical).
    Scores above 0.70 indicate a strong, reliable match for this domain.

    Args:
        query (str): A natural-language question or search phrase.
                     Example: "What evidence do I need to fight a chargeback?"
        top_k (int): Maximum number of results to return. Defaults to 3.
                     Higher values return more context but increase LLM token cost.

    Returns:
        str: A JSON array string where each element contains:
               - id      (str):   Document identifier.
               - title   (str):   Document title.
               - content (str):   Full document text.
               - score   (float): Cosine similarity score (0.0–1.0).
             Returns an error message string (not JSON) if the store is empty
             or if an exception occurs during embedding or search.
    """
    if len(_store) == 0:
        return "The knowledge base is empty. Add documents first with add_document."

    try:
        embedding = _embed(query)
        results = _store.search(embedding, top_k=top_k)
        return json.dumps(results, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"[search error] {type(e).__name__}: {e}"


@mcp.tool()
def list_documents() -> str:
    """
    List every document currently indexed in the knowledge base.

    Returns only the ID and title of each document — not the full content —
    to keep the response compact. Useful for verifying what has been indexed
    before running searches.

    Returns:
        str: A JSON array string where each element contains:
               - id    (str): Document identifier.
               - title (str): Document title.
             Returns the string "No documents indexed yet." if the store is empty.
    """
    docs = _store.list_documents()
    if not docs:
        return "No documents indexed yet."
    return json.dumps(docs, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
