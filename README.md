# Chargeback Assistant

A RAG-powered chargeback dispute assistant for Airtel Payments Bank merchants and bank admin staff. It combines a knowledge base of chargeback reason codes and dispute procedures with an LLM agent that walks merchants through fighting or accepting a chargeback, plus a natural-language query layer over chargeback records — with role-based access so merchants only ever see their own data while bank admins can see across all merchants.

## Features

- **Knowledge base Q&A** — ask about Visa/Mastercard/Amex/RuPay reason codes, evidence requirements, dispute timelines, fraud types, and regulations, answered from a 149-document encyclopedia via semantic search.
- **Dispute agent** — describe a chargeback and get evidence guidance, a fight-or-refund recommendation, and a drafted rebuttal letter (or refund guidance if fighting isn't worth it).
- **Natural-language chargeback queries** — ask things like "how many open chargebacks do I have?" or "give me all pending chargebacks" and get results converted to SQL, executed, and formatted.
- **Role-based access** — merchant logins are always scoped to their own data; bank admin roles (`bankopsadmin`, `bankadmin_maker`, `bankadmin_checker`) can query across all merchants or drill into a specific one.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Get a free API key from [console.groq.com](https://console.groq.com) and set it:

```bash
export GROQ_API_KEY=your_key_here
```

Without `GROQ_API_KEY`, the server still starts, but the dispute agent and natural-language query endpoints return 503.

## Running

```bash
python api_server.py
```

- Chat UI: [http://localhost:8000/](http://localhost:8000/)
- Interactive API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

Only one server process can run at a time — the vector store (Qdrant, local file mode) holds an exclusive lock on `./qdrant_data`. If you see `Storage folder ./qdrant_data is already accessed by another instance`, stop the other running instance first.

## Demo logins

The chat UI's merchant/admin selector is populated from seeded demo accounts (see `usermaster.py`):

| Role | Scope |
|---|---|
| `merchant` (×4, one per demo Airtel merchant) | Own chargeback data only |
| `bankopsadmin`, `bankadmin_maker`, `bankadmin_checker` | All merchants' chargeback data |

Re-seed at any time with:

```bash
python merchant_db.py   # chargeback records
python usermaster.py    # login identities / roles
```

## Project structure

- `api_server.py` — FastAPI server: serves the chat UI, wraps the vector store + dispute agent + SQL query layer, applies guardrails (rate limiting, audit logging, cost circuit breaker).
- `chargeback_agent.py` — LangGraph agent that runs the dispute workflow (evidence extraction → fight/refund decision → letter drafting).
- `classifier.py` / `decision_rules.py` / `evidence_tags.py` — deterministic, non-LLM rule engines for query classification and fight/refund decisions.
- `text_to_sql.py` / `merchant_db.py` / `usermaster.py` — natural-language-to-SQL query layer, chargeback records, and login identities/roles.
- `vector_store.py` / `load_encyclopedia.py` / `load_chargeback_docs.py` — Qdrant vector store wrapper and indexing scripts for `chargeback-encyclopedia/`.
- `auth.py` / `guardrails.py` — identity resolution and safety/operational guardrails (PII masking, prompt-injection detection, rate limiting, audit logging).
- `chargeback-encyclopedia/` — the knowledge base source content (markdown, organized by topic).
- `chat.html` — the frontend, served directly by `api_server.py`.

See `CLAUDE.md` for architectural details aimed at AI coding assistants working in this repo.

## Tests

```bash
pip install pytest
pytest test_classifier.py test_decision_rules.py -q
python test_search.py   # end-to-end RAG retrieval smoke test
```
