"""
test_classifier.py — Unit tests for classifier.py functions.

Run:
    python test_classifier.py
"""

import sys
from classifier import (
    classify_query_type,
    extract_network_and_code,
    detect_settlement_issue,
    looks_like_new_request,
    looks_like_explicit_resolution_request,
    resolve_help_scope_reply,
    count_consecutive_matches,
    detect_knowledge_type_intent,
    detect_actor_intent,
    detect_case_fact_ambiguity,
)


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


# ---------------------------------------------------------------------------
# looks_like_new_request
# ---------------------------------------------------------------------------

def test_new_request_vague_help_with_it_is_not_new():
    return _check(
        "'help me with it' -> False (vague, points back at the anchored case)",
        looks_like_new_request("help me with it") is False,
    )

def test_new_request_vague_help_withis_typo_is_not_new():
    return _check(
        "'help me withis' -> False ('with this' typo, still anaphoric)",
        looks_like_new_request("help me withis") is False,
    )

def test_new_request_vague_help_with_this_is_not_new():
    return _check(
        "'help me with this' -> False (bare 'this', no concrete subject)",
        looks_like_new_request("help me with this") is False,
    )

def test_new_request_bare_help_me_is_not_new():
    return _check(
        "'help me' alone -> False",
        looks_like_new_request("help me") is False,
    )

def test_new_request_concrete_subject_is_new():
    return _check(
        "'help me with all open questions' -> True (a genuinely different, broader ask)",
        looks_like_new_request("help me with all open questions") is True,
    )

def test_new_request_show_me_unaffected():
    return _check(
        "'show me my other cases' -> True (unaffected — not the 'help me' family)",
        looks_like_new_request("show me my other cases") is True,
    )


# ---------------------------------------------------------------------------
# looks_like_explicit_resolution_request
# ---------------------------------------------------------------------------

def test_explicit_resolution_need_a_resolution():
    return _check(
        "'i need a resolution for this' -> True",
        looks_like_explicit_resolution_request("i need a resolution for this") is True,
    )

def test_explicit_resolution_go_ahead():
    return _check(
        "'go ahead and draft it' -> True",
        looks_like_explicit_resolution_request("go ahead and draft it") is True,
    )

def test_explicit_resolution_draft_letter():
    return _check(
        "'please draft the rebuttal letter' -> True",
        looks_like_explicit_resolution_request("please draft the rebuttal letter") is True,
    )

def test_explicit_resolution_vague_help_is_false():
    return _check(
        "'help me with it' -> False (vague, not an explicit ask)",
        looks_like_explicit_resolution_request("help me with it") is False,
    )

def test_explicit_resolution_bare_ok_is_false():
    return _check(
        "'ok' -> False",
        looks_like_explicit_resolution_request("ok") is False,
    )


# ---------------------------------------------------------------------------
# resolve_help_scope_reply
#
# Regression coverage for the twelfth bug (CHARGEBACK_AGENT_GUIDE.md): the
# scoping question "want me to explain the evidence, or draft the response?"
# had no code consuming the answer at all -- "yes" and "explain it in a
# better way" both re-triggered the identical question forever.
# ---------------------------------------------------------------------------

def test_help_scope_bare_yes_is_draft():
    return _check(
        "'yes' -> 'draft'",
        resolve_help_scope_reply("yes") == "draft",
    )

def test_help_scope_yeah_is_draft():
    return _check(
        "'yeah' -> 'draft'",
        resolve_help_scope_reply("yeah") == "draft",
    )

def test_help_scope_go_ahead_is_draft():
    return _check(
        "'go ahead' -> 'draft'",
        resolve_help_scope_reply("go ahead") == "draft",
    )

def test_help_scope_explain_it_is_explain():
    return _check(
        "'explain it' -> 'explain'",
        resolve_help_scope_reply("explain it") == "explain",
    )

def test_help_scope_explain_better_way_is_explain():
    return _check(
        "'explain it in a better way' -> 'explain'",
        resolve_help_scope_reply("explain it in a better way") == "explain",
    )

def test_help_scope_great_explain_it_is_explain():
    return _check(
        "'great explain it' -> 'explain'",
        resolve_help_scope_reply("great explain it") == "explain",
    )

def test_help_scope_unrelated_question_is_none():
    return _check(
        "'what is the case ID?' -> None (not a scoping answer)",
        resolve_help_scope_reply("what is the case ID?") is None,
    )


# ---------------------------------------------------------------------------
# count_consecutive_matches
# ---------------------------------------------------------------------------

def test_consecutive_matches_only_current_segment():
    # Five unrelated segments, then one matching segment -- must be 1, not
    # "total conversation length" (the exact bug this function fixes).
    ctx = "\n\n".join([
        "unrelated segment one",
        "unrelated segment two",
        "unrelated segment three",
        "unrelated segment four",
        "MATCH",
    ])
    return _check(
        "5 segments, only the last matches -> streak of 1",
        count_consecutive_matches(ctx, lambda s: s == "MATCH") == 1,
    )

def test_consecutive_matches_counts_trailing_run():
    ctx = "\n\n".join(["no", "no", "MATCH", "MATCH", "MATCH"])
    return _check(
        "3 trailing matches after 2 non-matches -> streak of 3",
        count_consecutive_matches(ctx, lambda s: s == "MATCH") == 3,
    )

def test_consecutive_matches_stops_at_first_break():
    ctx = "\n\n".join(["MATCH", "no", "MATCH"])
    return _check(
        "a non-match in the middle breaks the streak -> streak of 1",
        count_consecutive_matches(ctx, lambda s: s == "MATCH") == 1,
    )

def test_consecutive_matches_zero_when_latest_doesnt_match():
    ctx = "\n\n".join(["MATCH", "MATCH", "no"])
    return _check(
        "latest segment doesn't match -> streak of 0",
        count_consecutive_matches(ctx, lambda s: s == "MATCH") == 0,
    )


# ---------------------------------------------------------------------------
# detect_knowledge_type_intent / detect_actor_intent
# ---------------------------------------------------------------------------

def test_knowledge_type_definition():
    return _check(
        "What does U002 mean? -> DEFINITION",
        detect_knowledge_type_intent("What does U002 mean?") == "DEFINITION",
    )

def test_knowledge_type_evidence():
    return _check(
        "What evidence do I need? -> EVIDENCE",
        detect_knowledge_type_intent("What evidence do I need for this?") == "EVIDENCE",
    )

def test_knowledge_type_evidence_all_proofs_phrasing():
    return _check(
        "What all proofs do I need? -> EVIDENCE (not misrouted by 'all')",
        detect_knowledge_type_intent("What all proofs do I need to submit?") == "EVIDENCE",
    )

def test_knowledge_type_responsibility():
    return _check(
        "Who is responsible for this? -> RESPONSIBILITY",
        detect_knowledge_type_intent("Who is responsible for this chargeback?") == "RESPONSIBILITY",
    )

def test_knowledge_type_deadline():
    return _check(
        "What is the deadline to respond? -> DEADLINE",
        detect_knowledge_type_intent("What is the deadline to respond?") == "DEADLINE",
    )

def test_knowledge_type_deadline_beats_evidence():
    return _check(
        "Deadline to submit evidence -> DEADLINE (more specific, checked first)",
        detect_knowledge_type_intent("What's the deadline to submit evidence?") == "DEADLINE",
    )

def test_knowledge_type_rebuttal():
    return _check(
        "How do I fight this chargeback? -> REBUTTAL",
        detect_knowledge_type_intent("How do I fight this chargeback?") == "REBUTTAL",
    )

def test_knowledge_type_scenario_psp():
    return _check(
        "What if the PSP charged the customer twice? -> SCENARIO",
        detect_knowledge_type_intent("What if the PSP charged the customer twice?") == "SCENARIO",
    )

def test_knowledge_type_exception():
    return _check(
        "Is there an exception if the customer confirmed delivery? -> EXCEPTION",
        detect_knowledge_type_intent("Is there an exception if the customer confirmed delivery?") == "EXCEPTION",
    )

def test_knowledge_type_none_for_unrelated():
    return _check(
        "Unrelated small talk -> None",
        detect_knowledge_type_intent("Thanks, that helps a lot!") is None,
    )

def test_actor_intent_psp():
    return _check(
        "PSP mention -> psp",
        detect_actor_intent("What if the PSP charged the customer twice?") == "psp",
    )

def test_actor_intent_network():
    return _check(
        "NPCI mention -> network",
        detect_actor_intent("What if NPCI charged the customer twice?") == "network",
    )

def test_actor_intent_merchant():
    return _check(
        "Merchant mention -> merchant",
        detect_actor_intent("Is the merchant liable here?") == "merchant",
    )

def test_actor_intent_none_when_unnamed():
    return _check(
        "No actor named -> None",
        detect_actor_intent("What does U002 mean?") is None,
    )


# ---------------------------------------------------------------------------
# detect_case_fact_ambiguity
# ---------------------------------------------------------------------------

def test_case_fact_ambiguity_detects_other_code():
    return _check(
        "Prior aside about a different code -> that code returned",
        detect_case_fact_ambiguity(
            "what is its amount?", "ohhh i have U003 also?", "U002",
        ) == "U003",
    )

def test_case_fact_ambiguity_none_when_same_code():
    return _check(
        "Prior segment names the SAME code as anchored -> None",
        detect_case_fact_ambiguity(
            "what is its amount?", "tell me about U002 again", "U002",
        ) is None,
    )

def test_case_fact_ambiguity_none_when_explicit_case_ref():
    return _check(
        "Prior segment already names a specific case -> None (upstream anchor logic handles this)",
        detect_case_fact_ambiguity(
            "what is its amount?", "what about case NPCI20260704M002013?", "U002",
        ) is None,
    )

def test_case_fact_ambiguity_none_when_this_case_demonstrative():
    return _check(
        "Prior segment says 'this case' -> None",
        detect_case_fact_ambiguity(
            "what is its amount?", "tell me more about this case", "U002",
        ) is None,
    )

def test_case_fact_ambiguity_none_when_no_previous_segment():
    return _check(
        "No previous segment (first turn) -> None",
        detect_case_fact_ambiguity("what is its amount?", "", "U002") is None,
    )

def test_case_fact_ambiguity_none_when_no_code_mentioned():
    return _check(
        "Prior segment names no reason code at all -> None",
        detect_case_fact_ambiguity(
            "what is its amount?", "thanks that helps a lot", "U002",
        ) is None,
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
        test_new_request_vague_help_with_it_is_not_new,
        test_new_request_vague_help_withis_typo_is_not_new,
        test_new_request_vague_help_with_this_is_not_new,
        test_new_request_bare_help_me_is_not_new,
        test_new_request_concrete_subject_is_new,
        test_new_request_show_me_unaffected,
        test_explicit_resolution_need_a_resolution,
        test_explicit_resolution_go_ahead,
        test_explicit_resolution_draft_letter,
        test_explicit_resolution_vague_help_is_false,
        test_explicit_resolution_bare_ok_is_false,
        test_consecutive_matches_only_current_segment,
        test_consecutive_matches_counts_trailing_run,
        test_consecutive_matches_stops_at_first_break,
        test_consecutive_matches_zero_when_latest_doesnt_match,
        test_knowledge_type_definition,
        test_knowledge_type_evidence,
        test_knowledge_type_evidence_all_proofs_phrasing,
        test_knowledge_type_responsibility,
        test_knowledge_type_deadline,
        test_knowledge_type_deadline_beats_evidence,
        test_knowledge_type_rebuttal,
        test_knowledge_type_scenario_psp,
        test_knowledge_type_exception,
        test_knowledge_type_none_for_unrelated,
        test_actor_intent_psp,
        test_actor_intent_network,
        test_actor_intent_merchant,
        test_actor_intent_none_when_unnamed,
        test_case_fact_ambiguity_detects_other_code,
        test_case_fact_ambiguity_none_when_same_code,
        test_case_fact_ambiguity_none_when_explicit_case_ref,
        test_case_fact_ambiguity_none_when_this_case_demonstrative,
        test_case_fact_ambiguity_none_when_no_previous_segment,
        test_case_fact_ambiguity_none_when_no_code_mentioned,
        test_help_scope_bare_yes_is_draft,
        test_help_scope_yeah_is_draft,
        test_help_scope_go_ahead_is_draft,
        test_help_scope_explain_it_is_explain,
        test_help_scope_explain_better_way_is_explain,
        test_help_scope_great_explain_it_is_explain,
        test_help_scope_unrelated_question_is_none,
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
