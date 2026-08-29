"""
merchant_db.py — SQLite database for NPCI UPI chargeback data.

Schema models NPCI dispute format for Airtel merchants.
Row-level security is enforced by the query layer (text_to_sql.py),
which always injects WHERE merchant_id = <logged-in-id>.

Run directly to create and seed the database:
    python merchant_db.py
"""

import sqlite3
from datetime import date, timedelta
from pathlib import Path
import random

DB_PATH = "chargebacks.db"

# NPCI UPI chargeback reason codes
NPCI_REASON_CODES = {
    "U001": "Transaction not done by customer (Fraud)",
    "U002": "Duplicate transaction",
    "U003": "Customer debited but merchant not credited",
    "U004": "Customer account debited multiple times",
    "U005": "Fraudulent transaction",
    "U006": "Transaction declined but amount debited",
    "U007": "Amount different from intended",
    "U008": "Goods or services not delivered",
    "U009": "Merchant not providing refund",
    "U010": "Technical error / system failure",
}

STATUSES   = ["Open", "Open", "Open", "Pending", "Won", "Lost", "Expired"]
BANKS      = ["SBI", "HDFC Bank", "ICICI Bank", "Axis Bank", "PNB", "Kotak", "Yes Bank"]
MERCHANTS  = [
    {"id": "AIRTEL_M001", "name": "Airtel Digital TV Services",    "vpa": "airteldtv@airtel"},
    {"id": "AIRTEL_M002", "name": "Airtel Broadband Solutions",     "vpa": "airtelbb@airtel"},
    {"id": "AIRTEL_M003", "name": "Airtel Mobile Recharge Store",   "vpa": "airtelmob@airtel"},
    {"id": "AIRTEL_M004", "name": "Airtel Xstream Premium",         "vpa": "airtelxstream@airtel"},
]


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """
    Return a SQLite connection with row_factory for dict-like rows.

    WAL mode + a busy_timeout are set because this file is now read/written
    from more than one process concurrently — the long-lived api_server.py
    process alongside short-lived scripts like auto_decision_poller.py and
    schema migrations. SQLite's default (rollback journal, 0ms busy timeout)
    fails immediately with "database is locked" on any overlap; WAL lets
    readers and a writer proceed without blocking each other, and the
    busy_timeout makes writer-vs-writer contention wait briefly and retry
    instead of erroring on the first collision.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=5000")
    try:
        # Switching journal mode requires momentary exclusive access — if
        # another process already holds the file open (e.g. a long-lived
        # checkpointer connection in api_server.py), this can fail even with
        # a busy_timeout set, since it's a mode change, not a normal write.
        # Non-fatal: busy_timeout alone still meaningfully helps with
        # ordinary write-vs-write contention even if WAL never gets applied.
        conn.execute("PRAGMA journal_mode=WAL")
    except sqlite3.OperationalError:
        pass
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chargebacks (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            merchant_id             TEXT NOT NULL,
            merchant_name           TEXT NOT NULL,
            merchant_vpa            TEXT NOT NULL,

            utr                     TEXT NOT NULL UNIQUE,   -- UPI Transaction Reference
            case_id                 TEXT NOT NULL UNIQUE,   -- NPCI dispute case ID

            customer_vpa            TEXT NOT NULL,
            customer_name           TEXT NOT NULL,
            issuing_bank            TEXT NOT NULL,

            transaction_amount      REAL NOT NULL,
            chargeback_amount       REAL NOT NULL,
            transaction_date        TEXT NOT NULL,          -- ISO date YYYY-MM-DD
            chargeback_filing_date  TEXT NOT NULL,
            response_deadline       TEXT NOT NULL,          -- merchant must respond by

            reason_code             TEXT NOT NULL,          -- U001 – U010
            reason_description      TEXT NOT NULL,

            status                  TEXT NOT NULL DEFAULT 'Open',
            resolution              TEXT DEFAULT NULL,      -- Fight / Accept / NULL
            resolution_date         TEXT DEFAULT NULL,

            notes                   TEXT DEFAULT '',

            suggested_action        TEXT DEFAULT NULL,      -- Fight / Accept / NULL — advisory
                                                              -- only, refreshed by suggestion_poller.py
                                                              -- (for merchants who have NOT opted into
                                                              -- auto-decision) AND by the live dispute
                                                              -- agent (chargeback_agent.py's DisputeAgent,
                                                              -- via case_recommendations.py) whenever a
                                                              -- live conversation reaches a real
                                                              -- recommendation for a case — regardless of
                                                              -- auto_decision preference, since that
                                                              -- toggle governs background automation, not
                                                              -- conversational help. Either writer only
                                                              -- ever touches these two columns, never
                                                              -- status/resolution/resolution_date.
            suggestion_reason       TEXT DEFAULT NULL
        )
    """)
    conn.commit()
    # Additive migration for DBs created before these columns existed.
    cols = {row["name"] for row in conn.execute("PRAGMA table_info(chargebacks)")}
    if "suggested_action" not in cols:
        conn.execute("ALTER TABLE chargebacks ADD COLUMN suggested_action TEXT DEFAULT NULL")
    if "suggestion_reason" not in cols:
        conn.execute("ALTER TABLE chargebacks ADD COLUMN suggestion_reason TEXT DEFAULT NULL")
    conn.commit()


def seed_data(conn: sqlite3.Connection, rows_per_merchant: int = 15) -> None:
    """Insert realistic sample NPCI chargeback rows for each merchant."""
    today     = date.today()
    reason_codes = list(NPCI_REASON_CODES.keys())
    inserted  = 0

    for merchant in MERCHANTS:
        for i in range(rows_per_merchant):
            txn_date       = today - timedelta(days=random.randint(1, 90))
            filing_date    = txn_date + timedelta(days=random.randint(3, 15))
            deadline       = filing_date + timedelta(days=30)
            status         = random.choice(STATUSES)
            reason_code    = random.choice(reason_codes)
            amount         = round(random.uniform(50, 25000), 2)
            res_date       = None
            resolution     = None

            if status in ("Won", "Lost"):
                resolution  = "Fight"
                res_date    = (filing_date + timedelta(days=random.randint(5, 25))).isoformat()
            elif status == "Expired":
                resolution  = "Accept"
                res_date    = deadline.isoformat()

            customer_idx   = random.randint(1000, 9999)
            utr            = f"UTR{txn_date.strftime('%Y%m%d')}{merchant['id'][-4:]}{i:03d}"
            case_id        = f"NPCI{filing_date.strftime('%Y%m%d')}{merchant['id'][-4:]}{i:03d}"

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
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    merchant["id"], merchant["name"], merchant["vpa"],
                    utr, case_id,
                    f"customer{customer_idx}@upi", f"Customer {customer_idx}",
                    random.choice(BANKS),
                    amount, amount,
                    txn_date.isoformat(), filing_date.isoformat(), deadline.isoformat(),
                    reason_code, NPCI_REASON_CODES[reason_code],
                    status, resolution, res_date, ""
                ))
                inserted += 1
            except sqlite3.IntegrityError:
                pass  # skip duplicate UTR/case_id on re-seed

    conn.commit()
    print(f"Seeded {inserted} chargeback rows across {len(MERCHANTS)} merchants.")


def init_db(db_path: str = DB_PATH) -> None:
    """Create schema and seed if the DB is empty."""
    conn = get_connection(db_path)
    create_schema(conn)
    count = conn.execute("SELECT COUNT(*) FROM chargebacks").fetchone()[0]
    if count == 0:
        seed_data(conn)
    else:
        print(f"DB already has {count} rows — skipping seed.")
    conn.close()


def list_open_chargebacks(
    merchant_id: str, limit: int = 10, db_path: str = DB_PATH
) -> list:
    """
    A merchant's own Open chargebacks, most urgent (soonest deadline) first.

    Plain parameterized SQL rather than an LLM call — this is a fixed,
    deterministic listing, not free-text reasoning, so it doesn't need
    text_to_sql.py's NL→SQL path (matches this project's general pattern of
    reserving LLM calls for genuinely open-ended tasks). Powers the Dispute
    Assistant tab's case-picker chips and open-case summary line.

    Args:
        merchant_id: Caller's own merchant ID (server-resolved, never
                     client-supplied — same trust boundary as text_to_sql.py).
        limit: Max rows to return.
        db_path: SQLite file path.

    Returns:
        list[dict]: rows with case_id, utr, reason_code, reason_description,
                    chargeback_amount, response_deadline — ordered by
                    response_deadline ascending.
    """
    conn = get_connection(db_path)
    rows = conn.execute(
        """
        SELECT case_id, utr, reason_code, reason_description,
               chargeback_amount, response_deadline
        FROM chargebacks
        WHERE merchant_id = ? AND status = 'Open'
        ORDER BY response_deadline ASC
        LIMIT ?
        """,
        (merchant_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


if __name__ == "__main__":
    if Path(DB_PATH).exists():
        Path(DB_PATH).unlink()
        print("Dropped existing DB.")
    init_db()
    conn = get_connection()
    for m in MERCHANTS:
        n = conn.execute(
            "SELECT COUNT(*) FROM chargebacks WHERE merchant_id=?", (m["id"],)
        ).fetchone()[0]
        print(f"  {m['id']} ({m['name']}): {n} chargebacks")
    conn.close()
