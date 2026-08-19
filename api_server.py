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
import os
import sqlite3
import time
from contextlib import asynccontextmanager
from typing import List, Optional

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastembed import TextEmbedding
from langgraph.checkpoint.sqlite import SqliteSaver
from pydantic import BaseModel

from auth import DEMO_IDENTITIES, Identity, require_identity
from chargeback_agent import build_dispute_agent
from guardrails import AuditLogger, CostCircuitBreaker, RateLimiter
from merchant_db import init_db, MERCHANTS
from network_detection import detect_network_title_keys
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

_model: Optional[TextEmbedding] = None
_store: Optional[VectorStore]   = None
_agent = None   # DisputeAgent — built in lifespan after _store and _model are ready

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
    global _model, _store, _agent
    print("Loading embedding model (BAAI/bge-small-en-v1.5)...")
    _model = TextEmbedding("BAAI/bge-small-en-v1.5")
    _store = VectorStore(persist_path="./qdrant_data")
    print(f"Server ready. Knowledge base has {len(_store)} document(s).")

    # Initialise SQLite chargeback DB (creates + seeds if missing)
    init_db()
    print(f"Merchant DB ready ({len(MERCHANTS)} merchants).")

    # Build the LangGraph dispute agent — shares _store and _embed so only
    # one Qdrant connection is open in this process. Skipped gracefully when
    # GROQ_API_KEY is absent; the /dispute endpoint returns 503 in that case.
    if os.environ.get("GROQ_API_KEY"):
        try:
            _agent = build_dispute_agent(store=_store, embed_fn=_embed)
            print("Dispute agent (LangGraph) ready.")
        except Exception as exc:
            print(f"Dispute agent not available: {exc}")
    else:
        print("GROQ_API_KEY not set — /dispute endpoint will return 503.")

    yield
    # Nothing to clean up — Qdrant and FastEmbed handle their own teardown.


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
    A single document returned by the GET /search endpoint.

    Attributes:
        id      (str):   Unique document identifier (8-char MD5 hex).
        title   (str):   Human-readable document name.
        content (str):   Full text of the document.
        score   (float): Cosine similarity score between 0.0 and 1.0.
                         Higher means more relevant to the query.
    """
    id: str
    title: str
    content: str
    score: float


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
    """
    query: str
    additional_context: str = ""


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


@app.get("/search", summary="Search for relevant documents", response_model=List[SearchResult])
async def search(query: str, top_k: int = 3):
    """
    Find the most semantically relevant documents for a natural-language query.

    Workflow:
      1. Validate that the knowledge base is not empty.
      2. Embed the query into a 384-dim vector using FastEmbed.
      3. Ask Qdrant to return the top-k closest document vectors.
      4. Filter out weak matches (score below 0.65) to avoid returning
         irrelevant results for off-topic or vague queries.

    Score guide:
      0.85+  Strong match — answer confidently.
      0.70+  Good match   — answer with context.
      0.65+  Weak match   — returned but borderline.
      Below 0.65 — filtered out; returns 404 with a helpful message.

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

    top_k = min(top_k, 10)
    embedding = _embed(query)
    results = _store.search(embedding, top_k=top_k)

    # Boost in network/app-specific docs even for this plain, LLM-free
    # search — a query naming a consumer UPI app ("PhonePe", "Google Pay")
    # rather than the technical term ("UPI", "NPCI") matches no network
    # keyword otherwise, and raw semantic ranking doesn't reliably surface
    # the network-specific doc even when a title-exact match exists
    # (verified: absent from the top 10 results for exactly this kind of
    # question). Mirrors the boost chargeback_agent.py's _answer_question_node
    # applies, via the shared network_detection module, so both surfaces
    # behave consistently. filter_by_title() results carry score=1.0, so
    # they always clear the relevance threshold below.
    title_keys, _ = detect_network_title_keys(query)
    if title_keys:
        title_matches = _store.filter_by_title(title_keys)[:3]
        seen_ids = {r["id"] for r in results}
        for r in title_matches:
            if r["id"] not in seen_ids:
                results.append(r)
                seen_ids.add(r["id"])

    # Discard results below the relevance threshold, and re-sort — the
    # title-boosted matches above were appended after the semantic results,
    # not merged in score order, so without this a 1.0-score boosted match
    # would display last instead of first.
    results = sorted(
        (r for r in results if r["score"] >= 0.65),
        key=lambda r: r["score"],
        reverse=True,
    )

    if not results:
        raise HTTPException(
            status_code=404,
            detail="I don't have information about that. Try asking something related to chargebacks."
        )

    return [SearchResult(**r) for r in results]


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
def dispute(req: DisputeRequest, request: Request) -> DisputeResponse:
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

    Requires the GROQ_API_KEY environment variable to be set.
    Get a free key at https://console.groq.com

    Args:
        req (DisputeRequest): JSON body with query and optional additional_context.

    Returns:
        DisputeResponse: Result containing the final answer, decision, reason code,
                         evidence assessment, and needs_more_info flag.

    Raises:
        HTTPException 503: If GROQ_API_KEY is not configured.
        HTTPException 500: If the agent encounters an unexpected error.
    """
    if _agent is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Dispute agent is not available. "
                "Set GROQ_API_KEY and restart the server. "
                "Get a free key at https://console.groq.com"
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

    try:
        result = _agent.run(req.query, req.additional_context)

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
