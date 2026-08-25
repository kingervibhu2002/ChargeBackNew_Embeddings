"""
test_retrieval_evaluator.py — Unit tests for retrieval_evaluator.evaluate_retrieval().

Plain-Python assertions, same style as test_decision_rules.py — runnable
directly (python test_retrieval_evaluator.py) or via pytest (function names
start with test_, no fixtures needed).

Run:
    python test_retrieval_evaluator.py
"""

import sys

from retrieval_evaluator import evaluate_retrieval


def _check(label: str, condition: bool, detail: str = "") -> bool:
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + (f" — {detail}" if detail and not condition else ""))
    return condition


def _doc(title: str, network: str) -> dict:
    return {"title": title, "network": network}


def test_no_network_detected_is_unassessed() -> bool:
    result = evaluate_retrieval("", [_doc("Visa 13.1", "Visa")])
    return _check("empty expected_network -> status=''", result.status == "")


def test_unknown_network_is_unassessed() -> bool:
    result = evaluate_retrieval("Unknown", [_doc("Visa 13.1", "Visa")])
    return _check("expected_network='Unknown' -> status=''", result.status == "")


def test_no_results_at_all_is_bad() -> bool:
    result = evaluate_retrieval("RuPay", [])
    return _check(
        "no results retrieved -> status='bad'",
        result.status == "bad" and not result.network_consistent,
        detail=str(result),
    )


def test_all_results_matching_network_is_good() -> bool:
    results = [_doc("NPCI U002", "RuPay"), _doc("NPCI U002 Overview", "RuPay")]
    result = evaluate_retrieval("RuPay", results)
    return _check(
        "all results tagged RuPay, expected RuPay -> status='good'",
        result.status == "good" and result.network_consistent and result.matched_fraction == 1.0,
        detail=str(result),
    )


def test_majority_mismatch_is_bad() -> bool:
    # The exact failure mode this module was built from: a RuPay query
    # whose retrieved set is mostly Visa/Mastercard content.
    results = [
        _doc("Visa 10.4 Fraud Policy", "Visa"),
        _doc("Mastercard Arbitration Fees", "Mastercard"),
        _doc("Generic Retrieval Request Guide", "Visa"),
        _doc("NPCI U002 Overview", "RuPay"),
    ]
    result = evaluate_retrieval("RuPay", results)
    return _check(
        "3/4 wrong-network results -> status='bad'",
        result.status == "bad" and not result.network_consistent and result.matched_fraction == 0.25,
        detail=str(result),
    )


def test_minority_mismatch_is_ambiguous() -> bool:
    results = [
        _doc("NPCI U002 Overview", "RuPay"),
        _doc("NPCI U002 Evidence", "RuPay"),
        _doc("Mastercard Arbitration Fees", "Mastercard"),
    ]
    result = evaluate_retrieval("RuPay", results)
    return _check(
        "1/3 wrong-network result, majority correct -> status='ambiguous'",
        result.status == "ambiguous" and result.network_consistent,
        detail=str(result),
    )


def test_untagged_results_are_neutral_not_mismatched() -> bool:
    # A general/cross-network background doc (empty network field) should
    # never count against matched_fraction -- only an EXPLICIT different
    # network tag is a real mismatch.
    results = [
        _doc("NPCI U002 Overview", "RuPay"),
        _doc("General Chargeback Lifecycle Guide", ""),
    ]
    result = evaluate_retrieval("RuPay", results)
    return _check(
        "one untagged (general) doc alongside one correct match -> status='good'",
        result.status == "good" and result.matched_fraction == 1.0,
        detail=str(result),
    )


def test_all_results_untagged_is_ambiguous() -> bool:
    results = [_doc("General Chargeback Lifecycle Guide", ""), _doc("General FAQ", "")]
    result = evaluate_retrieval("RuPay", results)
    return _check(
        "nothing in the result set is network-tagged -> status='ambiguous', not 'good'",
        result.status == "ambiguous" and result.network_consistent,
        detail=str(result),
    )


def test_issues_message_names_the_mismatched_titles() -> bool:
    results = [
        _doc("NPCI U002 Overview", "RuPay"),
        _doc("Visa 10.4 Fraud Policy", "Visa"),
    ]
    result = evaluate_retrieval("RuPay", results)
    return _check(
        "issues list is non-empty and names the mismatched title when status != 'good'",
        result.status == "ambiguous" and "Visa 10.4 Fraud Policy" in "".join(result.issues),
        detail=str(result),
    )


def test_multiple_acceptable_spellings() -> bool:
    # The real, verified situation for RuPay/Amex in this project's actual
    # index: documents split across two different network spellings for
    # the same real network. A caller passing BOTH as acceptable should
    # treat either as a match, not just the first one it happens to try.
    results = [
        _doc("NPCI U002 Overview", "RuPay"),
        _doc("NPCI U002 Evidence Requirements", "RuPay / NPCI"),
    ]
    result = evaluate_retrieval(["RuPay", "RuPay / NPCI"], results)
    return _check(
        "both real RuPay spellings passed as acceptable -> status='good', not a false mismatch",
        result.status == "good" and result.matched_fraction == 1.0,
        detail=str(result),
    )


def main() -> None:
    tests = [
        test_no_network_detected_is_unassessed,
        test_unknown_network_is_unassessed,
        test_no_results_at_all_is_bad,
        test_all_results_matching_network_is_good,
        test_majority_mismatch_is_bad,
        test_minority_mismatch_is_ambiguous,
        test_untagged_results_are_neutral_not_mismatched,
        test_all_results_untagged_is_ambiguous,
        test_issues_message_names_the_mismatched_titles,
        test_multiple_acceptable_spellings,
    ]
    print(f"Running {len(tests)} retrieval_evaluator tests...\n")
    results = [t() for t in tests]
    passed = sum(results)
    print(f"\n{passed}/{len(tests)} passed")
    sys.exit(0 if passed == len(tests) else 1)


if __name__ == "__main__":
    main()
