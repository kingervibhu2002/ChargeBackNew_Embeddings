"""
retrieval_evaluator.py — Deterministic retrieval-sufficiency check.

Answers a different question than eval_retrieval.py (an offline benchmark
run against a golden query set, ahead of time) and reflect_node's
groundedness check (which verifies the DRAFT ANSWER's citations after
generation). This module runs at request time, right after retrieval,
before generation — and asks: were the documents retrieved for THIS query
actually applicable to the network/reason code just detected, or merely
semantically similar to it?

Why this matters, concretely (not hypothetically): a query like "how much
is outstanding this case?" or "what documentation is required for this?"
can retrieve a document that scores well on cosine similarity — it shares
vocabulary like "outstanding," "documentation," "evidence" — while being a
Visa/Mastercard/Amex retrieval-request or arbitration-fee policy, entirely
inapplicable to the NPCI/UPI RuPay dispute actually being discussed.
Semantic relevance and policy applicability are not the same thing, and
nothing upstream of this checked for the second one before this existed.

Deliberately NOT an LLM call, and deliberately NOT a weighted composite
score guessed from intuition (a hard network/reason-code consistency gate
is enough to catch the two real failures this was built from — a weighted
blend of signals should only be introduced once there's a labeled dataset
of retrieval failures to fit those weights against, not before).

Scope note: this module currently only produces a signal (see
ChargebackState's retrieval_status/retrieval_issues fields, set by
_planner_node) — nothing yet routes on it or retries retrieval when it
comes back "bad". That's a deliberate, separate next step, not an
oversight.
"""

from dataclasses import dataclass, field
from typing import List, Union


@dataclass(frozen=True)
class RetrievalAssessment:
    """
    status:                 "good" (no network mismatch), "ambiguous" (a
                             minority of results are for a different
                             network — real cross-domain background docs
                             count too), "bad" (majority of the checkable
                             results are for a different network than the
                             one actually detected for this query), or ""
                             when no network was detected to check against
                             (nothing to assess yet — e.g. before the LLM
                             fallback in _planner_node's step 5 runs).
    network_consistent:      True unless a majority of checkable results
                             are tagged for a different network.
    matched_fraction:        Fraction of checkable results (those with a
                             non-empty `network` payload field) whose
                             network matches the one detected for this
                             query. 1.0 when there's nothing to check
                             (no results, or none are network-tagged).
    issues:                  Human-readable explanations, empty if none.
    """
    status:             str = ""
    network_consistent: bool = True
    matched_fraction:   float = 1.0
    issues:              List[str] = field(default_factory=list)


def evaluate_retrieval(
    expected_network: Union[str, List[str]], results: list
) -> RetrievalAssessment:
    """
    Check whether `results` (as returned by VectorStore.search()/
    hybrid_search() — dicts with a `network` and `title` field) are
    actually consistent with `expected_network`, the network already
    deterministically detected for this query.

    A result whose `network` payload field is empty is a general/not-
    network-specific document (see chargeback-encyclopedia's own frontmatter
    convention) — treated as neutral, never counted as a mismatch. Only a
    result explicitly tagged for a DIFFERENT network counts against
    `matched_fraction`, since a background/general document appearing
    alongside the right network-specific ones is normal and expected, not
    a sign retrieval went wrong.

    Args:
        expected_network: The network already detected for this query
                          (e.g. "RuPay", "Visa"), OR a list of all payload
                          spellings that should count as a match for it.
                          The latter matters in practice, not just in
                          theory: verified directly against this project's
                          real indexed data that RuPay documents are split
                          across BOTH "RuPay" (5 docs) and "RuPay / NPCI"
                          (6 docs), and Amex across both "Amex" (9) and
                          "American Express" (4) — chunking.py's
                          derive_network() only uses each document's own
                          frontmatter network: field when it's present and
                          non-empty, falling back to a short folder-based
                          name otherwise, and that fallback fires for
                          roughly half of each network's real documents.
                          A caller checking against only one spelling will
                          misjudge genuinely-correct retrieval as a
                          mismatch for the other half. Pass "" or "Unknown"
                          (or an empty list) when no network was detected
                          yet — returns an unassessed ("") result rather
                          than guessing.
        results: Documents as returned by VectorStore.search()/
                hybrid_search() — each a dict with at least `network` and
                `title` keys.

    Returns:
        RetrievalAssessment
    """
    if isinstance(expected_network, str):
        expected_set = {expected_network.strip()} if expected_network.strip() else set()
    else:
        expected_set = {n.strip() for n in expected_network if n and n.strip()}
    expected_set.discard("Unknown")

    if not expected_set:
        return RetrievalAssessment()

    expected_label = " / ".join(sorted(expected_set))

    if not results:
        return RetrievalAssessment(
            status="bad",
            network_consistent=False,
            matched_fraction=0.0,
            issues=["No documents were retrieved at all."],
        )

    checkable = [r for r in results if (r.get("network") or "").strip()]
    if not checkable:
        # Nothing in the result set carries a network tag at all (e.g. only
        # general/cross-network background docs came back) — no evidence
        # of a wrong-network mismatch, but also nothing confirming a right
        # one. Treated as "ambiguous" rather than "good": there's a real
        # difference between "checked and consistent" and "nothing to check".
        return RetrievalAssessment(
            status="ambiguous",
            network_consistent=True,
            matched_fraction=1.0,
            issues=["None of the retrieved documents are tagged with a specific network — "
                    "could not confirm they're actually about " + expected_label + "."],
        )

    matches    = sum(1 for r in checkable if (r.get("network") or "").strip() in expected_set)
    fraction   = matches / len(checkable)
    mismatched_titles = sorted({
        r.get("title", "?") for r in checkable
        if (r.get("network") or "").strip() not in expected_set
    })

    network_consistent = fraction >= 0.5
    issues = []
    if mismatched_titles:
        issues.append(
            f"{matches}/{len(checkable)} network-tagged results are for {expected_label}; "
            f"the rest are tagged for a different network: {', '.join(mismatched_titles[:3])}"
            + ("..." if len(mismatched_titles) > 3 else "")
        )

    if not network_consistent:
        status = "bad"
    elif mismatched_titles:
        status = "ambiguous"
    else:
        status = "good"

    return RetrievalAssessment(
        status=status,
        network_consistent=network_consistent,
        matched_fraction=round(fraction, 2),
        issues=issues,
    )
