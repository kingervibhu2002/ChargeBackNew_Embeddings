"""
auth.py — API key authentication for the chargeback portal.

Resolves an X-Merchant-Key header to a full Identity (user_id, role,
merchant_id) by looking it up in the usermaster table — not just a
merchant_id, since admin roles (bankopsadmin, bankadmin_maker,
bankadmin_checker) aren't scoped to any single merchant.

The identity is NEVER accepted from the client request body — it is always
resolved server-side from a verified key, so a merchant can't claim to be
an admin (or another merchant) by editing the request.
"""

import hashlib
import hmac
from dataclasses import dataclass
from typing import Optional

from fastapi import Header, HTTPException

from usermaster import ADMIN_ROLES, demo_identities, init_db as init_usermaster_db
from merchant_db import get_connection


@dataclass(frozen=True)
class Identity:
    """Resolved caller identity for one request."""
    user_id:     str
    username:    str
    role:        str             # 'merchant' | one of ADMIN_ROLES
    merchant_id: Optional[str]   # set for role='merchant', None for admin roles

    @property
    def is_admin(self) -> bool:
        return self.role in ADMIN_ROLES


def resolve_identity(api_key: str, db_path: str = "chargebacks.db") -> Optional[Identity]:
    """
    Return the Identity for a valid API key, or None if invalid.

    Uses constant-time comparison per row to prevent timing attacks — same
    approach as the old hardcoded-dict version, just now backed by the
    usermaster table so admin roles are representable too.
    """
    init_usermaster_db(db_path)  # no-op once seeded; cheap COUNT(*) check
    candidate = hashlib.sha256(api_key.encode()).hexdigest()
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT user_id, username, role, merchant_id, api_key_hash FROM usermaster"
        ).fetchall()
    finally:
        conn.close()

    for row in rows:
        if hmac.compare_digest(candidate, row["api_key_hash"]):
            return Identity(
                user_id=row["user_id"],
                username=row["username"],
                role=row["role"],
                merchant_id=row["merchant_id"],
            )
    return None


def require_identity(x_merchant_key: str = Header(default="")) -> Identity:
    """
    FastAPI dependency — resolves the caller's Identity from X-Merchant-Key.
    Raises 401 if the key is missing, 403 if it doesn't match any user.

    Usage in endpoint:
        @app.post("/query")
        def query(req: QueryRequest, identity: Identity = Depends(require_identity)):
            ...
    """
    if not x_merchant_key:
        raise HTTPException(
            status_code=401,
            detail="X-Merchant-Key header is required.",
        )
    identity = resolve_identity(x_merchant_key)
    if not identity:
        raise HTTPException(
            status_code=403,
            detail="Invalid or expired API key.",
        )
    return identity


def require_merchant(identity: Identity = None, x_merchant_key: str = Header(default="")) -> str:
    """
    Back-compat dependency for callers that only need merchant_id and should
    NOT be reachable by admin roles (e.g. anything that writes/edits a single
    merchant's dispute). Admin identities are rejected here — use
    require_identity() directly for endpoints that are admin-aware.
    """
    ident = require_identity(x_merchant_key)
    if ident.is_admin:
        raise HTTPException(
            status_code=403,
            detail="This endpoint is merchant-only; admin accounts are not scoped to a single merchant.",
        )
    return ident.merchant_id


# Demo helper — shows available demo identities (merchants + admins) for the
# UI login selector. Plaintext keys only ever live here / in usermaster.py's
# seed list, never derived from the hashed table.
DEMO_IDENTITIES: list = demo_identities()

# Back-compat: old callers importing DEMO_KEYS (merchant_id -> api_key) still work.
DEMO_KEYS: dict = {
    d["merchant_id"]: d["api_key"] for d in DEMO_IDENTITIES if d["merchant_id"]
}
