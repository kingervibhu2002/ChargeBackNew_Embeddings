"""
chargeback_analysis.py — Shared "what should happen to this chargeback"
logic, used by both auto_decision_poller.py (acts on it for merchants who
opted into auto-decision) and suggestion_poller.py (advises merchants who
didn't, without touching their case). Single source of truth so the two
pollers can never silently diverge on what a given case's recommendation is.
"""

from typing import NamedTuple, Optional

import decision_rules
from cbs import find_refund_for_utr

# All chargebacks in this schema are NPCI/UPI disputes — see
# auto_decision_poller.py's matching comment for why this is a constant
# rather than a column read.
_NETWORK = "RuPay"


class Analysis(NamedTuple):
    action: Optional[str]   # "fight" | "refund" | None (no confident recommendation)
    reason: str
    source: str              # "cbs" | "rules" | "" (empty when action is None)


def analyze_chargeback(row, db_path: str) -> Analysis:
    """
    Determine the recommended action for one chargeback row (anything
    dict-like with 'utr' and 'reason_code' keys — a sqlite3.Row works).

    1. CBS duplicate-refund check runs FIRST and takes priority over the
       reason-code rule table — a prior refund on this exact transaction
       makes the dispute moot/duplicate regardless of what its reason code
       claims, so it always means "fight" (dispute it, citing the refund).
    2. Otherwise, decision_rules.decide() with no evidence present — this
       project has no evidence-capture path outside a live chat session, so
       every call here is evidence-free. Per decide()'s logic, that means
       known reason codes resolve to "refund" (no evidence = no realistic
       chance of winning), and unmapped codes return no recommendation
       (action=None) rather than guessing.
    """
    cbs_refund = find_refund_for_utr(row["utr"], db_path=db_path)
    if cbs_refund:
        return Analysis(
            action="fight",
            reason=(
                f"CBS record shows this transaction was already refunded on "
                f"{cbs_refund['txn_date']} (ref: {cbs_refund['reference_id']}, "
                f"amount: {cbs_refund['amount']}) — the dispute appears moot/duplicate. "
                f"Disputing it should prevent a second payout for the same transaction."
            ),
            source="cbs",
        )

    result = decision_rules.decide(
        card_network=_NETWORK,
        reason_code=row["reason_code"],
        evidence_present=[],
        evidence_missing=[],
    )
    if result is None:
        return Analysis(action=None, reason="", source="")

    decision, reason = result
    return Analysis(action=decision, reason=reason, source="rules")
