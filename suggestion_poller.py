"""
suggestion_poller.py — Advisory heads-up for merchants who have NOT opted
into auto-decision mode (usermaster.auto_decision = 'manual').

Runs the exact same analysis auto_decision_poller.py acts on — see
chargeback_analysis.py — but never touches status/resolution. It only
writes suggested_action / suggestion_reason so the merchant can see a
recommendation and still decide for themselves. This is the deliberate
difference from the auto-decision poller: opting out of auto-decision means
"don't act for me," not "don't help me at all."

Prioritized by response_deadline: a heads-up is only useful with time left
to act on it, so this only surfaces suggestions for cases due within
--within-days (default 14) — a case with months left doesn't need a nudge
yet, one with days left does.

suggestion_reason stores ONLY the stable part of the recommendation (why —
CBS reference or the rule's reasoning) and deliberately does NOT bake in a
day-count. "Deadline in N days" drifts by definition every day that passes,
so freezing it into stored text goes stale the moment this script isn't
re-run — which, since this is a manually/cron-triggered script rather than
a live service, can be an arbitrarily long time. The urgency framing is
recomputed live from response_deadline wherever it's actually displayed
(see text_to_sql.py), which costs nothing and is never wrong.

Run periodically via cron, same as auto_decision_poller.py.

Usage:
    python suggestion_poller.py                    # default: due within 14 days
    python suggestion_poller.py --within-days 30    # wider window
"""

import argparse
from datetime import date, timedelta

from chargeback_analysis import analyze_chargeback
from guardrails import AuditLogger
from merchant_db import DB_PATH, get_connection


def poll_and_suggest(db_path: str = DB_PATH, within_days: int = 14, audit_logger: AuditLogger = None) -> dict:
    """
    Run one poll pass over every merchant with auto_decision='manual'.

    Returns:
        dict: {"merchants_checked", "suggested", "no_recommendation"}
    """
    logger = audit_logger or AuditLogger("audit.log")
    conn = get_connection(db_path)
    try:
        manual_merchants = conn.execute(
            "SELECT merchant_id FROM usermaster WHERE role = 'merchant' AND auto_decision = 'manual'"
        ).fetchall()
        merchant_ids = [r["merchant_id"] for r in manual_merchants]

        summary = {
            "merchants_checked": len(merchant_ids),
            "suggested":         0,
            "no_recommendation": 0,
        }
        if not merchant_ids:
            return summary

        deadline_cutoff = (date.today() + timedelta(days=within_days)).isoformat()
        placeholders = ",".join("?" for _ in merchant_ids)
        rows = conn.execute(
            f"SELECT * FROM chargebacks WHERE status = 'Open' AND resolution IS NULL "
            f"AND merchant_id IN ({placeholders}) AND response_deadline <= ?",
            merchant_ids + [deadline_cutoff],
        ).fetchall()

        today = date.today()

        for row in rows:
            analysis = analyze_chargeback(row, db_path)

            if analysis.action is None:
                # No confident recommendation (reason code not in RULES, no
                # CBS match) — clear any stale suggestion rather than leaving
                # an outdated one on a case whose facts may have changed.
                conn.execute(
                    "UPDATE chargebacks SET suggested_action = NULL, suggestion_reason = NULL WHERE id = ?",
                    (row["id"],),
                )
                summary["no_recommendation"] += 1
                continue

            # days_left is computed here only for the audit log / summary
            # print (point-in-time facts about this run) — never written into
            # suggestion_reason itself, which must stay valid indefinitely
            # until the next run, not just on the day it was computed.
            days_left = (date.fromisoformat(row["response_deadline"]) - today).days

            conn.execute(
                "UPDATE chargebacks SET suggested_action = ?, suggestion_reason = ? WHERE id = ?",
                (analysis.action, analysis.reason, row["id"]),
            )
            logger.log(
                user_id=row["merchant_id"],
                endpoint="suggestion_poller",
                query=f"case_id={row['case_id']} reason_code={row['reason_code']}",
                result={"suggested_action": analysis.action, "source": analysis.source,
                        "days_left": days_left},
                latency_ms=0,
            )
            summary["suggested"] += 1

        conn.commit()
        return summary
    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--within-days", type=int, default=14,
                         help="Only suggest for cases with a deadline within N days (default 14)")
    args = parser.parse_args()

    summary = poll_and_suggest(within_days=args.within_days)
    print(
        f"Checked {summary['merchants_checked']} manual-mode merchant(s) with deadlines "
        f"within {args.within_days} day(s): "
        f"{summary['suggested']} suggestion(s) generated, "
        f"{summary['no_recommendation']} had no confident recommendation."
    )
