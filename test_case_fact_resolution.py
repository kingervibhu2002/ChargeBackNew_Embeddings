"""
test_case_fact_resolution.py — Regression suite for case-context anchoring:
a bare follow-up ("what is its amount?", "great explain it") must resolve
against whichever case the merchant actually just meant, with case_context
itself moving to match — not silently answering from (or later evaluating
free text against) a stale or never-set anchor.

Reported live, in two parts:
  1. Mid-conversation about anchored case NPCI20260530M002010 (U002), the
     merchant asked "ohhh i have U003 also?" (correctly answered
     conceptually, not a case switch) and then "what is its amount?" —
     which answered with U002's amount (₹13,507.29) instead of U003's
     (NPCI20260704M002013, ₹20,302.80). Fixed once (answer text), then
     found to still leave case_context.case_id on the stale case even
     after answering correctly — fixed again (case_context itself now
     moves with the answer).
  2. A conversation that OPENS with a list query ("do i have any u003
     cases?") rather than naming a case directly never anchored
     case_context.case_id at all, even when the list resolved to exactly
     one case — leaving a later free-text follow-up ("great explain it")
     with no anchor to resolve against.

Runs directly against DisputeAgent._answer_clarification_node/
_answer_question_node with a crafted state — no LLM call needed for the
former (a deterministic case-fact fast path); the latter's one real LLM
call (_resolve_data_lookup_intent) is mocked so this suite stays fast and
independent of GROQ_API_KEY. Hits the real demo DB (chargebacks.db,
merchant AIRTEL_M002) the same way test_cbs.py/test_case_recommendations.py
do.

Run:
    python test_case_fact_resolution.py
"""

import sys
from unittest.mock import patch

from chargeback_agent import DisputeAgent

_MERCHANT_ID = "AIRTEL_M002"


def _check(label: str, condition: bool, detail: str = "") -> bool:
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + (f" — {detail}" if detail and not condition else ""))
    return condition


def _ask_full(agent: DisputeAgent, case_id: str, reason_code: str, turns: list) -> dict:
    state = {
        "case_context": {"case_id": case_id, "reason_code": reason_code, "network": "RuPay"},
        "additional_context": "\n\n".join(turns),
        "user_query": f"Help me with case {case_id}",
        "merchant_id": _MERCHANT_ID,
        "retrieved_docs": [],
    }
    return agent._answer_clarification_node(state)


def _ask(agent: DisputeAgent, case_id: str, reason_code: str, turns: list) -> str:
    return _ask_full(agent, case_id, reason_code, turns)["conversation"]["missing_info_question"]


def test_reported_bug_single_match_auto_resolves():
    agent = DisputeAgent(store=None, embed_fn=None)
    answer = _ask(agent, "NPCI20260530M002010", "U002", [
        "Show me this case.",
        "ohhh i have U003 also?",
        "what is its amount?",
    ])
    return _check(
        "Single-match other-code aside -> auto-resolves to the OTHER case's real amount",
        "20,302.80" in answer and "13,507.29" not in answer,
        detail=answer,
    )


def test_no_ambiguity_baseline_unaffected():
    agent = DisputeAgent(store=None, embed_fn=None)
    answer = _ask(agent, "NPCI20260530M002010", "U002", [
        "Show me this case.",
        "What is the amount?",
    ])
    return _check(
        "No other-code aside beforehand -> still answers the anchored case directly",
        "13,507.29" in answer,
        detail=answer,
    )


def test_multi_match_asks_instead_of_guessing():
    agent = DisputeAgent(store=None, embed_fn=None)
    answer = _ask(agent, "NPCI20260629M002006", "U007", [
        "Show me this case.",
        "what about U002",
        "what is its amount?",
    ])
    return _check(
        "Multiple open cases share the other code -> asks, doesn't guess an amount",
        "13,507.29" not in answer and "2,482.23" not in answer and "9,999.00" not in answer
        and "case ID" in answer,
        detail=answer,
    )


def test_multi_match_reply_resolves_back_to_anchor():
    agent = DisputeAgent(store=None, embed_fn=None)
    answer = _ask(agent, "NPCI20260629M002006", "U007", [
        "Show me this case.",
        "what about U002",
        "what is its amount?",
        "no the U007 one",
    ])
    return _check(
        "Replying 'the U007 one' to the multi-match question resolves back to the anchored case",
        "11,313.02" in answer,
        detail=answer,
    )


def test_hypothetical_code_falls_through_to_anchor():
    agent = DisputeAgent(store=None, embed_fn=None)
    # U010 has no open case on file for this merchant — purely conceptual mention.
    answer = _ask(agent, "NPCI20260530M002010", "U002", [
        "Show me this case.",
        "what does U010 mean?",
        "what is its amount?",
    ])
    return _check(
        "Mentioned code has no open case on file -> falls through to the anchored case, unchanged",
        "13,507.29" in answer,
        detail=answer,
    )


def test_single_match_auto_resolve_reanchors_case_context():
    # Regression for the follow-on bug found after the above fix shipped:
    # the auto-resolve branch answered correctly from the OTHER case but
    # left case_context.case_id pointing at the ORIGINAL one. The very
    # next free-text turn ("great explain it") then re-derived its case
    # from the stale anchor via planner_node's case_ref_token fallback
    # (case_context.case_id/anchored_case_id) — silently producing a full
    # recommendation for the case the merchant had already moved on from,
    # while the merchant believed they were still discussing the one they
    # just asked about. case_context must move as a full, internally
    # consistent set of fields (case_id + reason_code + ledger_decision +
    # ...) together, not just case_id — see _resolve_case_context's own
    # docstring for why a partial move is worse than no move at all.
    agent = DisputeAgent(store=None, embed_fn=None)
    result = _ask_full(agent, "NPCI20260530M002010", "U002", [
        "Show me this case.",
        "ohhh i have U003 also?",
        "what is its amount?",
    ])
    new_ctx = result.get("case_context", {})
    return _check(
        "Auto-resolve to the OTHER case re-anchors case_context to that case",
        new_ctx.get("case_id") == "NPCI20260704M002013"
        and new_ctx.get("reason_code") == "U003",
        detail=str(new_ctx),
    )


def test_no_ambiguity_baseline_does_not_reanchor():
    # The anchor must NOT move when the question is answered from the
    # already-anchored case unchanged — only a genuine cross-case
    # auto-resolve should rewrite case_context.
    agent = DisputeAgent(store=None, embed_fn=None)
    result = _ask_full(agent, "NPCI20260530M002010", "U002", [
        "Show me this case.",
        "What is the amount?",
    ])
    return _check(
        "No cross-case resolution -> case_context left untouched",
        "case_context" not in result,
        detail=str(result.get("case_context")),
    )


def test_list_intent_single_match_anchors_case_context():
    # Regression for a related gap found while verifying the fixes above:
    # a conversation that OPENS with a list query ("do i have any u003
    # cases?") rather than naming a case directly never anchored
    # case_context.case_id at all -- this branch only ever returned text.
    # A free-text follow-up on the next turn ("great explain it") then had
    # no case to resolve against and fell through to classify_query_type(),
    # which rejected it outright as an invalid query, instead of being
    # answered against the one case just shown.
    agent = DisputeAgent(store=None, embed_fn=None)
    with patch.object(
        agent, "_resolve_data_lookup_intent",
        return_value={"type": "list", "reason_code": "U003", "active_deadline_only": False},
    ):
        result = agent._answer_question_node({
            "user_query":  "do i have any u003 cases?",
            "merchant_id": _MERCHANT_ID,
        })
    new_ctx = result.get("case_context", {})
    return _check(
        "Single-match list result anchors case_context to that one case",
        new_ctx.get("case_id") == "NPCI20260704M002013"
        and new_ctx.get("reason_code") == "U003",
        detail=str(new_ctx),
    )


def test_list_intent_multi_match_does_not_anchor():
    # Multiple candidates -- genuinely ambiguous, must NOT guess an anchor.
    agent = DisputeAgent(store=None, embed_fn=None)
    with patch.object(
        agent, "_resolve_data_lookup_intent",
        return_value={"type": "list", "reason_code": "", "active_deadline_only": False},
    ):
        result = agent._answer_question_node({
            "user_query":  "do i have any open cases?",
            "merchant_id": _MERCHANT_ID,
        })
    return _check(
        "Multi-match list result leaves case_context unset",
        "case_context" not in result,
        detail=str(result.get("case_context")),
    )


def main() -> None:
    tests = [
        test_reported_bug_single_match_auto_resolves,
        test_no_ambiguity_baseline_unaffected,
        test_multi_match_asks_instead_of_guessing,
        test_multi_match_reply_resolves_back_to_anchor,
        test_hypothetical_code_falls_through_to_anchor,
        test_single_match_auto_resolve_reanchors_case_context,
        test_no_ambiguity_baseline_does_not_reanchor,
        test_list_intent_single_match_anchors_case_context,
        test_list_intent_multi_match_does_not_anchor,
    ]

    print(f"\nRunning {len(tests)} case-fact resolution tests...\n")
    results = [t() for t in tests]
    passed  = sum(results)
    total   = len(results)

    print(f"\n{'='*60}")
    print(f"  Passed: {passed}/{total}")
    print(f"{'='*60}")

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
