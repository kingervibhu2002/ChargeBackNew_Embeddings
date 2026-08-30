"""
test_decision_rules.py — Unit tests for decision_rules.decide().

Plain-Python assertions (no pytest dependency — matches test_search.py's
style, and pytest isn't installed in this project).

Run:
    python test_decision_rules.py
"""

import sys

from decision_rules import RULES, decide


def _check(label: str, condition: bool, detail: str = "") -> bool:
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + (f" — {detail}" if detail and not condition else ""))
    return condition


def test_visa_13_1_fight_with_delivery_proof() -> bool:
    result = decide("Visa", "13.1", ["tracking_number", "signature_confirmation"], [])
    return _check(
        "Visa 13.1 + tracking/signature → fight",
        result is not None and result[0] == "fight",
        detail=str(result),
    )


def test_visa_13_1_refund_with_no_evidence() -> bool:
    result = decide("Visa", "13.1", [], ["tracking_number"])
    return _check(
        "Visa 13.1 + no evidence → refund",
        result is not None and result[0] == "refund",
        detail=str(result),
    )


def test_visa_13_1_disqualified_by_existing_refund() -> bool:
    result = decide("Visa", "13.1", ["tracking_number", "refund_already_issued"], [])
    return _check(
        "Visa 13.1 + refund already issued → refund despite delivery proof",
        result is not None and result[0] == "refund",
        detail=str(result),
    )


def test_visa_10_4_fight_with_avs() -> bool:
    result = decide("Visa", "10.4", ["avs_match"], [])
    return _check(
        "Visa 10.4 + AVS match → fight",
        result is not None and result[0] == "fight",
        detail=str(result),
    )


def test_visa_12_6_1_refund_without_proof() -> bool:
    result = decide("Visa", "12.6.1", [], [])
    return _check(
        "Visa 12.6.1 + no proof → refund",
        result is not None and result[0] == "refund",
        detail=str(result),
    )


def test_visa_12_6_1_fight_with_single_credit_confirmed() -> bool:
    result = decide("Visa", "12.6.1", ["single_credit_confirmed"], [])
    return _check(
        "Visa 12.6.1 + single credit confirmed → fight",
        result is not None and result[0] == "fight",
        detail=str(result),
    )


def test_visa_12_6_1_refund_with_duplicate_charge_proof() -> bool:
    # duplicate_charge_proof means a duplicate charge DID occur — that's
    # evidence for the customer's claim, not against it. Previously
    # mis-modeled in required_any (→ fight); now disqualifying (→ refund),
    # regardless of any other evidence present.
    result = decide("Visa", "12.6.1", ["duplicate_charge_proof", "single_credit_confirmed"], [])
    return _check(
        "Visa 12.6.1 + duplicate charge proof → refund even with single-credit evidence too",
        result is not None and result[0] == "refund",
        detail=str(result),
    )


def test_mc_4853_credit_not_processed_fight() -> bool:
    result = decide(
        "Mastercard", "4853", ["refund_transaction_record"], [],
        context_text="customer says the credit was not processed",
    )
    return _check(
        "Mastercard 4853 (credit not processed subtype) + refund record → fight",
        result is not None and result[0] == "fight",
        detail=str(result),
    )


def test_mc_4853_not_as_described_refund() -> bool:
    result = decide(
        "Mastercard", "4853", [], ["client_acknowledgement"],
        context_text="customer says item was not as described",
    )
    return _check(
        "Mastercard 4853 (not as described subtype) + no evidence → refund",
        result is not None and result[0] == "refund",
        detail=str(result),
    )


def test_mc_4853_fraud_3ds_fight() -> bool:
    result = decide(
        "Mastercard", "4853", ["three_ds_authentication"], [],
        context_text="customer says the charge is fraudulent but they placed the order using our 3D Secure checkout",
    )
    return _check(
        "Mastercard 4853 + fraud claim + 3DS → fight (liability shift)",
        result is not None and result[0] == "fight",
        detail=str(result),
    )


def test_mc_4853_fraud_no_auth_refund() -> bool:
    result = decide(
        "Mastercard", "4853", [], [],
        context_text="customer says the charge is fraudulent, no 3DS was used",
    )
    return _check(
        "Mastercard 4853 + fraud claim + no auth evidence → refund",
        result is not None and result[0] == "refund",
        detail=str(result),
    )


def test_mc_4853_unmapped_subtype_falls_through() -> bool:
    result = decide("Mastercard", "4853", ["avs_match"], [], context_text="generic dispute, no clear subtype")
    return _check(
        "Mastercard 4853 with no detectable subtype → None (fall through to LLM)",
        result is None,
        detail=str(result),
    )


def test_mc_4837_fight_with_3ds() -> bool:
    result = decide("Mastercard", "4837", ["three_ds_authentication"], [])
    return _check(
        "Mastercard 4837 + 3DS auth → fight",
        result is not None and result[0] == "fight",
        detail=str(result),
    )


def test_mc_4870_fight_with_emv_chip_data() -> bool:
    result = decide("Mastercard", "4870", ["emv_chip_data"], [])
    return _check(
        "Mastercard 4870 + EMV chip data → fight (chip read, liability shifts to issuer)",
        result is not None and result[0] == "fight",
        detail=str(result),
    )


def test_mc_4870_refund_without_emv_data() -> bool:
    result = decide("Mastercard", "4870", [], [])
    return _check(
        "Mastercard 4870 + no chip data → refund (terminal swiped, merchant liable)",
        result is not None and result[0] == "refund",
        detail=str(result),
    )


def test_mc_4871_fight_with_emv_chip_data() -> bool:
    result = decide("Mastercard", "4871", ["emv_chip_data"], [])
    return _check(
        "Mastercard 4871 + EMV chip/PIN data → fight",
        result is not None and result[0] == "fight",
        detail=str(result),
    )


def test_mc_4871_refund_without_emv_data() -> bool:
    result = decide("Mastercard", "4871", [], [])
    return _check(
        "Mastercard 4871 + no chip/PIN data → refund",
        result is not None and result[0] == "refund",
        detail=str(result),
    )


def test_amex_c08_fight_with_delivery() -> bool:
    result = decide("Amex", "C08", ["delivery_confirmation"], [])
    return _check(
        "Amex C08 + delivery confirmation → fight",
        result is not None and result[0] == "fight",
        detail=str(result),
    )


def test_amex_f29_refund_without_auth() -> bool:
    result = decide("Amex", "F29", [], [])
    return _check(
        "Amex F29 + no auth evidence → refund",
        result is not None and result[0] == "refund",
        detail=str(result),
    )


def test_rupay_u001_fight_with_authentication() -> bool:
    # U001 = pure unauthorized-access fraud (customer had zero involvement).
    # Evidence corrected to match its real merchant defense (UPI PIN
    # authentication status / delivery to the customer's own registered
    # address) — cardholder_communication was never the right tag for this
    # code (that's evidence for a "goods didn't match description" claim).
    result = decide("RuPay", "U001", ["upi_pin_authenticated"], [])
    return _check(
        "RuPay U001 + UPI PIN authenticated → fight",
        result is not None and result[0] == "fight",
        detail=str(result),
    )


def test_rupay_u001_refund_without_authentication() -> bool:
    result = decide("RuPay", "U001", ["cardholder_communication"], [])
    return _check(
        "RuPay U001 + irrelevant evidence (cardholder_communication) → refund",
        result is not None and result[0] == "refund",
        detail=str(result),
    )


def test_rupay_u005_fight_with_confirmed_vpa() -> bool:
    # U005 = fraudster impersonation (customer participated, but was
    # deceived) — evidence is UPI-specific (beneficiary VPA/KYC), never
    # card-scheme concepts like AVS/CVV/3-D Secure, which don't exist in UPI.
    result = decide("RuPay", "U005", ["beneficiary_vpa_confirmed"], [])
    return _check(
        "RuPay U005 + confirmed beneficiary VPA → fight",
        result is not None and result[0] == "fight",
        detail=str(result),
    )


def test_rupay_u005_refund_without_evidence() -> bool:
    result = decide("RuPay", "U005", [], [])
    return _check(
        "RuPay U005 + no evidence → refund",
        result is not None and result[0] == "refund",
        detail=str(result),
    )


def test_rupay_u002_disqualified_by_refund() -> bool:
    result = decide("RuPay", "U002", ["duplicate_charge_proof", "refund_already_issued"], [])
    return _check(
        "RuPay U002 + refund already issued → refund despite duplicate-charge proof",
        result is not None and result[0] == "refund",
        detail=str(result),
    )


def test_rupay_u002_fights_with_single_credit_confirmed() -> bool:
    result = decide("RuPay", "U002", ["single_credit_confirmed"], [])
    return _check(
        "RuPay U002 + single credit confirmed → fight",
        result is not None and result[0] == "fight",
        detail=str(result),
    )


def test_rupay_u002_refunds_with_self_reported_credit_only() -> bool:
    # single_credit_self_reported (a bare, unverified merchant claim — see
    # evidence_tags.py and _extract_evidence_node's rule_guidance) must NEVER
    # independently satisfy U002's required_any on its own, unlike
    # single_credit_confirmed (an actual bank/CBS record). Proves the tag
    # split actually changes decide()'s behavior, not just its vocabulary —
    # this is the direct regression test for a reviewer-flagged bug where a
    # bare "I only got one payment" claim alone was recommending "fight"
    # with zero independent verification.
    result = decide("RuPay", "U002", ["single_credit_self_reported"], [])
    return _check(
        "RuPay U002 + bare self-reported single credit (no record cited) → refund, not fight",
        result is not None and result[0] == "refund",
        detail=str(result),
    )


def test_rupay_u002_refunds_with_duplicate_charge_proof() -> bool:
    # duplicate_charge_proof means a duplicate charge DID occur — per this
    # code's own encyclopedia doc (NPCI_U002.md, "If the Merchant Received
    # Two Credits... must refund the duplicate"), that's evidence FOR the
    # customer's claim, not against it. Was wrongly in required_any (→
    # fight) before this fix; now disqualifying (→ refund) regardless of
    # any other evidence present, same as refund_already_issued.
    result = decide("RuPay", "U002", ["duplicate_charge_proof", "single_credit_confirmed"], [])
    return _check(
        "RuPay U002 + duplicate charge proof → refund even with single-credit evidence too",
        result is not None and result[0] == "refund",
        detail=str(result),
    )


def test_unmapped_code_returns_none() -> bool:
    result = decide("Visa", "99.9", ["tracking_number"], [])
    return _check(
        "Unmapped reason code → None (fall through to LLM)",
        result is None,
        detail=str(result),
    )


def test_unmapped_network_returns_none() -> bool:
    result = decide("Discover", "13.1", ["tracking_number"], [])
    return _check(
        "Unmapped network → None (fall through to LLM)",
        result is None,
        detail=str(result),
    )


def test_every_rule_table_entry_is_reachable() -> bool:
    """
    Every entry in RULES should produce a 'fight' decision when given exactly
    its required_any/required_all evidence, and a 'refund' when given none —
    catches typos in the table itself (e.g. a tag that doesn't exist).
    """
    all_ok = True
    for (network, code), rule in RULES.items():
        evidence = set(rule.required_any) | set(rule.required_all)
        lookup_code = code.split("#")[0]
        context = code.split("#")[1].replace("_", " ") if "#" in code else ""
        fight_result = decide(network, lookup_code, list(evidence), [], context_text=context)
        ok = fight_result is not None and fight_result[0] == "fight"
        all_ok = _check(f"RULES[{network}, {code}] reachable with its own required evidence", ok, detail=str(fight_result)) and all_ok
    return all_ok


def main() -> None:
    tests = [
        test_visa_13_1_fight_with_delivery_proof,
        test_visa_13_1_refund_with_no_evidence,
        test_visa_13_1_disqualified_by_existing_refund,
        test_visa_10_4_fight_with_avs,
        test_visa_12_6_1_refund_without_proof,
        test_visa_12_6_1_fight_with_single_credit_confirmed,
        test_visa_12_6_1_refund_with_duplicate_charge_proof,
        test_mc_4853_credit_not_processed_fight,
        test_mc_4853_not_as_described_refund,
        test_mc_4853_fraud_3ds_fight,
        test_mc_4853_fraud_no_auth_refund,
        test_mc_4853_unmapped_subtype_falls_through,
        test_mc_4837_fight_with_3ds,
        test_mc_4870_fight_with_emv_chip_data,
        test_mc_4870_refund_without_emv_data,
        test_mc_4871_fight_with_emv_chip_data,
        test_mc_4871_refund_without_emv_data,
        test_amex_c08_fight_with_delivery,
        test_amex_f29_refund_without_auth,
        test_rupay_u001_fight_with_authentication,
        test_rupay_u001_refund_without_authentication,
        test_rupay_u005_fight_with_confirmed_vpa,
        test_rupay_u005_refund_without_evidence,
        test_rupay_u002_disqualified_by_refund,
        test_rupay_u002_fights_with_single_credit_confirmed,
        test_rupay_u002_refunds_with_self_reported_credit_only,
        test_rupay_u002_refunds_with_duplicate_charge_proof,
        test_unmapped_code_returns_none,
        test_unmapped_network_returns_none,
        test_every_rule_table_entry_is_reachable,
    ]

    print(f"\nRunning {len(tests)} decision_rules tests...\n")
    results = [t() for t in tests]
    passed = sum(results)
    total = len(results)

    print(f"\n{'='*60}")
    print(f"  Passed: {passed}/{total}")
    print(f"{'='*60}")

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
