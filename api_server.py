"""
api_server.py — Persistent RAG HTTP Server

Wraps the Qdrant vector store and FastEmbed model in a FastAPI server
that stays running until you stop it (Ctrl+C).

Unlike the MCP server (which starts and stops with each client), this server
stays alive indefinitely and accepts connections from any HTTP client —
browsers, mobile apps, curl, or other services.

Endpoints:
  GET  /          — serves the chat UI (chat.html)
  GET  /health    — confirm server is alive and return document count
  POST /add       — embed and index a document
  GET  /search    — semantic similarity search
  GET  /documents — list all indexed documents
  DELETE /documents — clear the entire knowledge base

Run:
    pip install -r requirements.txt
    python api_server.py

Then open http://localhost:8000/docs for the interactive Swagger UI.
"""

import hashlib
import sqlite3
import time
import uuid
from contextlib import asynccontextmanager
from typing import List, Optional

import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastembed import TextEmbedding
from fastembed.rerank.cross_encoder import TextCrossEncoder
from langgraph.checkpoint.sqlite import SqliteSaver
from pydantic import BaseModel

import classifier
import llm_provider
from auth import DEMO_IDENTITIES, Identity, require_identity, resolve_identity
from case_recommendations import (
    get_recommendation_history,
    init_schema as init_case_recommendations_schema,
    list_recent_recommendations,
)
from chargeback_agent import build_dispute_agent
from guardrails import AuditLogger, CostCircuitBreaker, RateLimiter
from merchant_db import init_db, list_open_chargebacks, MERCHANTS
from network_detection import DOMAIN_CANDIDATE_POOL_SIZE, detect_knowledge_domain, select_domain_chunk
from text_to_sql import query_chargebacks
from usermaster import get_auto_decision, set_auto_decision
from vector_store import VectorStore


def _is_llm_quota_error(exc: Exception) -> bool:
    """
    Detect an LLM provider rate-limit/quota exception by message content,
    rather than importing a provider-specific exception class — keeps this
    check working regardless of which LLM SDK raised it.
    """
    text = str(exc).lower()
    return any(s in text for s in (
        "rate_limit_exceeded", "rate limit", "429", "tokens per day",
        "tokens per minute", "quota",
    ))

# ---------------------------------------------------------------------------
# Module-level singletons
# Initialised once at startup and reused for every incoming request.
# ---------------------------------------------------------------------------

_model: Optional[TextEmbedding]       = None
_reranker: Optional[TextCrossEncoder] = None
_store: Optional[VectorStore]         = None
_agent = None   # DisputeAgent — built in lifespan after _store and _model are ready

# Checkpointer for /dispute conversation memory — a separate SQLite file
# from chargebacks.db, kept apart from authoritative transaction data on
# purpose (ephemeral conversation scratch state vs. the real chargeback
# record). SqliteSaver.from_conn_string() is a generator-based context
# manager, entered manually at startup and exited at shutdown since it
# needs to live for the whole process, not just one call.
_checkpointer_cm = None
_checkpointer = None

# Guardrail singletons — shared across all requests
_rate_limiter    = RateLimiter(max_requests=20, window_seconds=3600, abuse_threshold=5)
_audit_logger    = AuditLogger("audit.log")
_circuit_breaker = CostCircuitBreaker(max_daily_calls=500)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager — runs startup and shutdown logic.

    Everything before 'yield' executes once when the server starts.
    Everything after 'yield' executes once when the server stops (Ctrl+C).

    Loads the FastEmbed embedding model and connects to the Qdrant vector
    store on startup so they are ready for the first request immediately,
    rather than being lazily loaded on the first call (which would cause
    a slow first response).

    Args:
        app (FastAPI): The FastAPI application instance (injected by FastAPI).

    Yields:
        None: Control is returned to FastAPI to start serving requests.
    """
    global _model, _reranker, _store, _agent, _checkpointer_cm, _checkpointer
    print("Loading embedding model (BAAI/bge-small-en-v1.5)...")
    _model = TextEmbedding("BAAI/bge-small-en-v1.5")
    print("Loading reranker model (Xenova/ms-marco-MiniLM-L-6-v2)...")
    _reranker = TextCrossEncoder(model_name="Xenova/ms-marco-MiniLM-L-6-v2")
    _store = VectorStore(persist_path="./qdrant_data")
    print(f"Server ready. Knowledge base has {len(_store)} document(s).")

    # Initialise SQLite chargeback DB (creates + seeds if missing)
    init_db()
    print(f"Merchant DB ready ({len(MERCHANTS)} merchants).")

    init_case_recommendations_schema()
    print("Case recommendation history ready (case_recommendations table).")

    _checkpointer_cm = SqliteSaver.from_conn_string("checkpoints.db")
    _checkpointer    = _checkpointer_cm.__enter__()
    print("Conversation checkpointer ready (checkpoints.db).")

    # Build the LangGraph dispute agent — shares _store and _embed so only
    # one Qdrant connection is open in this process. Skipped gracefully when
    # the configured LLM provider's API key is absent (LLM_PROVIDER=groq|
    # openai, see llm_provider.py); the /dispute endpoint returns 503 in
    # that case.
    if llm_provider.is_configured():
        try:
            _agent = build_dispute_agent(store=_store, embed_fn=_embed, rerank_fn=_rerank,
                                          checkpointer=_checkpointer)
            print(f"Dispute agent (LangGraph, provider={llm_provider.get_provider_name()}) ready.")
        except Exception as exc:
            print(f"Dispute agent not available: {exc}")
    else:
        print(f"{llm_provider.get_env_key_name()} not set — /dispute endpoint will return 503.")

    yield

    if _checkpointer_cm is not None:
        _checkpointer_cm.__exit__(None, None, None)


app = FastAPI(
    title="Chargeback RAG API",
    description="Semantic search over a chargeback knowledge base using Qdrant + FastEmbed",
    version="2.0.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """
    HTTP middleware — enforce per-IP rate limits on search and dispute endpoints.

    Applies the sliding-window rate limiter to /search and /dispute.
    Returns 429 immediately if the limit is exceeded, without running the
    endpoint handler. All other paths (/, /health, /add, /documents) are
    passed through without rate limiting.

    Args:
        request  (Request):  The incoming HTTP request.
        call_next (callable): FastAPI's next handler in the chain.

    Returns:
        Response: 429 JSONResponse if rate-limited, otherwise the normal response.
    """
    if request.url.path in ("/search", "/dispute", "/query"):
        user_id = request.client.host if request.client else "unknown"
        error   = _rate_limiter.check(user_id)
        if error:
            return JSONResponse(status_code=429, content={"detail": error})
    return await call_next(request)


# ---------------------------------------------------------------------------
# Pydantic models — define the shape of request and response JSON bodies
# ---------------------------------------------------------------------------

class AddDocumentRequest(BaseModel):
    """
    Request body for the POST /add endpoint.

    Attributes:
        title   (str): Short name for the document (used to generate its ID).
        content (str): Full text to be embedded and stored in Qdrant.
        summary (str): Optional Overview paragraph for list queries.
    """
    title:   str
    content: str
    summary: str = ""


class SearchResult(BaseModel):
    """
    A single chunk returned by the GET /search endpoint.

    Backed by the chunk-level collection, not a whole document — `content`
    is a focused excerpt (one section/subsection/FAQ item), not an entire
    document's text, so a general question surfaces the relevant part of a
    document instead of its first N characters regardless of relevance.

    Attributes:
        id             (str):   Chunk identifier (document_id + position).
        title          (str):   Kept for backward compatibility with existing
                                callers/tests that key on document identity —
                                equal to document_title.
        content        (str):   The chunk's own text (a section excerpt, not
                                the whole document).
        score          (float): Cosine similarity score between 0.0 and 1.0.
        document_title (str):   Parent document's title (same as `title`).
        section        (Optional[str]): Enclosing ## heading text, if any.
    """
    id: str
    title: str
    content: str
    score: float
    document_title: str
    section: Optional[str] = None


class DocumentSummary(BaseModel):
    """
    Lightweight document representation returned by GET /documents.
    Contains only the ID and title — not the full content — to keep
    the list response compact.

    Attributes:
        id    (str): Unique document identifier.
        title (str): Human-readable document name.
    """
    id: str
    title: str


class DisputeRequest(BaseModel):
    """
    Request body for the POST /dispute endpoint.

    Attributes:
        query              (str): Merchant's description of the chargeback dispute.
        additional_context (str): Merchant's answer to the agent's follow-up question.
                                  Empty string on the first call; filled on the second.
        thread_id          (str): Conversation session id from a prior response's
                                  thread_id field. Empty on the first call — the
                                  server generates and returns a new one. Passing
                                  it back on a follow-up lets the agent resume via
                                  its LangGraph checkpointer instead of relying on
                                  additional_context alone. Validated server-side
                                  against the caller's own merchant scope (see the
                                  dispute() handler below) — a mismatched thread_id
                                  is rejected, never silently accepted.
        anchored_case_id   (str): The case_id from a prior response's own case_id
                                  field, if any. Empty on the first call and on any
                                  turn that never resolved to a specific case.
                                  Separate from — and much lighter-weight than —
                                  thread_id/the checkpointer above: this is a plain
                                  client-supplied HINT, not trusted state. The
                                  server still re-resolves it via the same
                                  merchant-scoped DB lookup a case reference found
                                  in `query` text would use (see
                                  chargeback_agent.py's _planner_node), and an
                                  explicit new case reference the merchant actually
                                  types always takes priority over this hint.
                                  Exists because chat.html reconstructs a case's
                                  identity by re-parsing accumulated conversation
                                  text on every turn — reliable most of the time,
                                  but confirmed live to occasionally lose track of
                                  a case named several turns back in a long,
                                  otherwise-unrelated conversation. Now that
                                  chat.html rounds-trips thread_id too, the
                                  checkpointer offers the same fallback more
                                  robustly (see _planner_node's fallback chain) —
                                  this hint stays wired up anyway as a second,
                                  independent line of defense, checked first since
                                  it's the cheaper/more direct of the two.
    """
    query: str
    additional_context: str = ""
    thread_id: str = ""
    anchored_case_id: str = ""


class DisputeResponse(BaseModel):
    """
    Response from the POST /dispute endpoint.

    Attributes:
        final_answer      (str):       Rebuttal letter, refund advice, or follow-up question.
        decision          (str):       "fight" or "refund". Empty if needs_more_info is True.
        reason_code       (str):       Identified reason code, e.g. "Visa 13.1".
        evidence_present  (List[str]): Evidence the merchant already mentioned.
        evidence_missing  (List[str]): Evidence still required.
        needs_more_info   (bool):      True when the agent returned a follow-up question
                                       instead of a final answer. Pass the merchant's reply
                                       as additional_context in the next request.
        thread_id         (str):       This conversation's session id — new or resumed.
                                       Pass back on the next request to resume via the
                                       checkpointer.
        retrieval_status  (str):       "good" | "ambiguous" | "bad" | "" (not assessed —
                                       e.g. no network detected yet). Whether the documents
                                       RETRIEVED were actually consistent with the detected
                                       network — a different question from is_grounded below,
                                       which checks whether the drafted ANSWER's own citations
                                       trace back to what was retrieved. Signal only for now;
                                       nothing currently blocks or retries on a "bad" result.
        retrieval_issues  (str):       Human-readable explanation when retrieval_status isn't
                                       "good".
        clarification_round  (int):    How many clarification rounds have already happened in
                                       this conversation (see chargeback_agent.py's
                                       MAX_CLARIFICATION_ROUNDS) — 0 on a fresh conversation.
        clarification_reason (str):    Why the pending question (if any) was asked — empty
                                       when final_answer isn't a question. Purely observational,
                                       not used for routing.
        case_id           (str):       The real case this turn resolved to, if any — empty for
                                       a generic question/list turn with no single case in
                                       focus. Lets a client link straight to
                                       GET /case-recommendations/{case_id} without re-parsing
                                       the query text.
    """
    final_answer:        str
    decision:            str
    reason_code:         str
    evidence_present:    List[str]
    evidence_missing:    List[str]
    needs_more_info:     bool
    confidence_score:    int
    is_grounded:         bool
    groundedness_issues: str
    retrieval_status:    str
    retrieval_issues:    str
    thread_id:           str
    clarification_round:  int
    clarification_reason: str
    case_id:               str


# ---------------------------------------------------------------------------
# Private helper functions
# ---------------------------------------------------------------------------

def _embed(text: str) -> List[float]:
    """
    Convert a plain text string into a 384-dimensional embedding vector.

    Calls the FastEmbed model that was loaded at server startup.
    The embed() method returns a generator; next() pulls the single result
    and tolist() converts it from a numpy array to a Python list of floats.

    Args:
        text (str): Any plain text to embed (a query or a document).

    Returns:
        List[float]: 384 floating-point numbers encoding the semantic
                     meaning of the input text.
    """
    return next(_model.embed([text])).tolist()


def _rerank(query: str, documents: List[str]) -> List[float]:
    """
    Score how relevant each document is to the query using a local
    cross-encoder (loaded at server startup, same lifecycle as _model).

    Unlike cosine similarity (comparing two independent embeddings), a
    cross-encoder reads the query and each document together, which makes
    it a stronger — but slower — relevance signal. Used to improve chunk
    selection specifically for open-ended questions with no confidently
    identified reason code (see chargeback_agent.py's _answer_question_node
    and this file's search_documents()) — the one case where cosine
    similarity is the only ranking signal available.

    Returns raw, unbounded logits (e.g. ~+11 for a strong match, ~-11 for
    an unrelated one) — NOT a 0-1 score comparable to cosine similarity.
    Callers must not compare this against the existing similarity
    thresholds (>= 0.65 etc.) used elsewhere in this codebase.

    Args:
        query: The user's question.
        documents: Candidate chunk contents to score against the query.

    Returns:
        List[float]: One relevance score per document, same order as input.
    """
    return list(_reranker.rerank(query, documents))


def _doc_id(title: str) -> str:
    """
    Generate a stable, deterministic 8-character document ID from a title.

    Uses MD5 so the same title always produces the same ID regardless of
    when or where the function is called. This ensures that re-indexing the
    same document overwrites the existing Qdrant point instead of creating
    a duplicate.

    Args:
        title (str): The document title to hash.

    Returns:
        str: First 8 characters of the MD5 hex digest (e.g. 'a1b2c3d4').
    """
    return hashlib.md5(title.encode()).hexdigest()[:8]


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@app.get("/", include_in_schema=False)
def chat_ui():
    """
    Serve the chatbot web interface.

    Returns the static chat.html file which provides a browser-based UI
    for querying the chargeback knowledge base. Excluded from the API
    schema (Swagger docs) since it is not a JSON endpoint.

    Returns:
        FileResponse: The chat.html file served as text/html.
    """
    return FileResponse("chat.html")


@app.get("/health")
def health():
    """
    Health check endpoint — confirms the server is running and responsive.

    Can be used by load balancers, monitoring tools, or the client app to
    verify the server is alive before sending queries.

    Returns:
        dict: A JSON object with:
              - status    (str): Always 'ok' if the server is reachable.
              - documents (int): Number of documents currently in Qdrant.
    """
    return {
        "status":           "ok",
        "documents":        len(_store),
        "llm_calls_today":  _circuit_breaker.daily_count,
        "llm_calls_limit":  _circuit_breaker.daily_limit,
        "circuit_open":     _circuit_breaker.is_open(),
    }


@app.post("/add", summary="Add a document to the knowledge base")
async def add_document(req: AddDocumentRequest) -> dict:
    """
    Embed a document and store it in the Qdrant knowledge base.

    Workflow:
      1. Generate a deterministic 8-char ID from the title using MD5.
      2. Embed the content text into a 384-dim vector using FastEmbed.
      3. Upsert into Qdrant — overwrites if a document with the same
         title already exists, preventing duplicates on re-indexing.

    Args:
        req (AddDocumentRequest): JSON body containing 'title' and 'content'.

    Returns:
        dict: A JSON object with:
              - message         (str): Confirmation text.
              - id              (str): The assigned document ID.
              - total_documents (int): Updated count of all documents in store.
    """
    try:
        doc_id = _doc_id(req.title)
        embedding = _embed(req.content)
        _store.add_document(doc_id, req.title, req.content, embedding, summary=req.summary)
        return {
            "message": f"Indexed '{req.title}'",
            "id": doc_id,
            "total_documents": len(_store),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def search_documents(store: VectorStore, embed_fn, query: str, top_k: int = 3, rerank_fn=None) -> List[dict]:
    """
    Core retrieval logic for GET /search, factored out of the route handler so
    it can be called directly (in-process, no HTTP, no rate limiting) by
    eval_retrieval.py's golden-set harness — going through the live HTTP
    endpoint for a 40+ query eval run trips RateLimiter's 20-requests/hour cap
    partway through, silently turning the back half of a run into 429s that
    look identical to genuine retrieval misses. This function is the single
    source of truth both callers share, so eval results reflect the exact
    same ranking logic real users get.

    Chunk-level, not whole-document: earlier this session, a whole-document
    version of this function needed a network-detection title-boost to
    compensate for embedding dilution — even the single most relevant
    document for a UPI question ("RuPay and NPCI Dispute Process — Complete
    Overview") scored 0.554, dead last among 11 NPCI-titled docs, because its
    one vector had to represent the doc's entire history/structure/timelines
    at once. Chunking substantially reduces this: that same doc's best
    section ("Merchant Obligations Under the NPCI Framework") rose to 0.670
    once split out on its own. But verified after migrating — that's still
    not always enough on its own: a generic FAQ chunk phrased "What happens
    if I don't respond..." can outscore a topically-correct but more
    narrative chunk purely on question-form similarity, regardless of topic
    (confirmed: exactly this happened for the query that motivated this
    whole migration, scoring ~0.80 against the NPCI chunk's 0.67). So a
    lighter-weight version of the old boost is still needed — not a title
    match against 11 loosely-related docs with a fake score, but a real,
    separately-ranked query into just the detected network's chunks, merged
    into the general candidates and re-sorted by genuine score. This can't
    resurface the old bug (an arbitrary wrong-code chunk winning by luck):
    everything here is ranked by real cosine similarity throughout, at chunk
    granularity, so only genuinely close matches make the merged list.

    Workflow:
      1. Embed the query into a 384-dim vector using FastEmbed.
      2. Ask Qdrant to return the top-k closest chunk vectors.
      3. If a network/app is named, also fetch top domain-specific chunks
         and merge them in (dedup by chunk_id).
      4. Filter out weak matches (score below 0.65), re-sort, cap to top_k.

    Score guide:
      0.85+  Strong match — answer confidently.
      0.70+  Good match   — answer with context.
      0.65+  Weak match   — returned but borderline.
      Below 0.65 — filtered out.

    Args:
        store:     Connected VectorStore.
        embed_fn:  Callable (str) -> list[float].
        query:     Natural-language question or search phrase.
        top_k:     Number of results to return.
        rerank_fn: Optional callable (query, documents) -> list[float] — a
                   cross-encoder reranker (see _rerank). When given, replaces
                   plain cosine-similarity selection for the general
                   candidate pool with reranked order; None falls back to
                   today's behavior unchanged.

    Returns:
        List[dict]: Ranked list of matching chunks with scores. Empty list
                    if the chunk collection has no documents or nothing
                    clears the relevance threshold.
    """
    embedding = embed_fn(query)

    # Cross-encoder rerank when available — see chargeback_agent.py's
    # _answer_question_node for the identical pattern and full reasoning
    # (kept in sync deliberately: both this route and that node build their
    # general candidate pool the same way, independently of each other).
    # rerank_score is additive only; nothing below reads it, so the
    # domain-boost logic that follows is unaffected either way.
    wide_candidates = store.search_chunks(embedding, top_k=DOMAIN_CANDIDATE_POOL_SIZE)
    results = None
    if wide_candidates and rerank_fn is not None:
        try:
            docs   = [c["content"] for c in wide_candidates]
            scores = rerank_fn(query, docs)
            for c, s in zip(wide_candidates, scores):
                c["rerank_score"] = s
            wide_candidates.sort(key=lambda c: c["rerank_score"], reverse=True)
            results = wide_candidates[:top_k]
        except Exception:
            results = None
    if results is None:
        results = [r for r in wide_candidates[:top_k] if r["score"] >= 0.65]

    domain = detect_knowledge_domain(query)
    promoted = None
    if domain:
        domain_hits = store.search_chunks(
            embedding, top_k=DOMAIN_CANDIDATE_POOL_SIZE, knowledge_domain=domain
        )
        seen = {r["chunk_id"] for r in results}

        # select_domain_chunk() prefers the domain's Overview document for a
        # general query rather than whatever scores marginally highest — a
        # narrow reason-code page's denser vocabulary routinely outscores
        # genuinely general content on raw similarity within one domain
        # (see network_detection.py for the measurement that showed this).
        _, detected_code = classifier.extract_network_and_code(query)
        tier, best = select_domain_chunk(domain_hits, "" if detected_code == "Unknown" else detected_code)

        if best and best["chunk_id"] not in seen:
            if tier == "strong":
                # Leads the answer (results[0], the large primary bubble in
                # chat.html) — a named network is a strong enough signal
                # that content clearing the same 0.65 bar as everything else
                # shouldn't just appear somewhere in the list. Confirmed
                # necessary: an earlier version only guaranteed a *slot*, but
                # the plain score-sort below put it back at its natural rank
                # regardless — a 0.69-scoring NPCI chunk was included yet
                # still displayed 4th, behind generic content the user
                # actually read as the answer.
                promoted = best
                seen.add(best["chunk_id"])
            else:
                # Below the full bar — guarantee a slot, not the lead.
                results = results[: max(top_k - 1, 0)] + [best]
                seen.add(best["chunk_id"])

        for r in domain_hits:
            if r["score"] >= 0.65 and r["chunk_id"] not in seen:
                results.append(r)
                seen.add(r["chunk_id"])

    results = sorted(results, key=lambda r: r["score"], reverse=True)
    if promoted:
        results = [promoted] + [r for r in results if r["chunk_id"] != promoted["chunk_id"]]
    return results[:top_k]


@app.get("/search", summary="Search for relevant documents", response_model=List[SearchResult])
async def search(query: str, top_k: int = 3):
    """
    Find the most semantically relevant documents for a natural-language query.

    Thin route wrapper around search_documents() — see that function for the
    retrieval workflow. This layer only handles HTTP concerns: the empty-store
    404, the top_k=10 ceiling, and the no-results 404.

    Args:
        query (str): Natural-language question or search phrase.
        top_k (int): Number of results to return. Capped at 10. Defaults to 3.

    Returns:
        List[SearchResult]: Ranked list of matching documents with scores.

    Raises:
        HTTPException 404: If the knowledge base is empty, or if no documents
                           score above the 0.65 relevance threshold.
    """
    if len(_store) == 0:
        raise HTTPException(
            status_code=404,
            detail="Knowledge base is empty. POST /add some documents first."
        )

    results = search_documents(_store, _embed, query, top_k=min(top_k, 10), rerank_fn=_rerank)

    if not results:
        raise HTTPException(
            status_code=404,
            detail="I don't have information about that. Try asking something related to chargebacks."
        )

    return [
        SearchResult(
            id=r["chunk_id"],
            title=r["document_title"],
            content=r["content"],
            score=r["score"],
            document_title=r["document_title"],
            section=r.get("section"),
        )
        for r in results
    ]


@app.get("/documents", summary="List all indexed documents", response_model=List[DocumentSummary])
async def list_documents():
    """
    Return a summary list of every document in the knowledge base.

    Fetches only the ID and title of each document — not the full content —
    to keep the response lightweight. Useful for verifying what has been
    indexed without retrieving large amounts of text.

    Returns:
        List[DocumentSummary]: List of all documents with their id and title.
                               Returns an empty list if no documents are indexed.
    """
    docs = _store.list_documents()
    return [DocumentSummary(**d) for d in docs]


@app.delete("/documents", summary="Clear the entire knowledge base")
def clear_documents():
    """
    Delete all documents and vectors from the Qdrant collection.

    This operation is permanent and cannot be undone. After calling this
    endpoint, the knowledge base is empty and all documents must be
    re-indexed by running load_chargeback_docs.py again.

    Returns:
        dict: Confirmation message: {"message": "Knowledge base cleared."}
    """
    _store.clear()
    return {"message": "Knowledge base cleared."}


@app.post("/dispute", summary="Run the LangGraph dispute agent", response_model=DisputeResponse)
def dispute(
    req: DisputeRequest,
    request: Request,
    x_merchant_key: str = Header(default=""),
) -> DisputeResponse:
    """
    Analyse a chargeback dispute and generate a rebuttal letter or refund advice.

    Runs the full LangGraph workflow:
      classify → search → evaluate → (ask_user | decide → generate → reflect)

    Two-turn conversation pattern:
      Turn 1 — POST {"query": "I received a Visa chargeback..."}
        If the agent needs more details, returns the follow-up question
        with needs_more_info=True. Present this question to the merchant.

      Turn 2 — POST {"query": "...", "additional_context": "merchant's answer"}
        Pass the same original query plus the merchant's reply. The agent
        skips asking again and returns the final letter or advice.

    Authentication is OPTIONAL here, unlike /query — the Q&A tab also calls
    this endpoint (for general knowledge-base questions) and must stay
    usable with no login at all. Pass X-Merchant-Key to unlock case-specific
    grounding: chargeback_agent.py's planner node already knows how to look
    up a real chargeback (by UTR or case ID mentioned in the query) scoped
    to the caller's own merchant_id and ground the answer in the real row
    instead of guessing from free text — this was previously unreachable
    since nothing ever resolved an identity for this route. An absent or
    invalid key behaves exactly as before this existed: merchant_id="",
    same as always.

    Requires an LLM provider to be configured — see llm_provider.py
    (LLM_PROVIDER=groq, default, + GROQ_API_KEY; or LLM_PROVIDER=openai +
    OPENAI_API_KEY).

    Args:
        req (DisputeRequest): JSON body with query and optional additional_context.
        x_merchant_key (str): Optional caller identity — see above.

    Returns:
        DisputeResponse: Result containing the final answer, decision, reason code,
                         evidence assessment, and needs_more_info flag.

    Raises:
        HTTPException 503: If the configured LLM provider's API key is not set.
        HTTPException 500: If the agent encounters an unexpected error.
    """
    if _agent is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Dispute agent is not available. "
                f"Set {llm_provider.get_env_key_name()} and restart the server "
                f"(current LLM_PROVIDER={llm_provider.get_provider_name()})."
            ),
        )

    # Circuit breaker — reject if daily LLM call limit is reached
    if _circuit_breaker.is_open():
        raise HTTPException(
            status_code=503,
            detail=(
                f"Daily request limit reached ({_circuit_breaker.daily_limit} LLM calls). "
                "Service will resume tomorrow."
            ),
        )

    user_id    = request.client.host if request.client else "unknown"
    start_time = time.time()

    # Optional identity — resolve_identity() returns None for a missing or
    # invalid key rather than raising, unlike require_identity(), so an
    # anonymous caller (e.g. the Q&A tab) is unaffected.
    identity    = resolve_identity(x_merchant_key) if x_merchant_key else None
    merchant_id = identity.merchant_id if identity and identity.merchant_id else ""

    # thread_id is prefixed with the resolving caller's own merchant scope
    # ("anon" for no/invalid key) at creation time, and that prefix is
    # checked on every resume — server-enforced, not just trusted from the
    # client, same "resolve and enforce scope server-side" pattern
    # text_to_sql.py already uses for cross-merchant query scoping. Without
    # this, any caller who obtained/guessed another merchant's thread_id
    # could resume that merchant's dispute conversation — a real risk now
    # that chat.html actually round-trips thread_id and the checkpointer
    # resumes state from it (see chargeback_agent.py's _planner_node
    # fallback chain), not just a hypothetical for a future wiring-up.
    owner_tag = merchant_id or "anon"
    thread_id = req.thread_id
    if thread_id and not thread_id.startswith(f"{owner_tag}:"):
        raise HTTPException(
            status_code=403,
            detail="Invalid or mismatched conversation session.",
        )
    if not thread_id:
        thread_id = f"{owner_tag}:{uuid.uuid4()}"

    try:
        result = _agent.run(req.query, req.additional_context, merchant_id=merchant_id,
                             thread_id=thread_id, anchored_case_id=req.anchored_case_id)

        # Record LLM calls made (~7 per full dispute run, 1 for rejected queries)
        calls_made = 1 if not result.get("is_valid_query") else 7
        _circuit_breaker.record_calls(calls_made)

        # Record abuse when the validate node rejected the input
        if not result.get("is_valid_query"):
            _rate_limiter.record_abuse(user_id)

        # Audit log — PII masking happens inside AuditLogger.log()
        _audit_logger.log(
            user_id    = user_id,
            endpoint   = "/dispute",
            query      = req.query,
            result     = result,
            latency_ms = int((time.time() - start_time) * 1000),
        )

        return DisputeResponse(
            final_answer        = result["final_answer"],
            decision            = result["decision"],
            reason_code         = result["reason_code"],
            evidence_present    = result["evidence_present"],
            evidence_missing    = result["evidence_missing"],
            needs_more_info     = result["needs_more_info"],
            confidence_score    = result.get("confidence_score",    0),
            is_grounded         = result.get("is_grounded",         True),
            groundedness_issues = result.get("groundedness_issues", ""),
            retrieval_status    = result.get("retrieval_status",    ""),
            retrieval_issues    = result.get("retrieval_issues",    ""),
            thread_id           = result.get("thread_id", thread_id),
            clarification_round  = result.get("clarification_round",  0),
            clarification_reason = result.get("clarification_reason", ""),
            case_id               = result.get("case_id", ""),
        )

    except Exception as exc:
        if _is_llm_quota_error(exc):
            # Don't leak the provider's raw error — it names the model,
            # org ID, and a billing upgrade link that are none of the
            # end user's business.
            raise HTTPException(
                status_code=503,
                detail=(
                    "Our AI assistant has reached its usage limit for now. "
                    "Please try again in a little while."
                ),
            ) from exc
        raise HTTPException(status_code=500, detail=str(exc)) from exc


class OpenChargebackSummary(BaseModel):
    case_id:            str
    utr:                str
    reason_code:        str
    reason_description: str
    chargeback_amount:  float
    response_deadline:  str


class OpenChargebacksResponse(BaseModel):
    total_open: int                          # total Open count, not just what's returned below
    cases:      List[OpenChargebackSummary]


@app.get("/my-open-chargebacks", summary="List the caller's own open chargebacks",
         response_model=OpenChargebacksResponse)
def my_open_chargebacks(identity: Identity = Depends(require_identity)) -> OpenChargebacksResponse:
    """
    Merchant-only. Powers the Dispute Assistant tab's case-picker: lets a
    logged-in merchant reference one of their real open chargebacks instead
    of needing to know its exact UTR/case ID, and see an at-a-glance count
    of what's outstanding. Same merchant-only pattern as /auto-decision —
    admins don't have a single merchant's cases to list.
    """
    if identity.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Open-chargeback listing is merchant-only.",
        )
    rows = list_open_chargebacks(identity.merchant_id, limit=10)
    total_open = len(list_open_chargebacks(identity.merchant_id, limit=10_000))
    return OpenChargebacksResponse(
        total_open=total_open,
        cases=[OpenChargebackSummary(**r) for r in rows],
    )


# ---------------------------------------------------------------------------
# Live-chat recommendation history (case_recommendations.py)
# ---------------------------------------------------------------------------

class CaseRecommendationEntry(BaseModel):
    action:           str
    reason:           str
    source:           str
    origin:           str
    confidence_score: Optional[int]
    thread_id:        Optional[str]
    created_at:       str


class CaseRecommendationHistoryResponse(BaseModel):
    case_id: str
    history: List[CaseRecommendationEntry]


@app.get("/case-recommendations/{case_id}", summary="Recommendation history for one case",
         response_model=CaseRecommendationHistoryResponse)
def case_recommendation_history(
    case_id:  str,
    identity: Identity = Depends(require_identity),
) -> CaseRecommendationHistoryResponse:
    """
    Every live-chat-derived fight/refund recommendation ever recorded for
    one case, most recent first — the queryable counterpart to
    guardrails.AuditLogger's audit.log (append-only JSONL, not
    joinable/queryable). A merchant caller only ever sees their OWN case's
    history; a case_id belonging to another merchant naturally returns an
    empty list rather than an error — never confirms or denies it exists,
    same defense-in-depth pattern as merchant_db.list_open_chargebacks and
    the case_ref_not_found handling in chargeback_agent.py. Admin roles can
    look up any case_id unscoped.
    """
    scope_merchant_id = None if identity.is_admin else identity.merchant_id
    rows = get_recommendation_history(case_id, merchant_id=scope_merchant_id)
    return CaseRecommendationHistoryResponse(
        case_id=case_id,
        history=[
            CaseRecommendationEntry(
                action=r["action"], reason=r["reason"], source=r["source"],
                origin=r["origin"], confidence_score=r["confidence_score"],
                thread_id=r["thread_id"], created_at=r["created_at"],
            )
            for r in rows
        ],
    )


class RecentRecommendationEntry(CaseRecommendationEntry):
    case_id:     str
    merchant_id: str


class RecentRecommendationsResponse(BaseModel):
    total:           int
    recommendations: List[RecentRecommendationEntry]


@app.get("/case-recommendations", summary="Recent recommendations (admin: all/one merchant; merchant: own only)",
         response_model=RecentRecommendationsResponse)
def recent_case_recommendations(
    merchant_id: str = "",   # admin-only narrowing; ignored for merchant callers
    days:        int = 30,
    identity:    Identity = Depends(require_identity),
) -> RecentRecommendationsResponse:
    """
    Cross-case "recommendations in the last N days" view. Merchant callers
    are always forced to their own merchant_id (the query param is ignored
    for them, same defense-in-depth as text_to_sql.py's forced WHERE
    merchant_id filter) — admin roles may narrow to one merchant via the
    param or leave it blank to see every merchant's recommendations.
    """
    scope = (merchant_id or None) if identity.is_admin else identity.merchant_id
    rows = list_recent_recommendations(merchant_id=scope, days=days)
    return RecentRecommendationsResponse(
        total=len(rows),
        recommendations=[
            RecentRecommendationEntry(
                case_id=r["case_id"], merchant_id=r["merchant_id"],
                action=r["action"], reason=r["reason"], source=r["source"],
                origin=r["origin"], confidence_score=r["confidence_score"],
                thread_id=r["thread_id"], created_at=r["created_at"],
            )
            for r in rows
        ],
    )


# ---------------------------------------------------------------------------
# Merchant DB query endpoint
# ---------------------------------------------------------------------------

class QueryRequest(BaseModel):
    question:     str            # natural-language question; merchant_id comes from X-Merchant-Key header
    previous_sql: str = ""       # SQL executed for the prior turn, if any — lets the
                                  # LLM resolve follow-ups like "give me the complete row
                                  # for this earlier result". Client-echoed, not trusted:
                                  # only informs the prompt, never bypasses the safety
                                  # pipeline the freshly-generated SQL still goes through.


class QueryResponse(BaseModel):
    answer:    str        # formatted human-readable result
    sql:       str        # SQL that was executed
    rows:      int        # number of rows returned
    error:     str        # non-empty if something went wrong
    rows_data: List[dict] # raw masked rows for client-side CSV export


@app.get("/merchants", summary="List available demo identities with their API keys")
def list_merchants():
    """
    Return demo identities (merchants + bank admin accounts) with their API
    keys, for the UI login selector. Name kept as /merchants for backward
    compatibility with the existing frontend fetch call.
    """
    return [
        {
            "id":          d["merchant_id"] or d["user_id"],
            "name":        d["username"],
            "role":        d["role"],
            "merchant_id": d["merchant_id"],
            "api_key":     d["api_key"],
        }
        for d in DEMO_IDENTITIES
    ]


@app.post("/query", summary="Query chargeback DB in natural language",
          response_model=QueryResponse)
def merchant_query(
    req:      QueryRequest,
    request:  Request,
    identity: Identity = Depends(require_identity),   # resolved from X-Merchant-Key header
) -> QueryResponse:
    """
    Convert a natural-language question to SQL and return results.

    Authentication:
      Pass X-Merchant-Key header — the caller's role and merchant scope are
      resolved server-side from the usermaster table. The request body does
      not accept merchant_id (ignored if sent).

    Security pipeline in text_to_sql.py:
      1. Prompt injection check on the question (+ cross-merchant escalation
         check when role='merchant')
      2. LLM generates SQL, scoped per role
      3. SQL validated: SELECT only, no UNION/comments/writes
      4. Merchant filter enforced via parameterized binding for role='merchant';
         admin roles (bankopsadmin, bankadmin_maker, bankadmin_checker) query
         across all merchants, or one specific merchant if named in the question
      5. Raw DB errors suppressed (never leak schema to client)
    """
    user_id    = request.client.host if request.client else "unknown"
    start_time = time.time()

    result = query_chargebacks(
        question     = req.question,
        role         = identity.role,
        merchant_id  = identity.merchant_id,   # from verified header, not client body
        db_path      = "chargebacks.db",
        previous_sql = req.previous_sql,
    )

    _audit_logger.log(
        user_id    = f"{user_id}:{identity.user_id}:{identity.role}",
        endpoint   = "/query",
        query      = req.question,
        result     = {
            "rows":       result["rows"],
            "error":      result["error"],
            "suspicious": result.get("suspicious", False),
        },
        latency_ms = int((time.time() - start_time) * 1000),
    )

    if result["error"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return QueryResponse(
        answer    = result["answer"],
        sql       = result["sql"],
        rows      = result["rows"],
        error     = result["error"],
        rows_data = result.get("rows_data", []),
    )


# ---------------------------------------------------------------------------
# Auto-decision preference
# ---------------------------------------------------------------------------

class AutoDecisionRequest(BaseModel):
    enabled: bool   # True -> 'auto', False -> 'manual'


class AutoDecisionResponse(BaseModel):
    auto_decision: str   # 'manual' | 'auto'


@app.get("/auto-decision", summary="Get this merchant's auto-decision preference",
         response_model=AutoDecisionResponse)
def get_auto_decision_preference(identity: Identity = Depends(require_identity)) -> AutoDecisionResponse:
    """
    Merchant-only. Admin roles have no merchant_id, so this preference
    doesn't apply to them — they're not the ones with chargebacks to resolve.
    """
    if identity.is_admin:
        raise HTTPException(status_code=403, detail="Auto-decision preference is merchant-only.")
    value = get_auto_decision(identity.merchant_id) or "manual"
    return AutoDecisionResponse(auto_decision=value)


@app.post("/auto-decision", summary="Set this merchant's auto-decision preference",
          response_model=AutoDecisionResponse)
def set_auto_decision_preference(
    req:      AutoDecisionRequest,
    identity: Identity = Depends(require_identity),
) -> AutoDecisionResponse:
    """
    Merchant-only. When enabled, auto_decision_poller.py (run separately, e.g.
    via cron) will auto-apply decision_rules.py's per-case recommendation to
    this merchant's new Open chargebacks without waiting for manual
    confirmation — it does not blanket-accept or blanket-fight regardless of
    the case, it just removes the human-confirmation step from the same rule
    engine the interactive dispute agent already uses.
    """
    if identity.is_admin:
        raise HTTPException(status_code=403, detail="Auto-decision preference is merchant-only.")
    value = "auto" if req.enabled else "manual"
    ok = set_auto_decision(identity.merchant_id, value)
    if not ok:
        raise HTTPException(status_code=500, detail="Could not update preference.")
    return AutoDecisionResponse(auto_decision=value)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",  # accept connections from any device on the network
        port=8000,
        reload=False,
    )
