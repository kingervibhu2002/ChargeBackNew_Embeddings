"""
decision_rules.py — Deterministic fight/refund rule engine.

Replaces the LLM "judgment call" in _decide_node with a hand-curated lookup
table for codes we have clear evidence requirements for. Reason codes not in
RULES fall through to the existing LLM call in chargeback_agent.py — this
table is additive, not a replacement for the LLM path.

Why hand-curated instead of derived from the encyclopedia frontmatter: the
149 encyclopedia docs use two incompatible YAML frontmatter schemas (some
have network/reason_code fields, others have description/chargeback_type/
win_rate with neither), so auto-deriving this table isn't reliable without a
separate normalization pass that's out of scope for v1.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from evidence_tags import humanize_evidence


@dataclass(frozen=True)
class DecisionRule:
    """
    One reason code's evidence requirements.

    required_any: at least one of these tags in evidence_present → fight.
    required_all: every one of these tags must be in evidence_present → fight
                  (use alongside required_any for "and" requirements; leave
                  empty to only require the "any" set).
    disqualifying: if any of these tags are in evidence_present, always
                   refund regardless of required_any/required_all — used for
                   cases where the dispute is already moot (e.g. merchant
                   already refunded an item-not-received claim).
    always_refund: for codes where NO evidence the merchant could supply
                   changes the outcome — liability sits with a third party
                   (e.g. the bank/PSP for a technical-failure code) by the
                   reason code's own definition, not by anything the
                   merchant did or didn't do. Checked before required_any/
                   required_all (which default to "trivially satisfied" when
                   empty and would otherwise resolve to "fight" — the
                   opposite of what this represents). Distinct from asking
                   for evidence and getting none: this is "don't ask," not
                   "asked and found nothing."
    """
    required_any:  Set[str] = field(default_factory=set)
    required_all:  Set[str] = field(default_factory=set)
    disqualifying: Set[str] = field(default_factory=set)
    always_refund: bool = False
    fight_reason:  str = ""
    refund_reason: str = ""


# Keyword hints used to pick a Mastercard 4853 sub-type from the dispute
# text. 4853 alone covers six dispute sub-types with incompatible evidence
# requirements (Credit Not Processed vs Not As Described vs Cancelled
# Merchandise vs Digital Goods), so the plain (network, reason_code) key
# isn't precise enough for that one code.
#
# Each subtype needs one keyword from EACH of its groups (AND across groups,
# OR within a group) rather than one exact phrase — merchants phrase the
# same complaint many ways ("credit not processed" / "never got my refund" /
# "refund was never processed"), and a literal phrase list missed common
# rewordings during testing.
_MC_4853_SUBTYPE_HINT_GROUPS: Dict[str, List[List[str]]] = {
    # Checked first — a fraud/unauthorized claim under 4853 is handled the
    # same way as 4837: 3DS auth / AVS / CVV shifts liability back to issuer.
    "no_cardholder_authorization": [
        ["fraud", "fraudulent", "unauthorized", "didn't authorize",
         "did not authorize", "never authorized", "not authorize",
         "claim fraud", "says fraud", "says it's fraud",
         "no cardholder authorization", "cardholder did not authorize"],
    ],
    "credit_not_processed": [
        ["credit", "refund"],
        ["not processed", "never processed", "never refunded", "didn't refund",
         "did not refund", "haven't received", "have not received", "no refund",
         "never came", "never arrived", "wasn't processed", "was not processed"],
    ],
    "not_as_described": [
        ["not as described", "not match", "didn't match", "different from",
         "defective", "wrong item", "wasn't what", "was not what"],
    ],
    "cancelled_merchandise": [
        ["cancel", "cancellation"],
    ],
    "digital_goods": [
        ["digital", "download", "subscription", "online service", "streaming"],
    ],
}


def _detect_mc_4853_subtype(context_text: str) -> Optional[str]:
    text = context_text.lower()
    for subtype, groups in _MC_4853_SUBTYPE_HINT_GROUPS.items():
        if all(any(kw in text for kw in group) for group in groups):
            return subtype
    return None


RULES: Dict[Tuple[str, str], DecisionRule] = {
    ("Visa", "13.1"): DecisionRule(
        required_any={"tracking_number", "delivery_confirmation", "signature_confirmation", "photo_at_door"},
        disqualifying={"refund_already_issued"},
        fight_reason="Proof of delivery (tracking, signature, or photo) directly rebuts an item-not-received claim.",
        refund_reason="No delivery evidence on file — a 13.1 claim cannot be rebutted without proof the item reached the customer.",
    ),
    ("Visa", "10.4"): DecisionRule(
        required_any={"avs_match", "cvv_match", "three_ds_authentication"},
        fight_reason="AVS/CVV match or 3-D Secure authentication indicates the genuine cardholder authorized the transaction.",
        refund_reason="No authentication evidence on file — fraud claims are very difficult to rebut without an AVS/CVV/3DS match.",
    ),
    ("Visa", "12.6.1"): DecisionRule(
        required_any={"duplicate_charge_proof", "single_credit_confirmed"},
        fight_reason="Records show only a single valid charge/credit — the duplicate-processing claim doesn't hold.",
        refund_reason="Records don't clearly confirm only one valid transaction occurred — safer to refund than contest.",
    ),
    ("Mastercard", "4853#no_cardholder_authorization"): DecisionRule(
        required_any={"avs_match", "cvv_match", "three_ds_authentication"},
        fight_reason="3-D Secure authentication (or AVS/CVV match) shifts fraud liability to the issuer — the merchant is protected against this unauthorized-transaction claim.",
        refund_reason="No authentication evidence on file — a fraud claim under 4853 is very difficult to rebut without AVS/CVV/3DS proof.",
    ),
    ("Mastercard", "4853#credit_not_processed"): DecisionRule(
        required_any={"refund_already_issued", "refund_transaction_record"},
        fight_reason="A refund transaction record proves credit was already issued — the dispute is invalid.",
        refund_reason="No proof of refund on file — if credit truly wasn't issued yet, refunding resolves it faster than fighting.",
    ),
    ("Mastercard", "4853#not_as_described"): DecisionRule(
        required_any={"client_acknowledgement", "cardholder_communication"},
        fight_reason="Customer acknowledgement or communication confirming the goods matched the listing supports fighting.",
        refund_reason="No documentation showing the goods matched the description — hard to win not-as-described disputes without it.",
    ),
    ("Mastercard", "4853#cancelled_merchandise"): DecisionRule(
        required_any={"cancellation_policy_disclosed", "refund_transaction_record"},
        fight_reason="The cancellation policy was clearly disclosed and/or honored per its terms.",
        refund_reason="No proof the cancellation policy was disclosed or followed correctly.",
    ),
    ("Mastercard", "4853#digital_goods"): DecisionRule(
        required_any={"download_logs", "activation_records", "account_access_logs_post_purchase"},
        fight_reason="Download, activation, or post-purchase access logs show the customer received and used the digital product.",
        refund_reason="No usage evidence on file — digital delivery disputes are hard to win without download or access logs.",
    ),
    ("Mastercard", "4837"): DecisionRule(
        required_any={"avs_match", "cvv_match", "three_ds_authentication"},
        fight_reason="AVS/CVV match or 3-D Secure authentication indicates the genuine cardholder authorized the transaction.",
        refund_reason="No authentication evidence on file — unauthorized-transaction claims are very difficult to rebut without it.",
    ),
    ("Mastercard", "4870"): DecisionRule(
        required_any={"emv_chip_data"},
        fight_reason="Authorization record shows POS Entry Mode 05/07 and EMV cryptogram — the genuine chip was read, shifting counterfeit fraud liability back to the issuer.",
        refund_reason="No EMV chip data on file — if the terminal swiped instead of reading the chip, the liability shift assigns counterfeit fraud loss to the merchant. Obtain your authorization record from your acquirer to confirm.",
    ),
    ("Mastercard", "4871"): DecisionRule(
        required_any={"emv_chip_data"},
        fight_reason="Authorization record confirms chip was read and PIN was verified (or card is signature-only / below CVM floor limit) — lost/stolen fraud liability remains with the issuer.",
        refund_reason="No EMV chip/PIN data on file — if the terminal accepted signature on a PIN-capable card, the liability shift assigns the loss to the merchant. Obtain your authorization record from your acquirer to confirm.",
    ),
    ("Amex", "C08"): DecisionRule(
        required_any={"tracking_number", "delivery_confirmation", "signature_confirmation"},
        disqualifying={"refund_already_issued"},
        fight_reason="Proof of delivery (tracking, signature, or carrier confirmation) directly rebuts a goods-not-received claim.",
        refund_reason="No delivery evidence on file — a C08 claim cannot be rebutted without proof the item reached the customer.",
    ),
    ("Amex", "F29"): DecisionRule(
        required_any={"avs_match", "cvv_match", "three_ds_authentication"},
        fight_reason="AVS/CVV match or 3-D Secure authentication indicates the genuine cardholder authorized the transaction.",
        refund_reason="No authentication evidence on file — card-not-present fraud claims are very difficult to rebut without it.",
    ),
    ("RuPay", "U001"): DecisionRule(
        required_any={"client_acknowledgement", "cardholder_communication"},
        fight_reason="Customer acknowledgement or communication confirming the goods/service matched what was offered supports fighting.",
        refund_reason="No documentation showing the goods/service matched the description — hard to win without it.",
    ),
    ("RuPay", "U002"): DecisionRule(
        # U002 is "Duplicate transaction" (see merchant_db.NPCI_REASON_CODES) —
        # a billing dispute, not a delivery dispute. This previously required
        # delivery_confirmation/tracking_number (copied from a non-delivery
        # code like U008/C08/13.1), asking merchants for the wrong evidence
        # entirely. The correct evidence category is the same one Visa's
        # actual duplicate-processing code (12.6.1) uses.
        required_any={"duplicate_charge_proof", "single_credit_confirmed"},
        disqualifying={"refund_already_issued"},
        fight_reason="Records show only a single valid charge — the duplicate-transaction claim doesn't hold.",
        refund_reason="No proof on file that only one valid transaction occurred — a U002 claim cannot be rebutted without evidence the customer wasn't actually charged twice.",
    ),
    ("RuPay", "U010"): DecisionRule(
        # U010 is "Technical error / system failure" (merchant_db.NPCI_REASON_CODES).
        # Per chargeback-encyclopedia/07_RuPay/NPCI_U010.md's own definition:
        # "no party acted incorrectly — the failure is in the technology
        # stack" and "the bank or PSP whose system failed bears the
        # liability, not the customer [or merchant]." No evidence tag in
        # this project's vocabulary bears on a technical failure the
        # merchant wasn't party to, so this is always_refund rather than an
        # evidence requirement — without this entry, U010 fell through to
        # chargeback_agent.py's LLM fallback for both evidence-gathering and
        # the fight/refund call, which proved unreliable in practice
        # (observed asking for "refund transaction ID" — evidence that
        # belongs to a different code, U009 "merchant not providing refund"
        # — in roughly 2 of 3 identical live runs).
        always_refund=True,
        refund_reason="U010 is a technical/system failure — NPCI attributes liability to the bank or PSP whose system failed, not the merchant. No evidence the merchant can supply changes that; the customer should be made whole via auto-reversal or manual credit.",
    ),
}


def decide(
    card_network: str,
    reason_code: str,
    evidence_present: List[str],
    evidence_missing: List[str],
    context_text: str = "",
) -> Optional[Tuple[str, str]]:
    """
    Look up a deterministic fight/refund decision for this network+reason
    code. Returns None if the code isn't in the table — the caller should
    fall through to the LLM in that case.

    Args:
        card_network:     e.g. "Visa", "Mastercard", "Amex", "RuPay".
        reason_code:      e.g. "13.1", "4853", "C08".
        evidence_present: Tags from EvidenceTag found by evaluate_node.
        evidence_missing: Tags from EvidenceTag found missing by evaluate_node.
        context_text:      user_query + additional_context, used only to pick
                           a Mastercard 4853 sub-type (that one code covers
                           six dispute types with different evidence needs).

    Returns:
        (decision, decision_reason) tuple, or None if unmapped.
    """
    network = (card_network or "").strip()
    code    = (reason_code or "").strip()

    lookup_key = (network, code)
    if code == "4853" and network == "Mastercard":
        subtype = _detect_mc_4853_subtype(context_text)
        if subtype is None:
            return None
        lookup_key = (network, f"4853#{subtype}")

    rule = RULES.get(lookup_key)
    if rule is None:
        return None

    if rule.always_refund:
        return "refund", rule.refund_reason

    present = set(evidence_present)

    if rule.disqualifying & present:
        return "refund", rule.refund_reason

    has_any = (not rule.required_any) or bool(rule.required_any & present)
    has_all = rule.required_all <= present

    if has_any and has_all:
        matched = humanize_evidence(list(rule.required_any & present))
        reason = rule.fight_reason
        if matched:
            reason = f"{reason} (matched: {', '.join(matched)})"
        return "fight", reason

    return "refund", rule.refund_reason
