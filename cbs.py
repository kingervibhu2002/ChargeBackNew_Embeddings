"""
cbs.py — Dummy Core Banking System ledger.

Models the one piece of ground truth neither the merchant's claims nor the
customer's dispute can be trusted to report accurately on their own: what
actually happened to a given transaction's money, as posted by the bank
itself. A customer can mistakenly claim a duplicate charge that never
happened, or fail to notice a refund they already received — that's a
dispute the bank's own ledger can settle directly, without needing the
merchant to argue it from scratch.

Started as a single flat "was this transaction refunded, yes/no" table
(`cbs_transactions`). Evolved into `ledger_entries` — real per-posting rows
per transaction (a transaction can have MORE than one credit, a pending/
unresolved entry, a refund, or a reversal) — because a flat existence check
can only ever answer "was there a refund." It can never answer "did the
bank's ledger actually show two separate credits for this one transaction,"
which is exactly the question a U002 (duplicate transaction) dispute needs
answered from real bank-side evidence rather than the absence of a
merchant-supplied counter-argument. See chargeback_analysis.py's use of
count_credits()/has_pending_suspense() for where this actually gets used.

Deliberately NOT modeled as "the real schema a production CBS uses" — there
is no single universal one; real banking systems distribute this across a
payment switch, CBS, GL/ledger, reconciliation platform, and more. This is a
synthetic, production-inspired schema scoped to exactly what a chargeback
investigation needs: was money credited once or more than once, is anything
still pending, and was it refunded.

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
        CREATE TABLE IF NOT EXISTS ledger_entries (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            utr          TEXT NOT NULL,           -- matches chargebacks.utr
            entry_type   TEXT NOT NULL,           -- 'credit' | 'refund' | 'reversal'
            amount       REAL NOT NULL,
            status       TEXT NOT NULL DEFAULT 'posted',  -- 'posted' | 'pending' | 'reversed'
            posting_date TEXT NOT NULL,           -- ISO date
            reference_id TEXT NOT NULL UNIQUE,     -- CBS's own posting reference
            remarks      TEXT DEFAULT ''
        )
    """)
    conn.commit()


def seed_data(
    conn: sqlite3.Connection,
    refund_fraction: float = 0.2,
    duplicate_fraction: float = 0.15,
    pending_fraction: float = 0.1,
) -> None:
    """
    Seed one baseline 'credit' entry (the expected single settlement credit)
    for every existing chargeback's transaction, then layer one of three
    mutually-exclusive scenarios onto a random subset — mirroring what a
    real bank's ledger actually looks like across a real transaction volume:
    most transactions are unremarkable (exactly one posted credit, nothing
    else), a minority were already refunded outside the dispute flow, a
    smaller minority genuinely received a second credit (the real-world
    case a U002 duplicate-transaction dispute is actually about), and a
    smaller minority still have an unresolved/pending entry sitting in the
    ledger (money that hasn't settled yet, one way or the other).

    Args:
        refund_fraction:    Fraction of transactions that already have a
                            goodwill refund posted (the scenario this table
                            originally existed to catch).
        duplicate_fraction: Fraction that genuinely received a SECOND
                            posted credit — real bank-side evidence that a
                            duplicate-transaction claim is valid, not just
                            unrebutted.
        pending_fraction:   Fraction with a credit still stuck in 'pending'
                            status — can't yet be confidently resolved
                            either way.
    """
    rows = conn.execute(
        "SELECT utr, transaction_amount, transaction_date FROM chargebacks"
    ).fetchall()
    inserted = 0
    for row in rows:
        credit_date = _parse_date(row["transaction_date"]) + timedelta(days=random.randint(0, 2))
        credit_status = "posted"

        roll = random.random()
        is_pending = roll < pending_fraction
        is_duplicate = pending_fraction <= roll < pending_fraction + duplicate_fraction
        is_refunded = (
            pending_fraction + duplicate_fraction
            <= roll < pending_fraction + duplicate_fraction + refund_fraction
        )
        if is_pending:
            credit_status = "pending"

        try:
            conn.execute(
                "INSERT INTO ledger_entries (utr, entry_type, amount, status, posting_date, reference_id, remarks) "
                "VALUES (?, 'credit', ?, ?, ?, ?, ?)",
                (row["utr"], row["transaction_amount"], credit_status, credit_date.isoformat(),
                 f"CBS-CR-{row['utr']}", "Original settlement credit"),
            )
            inserted += 1
        except sqlite3.IntegrityError:
            pass  # skip duplicate reference_id on re-seed

        if is_duplicate:
            dup_date = credit_date + timedelta(days=random.randint(1, 3))
            try:
                conn.execute(
                    "INSERT INTO ledger_entries (utr, entry_type, amount, status, posting_date, reference_id, remarks) "
                    "VALUES (?, 'credit', ?, 'posted', ?, ?, ?)",
                    (row["utr"], row["transaction_amount"], dup_date.isoformat(),
                     f"CBS-CR2-{row['utr']}", "Second settlement credit — system retry"),
                )
            except sqlite3.IntegrityError:
                pass
        elif is_refunded:
            refund_date = credit_date + timedelta(days=random.randint(1, 5))
            try:
                conn.execute(
                    "INSERT INTO ledger_entries (utr, entry_type, amount, status, posting_date, reference_id, remarks) "
                    "VALUES (?, 'refund', ?, 'posted', ?, ?, ?)",
                    (row["utr"], row["transaction_amount"], refund_date.isoformat(),
                     f"CBS-RFND-{row['utr']}", "Goodwill refund processed via CBS, outside dispute flow"),
                )
            except sqlite3.IntegrityError:
                pass

    conn.commit()
    print(
        f"Seeded ledger entries for {inserted} transactions "
        f"(~{refund_fraction:.0%} refunded, ~{duplicate_fraction:.0%} duplicate credit, "
        f"~{pending_fraction:.0%} pending)."
    )


def _parse_date(iso_str: str):
    from datetime import date
    return date.fromisoformat(iso_str)


def init_db(db_path: str = DB_PATH) -> None:
    """Create schema and seed if the table is empty."""
    conn = get_connection(db_path)
    create_schema(conn)
    count = conn.execute("SELECT COUNT(*) FROM ledger_entries").fetchone()[0]
    if count == 0:
        seed_data(conn)
    else:
        print(f"ledger_entries already has {count} rows — skipping seed.")
    conn.close()


def get_ledger_entries(utr: str, db_path: str = DB_PATH) -> list:
    """
    All ledger entries for a UTR, oldest first — the full posting history
    for this transaction (every credit, refund, or reversal the bank has
    recorded against it).
    """
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM ledger_entries WHERE utr = ? ORDER BY posting_date ASC",
            (utr,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def count_credits(utr: str, db_path: str = DB_PATH) -> int:
    """
    How many times the merchant's account was actually credited for this
    UTR, per the bank's own ledger — the real-evidence answer to "did we
    get charged/credited twice," not an inference from absence of a
    refund. Excludes 'pending' (hasn't landed yet) and 'reversed' (no
    longer valid) entries — only a posted credit counts as money that
    actually, currently sits in the merchant's account.
    """
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT COUNT(*) AS n FROM ledger_entries "
            "WHERE utr = ? AND entry_type = 'credit' AND status = 'posted'",
            (utr,),
        ).fetchone()
        return row["n"]
    finally:
        conn.close()


def has_pending_suspense(utr: str, db_path: str = DB_PATH) -> bool:
    """
    True if any ledger entry for this UTR is still 'pending' — money that
    hasn't settled one way or the other yet. A case with a pending entry
    can't be confidently resolved until it does.
    """
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT 1 FROM ledger_entries WHERE utr = ? AND status = 'pending' LIMIT 1",
            (utr,),
        ).fetchone()
        return row is not None
    finally:
        conn.close()


def find_refund_for_utr(utr: str, db_path: str = DB_PATH) -> Optional[dict]:
    """
    Return the ledger's refund record for this transaction's UTR, if one
    exists — ground truth for "was this already refunded outside the
    dispute process," independent of anything the merchant or customer
    claims. Returns None if no such record exists (the normal case).
    """
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM ledger_entries WHERE utr = ? AND entry_type = 'refund' AND status = 'posted' "
            "ORDER BY posting_date DESC LIMIT 1",
            (utr,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


if __name__ == "__main__":
    conn = get_connection()
    create_schema(conn)
    conn.execute("DELETE FROM ledger_entries")
    conn.commit()
    seed_data(conn)
    conn.close()
