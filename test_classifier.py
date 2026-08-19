"""
test_classifier.py — Unit tests for classifier.py functions.

Run:
    python test_classifier.py
"""

import sys
from classifier import classify_query_type, extract_network_and_code, detect_settlement_issue


def _check(label: str, condition: bool, detail: str = "") -> bool:
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + (f" — {detail}" if detail and not condition else ""))
    return condition


# ---------------------------------------------------------------------------
# classify_query_type
# ---------------------------------------------------------------------------

def test_classify_dispute_explicit_code():
    return _check(
        "Explicit Visa 13.1 → dispute",
        classify_query_type("I got a Visa 13.1 chargeback for $300") == "dispute",
    )

def test_classify_dispute_hinglish():
    return _check(
        "Hinglish settlement → dispute",
        classify_query_type("paise nahi aaye mere account mein") == "dispute",
    )

def test_classify_question_english():
    return _check(
        "What is a chargeback? → question",
        classify_query_type("What is a chargeback?") == "question",
    )

def test_classify_question_hinglish():
    return _check(
        "chargeback kya hota hai → question",
        classify_query_type("chargeback kya hota hai") == "question",
    )

def test_classify_escalation_english():
    return _check(
        "Connect me with helpline → escalation",
        classify_query_type("connect me with helpline") == "escalation",
    )

def test_classify_escalation_hinglish():
    return _check(
        "kisi se baat karni hai → escalation",
        classify_query_type("mujhe kisi se baat karni hai") == "escalation",
    )

def test_classify_invalid_gibberish():
    return _check(
        "Random gibberish → invalid",
        classify_query_type("asdf qwerty zxcv 123") == "invalid",
    )

def test_classify_invalid_short():
    return _check(
        "Single unrelated word → invalid",
        classify_query_type("hello") == "invalid",
    )

def test_classify_dispute_mastercard():
    return _check(
        "Mastercard 4853 dispute → dispute",
        classify_query_type("customer filed a Mastercard 4853 dispute against me") == "dispute",
    )

def test_classify_question_how():
    return _check(
        "How do I respond to a chargeback? → question",
        classify_query_type("How do I respond to a chargeback?") == "question",
    )

def test_classify_question_concept_types():
    return _check(
        "mastercard and its dispute types → question",
        classify_query_type("mastercard and its dispute types") == "question",
    )

def test_classify_question_list_of():
    return _check(
        "list of visa reason codes → question",
        classify_query_type("list of visa reason codes") == "question",
    )

def test_classify_question_difference_between():
    return _check(
        "difference between 4853 and 4837 → question",
        classify_query_type("difference between 4853 and 4837") == "question",
    )

def test_classify_dispute_correction_with_code():
    return _check(
        "correction message with code 4870 → dispute",
        classify_query_type("this is incorrect code, my bad it must be 4870") == "dispute",
    )

def test_classify_dispute_bare_code_with_network_abbrev():
    return _check(
        "MC 4870 (bare abbrev + code) → dispute",
        classify_query_type("MC 4870") == "dispute",
    )

def test_classify_dispute_bare_visa_code():
    return _check(
        "bare Visa code 13.1 → dispute",
        classify_query_type("13.1") == "dispute",
    )


# ---------------------------------------------------------------------------
# extract_network_and_code
# ---------------------------------------------------------------------------

def test_extract_visa_13_1():
    n, c = extract_network_and_code("I received a Visa 13.1 chargeback")
    return _check("Extract Visa 13.1", n == "Visa" and c == "13.1", detail=f"({n}, {c})")

def test_extract_visa_10_4():
    n, c = extract_network_and_code("dispute under 10.4 card-not-present fraud")
    return _check("Extract Visa 10.4", n == "Visa" and c == "10.4", detail=f"({n}, {c})")

def test_extract_mastercard_4853():
    n, c = extract_network_and_code("Mastercard reason code 4853")
    return _check("Extract Mastercard 4853", n == "Mastercard" and c == "4853", detail=f"({n}, {c})")

def test_extract_mastercard_4837():
    n, c = extract_network_and_code("4837 no cardholder authorization")
    return _check("Extract Mastercard 4837", n == "Mastercard" and c == "4837", detail=f"({n}, {c})")

def test_extract_amex_c08():
    n, c = extract_network_and_code("Amex C08 goods not received")
    return _check("Extract Amex C08", n == "Amex" and c == "C08", detail=f"({n}, {c})")

def test_extract_amex_f29():
    n, c = extract_network_and_code("dispute code F29")
    return _check("Extract Amex F29", n == "Amex" and c == "F29", detail=f"({n}, {c})")

def test_extract_rupay_u002():
    n, c = extract_network_and_code("RuPay U002 goods not received")
    return _check("Extract RuPay U002", n == "RuPay" and c == "U002", detail=f"({n}, {c})")

def test_extract_network_only_visa():
    n, c = extract_network_and_code("I got a Visa chargeback but don't know the code")
    return _check("Network-only: Visa → code Unknown", n == "Visa" and c == "Unknown", detail=f"({n}, {c})")

def test_extract_network_only_rupay():
    n, c = extract_network_and_code("NPCI dispute on my UPI account")
    return _check("Network-only: NPCI/UPI → RuPay", n == "RuPay" and c == "Unknown", detail=f"({n}, {c})")

def test_extract_nothing():
    n, c = extract_network_and_code("customer complained about something")
    return _check("No code or network → Unknown/Unknown", n == "Unknown" and c == "Unknown", detail=f"({n}, {c})")

def test_extract_visa_not_mc_4digit():
    # A 4-digit number that is NOT in the Mastercard dispute code allow-list
    n, c = extract_network_and_code("transaction id 4999 was charged")
    return _check("4999 (not a MC code) → Unknown/Unknown", n == "Unknown" and c == "Unknown", detail=f"({n}, {c})")

def test_extract_mastercard_4849():
    n, c = extract_network_and_code("i got mastercard 4849")
    return _check("Extract Mastercard 4849 (Questionable Merchant Activity)", n == "Mastercard" and c == "4849", detail=f"({n}, {c})")

def test_extract_mc_abbreviation_with_code():
    n, c = extract_network_and_code("MC 4849")
    return _check("Extract 'MC' abbreviation + 4849", n == "Mastercard" and c == "4849", detail=f"({n}, {c})")

def test_extract_mc_abbreviation_network_only():
    n, c = extract_network_and_code("mc dispute, no code yet")
    return _check("'mc' abbreviation alone → Mastercard, code Unknown", n == "Mastercard" and c == "Unknown", detail=f"({n}, {c})")


# ---------------------------------------------------------------------------
# detect_settlement_issue
# ---------------------------------------------------------------------------

def test_settlement_specific_payment_never_arrived():
    return _check(
        "customer paid but money never arrived → True",
        detect_settlement_issue("customer paid but money never arrived in my account"),
    )

def test_settlement_hinglish_positive():
    return _check(
        "paise nahi aaye → True",
        detect_settlement_issue("paise nahi aaye mere account mein"),
    )

def test_settlement_generic_balance_false():
    return _check(
        "mera balance khatam → False",
        not detect_settlement_issue("mera balance khatam ho gya"),
    )

def test_settlement_account_empty_false():
    return _check(
        "account empty → False",
        not detect_settlement_issue("my account is empty"),
    )

def test_settlement_low_balance_false():
    return _check(
        "balance low → False",
        not detect_settlement_issue("my balance is low"),
    )

def test_settlement_funds_never_arrived():
    return _check(
        "funds never arrived → True",
        detect_settlement_issue("I processed a sale but funds never arrived"),
    )

def test_settlement_unrelated_false():
    return _check(
        "Unrelated text → False",
        not detect_settlement_issue("I want to know about chargeback policies"),
    )


def main() -> None:
    tests = [
        test_classify_dispute_explicit_code,
        test_classify_dispute_hinglish,
        test_classify_question_english,
        test_classify_question_hinglish,
        test_classify_escalation_english,
        test_classify_escalation_hinglish,
        test_classify_invalid_gibberish,
        test_classify_invalid_short,
        test_classify_dispute_mastercard,
        test_classify_question_how,
        test_classify_question_concept_types,
        test_classify_question_list_of,
        test_classify_question_difference_between,
        test_classify_dispute_correction_with_code,
        test_classify_dispute_bare_code_with_network_abbrev,
        test_classify_dispute_bare_visa_code,
        test_extract_visa_13_1,
        test_extract_visa_10_4,
        test_extract_mastercard_4853,
        test_extract_mastercard_4837,
        test_extract_amex_c08,
        test_extract_amex_f29,
        test_extract_rupay_u002,
        test_extract_network_only_visa,
        test_extract_network_only_rupay,
        test_extract_nothing,
        test_extract_visa_not_mc_4digit,
        test_extract_mastercard_4849,
        test_extract_mc_abbreviation_with_code,
        test_extract_mc_abbreviation_network_only,
        test_settlement_specific_payment_never_arrived,
        test_settlement_hinglish_positive,
        test_settlement_generic_balance_false,
        test_settlement_account_empty_false,
        test_settlement_low_balance_false,
        test_settlement_funds_never_arrived,
        test_settlement_unrelated_false,
    ]

    print(f"\nRunning {len(tests)} classifier tests...\n")
    results = [t() for t in tests]
    passed  = sum(results)
    total   = len(results)

    print(f"\n{'='*60}")
    print(f"  Passed: {passed}/{total}")
    print(f"{'='*60}")

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
