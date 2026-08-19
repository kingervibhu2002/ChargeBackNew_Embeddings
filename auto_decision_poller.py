"""
auto_decision_poller.py — Applies chargeback_analysis.py's recommendation to
Open chargebacks for merchants who've opted into auto-decision mode.

This does NOT let a merchant blanket-toggle "always accept" or "always
fight" — it auto-applies whatever the shared per-case analysis in
chargeback_analysis.py would recommend (CBS duplicate-refund check, then
decision_rules.py's evidence-based rule table), the same logic
suggestion_poller.py uses to advise merchants who haven't opted in. The
toggle only removes the manual confirmation step; it doesn't change how the
decision itself gets made. See chargeback_analysis.py for the full
CBS-priority / evidence-gap reasoning.

Run periodically via cron — this is a plain script, not wired into
api_server.py's process. It only touches chargebacks.db, not Qdrant, so it's
safe to run as a separate process without conflicting with the server's
single-instance Qdrant lock.

Usage:
    python auto_decision_poller.py                 # one poll pass, then exit
    */15 * * * * cd /path/to/project && \\
        venv/bin/python auto_decision_poller.py     # example cron entry
"""

from datetime import date

from chargeback_analysis import analyze_chargeback
from guardrails import AuditLogger
from merchant_db import DB_PATH, get_connection


def poll_and_apply(db_path: str = DB_PATH, audit_logger: AuditLogger = None) -> dict:
    """
    Run one poll pass over every merchant with auto_decision='auto'.

    Returns:
        dict: {"merchants_polled", "disputed_as_duplicate", "accepted",
               "flagged_to_fight", "skipped"}
    """
    logger = audit_logger or AuditLogger("audit.log")
    conn = get_connection(db_path)
    try:
        opted_in = conn.execute(
            "SELECT merchant_id FROM usermaster WHERE role = 'merchant' AND auto_decision = 'auto'"
        ).fetchall()
        merchant_ids = [r["merchant_id"] for r in opted_in]

        summary = {
            "merchants_polled":      len(merchant_ids),
            "disputed_as_duplicate": 0,
            "accepted":              0,
            "flagged_to_fight":      0,
            "skipped":               0,
        }
        if not merchant_ids:
            return summary

        placeholders = ",".join("?" for _ in merchant_ids)
        rows = conn.execute(
            f"SELECT * FROM chargebacks WHERE status = 'Open' AND resolution IS NULL "
            f"AND merchant_id IN ({placeholders})",
            merchant_ids,
        ).fetchall()

        today = date.today().isoformat()

        for row in rows:
            analysis = analyze_chargeback(row, db_path)

            if analysis.action is None:
                summary["skipped"] += 1
                continue

            if analysis.source == "cbs":
                new_status, resolution, note = (
                    "Pending", "Fight", f"Auto-disputed as duplicate — {analysis.reason}",
                )
                summary["disputed_as_duplicate"] += 1
            elif analysis.action == "refund":
                new_status, resolution, note = (
                    "Accepted", "Accept", f"Auto-accepted (no evidence on file): {analysis.reason}",
                )
                summary["accepted"] += 1
            else:
                # "fight" from the rule table with zero evidence is only
                # reachable for a future rule with no required evidence tags
                # — nothing in RULES today produces it. Left unresolved
                # (resolution stays NULL) rather than marked Fight/closed,
                # since actually fighting needs a rebuttal letter with real
                # evidence this poller doesn't have — this only flags it for
                # a human to pick up.
                new_status, resolution, note = (
                    "Pending", None,
                    f"Auto-flagged to FIGHT — needs manual evidence submission: {analysis.reason}",
                )
                summary["flagged_to_fight"] += 1

            conn.execute(
                "UPDATE chargebacks SET status = ?, resolution = ?, resolution_date = ?, notes = ? "
                "WHERE id = ?",
                (new_status, resolution, today if resolution else None, note, row["id"]),
            )
            logger.log(
                user_id=row["merchant_id"],
                endpoint="auto_decision_poller",
                query=f"case_id={row['case_id']} reason_code={row['reason_code']}",
                result={"decision": analysis.action, "reason_code": row["reason_code"],
                        "source": analysis.source},
                latency_ms=0,
            )

        conn.commit()
        return summary
    finally:
        conn.close()


if __name__ == "__main__":
    summary = poll_and_apply()
    print(
        f"Polled {summary['merchants_polled']} opted-in merchant(s): "
        f"{summary['disputed_as_duplicate']} auto-disputed as duplicate (CBS refund on file), "
        f"{summary['accepted']} auto-accepted, "
        f"{summary['flagged_to_fight']} flagged to fight (needs manual follow-through), "
        f"{summary['skipped']} skipped (no rule for that reason code)."
    )
