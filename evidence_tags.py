"""
evidence_tags.py — Closed evidence tag vocabulary shared by chargeback_agent.py
and decision_rules.py.

Lives in its own module (rather than inside chargeback_agent.py) so that
decision_rules.py can import it without creating a circular import — the
agent needs to call decide() from decision_rules, and decision_rules needs
the tag vocabulary, so neither of those two can own it.
"""

from typing import List, Literal

# evidence_present/evidence_missing are constrained to this closed set rather
# than free text. A deterministic decision_rules.py matches evidence tags
# against a rule table — that only works if "delivery confirmation" and
# "proof of delivery" can't mean the same thing as two different strings.
EvidenceTag = Literal[
    "tracking_number",
    "delivery_confirmation",
    "signature_confirmation",
    "photo_at_door",
    "avs_match",
    "cvv_match",
    "three_ds_authentication",
    "emv_chip_data",
    "refund_already_issued",
    "refund_transaction_record",
    "cancellation_request_record",
    "cancellation_policy_disclosed",
    "download_logs",
    "activation_records",
    "account_access_logs_post_purchase",
    "email_delivery_logs",
    "service_completion_record",
    "client_acknowledgement",
    "cardholder_communication",
    "duplicate_charge_proof",
    "single_credit_confirmed",
]

EVIDENCE_TAG_LABELS: dict = {
    "tracking_number":                  "Shipment tracking number",
    "delivery_confirmation":            "Carrier delivery confirmation",
    "signature_confirmation":           "Delivery signature confirmation",
    "photo_at_door":                    "Photo of delivery at door",
    "avs_match":                        "AVS (address verification) match",
    "cvv_match":                        "CVV match",
    "three_ds_authentication":          "3-D Secure / SafeKey authentication",
    "emv_chip_data":                    "EMV chip authorization data (POS Entry Mode 05/07 + cryptogram)",
    "refund_already_issued":            "Refund already issued to customer",
    "refund_transaction_record":        "Refund transaction record",
    "cancellation_request_record":      "Record of cancellation request",
    "cancellation_policy_disclosed":    "Cancellation policy disclosed to customer",
    "download_logs":                    "Digital download/access logs",
    "activation_records":               "Product/service activation records",
    "account_access_logs_post_purchase": "Account access logs after purchase",
    "email_delivery_logs":              "Email delivery confirmation logs",
    "service_completion_record":        "Record of service completion",
    "client_acknowledgement":           "Client acknowledgement/sign-off",
    "cardholder_communication":         "Communication with cardholder",
    "duplicate_charge_proof":           "Proof of duplicate charge",
    "single_credit_confirmed":          "Confirmed only one credit was issued",
}


def humanize_evidence(tags: List[str]) -> List[str]:
    """
    Map evidence tags to merchant-facing phrases for prompts/UI display.
    Falls back to a title-cased version of the raw string for anything
    outside the known vocabulary (e.g. legacy free-text entries from the
    settlement/reason-code early-exit branches in _evaluate_node, which
    aren't drawn from EvidenceTag at all).
    """
    return [EVIDENCE_TAG_LABELS.get(t, t.replace("_", " ").capitalize()) for t in tags]
