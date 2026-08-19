"""
cbs.py — Dummy Core Banking System transaction ledger.

Models the one piece of ground truth neither the merchant's claims nor the
customer's dispute can be trusted to report accurately on their own: whether
a given transaction (by UTR) was already refunded outside the dispute
process. A customer can mistakenly file a chargeback on a transaction they
were already refunded for (e.g. a goodwill refund, a refund for an unrelated
reason, or simply not noticing the credit) — that dispute is moot/duplicate
regardless of what the chargeback's reason code claims, and should always be
disputed by citing this record, not evaluated as if it were a normal
evidence-based fight/refund judgment call.

This is deliberately separate from decision_rules.py's `refund_already_issued`
evidence tag, which the merchant supplies by assertion during a live chat
(unverified). This table is the authoritative source that assertion should
have been checked against — a merchant claiming "I already refunded this" in
chat isn't evidence; a matching row here is.

Run directly to create and seed the table:
    python cbs.py
"""

import random
import sqlite3
from datetime import timedelta
from typing import Optional

from merchant_db import DB_PATH, get_connection


def create_schema(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cbs_transactions (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            utr          TEXT NOT NULL,           -- matches chargebacks.utr
            txn_type     TEXT NOT NULL,           -- 'refund' | 'payment'
            amount       REAL NOT NULL,
            txn_date     TEXT NOT NULL,           -- ISO date
            reference_id TEXT NOT NULL UNIQUE,     -- CBS's own transaction reference
            remarks      TEXT DEFAULT ''
        )
    """)
    conn.commit()


def seed_data(conn: sqlite3.Connection, refund_fraction: float = 0.2) -> None:
    """
    Seed a refund record for a random subset of existing chargebacks'
    transactions — simulating the realistic case where most disputes have no
    prior refund on file, but some do (the exact scenario this table exists
    to catch).
    """
    rows = conn.execute(
        "SELECT utr, transaction_amount, transaction_date FROM chargebacks"
    ).fetchall()
    inserted = 0
    for row in rows:
        if random.random() >= refund_fraction:
            continue
        refund_date = (
            _parse_date(row["transaction_date"]) + timedelta(days=random.randint(1, 5))
        ).isoformat()
        reference_id = f"CBS-RFND-{row['utr']}"
        try:
            conn.execute(
                "INSERT INTO cbs_transactions (utr, txn_type, amount, txn_date, reference_id, remarks) "
                "VALUES (?, 'refund', ?, ?, ?, ?)",
                (row["utr"], row["transaction_amount"], refund_date, reference_id,
                 "Goodwill refund processed via CBS, outside dispute flow"),
            )
            inserted += 1
        except sqlite3.IntegrityError:
            pass  # skip duplicate reference_id on re-seed
    conn.commit()
    print(f"Seeded {inserted} CBS refund records (out of {len(rows)} transactions).")


def _parse_date(iso_str: str):
    from datetime import date
    return date.fromisoformat(iso_str)


def init_db(db_path: str = DB_PATH) -> None:
    """Create schema and seed if the table is empty."""
    conn = get_connection(db_path)
    create_schema(conn)
    count = conn.execute("SELECT COUNT(*) FROM cbs_transactions").fetchone()[0]
    if count == 0:
        seed_data(conn)
    else:
        print(f"cbs_transactions already has {count} rows — skipping seed.")
    conn.close()


def find_refund_for_utr(utr: str, db_path: str = DB_PATH) -> Optional[dict]:
    """
    Return the CBS refund record for this transaction's UTR, if one exists —
    ground truth for "was this already refunded outside the dispute
    process," independent of anything the merchant or customer claims.
    Returns None if no such record exists (the normal case).
    """
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM cbs_transactions WHERE utr = ? AND txn_type = 'refund' "
            "ORDER BY txn_date DESC LIMIT 1",
            (utr,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


if __name__ == "__main__":
    conn = get_connection()
    create_schema(conn)
    conn.execute("DELETE FROM cbs_transactions")
    conn.commit()
    seed_data(conn)
    conn.close()
