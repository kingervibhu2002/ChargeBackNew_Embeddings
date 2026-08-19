"""
usermaster.py — User/role table for the chargeback portal.

Models the login-time identity every request resolves to: which user,
what role, and — for merchant users only — which merchant they're scoped to.
Admin roles (bankopsadmin, bankadmin_maker, bankadmin_checker) have no
merchant_id: they represent Airtel bank staff who can see across merchants.

Lives in its own module (rather than merchant_db.py) because merchant_db.py
owns the `chargebacks` business table, while this owns portal identity —
same separation as auth.py (identity resolution) vs. this (identity storage).

Run directly to create and seed the table:
    python usermaster.py
"""

import hashlib
import sqlite3
from pathlib import Path
from typing import Optional

from merchant_db import DB_PATH, MERCHANTS, get_connection

# Bank-side roles that can see across all merchants. Distinct from "merchant",
# the single role scoped to one merchant_id.
ADMIN_ROLES = {"bankopsadmin", "bankadmin_maker", "bankadmin_checker"}

# Demo seed — plaintext keys here (hashed before storage), mirroring the
# pattern auth.py used to hardcode directly. One merchant user per existing
# demo merchant, plus one user per admin role.
#
# Merchant usernames are derived from MERCHANTS' actual `name` field (not a
# separately-invented display name) — they must match exactly, because
# text_to_sql.py's merchant-escalation check and any UI copy compare what a
# caller types against this same name. A mismatch here previously let a
# merchant type the login-screen's display name for another merchant ("Airtel
# Broadband Ops") that didn't match the real merchant_name in the chargebacks
# table ("Airtel Broadband Solutions") at all, so the escalation-detection
# code couldn't recognize it as naming another merchant.
_ADMIN_USERS = [
    # user_id,  username,               role,                merchant_id,  api_key
    ("U-A001",  "Bank Ops Admin",       "bankopsadmin",       None,         "key-bank-opsadmin-x1"),
    ("U-A002",  "Bank Admin Maker",     "bankadmin_maker",    None,         "key-bank-maker-x2"),
    ("U-A003",  "Bank Admin Checker",   "bankadmin_checker",  None,         "key-bank-checker-x3"),
]

_MERCHANT_API_KEYS = {
    "AIRTEL_M001": "key-airtel-m001-alpha9",
    "AIRTEL_M002": "key-airtel-m002-beta7",
    "AIRTEL_M003": "key-airtel-m003-gamma5",
    "AIRTEL_M004": "key-airtel-m004-delta3",
}

_DEMO_USERS = [
    (f"U-{m['id'].split('_')[-1]}", m["name"], "merchant", m["id"], _MERCHANT_API_KEYS[m["id"]])
    for m in MERCHANTS
] + _ADMIN_USERS


def create_schema(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usermaster (
            user_id       TEXT PRIMARY KEY,
            username      TEXT NOT NULL,
            role          TEXT NOT NULL,             -- 'merchant' | one of ADMIN_ROLES
            merchant_id   TEXT,                       -- set for role='merchant', NULL for admin roles
            api_key_hash  TEXT NOT NULL UNIQUE,
            auto_decision TEXT NOT NULL DEFAULT 'manual'  -- 'manual' | 'auto' — merchant-only;
                                                            -- 'auto' lets auto_decision_poller.py
                                                            -- apply decision_rules.py's recommendation
                                                            -- to new Open chargebacks without a human
                                                            -- confirming each one. Meaningless for
                                                            -- admin roles (no chargebacks of their own).
        )
    """)
    conn.commit()
    # Additive migration for DBs created before this column existed — CREATE
    # TABLE IF NOT EXISTS above is a no-op on an existing table, so a
    # pre-existing usermaster.db needs the column added explicitly.
    cols = {row["name"] for row in conn.execute("PRAGMA table_info(usermaster)")}
    if "auto_decision" not in cols:
        conn.execute("ALTER TABLE usermaster ADD COLUMN auto_decision TEXT NOT NULL DEFAULT 'manual'")
        conn.commit()


def seed_data(conn: sqlite3.Connection) -> None:
    inserted = 0
    for user_id, username, role, merchant_id, api_key in _DEMO_USERS:
        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        try:
            conn.execute(
                "INSERT INTO usermaster (user_id, username, role, merchant_id, api_key_hash) "
                "VALUES (?,?,?,?,?)",
                (user_id, username, role, merchant_id, api_key_hash),
            )
            inserted += 1
        except sqlite3.IntegrityError:
            pass  # skip duplicate user_id/api_key_hash on re-seed
    conn.commit()
    print(f"Seeded {inserted} usermaster rows.")


def init_db(db_path: str = DB_PATH) -> None:
    """Create schema and seed if the table is empty."""
    conn = get_connection(db_path)
    create_schema(conn)
    count = conn.execute("SELECT COUNT(*) FROM usermaster").fetchone()[0]
    if count == 0:
        seed_data(conn)
    else:
        print(f"usermaster already has {count} rows — skipping seed.")
    conn.close()


_VALID_AUTO_DECISION = {"manual", "auto"}


def set_auto_decision(merchant_id: str, value: str, db_path: str = DB_PATH) -> bool:
    """
    Set a merchant's auto-decision preference. Returns False (no-op) if
    merchant_id doesn't resolve to a merchant row or value isn't recognized —
    callers should treat that as a 400, not silently ignore it.
    """
    if value not in _VALID_AUTO_DECISION:
        return False
    conn = get_connection(db_path)
    try:
        cur = conn.execute(
            "UPDATE usermaster SET auto_decision = ? WHERE merchant_id = ? AND role = 'merchant'",
            (value, merchant_id),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def get_auto_decision(merchant_id: str, db_path: str = DB_PATH) -> Optional[str]:
    """Return a merchant's current auto-decision preference, or None if not found."""
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT auto_decision FROM usermaster WHERE merchant_id = ? AND role = 'merchant'",
            (merchant_id,),
        ).fetchone()
        return row["auto_decision"] if row else None
    finally:
        conn.close()


def demo_identities() -> list:
    """
    Plaintext demo identities for the UI login selector — never derived from
    the hashed table (hashes aren't reversible), so this list is the source
    of truth both for seeding and for what the UI offers to log in as.
    """
    return [
        {
            "user_id":     user_id,
            "username":    username,
            "role":        role,
            "merchant_id": merchant_id,
            "api_key":     api_key,
        }
        for user_id, username, role, merchant_id, api_key in _DEMO_USERS
    ]


if __name__ == "__main__":
    conn = get_connection()
    create_schema(conn)
    conn.execute("DELETE FROM usermaster")
    conn.commit()
    seed_data(conn)
    for row in conn.execute("SELECT user_id, username, role, merchant_id FROM usermaster"):
        print(f"  {row['user_id']:8s} {row['role']:18s} merchant={row['merchant_id']}  ({row['username']})")
    conn.close()
