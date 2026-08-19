# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A RAG-powered chargeback dispute assistant for Airtel Payments Bank merchants and bank admin staff. It combines a Qdrant-backed knowledge base (chargeback reason codes, evidence requirements, dispute lifecycle — 149 docs in `chargeback-encyclopedia/`) with a LangGraph dispute-resolution agent and a natural-language-to-SQL layer over merchant chargeback records, all served through one FastAPI app (`api_server.py`) with a single-file chat UI (`chat.html`).

## Commands

Setup:
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export GROQ_API_KEY=your_key_here   # required for chargeback_agent.py + text_to_sql.py; free at console.groq.com
```

Run the server (serves the chat UI at `/`, Swagger docs at `/docs`):
```bash
python api_server.py
```
Runs on `0.0.0.0:8000`. Only one process can hold this server at a time — Qdrant's local file mode (`./qdrant_data`) takes an exclusive lock, so a second instance fails at startup with `RuntimeError: Storage folder ... already accessed by another instance`.

(Re)seed the SQLite databases (`chargebacks.db`):
```bash
python merchant_db.py    # drops and recreates the `chargebacks` table + demo data
python usermaster.py     # recreates the `usermaster` table + demo login identities
```

Index the knowledge base into Qdrant (only needed once, or after editing `chargeback-encyclopedia/`):
```bash
python load_encyclopedia.py
python load_chargeback_docs.py
```

Tests (plain pytest, no config file — discovery is by `test_*.py` filename):
```bash
pip install pytest
pytest test_classifier.py test_decision_rules.py -q   # pure-Python, no external deps
pytest test_classifier.py::test_name -q               # single test
python test_search.py                                  # separate: end-to-end RAG smoke test, needs the embedding model but no API key
```

## Architecture

### Two entry points — don't confuse them
- `api_server.py` — the real, actively-developed server. Persistent FastAPI process wrapping one shared `VectorStore` + embedding model instance, used by every request.
- `rag_server.py` / `rag_client.py` — an earlier MCP-based RAG server/client pair, kept separate and not wired into `api_server.py`. Don't assume changes to one affect the other.

### Rule-based over LLM-based, deliberately
Query classification, network/reason-code extraction, and fight-vs-refund decisions for known codes are regex/lookup-table driven rather than LLM calls:
- `classifier.py` — `classify_query_type()` (dispute/question/escalation/invalid), `extract_network_and_code()`, `detect_settlement_issue()`. Pure Python, no LLM, handles English + Hinglish.
- `decision_rules.py` — hand-curated `RULES` table mapping (network, reason_code) → required/disqualifying evidence tags → fight or refund. Falls through to an LLM call in `chargeback_agent.py` only for codes not in the table. Curated by hand rather than derived from the encyclopedia because the 149 docs use two incompatible YAML frontmatter schemas.
- `evidence_tags.py` — the closed `EvidenceTag` vocabulary both of the above depend on (kept in its own module to avoid a circular import between `chargeback_agent.py` and `decision_rules.py`).

### The dispute agent (`chargeback_agent.py`)
A LangGraph state machine (`ChargebackState`) with single-responsibility nodes; routing lives only in `_route_after_*` conditional-edge functions, never inside node bodies:
```
validate → planner → detect_settlement ─┬→ ask_user (END)
        ↘ answer_question (END)          ├→ decide → generate → reflect → END
        ↘ END                            ╰→ extract_code → detect_clarification ─┬→ answer_clarification → ask_user (END)
                                                                                    ╰→ extract_evidence ─┬→ ask_user (END)
                                                                                                           ╰→ decide → generate → reflect → END
```
Each LLM-calling node gets its own narrow system-prompt persona (e.g. "chargeback evidence analyst," "chargeback strategy consultant") rather than one persistent character across the conversation. `reflect_node` no longer calls an LLM at all — despite `ChargebackState`'s docstring still describing a "peer-reviewer," it was replaced with a deterministic groundedness check (regex-extract reason codes from the draft, verify each appears in retrieved docs or the rule table) and a formula-based confidence score.

`_answer_question_node` handles general knowledge-base questions (routed here instead of the full dispute flow) and picks retrieval/prompt strategy from several detected intents (list, compare, lifecycle-stage, coverage-confirmation) via keyword/regex checks on the query — these checks need to be word-boundary-aware, not naive substring matches, or unrelated phrasing (e.g. "what **all** proofs...") can misroute into the wrong branch.

Primary LLM is `openai/gpt-oss-120b` via Groq, with automatic fallback to `openai/gpt-oss-20b` on failure (originally `llama-3.3-70b-versatile`/`llama-3.1-8b-instant` — Meta's Llama-3 line was fully retired from Groq's catalog as of 2026-08-17; check `GET /openai/v1/models` if this needs to change again).

### Identity and role-based data scoping
`usermaster.py` defines the `usermaster` table and `ADMIN_ROLES = {bankopsadmin, bankadmin_maker, bankadmin_checker}`. `auth.py` resolves the `X-Merchant-Key` header to a full `Identity(user_id, role, merchant_id)` via constant-time hash comparison against that table — identity is never accepted from the request body.

`text_to_sql.py`'s `query_chargebacks(question, role, merchant_id=...)` branches on role:
- `role="merchant"` — the server force-injects `WHERE merchant_id = <caller's own>` into the generated SQL regardless of what the LLM wrote, even if the question names a different merchant. This is defense-in-depth: the system prompt also instructs the scoping rule, but the enforcement doesn't rely on the LLM obeying it.
- `role` in `ADMIN_ROLES` — no forced filter; can query across all merchants or narrow to one if named. Row formatting (`_format_rows`, `_rows_to_dicts`) also differs by role: merchant identity columns are hidden from merchant callers (redundant — it's their own data) but shown for admins (needed to tell whose row is whose in a cross-merchant result set).

Same layered pattern is used for SQL safety generally: `_is_safe_sql()` (SELECT-only, no UNION/writes/comments/stacked queries) and `_is_safe_question()` (prompt-injection + role-aware escalation phrasing) run regardless of what the LLM-generated SQL looks like.

### Guardrails (`guardrails.py`)
Six standalone utilities, each independently importable, layered across `api_server.py` and `chargeback_agent.py`: `mask_pii()`, `detect_prompt_injection()`, `check_length()`, `RateLimiter` (sliding-window + abuse blocking), `AuditLogger` (append-only JSONL, PII masked before write), `CostCircuitBreaker` (daily LLM call cap, trips to 503).

### Data stores
- `chargebacks.db` (SQLite) — `chargebacks` table (NPCI/UPI dispute records, seeded by `merchant_db.py`) + `usermaster` table (login identities, seeded by `usermaster.py`).
- `qdrant_data/` — Qdrant local file-mode collection (`chargeback_docs`) holding embedded `chargeback-encyclopedia/` content. Single-process access only (see server note above).
