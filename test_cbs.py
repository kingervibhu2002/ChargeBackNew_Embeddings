"""
test_cbs.py — Unit tests for cbs.py's ledger functions and
chargeback_analysis.py's ledger-based U002 investigation.

Plain-Python assertions, same style as test_decision_rules.py — runnable
directly (python test_cbs.py) or via pytest. Uses an isolated temp SQLite
file per test run (never the real chargebacks.db) with a minimal schema
and hand-picked rows, so scenarios are exact and reproducible rather than
depending on cbs.py's own randomized seed_data().

Run:
    python test_cbs.py
"""

import os
import sys
import tempfile

from cbs import (
    count_credits,
    create_schema,
    find_refund_for_utr,
    get_ledger_entries,
    has_pending_suspense,
    reconcile_utr,
    total_credit_amount,
)
from chargeback_analysis import analyze_chargeback
from merchant_db import get_connection


def _check(label: str, condition: bool, detail: str = "") -> bool:
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + (f" — {detail}" if detail and not condition else ""))
    return condition


def _make_test_db() -> str:
    """A fresh temp SQLite file with a minimal chargebacks table (just the
    columns analyze_chargeback()/count_credits() actually touch) plus the
    real ledger_entries schema from cbs.py."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    conn = get_connection(path)
    conn.execute("""
        CREATE TABLE chargebacks (
            utr TEXT NOT NULL,
            reason_code TEXT NOT NULL
        )
    """)
    create_schema(conn)
    conn.commit()
    conn.close()
    return path


def _insert_ledger_entry(db_path, utr, entry_type, amount, status="posted", posting_date="2026-01-01", ref=None):
    conn = get_connection(db_path)
    conn.execute(
        "INSERT INTO ledger_entries (utr, entry_type, amount, status, posting_date, reference_id) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (utr, entry_type, amount, status, posting_date, ref or f"REF-{utr}-{entry_type}-{status}-{amount}-{posting_date}"),
    )
    conn.commit()
    conn.close()


def _insert_settlement_entry(db_path, utr, amount, settlement_type="AUTH", settlement_date="2026-01-01", ref=None):
    conn = get_connection(db_path)
    conn.execute(
        "INSERT INTO settlement_entries (utr, amount, settlement_type, settlement_date, cycle_id, reference_id) "
        "VALUES (?, ?, ?, ?, 'CYCLE-1', ?)",
        (utr, amount, settlement_type, settlement_date, ref or f"SETREF-{utr}-{amount}-{settlement_date}"),
    )
    conn.commit()
    conn.close()


def _get_ledger_entry_id(db_path, reference_id):
    conn = get_connection(db_path)
    row = conn.execute("SELECT id FROM ledger_entries WHERE reference_id = ?", (reference_id,)).fetchone()
    conn.close()
    return row["id"]


def test_count_credits_zero_when_no_entries() -> bool:
    db = _make_test_db()
    try:
        return _check("count_credits() == 0 with no ledger entries at all",
                       count_credits("UTR_NONE", db_path=db) == 0)
    finally:
        os.remove(db)


def test_count_credits_counts_only_posted_credits() -> bool:
    db = _make_test_db()
    try:
        _insert_ledger_entry(db, "UTR1", "credit", 500, status="posted")
        _insert_ledger_entry(db, "UTR1", "credit", 500, status="pending")   # not counted
        _insert_ledger_entry(db, "UTR1", "credit", 500, status="reversed")  # not counted
        _insert_ledger_entry(db, "UTR1", "refund", 500, status="posted")    # not a credit
        return _check("count_credits() only counts entry_type='credit', status='posted'",
                       count_credits("UTR1", db_path=db) == 1,
                       detail=str(count_credits("UTR1", db_path=db)))
    finally:
        os.remove(db)


def test_count_credits_two_posted_credits() -> bool:
    db = _make_test_db()
    try:
        _insert_ledger_entry(db, "UTR2", "credit", 500, status="posted", posting_date="2026-01-01")
        _insert_ledger_entry(db, "UTR2", "credit", 500, status="posted", posting_date="2026-01-03")
        return _check("count_credits() == 2 with two genuinely posted credits",
                       count_credits("UTR2", db_path=db) == 2)
    finally:
        os.remove(db)


def test_has_pending_suspense_true() -> bool:
    db = _make_test_db()
    try:
        _insert_ledger_entry(db, "UTR3", "credit", 500, status="pending")
        return _check("has_pending_suspense() == True with a pending entry",
                       has_pending_suspense("UTR3", db_path=db) is True)
    finally:
        os.remove(db)


def test_has_pending_suspense_false() -> bool:
    db = _make_test_db()
    try:
        _insert_ledger_entry(db, "UTR4", "credit", 500, status="posted")
        return _check("has_pending_suspense() == False with only posted entries",
                       has_pending_suspense("UTR4", db_path=db) is False)
    finally:
        os.remove(db)


def test_find_refund_for_utr_found() -> bool:
    db = _make_test_db()
    try:
        _insert_ledger_entry(db, "UTR5", "credit", 500, status="posted", posting_date="2026-01-01")
        _insert_ledger_entry(db, "UTR5", "refund", 500, status="posted", posting_date="2026-01-05")
        result = find_refund_for_utr("UTR5", db_path=db)
        return _check("find_refund_for_utr() finds a posted refund entry",
                       result is not None and result["amount"] == 500,
                       detail=str(result))
    finally:
        os.remove(db)


def test_find_refund_for_utr_none() -> bool:
    db = _make_test_db()
    try:
        _insert_ledger_entry(db, "UTR6", "credit", 500, status="posted")
        return _check("find_refund_for_utr() returns None with no refund entry",
                       find_refund_for_utr("UTR6", db_path=db) is None)
    finally:
        os.remove(db)


def test_count_credits_nets_out_reversed_credit_with_no_repost() -> bool:
    db = _make_test_db()
    try:
        _insert_ledger_entry(db, "UTR_REV", "credit", 500, status="posted", posting_date="2026-01-01", ref="REV-CR1")
        credit_id = _get_ledger_entry_id(db, "REV-CR1")
        conn = get_connection(db)
        conn.execute(
            "INSERT INTO ledger_entries (utr, entry_type, amount, status, posting_date, reference_id, reversal_of_id) "
            "VALUES (?, 'reversal', ?, 'posted', ?, ?, ?)",
            ("UTR_REV", 500, "2026-01-03", "REV-REV1", credit_id),
        )
        conn.commit()
        conn.close()
        return _check("count_credits() == 0 when the only credit was reversed and never reposted",
                       count_credits("UTR_REV", db_path=db) == 0,
                       detail=str(count_credits("UTR_REV", db_path=db)))
    finally:
        os.remove(db)


def test_count_credits_reversal_then_repost_nets_to_one() -> bool:
    # The exact scenario a naive entry_type='credit' row count would
    # misread as a duplicate: credit -> reversal -> repost. Two raw
    # 'credit' rows exist, but only one is still standing.
    db = _make_test_db()
    try:
        _insert_ledger_entry(db, "UTR_REPOST", "credit", 500, status="posted", posting_date="2026-01-01", ref="REPOST-CR1")
        credit_id = _get_ledger_entry_id(db, "REPOST-CR1")
        conn = get_connection(db)
        conn.execute(
            "INSERT INTO ledger_entries (utr, entry_type, amount, status, posting_date, reference_id, reversal_of_id) "
            "VALUES (?, 'reversal', ?, 'posted', ?, ?, ?)",
            ("UTR_REPOST", 500, "2026-01-02", "REPOST-REV1", credit_id),
        )
        conn.commit()
        conn.close()
        _insert_ledger_entry(db, "UTR_REPOST", "credit", 500, status="posted", posting_date="2026-01-03", ref="REPOST-CR2")
        return _check(
            "count_credits() == 1 after credit -> reversal -> repost (not 2, despite two 'credit' rows)",
            count_credits("UTR_REPOST", db_path=db) == 1,
            detail=str(count_credits("UTR_REPOST", db_path=db)),
        )
    finally:
        os.remove(db)


def test_total_credit_amount_nets_reversals_too() -> bool:
    db = _make_test_db()
    try:
        _insert_ledger_entry(db, "UTR_AMT", "credit", 500, status="posted", posting_date="2026-01-01", ref="AMT-CR1")
        credit_id = _get_ledger_entry_id(db, "AMT-CR1")
        conn = get_connection(db)
        conn.execute(
            "INSERT INTO ledger_entries (utr, entry_type, amount, status, posting_date, reference_id, reversal_of_id) "
            "VALUES (?, 'reversal', ?, 'posted', ?, ?, ?)",
            ("UTR_AMT", 500, "2026-01-02", "AMT-REV1", credit_id),
        )
        conn.commit()
        conn.close()
        _insert_ledger_entry(db, "UTR_AMT", "credit", 500, status="posted", posting_date="2026-01-03", ref="AMT-CR2")
        return _check("total_credit_amount() == 500 (net), not 1000, after reversal+repost",
                       total_credit_amount("UTR_AMT", db_path=db) == 500,
                       detail=str(total_credit_amount("UTR_AMT", db_path=db)))
    finally:
        os.remove(db)


def test_reconcile_utr_matched() -> bool:
    db = _make_test_db()
    try:
        _insert_ledger_entry(db, "UTR_MATCH", "credit", 500, status="posted")
        _insert_settlement_entry(db, "UTR_MATCH", 500)
        result = reconcile_utr("UTR_MATCH", db_path=db)
        return _check("reconcile_utr() == 'matched' when settlement equals net ledger credit",
                       result["status"] == "matched", detail=str(result))
    finally:
        os.remove(db)


def test_reconcile_utr_mismatch() -> bool:
    db = _make_test_db()
    try:
        _insert_ledger_entry(db, "UTR_MISMATCH", "credit", 500, status="posted")
        _insert_settlement_entry(db, "UTR_MISMATCH", 300)
        result = reconcile_utr("UTR_MISMATCH", db_path=db)
        return _check("reconcile_utr() == 'mismatch' when settlement and ledger disagree",
                       result["status"] == "mismatch", detail=str(result))
    finally:
        os.remove(db)


def test_reconcile_utr_no_data() -> bool:
    db = _make_test_db()
    try:
        result = reconcile_utr("UTR_NODATA", db_path=db)
        return _check("reconcile_utr() == 'no_data' when neither settlement nor ledger has anything",
                       result["status"] == "no_data", detail=str(result))
    finally:
        os.remove(db)


def test_get_ledger_entries_ordered() -> bool:
    db = _make_test_db()
    try:
        _insert_ledger_entry(db, "UTR7", "credit", 500, status="posted", posting_date="2026-01-05")
        _insert_ledger_entry(db, "UTR7", "credit", 500, status="posted", posting_date="2026-01-01")
        entries = get_ledger_entries("UTR7", db_path=db)
        return _check("get_ledger_entries() returns entries oldest-first",
                       len(entries) == 2 and entries[0]["posting_date"] == "2026-01-01",
                       detail=str(entries))
    finally:
        os.remove(db)


def _insert_chargeback(db_path, utr, reason_code):
    conn = get_connection(db_path)
    conn.execute("INSERT INTO chargebacks (utr, reason_code) VALUES (?, ?)", (utr, reason_code))
    conn.commit()
    conn.close()


def _get_chargeback_row(db_path, utr):
    conn = get_connection(db_path)
    row = conn.execute("SELECT * FROM chargebacks WHERE utr = ?", (utr,)).fetchone()
    conn.close()
    return row


def test_u002_two_credits_recommends_refund_via_ledger() -> bool:
    db = _make_test_db()
    try:
        _insert_chargeback(db, "UTR_DUP", "U002")
        _insert_ledger_entry(db, "UTR_DUP", "credit", 500, status="posted", posting_date="2026-01-01")
        _insert_ledger_entry(db, "UTR_DUP", "credit", 500, status="posted", posting_date="2026-01-03")
        row = _get_chargeback_row(db, "UTR_DUP")
        result = analyze_chargeback(row, db_path=db)
        return _check("U002 + 2 posted credits -> action='refund', source='ledger'",
                       result.action == "refund" and result.source == "ledger",
                       detail=str(result))
    finally:
        os.remove(db)


def test_u002_one_credit_recommends_fight_via_ledger() -> bool:
    db = _make_test_db()
    try:
        _insert_chargeback(db, "UTR_ONE", "U002")
        _insert_ledger_entry(db, "UTR_ONE", "credit", 500, status="posted")
        _insert_settlement_entry(db, "UTR_ONE", 500)  # reconciled — matches the ledger
        row = _get_chargeback_row(db, "UTR_ONE")
        result = analyze_chargeback(row, db_path=db)
        return _check("U002 + exactly 1 posted credit, nothing pending, reconciled -> action='fight', source='ledger'",
                       result.action == "fight" and result.source == "ledger",
                       detail=str(result))
    finally:
        os.remove(db)


def test_u002_one_credit_unreconciled_returns_no_recommendation() -> bool:
    # Ledger looks internally fine (exactly one clean credit), but nothing
    # the network reported as settled matches it -- a mismatch a same-
    # source-only check could never surface. Must NOT resolve to "fight"
    # just because the ledger alone looks clean.
    db = _make_test_db()
    try:
        _insert_chargeback(db, "UTR_UNRECON", "U002")
        _insert_ledger_entry(db, "UTR_UNRECON", "credit", 500, status="posted")
        _insert_settlement_entry(db, "UTR_UNRECON", 0)  # network reports nothing settled
        row = _get_chargeback_row(db, "UTR_UNRECON")
        result = analyze_chargeback(row, db_path=db)
        return _check(
            "U002 + 1 posted credit but settlement mismatch -> action=None, source='ledger'",
            result.action is None and result.source == "ledger",
            detail=str(result),
        )
    finally:
        os.remove(db)


def test_u002_pending_entry_returns_no_recommendation() -> bool:
    db = _make_test_db()
    try:
        _insert_chargeback(db, "UTR_PEND", "U002")
        _insert_ledger_entry(db, "UTR_PEND", "credit", 500, status="pending")
        row = _get_chargeback_row(db, "UTR_PEND")
        result = analyze_chargeback(row, db_path=db)
        return _check("U002 + pending entry, no posted credit -> action=None, source='ledger'",
                       result.action is None and result.source == "ledger",
                       detail=str(result))
    finally:
        os.remove(db)


def test_u002_zero_credits_falls_through_to_rule_table() -> bool:
    db = _make_test_db()
    try:
        _insert_chargeback(db, "UTR_ZERO", "U002")
        # No ledger entries at all for this UTR.
        row = _get_chargeback_row(db, "UTR_ZERO")
        result = analyze_chargeback(row, db_path=db)
        return _check("U002 + 0 ledger entries -> falls through to decision_rules (source='rules')",
                       result.source == "rules",
                       detail=str(result))
    finally:
        os.remove(db)


def test_cbs_refund_check_still_takes_priority_over_ledger_check() -> bool:
    db = _make_test_db()
    try:
        _insert_chargeback(db, "UTR_BOTH", "U002")
        _insert_ledger_entry(db, "UTR_BOTH", "credit", 500, status="posted", posting_date="2026-01-01")
        _insert_ledger_entry(db, "UTR_BOTH", "credit", 500, status="posted", posting_date="2026-01-03")
        _insert_ledger_entry(db, "UTR_BOTH", "refund", 500, status="posted", posting_date="2026-01-05")
        row = _get_chargeback_row(db, "UTR_BOTH")
        result = analyze_chargeback(row, db_path=db)
        return _check("a refund entry wins over the duplicate-credit check — source='cbs', not 'ledger'",
                       result.source == "cbs" and result.action == "fight",
                       detail=str(result))
    finally:
        os.remove(db)


def test_non_u002_code_unaffected_by_ledger_check() -> bool:
    db = _make_test_db()
    try:
        _insert_chargeback(db, "UTR_U001", "U001")
        # Two credits present, but U001 isn't the code this check is scoped to.
        _insert_ledger_entry(db, "UTR_U001", "credit", 500, status="posted", posting_date="2026-01-01")
        _insert_ledger_entry(db, "UTR_U001", "credit", 500, status="posted", posting_date="2026-01-03")
        row = _get_chargeback_row(db, "UTR_U001")
        result = analyze_chargeback(row, db_path=db)
        return _check("U001 (not U002) with 2 credits still goes straight to the rule table",
                       result.source == "rules",
                       detail=str(result))
    finally:
        os.remove(db)


def main() -> None:
    tests = [
        test_count_credits_zero_when_no_entries,
        test_count_credits_counts_only_posted_credits,
        test_count_credits_two_posted_credits,
        test_has_pending_suspense_true,
        test_has_pending_suspense_false,
        test_find_refund_for_utr_found,
        test_find_refund_for_utr_none,
        test_get_ledger_entries_ordered,
        test_count_credits_nets_out_reversed_credit_with_no_repost,
        test_count_credits_reversal_then_repost_nets_to_one,
        test_total_credit_amount_nets_reversals_too,
        test_reconcile_utr_matched,
        test_reconcile_utr_mismatch,
        test_reconcile_utr_no_data,
        test_u002_two_credits_recommends_refund_via_ledger,
        test_u002_one_credit_recommends_fight_via_ledger,
        test_u002_one_credit_unreconciled_returns_no_recommendation,
        test_u002_pending_entry_returns_no_recommendation,
        test_u002_zero_credits_falls_through_to_rule_table,
        test_cbs_refund_check_still_takes_priority_over_ledger_check,
        test_non_u002_code_unaffected_by_ledger_check,
    ]
    print(f"Running {len(tests)} cbs.py / chargeback_analysis.py tests...\n")
    results = [t() for t in tests]
    passed = sum(results)
    print(f"\n{passed}/{len(tests)} passed")
    sys.exit(0 if passed == len(tests) else 1)


if __name__ == "__main__":
    main()
