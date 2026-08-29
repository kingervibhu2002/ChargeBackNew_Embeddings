"""
test_case_recommendations.py — Unit tests for case_recommendations.py, the
persistence layer behind live-chat dispute recommendations.

Plain-Python assertions, same style as test_cbs.py — runnable directly
(python test_case_recommendations.py) or via pytest. Uses an isolated temp
SQLite file per test run (never the real chargebacks.db) with a minimal,
hand-picked chargebacks row, so scenarios are exact and reproducible.

The single most important guard here is the HARD SAFETY CONSTRAINT
case_recommendations.py's own module docstring states: a live-chat
recommendation must NEVER touch chargebacks.status/resolution/
resolution_date — only suggested_action/suggestion_reason and the new
case_recommendations history table. Every write test asserts this
explicitly, not just the fields that were supposed to change.

Run:
    python test_case_recommendations.py
"""

import os
import sys
import tempfile

from case_recommendations import (
    create_schema as create_recommendations_schema,
    get_recommendation_history,
    list_recent_recommendations,
    record_recommendation,
)
from merchant_db import create_schema as create_chargebacks_schema, get_connection


CASE_ID     = "NPCI20260616M002008"
MERCHANT_ID = "AIRTEL_M002"
OTHER_MERCHANT_ID = "AIRTEL_M003"


def _check(label: str, condition: bool, detail: str = "") -> bool:
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + (f" — {detail}" if detail and not condition else ""))
    return condition


def _make_test_db() -> str:
    """A fresh temp SQLite file with the real chargebacks schema (one
    hand-picked seeded row, status='Open', resolution=NULL) plus the new
    case_recommendations schema."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    conn = get_connection(path)
    create_chargebacks_schema(conn)
    create_recommendations_schema(conn)
    conn.execute(
        """
        INSERT INTO chargebacks (
            merchant_id, merchant_name, merchant_vpa, utr, case_id,
            customer_vpa, customer_name, issuing_bank,
            transaction_amount, chargeback_amount, transaction_date,
            chargeback_filing_date, response_deadline,
            reason_code, reason_description, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Open')
        """,
        (
            MERCHANT_ID, "Airtel Broadband Solutions", "airtelbb@airtel",
            "UTR000000000123", CASE_ID,
            "customer@upi", "Test Customer", "HDFC Bank",
            2482.23, 2482.23, "2026-06-16",
            "2026-06-16", "2026-07-16",
            "U002", "Duplicate transaction",
        ),
    )
    conn.commit()
    conn.close()
    return path


def _get_chargeback_row(db_path: str) -> dict:
    conn = get_connection(db_path)
    row = conn.execute(
        "SELECT status, resolution, resolution_date, suggested_action, suggestion_reason "
        "FROM chargebacks WHERE case_id = ?",
        (CASE_ID,),
    ).fetchone()
    conn.close()
    return dict(row)


def test_record_recommendation_writes_history_and_cache() -> bool:
    db = _make_test_db()
    try:
        record_recommendation(
            case_id=CASE_ID, merchant_id=MERCHANT_ID, action="fight",
            reason="Ledger shows only one posted credit.", source="ledger",
            origin="live_chat_preview", confidence_score=8, db_path=db,
        )
        history = get_recommendation_history(CASE_ID, merchant_id=MERCHANT_ID, db_path=db)
        row = _get_chargeback_row(db)
        ok = (
            len(history) == 1
            and history[0]["action"] == "fight"
            and history[0]["source"] == "ledger"
            and history[0]["origin"] == "live_chat_preview"
            and history[0]["confidence_score"] == 8
            and row["suggested_action"] == "fight"
            and row["suggestion_reason"] == "Ledger shows only one posted credit."
        )
        return _check("record_recommendation() writes one history row + refreshes the cache",
                       ok, detail=f"history={history} row={row}")
    finally:
        os.remove(db)


def test_record_recommendation_never_touches_status_or_resolution() -> bool:
    """The single most important regression guard for this whole module —
    see the module docstring's HARD CONSTRAINT."""
    db = _make_test_db()
    try:
        before = _get_chargeback_row(db)
        record_recommendation(
            case_id=CASE_ID, merchant_id=MERCHANT_ID, action="fight",
            reason="Ledger shows only one posted credit.", source="ledger",
            origin="live_chat_preview", confidence_score=8, db_path=db,
        )
        after = _get_chargeback_row(db)
        ok = (
            before["status"] == after["status"] == "Open"
            and before["resolution"] is None and after["resolution"] is None
            and before["resolution_date"] is None and after["resolution_date"] is None
        )
        return _check("record_recommendation() never touches status/resolution/resolution_date",
                       ok, detail=f"before={before} after={after}")
    finally:
        os.remove(db)


def test_reconfirmation_appends_not_overwrites_history() -> bool:
    db = _make_test_db()
    try:
        record_recommendation(
            case_id=CASE_ID, merchant_id=MERCHANT_ID, action="fight",
            reason="First pass.", source="ledger", origin="live_chat_preview",
            confidence_score=8, db_path=db,
        )
        record_recommendation(
            case_id=CASE_ID, merchant_id=MERCHANT_ID, action="refund",
            reason="Reconsidered on a later conversation.", source="llm",
            origin="live_chat", confidence_score=6, db_path=db,
        )
        history = get_recommendation_history(CASE_ID, merchant_id=MERCHANT_ID, db_path=db)
        row = _get_chargeback_row(db)
        ok = (
            len(history) == 2
            and history[0]["action"] == "refund"       # most recent first
            and history[1]["action"] == "fight"
            and row["suggested_action"] == "refund"    # cache reflects only the latest
        )
        return _check("a second recommendation appends a new history row, cache reflects only the latest",
                       ok, detail=f"history={history} row={row}")
    finally:
        os.remove(db)


def test_history_scoped_to_correct_merchant() -> bool:
    db = _make_test_db()
    try:
        record_recommendation(
            case_id=CASE_ID, merchant_id=MERCHANT_ID, action="fight",
            reason="x", source="ledger", origin="live_chat_preview", db_path=db,
        )
        wrong_merchant = get_recommendation_history(CASE_ID, merchant_id=OTHER_MERCHANT_ID, db_path=db)
        right_merchant = get_recommendation_history(CASE_ID, merchant_id=MERCHANT_ID, db_path=db)
        admin_view     = get_recommendation_history(CASE_ID, merchant_id=None, db_path=db)
        ok = wrong_merchant == [] and len(right_merchant) == 1 and len(admin_view) == 1
        return _check("get_recommendation_history() scopes to the right merchant; None (admin) sees it unscoped",
                       ok, detail=f"wrong={wrong_merchant} right={right_merchant} admin={admin_view}")
    finally:
        os.remove(db)


def test_list_recent_excludes_stale_rows() -> bool:
    db = _make_test_db()
    try:
        record_recommendation(
            case_id=CASE_ID, merchant_id=MERCHANT_ID, action="fight",
            reason="x", source="ledger", origin="live_chat_preview", db_path=db,
        )
        conn = get_connection(db)
        conn.execute(
            "UPDATE case_recommendations SET created_at = datetime('now', '-60 days') "
            "WHERE case_id = ?", (CASE_ID,),
        )
        conn.commit()
        conn.close()
        recent = list_recent_recommendations(merchant_id=MERCHANT_ID, days=30, db_path=db)
        return _check("list_recent_recommendations() excludes a row backdated past the window",
                       recent == [], detail=f"recent={recent}")
    finally:
        os.remove(db)


def main() -> None:
    tests = [
        test_record_recommendation_writes_history_and_cache,
        test_record_recommendation_never_touches_status_or_resolution,
        test_reconfirmation_appends_not_overwrites_history,
        test_history_scoped_to_correct_merchant,
        test_list_recent_excludes_stale_rows,
    ]
    print(f"Running {len(tests)} case_recommendations.py tests...\n")
    results = [t() for t in tests]
    passed = sum(results)
    print(f"\n{passed}/{len(tests)} passed")
    sys.exit(0 if passed == len(tests) else 1)


if __name__ == "__main__":
    main()
