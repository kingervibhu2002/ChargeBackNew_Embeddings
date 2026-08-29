"""
cbs.py — Dummy Core Banking System ledger + network settlement records.

Models the two independent pieces of ground truth neither the merchant's
claims nor the customer's dispute can be trusted to report accurately on
their own: what the bank's own ledger shows happened to a transaction's
money (ledger_entries), and what the payment network independently reported
as settled for it (settlement_entries). A customer can mistakenly claim a
duplicate charge that never happened, or fail to notice a refund they
already received — the ledger settles that directly. But the ledger alone
is only ONE source; comparing it against an independent settlement record
(reconcile_utr()) is what NPCI's own operating material actually requires
for UPI exception/dispute handling — a three-way reconciliation across the
network feed, the bank's switch, and its CBS. This module doesn't model all
three, but it models the two that matter most for a chargeback
investigation: does the bank's internal ledger agree with what the network
independently says was settled.

History: started as a single flat "was this transaction refunded, yes/no"
table (`cbs_transactions`). Evolved into `ledger_entries` — real per-posting
rows (a transaction can have MORE than one credit, a pending/unresolved
entry, a refund, or a reversal) — because a flat existence check can only
ever answer "was there a refund," never "did the bank's ledger actually show
two separate credits for this one transaction," the real-evidence question a
U002 (duplicate transaction) dispute needs answered. Then added
`reversal_of_id` (a reversal row references the specific credit it cancels)
so a credit → reversal → repost sequence nets to ONE effective credit, not
two raw rows that look like a duplicate but aren't — a naive row count over
`entry_type='credit'` alone would get this wrong the moment a reversal ever
existed, so this is fixed before any code path actually creates one, not
after a real bug was hit. Then added `settlement_entries` +
`reconcile_utr()` for the same reason: a bank's own ledger can be
internally consistent and still not match what the network actually
settled, and that mismatch is itself real, useful investigative signal —
not "no evidence," a THIRD kind of finding entirely.

Deliberately NOT modeled as "the real schema a production CBS uses" — there
is no single universal one; real banking systems distribute this across a
payment switch, CBS, GL/ledger, reconciliation platform, and more. This is a
synthetic, production-inspired schema scoped to exactly what a chargeback
investigation needs.

Then added `network_debit_attempts`, for a gap in the reasoning above it,
not the schema: `reconcile_utr()` proves the bank's ledger agrees with what
the network settled TO THE MERCHANT — it says nothing about how many times
the CUSTOMER's account was actually debited upstream, at the NPCI switch.
A U002 (duplicate transaction) case with a clean, reconciled single credit
was being treated as proof the customer's duplicate-charge claim was false
— but a genuine duplicate debit could occur at an intermediary/PSP layer
and be reversed (or, worse, simply never make it into this merchant's
ledger at all) without that clean-ledger picture ever changing. This table
is the customer-side half of the same investigation: what the network's
own transaction log shows was actually attempted against the customer,
independent of what reached the merchant. See get_debit_attempt_status()
and chargeback_analysis.py's U002 branch for how the two halves combine.

This is deliberately separate from decision_rules.py's `refund_already_issued`
evidence tag, which the merchant supplies by assertion during a live chat
(unverified). This table is the authoritative source that assertion should
have been checked against — a merchant claiming "I already refunded this" in
chat isn't evidence; a matching row here is.

Run directly to create and seed the tables:
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
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            utr            TEXT NOT NULL,           -- matches chargebacks.utr
            entry_type     TEXT NOT NULL,           -- 'credit' | 'refund' | 'reversal'
            amount         REAL NOT NULL,
            status         TEXT NOT NULL DEFAULT 'posted',  -- 'posted' | 'pending' | 'reversed'
            posting_date   TEXT NOT NULL,           -- ISO date
            reference_id   TEXT NOT NULL UNIQUE,     -- CBS's own posting reference
            reversal_of_id INTEGER DEFAULT NULL,     -- for entry_type='reversal': the
                                                      -- ledger_entries.id this cancels out
            remarks        TEXT DEFAULT ''
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS settlement_entries (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            utr             TEXT NOT NULL,           -- matches chargebacks.utr
            amount          REAL NOT NULL,
            settlement_type TEXT NOT NULL DEFAULT 'AUTH',  -- 'AUTH' | 'DISPUTE' | 'ADJUSTMENT'
                                                      -- NPCI runs AUTH and dispute settlement
                                                      -- as separate cycles, not one generic
                                                      -- "settlement" concept — kept distinct
                                                      -- here for the same reason.
            settlement_date TEXT NOT NULL,
            cycle_id        TEXT NOT NULL,
            reference_id    TEXT NOT NULL UNIQUE,
            remarks         TEXT DEFAULT ''
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS network_debit_attempts (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            utr            TEXT NOT NULL,           -- matches chargebacks.utr
            attempt_seq    INTEGER NOT NULL,        -- 1st, 2nd, ... debit attempt against
                                                      -- the CUSTOMER's account for this
                                                      -- transaction, as seen at the NPCI/PSP
                                                      -- switch — independent of whether it
                                                      -- ever produced a merchant-side credit.
            outcome        TEXT NOT NULL,           -- 'success' | 'reversed' — 'reversed'
                                                      -- means NPCI/the issuer reversed THIS
                                                      -- attempt before settlement (customer
                                                      -- not net-charged for it), the same
                                                      -- distinction ledger_entries.reversal_
                                                      -- of_id draws on the merchant's side.
            npci_txn_ref   TEXT NOT NULL UNIQUE,
            initiated_at   TEXT NOT NULL,            -- ISO date
            remarks        TEXT DEFAULT ''
        )
    """)
    conn.commit()


def seed_data(
    conn: sqlite3.Connection,
    refund_fraction: float = 0.2,
    duplicate_fraction: float = 0.15,
    pending_fraction: float = 0.1,
    reversal_repost_fraction: float = 0.08,
    settlement_mismatch_fraction: float = 0.05,
) -> None:
    """
    Seed one baseline 'credit' entry (the expected single settlement credit)
    and one matching 'AUTH' settlement entry for every existing chargeback's
    transaction, then layer one of several mutually-exclusive ledger
    scenarios onto a random subset — mirroring what a real bank's ledger and
    network settlement actually look like across real transaction volume:
    most transactions are unremarkable, a minority were already refunded
    outside the dispute flow, a smaller minority genuinely received a
    second credit (a true duplicate — the real-world case a U002 dispute is
    actually about), a smaller minority still have an unresolved/pending
    entry, and a smaller minority still show a credit that was reversed and
    then correctly reposted (net ONE effective credit, even though two raw
    'credit' rows exist — the exact scenario a reversal-unaware credit count
    would misread as a duplicate). Independently, a small fraction of the
    otherwise-unremarkable cases get a settlement amount that doesn't match
    the ledger at all — a genuine reconciliation exception, not explained by
    any of the ledger-side scenarios above.

    Args:
        refund_fraction:              Fraction with a goodwill refund posted.
        duplicate_fraction:           Fraction with a genuine SECOND posted
                                     credit (true duplicate, no reversal).
        pending_fraction:             Fraction with a credit stuck 'pending'.
        reversal_repost_fraction:     Fraction where the original credit was
                                     reversed and then reposted — nets to
                                     one effective credit despite two raw
                                     'credit' rows.
        settlement_mismatch_fraction: Of the remaining (otherwise normal)
                                     cases, fraction whose settlement amount
                                     doesn't match the ledger at all.
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
        is_reversal_repost = (
            pending_fraction + duplicate_fraction + refund_fraction
            <= roll < pending_fraction + duplicate_fraction + refund_fraction + reversal_repost_fraction
        )
        is_normal = not (is_pending or is_duplicate or is_refunded or is_reversal_repost)
        if is_pending:
            credit_status = "pending"

        credit_id = None
        try:
            cur = conn.execute(
                "INSERT INTO ledger_entries (utr, entry_type, amount, status, posting_date, reference_id, remarks) "
                "VALUES (?, 'credit', ?, ?, ?, ?, ?)",
                (row["utr"], row["transaction_amount"], credit_status, credit_date.isoformat(),
                 f"CBS-CR-{row['utr']}", "Original settlement credit"),
            )
            credit_id = cur.lastrowid
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
        elif is_reversal_repost and credit_id is not None:
            reversal_date = credit_date + timedelta(days=random.randint(1, 2))
            repost_date = reversal_date + timedelta(days=random.randint(1, 2))
            try:
                conn.execute(
                    "INSERT INTO ledger_entries "
                    "(utr, entry_type, amount, status, posting_date, reference_id, reversal_of_id, remarks) "
                    "VALUES (?, 'reversal', ?, 'posted', ?, ?, ?, ?)",
                    (row["utr"], row["transaction_amount"], reversal_date.isoformat(),
                     f"CBS-REV-{row['utr']}", credit_id,
                     "Original credit reversed — posting error"),
                )
                conn.execute(
                    "INSERT INTO ledger_entries (utr, entry_type, amount, status, posting_date, reference_id, remarks) "
                    "VALUES (?, 'credit', ?, 'posted', ?, ?, ?)",
                    (row["utr"], row["transaction_amount"], repost_date.isoformat(),
                     f"CBS-CR-REPOST-{row['utr']}", "Reposted after reversal — corrected posting"),
                )
            except sqlite3.IntegrityError:
                pass

        # Settlement — one AUTH entry per transaction. Deliberately mismatched
        # for a small subset of otherwise-normal cases (never the duplicate/
        # refunded/pending/reversal-repost scenarios above, which already
        # have their own, differently-shaped ledger story) — a genuine
        # reconciliation exception with no other explanation.
        settlement_date = credit_date + timedelta(days=random.randint(0, 1))
        settlement_amount = row["transaction_amount"]
        if is_normal and random.random() < settlement_mismatch_fraction:
            settlement_amount = 0.0  # network reports nothing settled at all
        try:
            conn.execute(
                "INSERT INTO settlement_entries "
                "(utr, amount, settlement_type, settlement_date, cycle_id, reference_id, remarks) "
                "VALUES (?, ?, 'AUTH', ?, ?, ?, ?)",
                (row["utr"], settlement_amount, settlement_date.isoformat(),
                 f"AUTH-{settlement_date.strftime('%Y%m')}", f"SET-{row['utr']}",
                 "Network settlement record"),
            )
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    print(
        f"Seeded ledger entries for {inserted} transactions "
        f"(~{refund_fraction:.0%} refunded, ~{duplicate_fraction:.0%} duplicate credit, "
        f"~{pending_fraction:.0%} pending, ~{reversal_repost_fraction:.0%} reversed+reposted), "
        f"plus one settlement record each (~{settlement_mismatch_fraction:.0%} of normal cases "
        f"deliberately mismatched)."
    )


def seed_network_data(
    conn: sqlite3.Connection,
    no_data_fraction: float = 0.15,
    duplicate_reversed_fraction: float = 0.07,
    duplicate_unreversed_fraction: float = 0.03,
) -> None:
    """
    Seed network_debit_attempts — kept as its own pass over `chargebacks`,
    independent of seed_data()'s ledger/settlement scenarios above (a
    different random roll, not conditioned on is_duplicate/is_refunded/
    etc.), so this table can be added to an ALREADY-seeded database (see
    init_db()) without re-touching ledger_entries/settlement_entries at all.

    Most transactions get a single, unremarkable debit attempt — matching
    the single merchant credit seed_data() already gave them. A minority
    haven't been reconciled with the network yet at all (no rows — see
    get_debit_attempt_status()'s "no_data" status). Of the rest, a smaller
    minority show a genuine second attempt: most of THOSE were reversed by
    the network before settlement (a real duplicate attempt the customer
    was never net-charged for), and a smaller remainder succeeded and were
    never reversed — a genuine network-level duplicate debit that this
    merchant's own ledger has no way to see, the exact gap this table
    exists to close.

    Args:
        no_data_fraction:             Fraction with NO network record at
                                     all yet (not yet reconciled).
        duplicate_reversed_fraction:  Fraction with a second attempt that
                                     was reversed before settlement.
        duplicate_unreversed_fraction: Fraction with a second attempt that
                                     succeeded and was never reversed — a
                                     real duplicate debit invisible to the
                                     merchant's own ledger.
    """
    rows = conn.execute("SELECT utr, transaction_date FROM chargebacks").fetchall()
    inserted = 0
    for row in rows:
        roll = random.random()
        if roll < no_data_fraction:
            continue  # not yet reconciled with the network — no rows at all

        attempt_date = _parse_date(row["transaction_date"])
        try:
            conn.execute(
                "INSERT INTO network_debit_attempts "
                "(utr, attempt_seq, outcome, npci_txn_ref, initiated_at, remarks) "
                "VALUES (?, 1, 'success', ?, ?, ?)",
                (row["utr"], f"NPCI-{row['utr']}-1", attempt_date.isoformat(),
                 "First debit attempt against the customer"),
            )
            inserted += 1
        except sqlite3.IntegrityError:
            pass

        second_outcome = None
        if roll < no_data_fraction + duplicate_reversed_fraction:
            second_outcome = "reversed"
        elif roll < no_data_fraction + duplicate_reversed_fraction + duplicate_unreversed_fraction:
            second_outcome = "success"
        if second_outcome:
            second_date = attempt_date + timedelta(minutes=random.randint(1, 30))
            remarks = (
                "Retry attempt — reversed by the network before settlement"
                if second_outcome == "reversed" else
                "Second successful debit — not reflected in the merchant's ledger credit"
            )
            try:
                conn.execute(
                    "INSERT INTO network_debit_attempts "
                    "(utr, attempt_seq, outcome, npci_txn_ref, initiated_at, remarks) "
                    "VALUES (?, 2, ?, ?, ?, ?)",
                    (row["utr"], second_outcome, f"NPCI-{row['utr']}-2",
                     second_date.isoformat(), remarks),
                )
            except sqlite3.IntegrityError:
                pass

    conn.commit()
    print(
        f"Seeded network debit-attempt records for {inserted} transactions "
        f"(~{no_data_fraction:.0%} not yet reconciled with the network, "
        f"~{duplicate_reversed_fraction:.0%} a second attempt reversed before "
        f"settlement, ~{duplicate_unreversed_fraction:.0%} a second attempt that "
        f"succeeded but isn't reflected in the merchant's ledger)."
    )


def _parse_date(iso_str: str):
    from datetime import date
    return date.fromisoformat(iso_str)


def get_debit_attempt_status(utr: str, db_path: str = DB_PATH) -> dict:
    """
    What the payment network's OWN transaction log shows about how many
    times the CUSTOMER's account was actually debited for this UTR —
    independent of, and answering a different question than, count_credits()
    (which only says how many times the MERCHANT was credited).

    This is the customer-side half of a U002 investigation: a clean,
    reconciled merchant ledger (reconcile_utr()) only proves what reached
    the merchant. It says nothing about whether a duplicate debit occurred
    upstream — at an intermediary/PSP layer — that was later reversed, or
    (worse) one that succeeded but whose credit never reached this
    merchant's ledger at all. See cbs.py's module docstring for the live
    U002 case that made this gap concrete.

    Returns:
        {"attempt_count": int, "unreversed_count": int,
         "status": "no_data" | "single_attempt" | "duplicate_reversed" |
                    "duplicate_unreversed"}
        "no_data" means this UTR hasn't been reconciled with the network
        yet — nothing here to confirm OR refute a duplicate-debit claim,
        not the same as a confirmed single attempt.
    """
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT outcome FROM network_debit_attempts WHERE utr = ?",
            (utr,),
        ).fetchall()
    finally:
        conn.close()

    if not rows:
        return {"attempt_count": 0, "unreversed_count": 0, "status": "no_data"}

    attempt_count = len(rows)
    unreversed_count = sum(1 for r in rows if r["outcome"] != "reversed")

    if attempt_count == 1:
        status = "single_attempt"
    elif unreversed_count <= 1:
        status = "duplicate_reversed"
    else:
        status = "duplicate_unreversed"

    return {
        "attempt_count": attempt_count,
        "unreversed_count": unreversed_count,
        "status": status,
    }


def init_db(db_path: str = DB_PATH) -> None:
    """Create schema and seed if the tables are empty."""
    conn = get_connection(db_path)
    create_schema(conn)
    count = conn.execute("SELECT COUNT(*) FROM ledger_entries").fetchone()[0]
    if count == 0:
        seed_data(conn)
    else:
        print(f"ledger_entries already has {count} rows — skipping seed.")

    # A separate presence check, not folded into the one above — this table
    # was added after ledger_entries/settlement_entries were already in
    # production use, and needs to backfill onto an existing database
    # without re-touching (or re-randomizing) either of those.
    net_count = conn.execute("SELECT COUNT(*) FROM network_debit_attempts").fetchone()[0]
    if net_count == 0:
        seed_network_data(conn)
    else:
        print(f"network_debit_attempts already has {net_count} rows — skipping seed.")
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


def _net_posted_credits(conn: sqlite3.Connection, utr: str) -> list:
    """
    Posted 'credit' rows for this UTR, EXCLUDING any that a posted
    'reversal' row references — the shared logic behind count_credits() and
    total_credit_amount(). A raw `entry_type='credit'` count alone would
    misread a credit → reversal → repost sequence as two credits instead of
    the one that's actually still standing; this is what actually nets that
    out, using the reversal's own reversal_of_id reference rather than
    guessing from amounts or ordering.
    """
    reversed_ids = {
        r["reversal_of_id"] for r in conn.execute(
            "SELECT reversal_of_id FROM ledger_entries "
            "WHERE utr = ? AND entry_type = 'reversal' AND status = 'posted' AND reversal_of_id IS NOT NULL",
            (utr,),
        ).fetchall()
    }
    credits = conn.execute(
        "SELECT id, amount FROM ledger_entries WHERE utr = ? AND entry_type = 'credit' AND status = 'posted'",
        (utr,),
    ).fetchall()
    return [c for c in credits if c["id"] not in reversed_ids]


def count_credits(utr: str, db_path: str = DB_PATH) -> int:
    """
    How many times the merchant's account was actually, currently credited
    for this UTR, per the bank's own ledger — the real-evidence answer to
    "did we get charged/credited twice," not an inference from absence of a
    refund. Excludes 'pending' (hasn't landed yet) and 'reversed' entries,
    AND nets out any posted credit that a posted reversal specifically
    references — a credit that was reversed and then correctly reposted
    counts as ONE effective credit, not two raw rows.
    """
    conn = get_connection(db_path)
    try:
        return len(_net_posted_credits(conn, utr))
    finally:
        conn.close()


def total_credit_amount(utr: str, db_path: str = DB_PATH) -> float:
    """
    Net posted credit amount for this UTR — the amount-based counterpart to
    count_credits(), used by reconcile_utr() to compare against what the
    network independently reported as settled.
    """
    conn = get_connection(db_path)
    try:
        return round(sum(c["amount"] for c in _net_posted_credits(conn, utr)), 2)
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


def reconcile_utr(utr: str, db_path: str = DB_PATH) -> dict:
    """
    Compare the network's independently-reported AUTH settlement amount for
    this UTR against the bank's own net ledger credit total — a genuinely
    independent-source check, not just "does our own ledger look
    internally consistent." NPCI's own operating material requires exactly
    this kind of reconciliation (network feed vs. bank records) for UPI
    exception/dispute handling; a mismatch here is real investigative
    signal in its own right; it means something an "own ledger looks fine"
    check can never surface on its own.

    Returns:
        {"settlement_amount": float, "ledger_credit_total": float,
         "status": "matched" | "mismatch" | "no_data"}
        "no_data" means neither a settlement nor a ledger credit exists for
        this UTR at all — nothing to reconcile, not the same as a genuine
        mismatch.
    """
    conn = get_connection(db_path)
    try:
        settlement_total = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM settlement_entries "
            "WHERE utr = ? AND settlement_type = 'AUTH'",
            (utr,),
        ).fetchone()["total"]
    finally:
        conn.close()

    ledger_total = total_credit_amount(utr, db_path=db_path)

    if settlement_total == 0 and ledger_total == 0:
        status = "no_data"
    elif abs(settlement_total - ledger_total) < 0.01:
        status = "matched"
    else:
        status = "mismatch"

    return {
        "settlement_amount": round(settlement_total, 2),
        "ledger_credit_total": ledger_total,
        "status": status,
    }


if __name__ == "__main__":
    conn = get_connection()
    # DROP, not DELETE — this table has no migration tooling (a deliberate,
    # documented tradeoff for a synthetic demo schema, same as merchant_db.py/
    # usermaster.py's own re-seed convention); a schema change (e.g. adding
    # reversal_of_id) needs a fresh CREATE TABLE, not just cleared rows in
    # the old one.
    conn.execute("DROP TABLE IF EXISTS ledger_entries")
    conn.execute("DROP TABLE IF EXISTS settlement_entries")
    conn.execute("DROP TABLE IF EXISTS network_debit_attempts")
    conn.commit()
    create_schema(conn)
    seed_data(conn)
    seed_network_data(conn)
    conn.close()
