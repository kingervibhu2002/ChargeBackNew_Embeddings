"""
case_recommendations.py — Append-only history of every fight/refund
recommendation the LIVE CHAT dispute agent (chargeback_agent.py's
DisputeAgent) has actually shown a merchant, for one real, DB-backed case.

Fills the gap guardrails.AuditLogger's audit.log leaves open: audit.log is
append-only JSONL — good for compliance/incident review, not
queryable/joinable. "Show me every fight recommendation for merchant X in
the last 30 days" has no answer today without grepping a log file. This
table is the queryable version of exactly that, for live chat only.

Deliberately scoped to live chat. auto_decision_poller.py /
suggestion_poller.py already write their own audit.log entries per poll
pass; wiring them into this same table is a natural future extension (the
`origin` column already has room for it) but is out of scope here — no
speculative abstraction for a use case not yet asked for.

Two kinds of write, both funneled through record_recommendation():
  - origin="live_chat"          — the main pipeline's EVIDENCE-INFORMED
                                   decision (decide_node -> reflect_node),
                                   using whatever the merchant actually
                                   supplied this conversation.
  - origin="live_chat_preview"  — _build_case_intro()'s EVIDENCE-BLIND
                                   preview: the same CBS/ledger-only
                                   chargeback_analysis.analyze_chargeback()
                                   view the two background pollers already
                                   act on/advise from, just surfaced live.

HARD CONSTRAINT: record_recommendation() only ever writes
case_recommendations (this table) + chargebacks.suggested_action/
suggestion_reason. It must NEVER write chargebacks.status/resolution/
resolution_date — those columns are reserved for the merchant's own
confirmed action or auto_decision_poller.py. A live-chat recommendation is
advice, never an action taken on the merchant's behalf.
"""

from typing import Optional

from merchant_db import DB_PATH, get_connection


def create_schema(conn) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS case_recommendations (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id           TEXT NOT NULL,
            merchant_id       TEXT NOT NULL,
            action            TEXT NOT NULL,          -- 'fight' | 'refund' — never NULL,
                                                        -- only inserted for a real decision
            reason            TEXT NOT NULL DEFAULT '',
            source            TEXT NOT NULL,           -- 'cbs' | 'ledger' | 'rules' | 'llm' —
                                                        -- HOW the action was derived. Extends
                                                        -- chargeback_analysis.Analysis.source's
                                                        -- vocabulary with 'llm' for the main
                                                        -- pipeline's structured-output decision
                                                        -- when no rule-table entry matched.
            origin            TEXT NOT NULL,           -- 'live_chat' | 'live_chat_preview' —
                                                        -- WHICH code path produced this row.
            confidence_score  INTEGER,                 -- 1-10, whatever was actually shown to
                                                        -- the merchant this turn; NULL if
                                                        -- genuinely unavailable
            thread_id         TEXT,
            created_at        TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_case_recommendations_case_id "
        "ON case_recommendations(case_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_case_recommendations_merchant_id "
        "ON case_recommendations(merchant_id)"
    )
    conn.commit()


def record_recommendation(
    case_id: str,
    merchant_id: str,
    action: str,
    reason: str,
    source: str,
    origin: str,
    confidence_score: Optional[int] = None,
    thread_id: str = "",
    db_path: str = DB_PATH,
) -> None:
    """
    Append one history row AND refresh chargebacks.suggested_action/
    suggestion_reason to match — the same "latest recommendation cache"
    semantics suggestion_poller.py already established, just also kept in
    sync from a live conversation. Both writes share one connection/commit
    so this can never be left half-recorded.

    Always inserts a NEW history row, even for a case seen before in an
    earlier conversation — an audit trail should show a recommendation was
    reconfirmed, not silently deduplicate it away.
    """
    conn = get_connection(db_path)
    try:
        conn.execute(
            "INSERT INTO case_recommendations "
            "(case_id, merchant_id, action, reason, source, origin, confidence_score, thread_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (case_id, merchant_id, action, reason, source, origin, confidence_score, thread_id or None),
        )
        # Deliberately touches ONLY suggested_action/suggestion_reason —
        # never status/resolution/resolution_date. See module docstring.
        conn.execute(
            "UPDATE chargebacks SET suggested_action = ?, suggestion_reason = ? "
            "WHERE case_id = ? AND merchant_id = ?",
            (action, reason, case_id, merchant_id),
        )
        conn.commit()
    finally:
        conn.close()


def get_recommendation_history(
    case_id: str,
    merchant_id: Optional[str] = None,
    db_path: str = DB_PATH,
) -> list:
    """
    Full history for one case, most recent first. merchant_id, when given,
    scopes the lookup so a merchant only ever sees their OWN case's
    history (same defense-in-depth pattern as
    merchant_db.list_open_chargebacks) — a mismatched merchant_id
    naturally returns [], never confirming or denying another tenant's
    case exists. None (admin callers) skips the filter.
    """
    conn = get_connection(db_path)
    try:
        if merchant_id is not None:
            rows = conn.execute(
                "SELECT * FROM case_recommendations WHERE case_id = ? AND merchant_id = ? "
                "ORDER BY created_at DESC, id DESC",
                (case_id, merchant_id),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM case_recommendations WHERE case_id = ? "
                "ORDER BY created_at DESC, id DESC",
                (case_id,),
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def list_recent_recommendations(
    merchant_id: Optional[str] = None,
    days: int = 30,
    limit: int = 100,
    db_path: str = DB_PATH,
) -> list:
    """Cross-merchant (or one-merchant) "recommendations in the last N days" view."""
    conn = get_connection(db_path)
    try:
        if merchant_id is not None:
            where  = "WHERE merchant_id = ? AND created_at >= datetime('now', ?)"
            params = (merchant_id, f"-{days} days", limit)
        else:
            where  = "WHERE created_at >= datetime('now', ?)"
            params = (f"-{days} days", limit)
        rows = conn.execute(
            f"SELECT * FROM case_recommendations {where} ORDER BY created_at DESC, id DESC LIMIT ?",
            params,
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def init_schema(db_path: str = DB_PATH) -> None:
    conn = get_connection(db_path)
    create_schema(conn)
    conn.close()


if __name__ == "__main__":
    init_schema()
    print("case_recommendations table ready.")
