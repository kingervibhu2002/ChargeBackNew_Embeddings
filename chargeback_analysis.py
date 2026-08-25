"""
chargeback_analysis.py — Shared "what should happen to this chargeback"
logic, used by both auto_decision_poller.py (acts on it for merchants who
opted into auto-decision) and suggestion_poller.py (advises merchants who
didn't, without touching their case). Single source of truth so the two
pollers can never silently diverge on what a given case's recommendation is.
"""

from typing import NamedTuple, Optional

import decision_rules
from cbs import count_credits, find_refund_for_utr, has_pending_suspense

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
    2. For U002 (duplicate transaction) specifically: the bank's own
       ledger can directly confirm or refute the claim, rather than
       falling through to decision_rules.py's evidence-free "refund"
       default. That default exists because this project has no
       evidence-capture path outside a live chat session — every call
       here would otherwise be evidence-free, and per decide()'s logic,
       no evidence means no realistic chance of winning, so EVERY U002
       case would resolve to "refund" purely because there's nothing to
       ask the merchant for — even when the ledger clearly shows only one
       credit landed and the customer's duplicate-charge claim doesn't
       hold. The ledger is real, bank-side evidence a background poller
       can act on with no merchant involved, same justification as the
       CBS refund check above.
    3. Otherwise, decision_rules.decide() with no evidence present, same
       as before: known reason codes resolve to "refund", unmapped codes
       return no recommendation (action=None) rather than guessing.
    """
    cbs_refund = find_refund_for_utr(row["utr"], db_path=db_path)
    if cbs_refund:
        return Analysis(
            action="fight",
            reason=(
                f"CBS record shows this transaction was already refunded on "
                f"{cbs_refund['posting_date']} (ref: {cbs_refund['reference_id']}, "
                f"amount: {cbs_refund['amount']}) — the dispute appears moot/duplicate. "
                f"Disputing it should prevent a second payout for the same transaction."
            ),
            source="cbs",
        )

    if row["reason_code"] == "U002":
        credits = count_credits(row["utr"], db_path=db_path)
        if credits >= 2:
            return Analysis(
                action="refund",
                reason=(
                    f"Ledger shows {credits} separate credits posted for this transaction "
                    f"— the customer's duplicate-charge claim is confirmed by the bank's own "
                    f"posting records, not merely unrebutted. The duplicate amount should be "
                    f"refunded."
                ),
                source="ledger",
            )
        if has_pending_suspense(row["utr"], db_path=db_path):
            return Analysis(
                action=None,
                reason=(
                    "A ledger entry for this transaction is still pending/unresolved — "
                    "cannot confidently recommend fight or refund until it settles."
                ),
                source="ledger",
            )
        if credits == 1:
            return Analysis(
                action="fight",
                reason=(
                    "Ledger shows exactly one posted credit for this transaction and no "
                    "unresolved pending entries — the duplicate-charge claim is not supported "
                    "by the bank's own records."
                ),
                source="ledger",
            )
        # credits == 0: no credit ever posted for this UTR at all — an odd
        # situation the ledger itself can't resolve either way (not "one
        # credit, claim refuted" and not "two credits, claim confirmed").
        # Falls through to the rule table below rather than guess.

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
