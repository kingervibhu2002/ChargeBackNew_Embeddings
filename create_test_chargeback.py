"""
create_test_chargeback.py — Insert one fresh Open chargeback for a specific
merchant, optionally with a matching CBS ledger record, for testing
auto_decision_poller.py without wiping/re-seeding the whole database.

Usage:
    # Plain chargeback, no ledger match — should auto-accept (if reason_code
    # is in decision_rules.RULES) or get skipped (if not), once the poller runs.
    python create_test_chargeback.py --merchant AIRTEL_M001 --reason U001

    # Same, but also insert a CBS refund for it — should auto-dispute as
    # duplicate regardless of reason_code, since the CBS check runs first.
    python create_test_chargeback.py --merchant AIRTEL_M001 --reason U010 --with-refund

    # A genuine second credit posted for this UTR — for U002 specifically,
    # this should auto-dispute as "refund" via chargeback_analysis.py's
    # ledger-based check (count_credits() >= 2), not the rule table.
    python create_test_chargeback.py --merchant AIRTEL_M002 --reason U002 --with-duplicate-credit

    # Explicit amount instead of a random one:
    python create_test_chargeback.py --merchant AIRTEL_M002 --reason U002 --amount 5000 --with-refund

Then:
    python auto_decision_poller.py
"""

import argparse
import random
import sys
from datetime import date, timedelta

from merchant_db import MERCHANTS, NPCI_REASON_CODES, get_connection

BANKS = ["SBI", "HDFC Bank", "ICICI Bank", "Axis Bank", "PNB", "Kotak", "Yes Bank"]

_MERCHANTS_BY_ID = {m["id"]: m for m in MERCHANTS}


def insert_test_chargeback(
    merchant_id: str,
    reason_code: str,
    amount: float = None,
    with_refund: bool = False,
    with_duplicate_credit: bool = False,
    db_path: str = "chargebacks.db",
) -> dict:
    if merchant_id not in _MERCHANTS_BY_ID:
        valid = ", ".join(_MERCHANTS_BY_ID)
        raise ValueError(f"Unknown merchant_id {merchant_id!r}. Valid: {valid}")
    if reason_code not in NPCI_REASON_CODES:
        valid = ", ".join(NPCI_REASON_CODES)
        raise ValueError(f"Unknown reason_code {reason_code!r}. Valid: {valid}")

    merchant = _MERCHANTS_BY_ID[merchant_id]
    amount   = round(amount if amount is not None else random.uniform(50, 25000), 2)

    today       = date.today()
    txn_date    = today - timedelta(days=random.randint(1, 30))
    filing_date = today
    deadline    = filing_date + timedelta(days=30)

    # Random suffix (not the sequential per-merchant index seed_data() uses)
    # to avoid colliding with existing rows when inserting a single one-off.
    suffix       = random.randint(100000, 999999)
    utr          = f"UTR{txn_date.strftime('%Y%m%d')}{merchant_id[-4:]}{suffix}"
    case_id      = f"NPCI{filing_date.strftime('%Y%m%d')}{merchant_id[-4:]}{suffix}"
    customer_idx = random.randint(1000, 9999)

    conn = get_connection(db_path)
    try:
        conn.execute("""
            INSERT INTO chargebacks (
                merchant_id, merchant_name, merchant_vpa,
                utr, case_id,
                customer_vpa, customer_name, issuing_bank,
                transaction_amount, chargeback_amount,
                transaction_date, chargeback_filing_date, response_deadline,
                reason_code, reason_description,
                status, resolution, resolution_date, notes
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, 'Open', NULL, NULL, '')
        """, (
            merchant_id, merchant["name"], merchant["vpa"],
            utr, case_id,
            f"customer{customer_idx}@upi", f"Customer {customer_idx}",
            random.choice(BANKS),
            amount, amount,
            txn_date.isoformat(), filing_date.isoformat(), deadline.isoformat(),
            reason_code, NPCI_REASON_CODES[reason_code],
        ))

        # Baseline ledger entry — the expected single settlement credit for
        # this transaction, same as cbs.py's own seed_data() inserts for
        # every real chargeback. Without this, a test-inserted row would
        # have ZERO ledger entries at all (count_credits()==0), which
        # chargeback_analysis.py's U002 check deliberately treats as "can't
        # resolve either way, fall through to the rule table" rather than
        # a real "one clean credit, claim refuted" case — inserting it here
        # keeps a plain test chargeback (no flags) behaving like the common,
        # unremarkable case it's meant to simulate.
        credit_ref = f"CBS-CR-{utr}"
        conn.execute("""
            INSERT INTO ledger_entries (utr, entry_type, amount, status, posting_date, reference_id, remarks)
            VALUES (?, 'credit', ?, 'posted', ?, ?, 'Original settlement credit (test)')
        """, (utr, amount, txn_date.isoformat(), credit_ref))

        refund_ref = None
        if with_refund:
            refund_date = (txn_date + timedelta(days=random.randint(1, 5))).isoformat()
            refund_ref  = f"CBS-RFND-{utr}"
            conn.execute("""
                INSERT INTO ledger_entries (utr, entry_type, amount, status, posting_date, reference_id, remarks)
                VALUES (?, 'refund', ?, 'posted', ?, ?, 'Test refund inserted by create_test_chargeback.py')
            """, (utr, amount, refund_date, refund_ref))

        duplicate_ref = None
        if with_duplicate_credit:
            dup_date = (txn_date + timedelta(days=random.randint(1, 3))).isoformat()
            duplicate_ref = f"CBS-CR2-{utr}"
            conn.execute("""
                INSERT INTO ledger_entries (utr, entry_type, amount, status, posting_date, reference_id, remarks)
                VALUES (?, 'credit', ?, 'posted', ?, ?, 'Test duplicate credit inserted by create_test_chargeback.py')
            """, (utr, amount, dup_date, duplicate_ref))

        conn.commit()
    finally:
        conn.close()

    return {
        "merchant_id": merchant_id,
        "merchant_name": merchant["name"],
        "utr": utr,
        "case_id": case_id,
        "reason_code": reason_code,
        "amount": amount,
        "with_refund": with_refund,
        "cbs_reference": refund_ref,
        "with_duplicate_credit": with_duplicate_credit,
        "duplicate_reference": duplicate_ref,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--merchant", required=True, help=f"One of: {', '.join(_MERCHANTS_BY_ID)}")
    parser.add_argument("--reason", required=True, help=f"One of: {', '.join(NPCI_REASON_CODES)}")
    parser.add_argument("--amount", type=float, default=None, help="Defaults to a random amount")
    parser.add_argument("--with-refund", action="store_true",
                         help="Also insert a matching CBS ledger refund entry for this transaction")
    parser.add_argument("--with-duplicate-credit", action="store_true",
                         help="Also insert a genuine second ledger credit entry for this transaction "
                              "(tests chargeback_analysis.py's U002 ledger-based check)")
    parser.add_argument("--db-path", default="chargebacks.db")
    args = parser.parse_args()

    try:
        result = insert_test_chargeback(
            merchant_id=args.merchant,
            reason_code=args.reason,
            amount=args.amount,
            with_refund=args.with_refund,
            with_duplicate_credit=args.with_duplicate_credit,
            db_path=args.db_path,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Inserted chargeback for {result['merchant_name']} ({result['merchant_id']}):")
    print(f"  UTR:         {result['utr']}")
    print(f"  Case ID:     {result['case_id']}")
    print(f"  Reason code: {result['reason_code']}")
    print(f"  Amount:      ₹{result['amount']:,.2f}")
    if result["with_refund"]:
        print(f"  CBS refund:  {result['cbs_reference']} (should auto-dispute as duplicate)")
    else:
        print(f"  CBS refund:  none")
    if result["with_duplicate_credit"]:
        print(f"  2nd credit:  {result['duplicate_reference']} (should auto-refund via ledger check, U002 only)")
    if not result["with_refund"] and not result["with_duplicate_credit"]:
        print(f"               (will follow decision_rules.py's normal evidence-free outcome)")
    print()
    print("Now run: python auto_decision_poller.py")
