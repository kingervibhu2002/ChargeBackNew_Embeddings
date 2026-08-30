"""
test_chunking.py — Unit tests for chunking.py's knowledge_type/actor/
evidence_tag taxonomy derivation and the exception-heading short-section
merge fix.

Run:
    python test_chunking.py
"""

import sys
from chunking import (
    derive_knowledge_type,
    derive_actors,
    derive_evidence_tags,
    split_into_chunks,
)


def _check(label: str, condition: bool, detail: str = "") -> bool:
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + (f" — {detail}" if detail and not condition else ""))
    return condition


# ---------------------------------------------------------------------------
# derive_knowledge_type — real headings pulled from the corpus
# ---------------------------------------------------------------------------

def test_knowledge_type_definition():
    return _check(
        "'Definition' section -> DEFINITION",
        derive_knowledge_type("Definition", None) == "DEFINITION",
    )

def test_knowledge_type_what_this_means():
    return _check(
        "'What This Dispute Code Means' -> DEFINITION",
        derive_knowledge_type("What This Dispute Code Means", None) == "DEFINITION",
    )

def test_knowledge_type_required_evidence():
    return _check(
        "'Required Evidence' -> EVIDENCE",
        derive_knowledge_type("Required Evidence", None) == "EVIDENCE",
    )

def test_knowledge_type_merchant_liability():
    return _check(
        "'Merchant Liability' -> RESPONSIBILITY",
        derive_knowledge_type("Merchant Liability", None) == "RESPONSIBILITY",
    )

def test_knowledge_type_timeline():
    return _check(
        "'Timeline' -> DEADLINE",
        derive_knowledge_type("Timeline", None) == "DEADLINE",
    )

def test_knowledge_type_rebuttal_template():
    return _check(
        "'Rebuttal Letter Template' -> REBUTTAL",
        derive_knowledge_type("Rebuttal Letter Template", None) == "REBUTTAL",
    )

def test_knowledge_type_winning_strategy():
    return _check(
        "'Winning Strategy' -> OUTCOME",
        derive_knowledge_type("Winning Strategy", None) == "OUTCOME",
    )

def test_knowledge_type_pre_submission_checklist():
    return _check(
        "'Pre-Submission Checklist' -> PROCEDURE",
        derive_knowledge_type("Pre-Submission Checklist", None) == "PROCEDURE",
    )

def test_knowledge_type_common_scenarios():
    return _check(
        "'Common Scenarios' -> SCENARIO",
        derive_knowledge_type("Common Scenarios", None) == "SCENARIO",
    )

def test_knowledge_type_key_takeaways():
    return _check(
        "'Key Takeaways' -> SUMMARY",
        derive_knowledge_type("Key Takeaways", None) == "SUMMARY",
    )

def test_knowledge_type_subsection_overrides_section():
    return _check(
        "Subsection more specific than enclosing section wins",
        derive_knowledge_type("Overview", "Required Evidence") == "EVIDENCE",
    )

def test_knowledge_type_unmatched_heading_is_none():
    return _check(
        "A heading matching no keyword -> None, not a guess",
        derive_knowledge_type("Related Codes", None) is None,
    )

def test_knowledge_type_no_heading_is_none():
    return _check(
        "No section/subsection at all -> None",
        derive_knowledge_type(None, None) is None,
    )


# ---------------------------------------------------------------------------
# derive_actors
# ---------------------------------------------------------------------------

def test_actors_merchant_and_customer():
    actors = derive_actors("The merchant must show the customer's signed delivery receipt.")
    return _check(
        "Content naming both merchant and customer -> both found",
        set(actors) == {"merchant", "customer"},
        detail=str(actors),
    )

def test_actors_psp():
    actors = derive_actors("If the PSP or payment gateway double-charges the customer...")
    return _check(
        "PSP/payment gateway mention -> psp found",
        "psp" in actors,
        detail=str(actors),
    )

def test_actors_none_mentioned():
    return _check(
        "No role words -> empty list",
        derive_actors("This chargeback must be resolved within 45 days.") == [],
    )


# ---------------------------------------------------------------------------
# derive_evidence_tags — reuses evidence_tags.EVIDENCE_TAG_LABELS
# ---------------------------------------------------------------------------

def test_evidence_tags_tracking_number():
    tags = derive_evidence_tags("The merchant should provide a shipment tracking number as proof.")
    return _check(
        "Content matching an EvidenceTag label -> tag found",
        "tracking_number" in tags,
        detail=str(tags),
    )

def test_evidence_tags_none_mentioned():
    return _check(
        "Generic content with no evidence-tag phrase -> empty list",
        derive_evidence_tags("This section explains the dispute lifecycle in general terms.") == [],
    )


# ---------------------------------------------------------------------------
# split_into_chunks — exception-heading short-section merge fix
# ---------------------------------------------------------------------------

def test_exception_short_section_not_merged():
    body = (
        "## Required Evidence\n\n"
        + " ".join(["word"] * 60)
        + "\n\n## Exceptions\n\nNo evidence is required if the customer already confirmed receipt.\n"
    )
    chunks = split_into_chunks(body)
    exception_chunks = [c for c in chunks if c["section"] == "Exceptions"]
    return _check(
        "Short 'Exceptions' section stays its own chunk, not merged into Evidence",
        len(exception_chunks) == 1
        and "No evidence is required" in exception_chunks[0]["content"]
        and "word word" not in exception_chunks[0]["content"],
        detail=str(chunks),
    )

def test_ordinary_short_section_still_merges():
    body = (
        "## Required Evidence\n\n"
        + " ".join(["word"] * 60)
        + "\n\n## Related Codes\n\nSee also U001.\n"
    )
    chunks = split_into_chunks(body)
    return _check(
        "A short, non-exception section still merges into the preceding chunk (unchanged behavior)",
        len(chunks) == 1 and "See also U001." in chunks[0]["content"],
        detail=str(chunks),
    )

def test_faq_chunk_tagged_faq():
    body = "## FAQs\n\n**Q: What is U002?**\nA: It means a duplicate transaction.\n"
    chunks = split_into_chunks(body)
    return _check(
        "A split FAQ chunk is tagged knowledge_type=FAQ",
        len(chunks) == 1 and chunks[0]["knowledge_type"] == "FAQ",
        detail=str(chunks),
    )

def test_regular_chunk_carries_knowledge_type():
    body = "## Required Evidence\n\n" + " ".join(["word"] * 60) + "\n"
    chunks = split_into_chunks(body)
    return _check(
        "A regular heading-derived chunk carries the derived knowledge_type",
        len(chunks) == 1 and chunks[0]["knowledge_type"] == "EVIDENCE",
        detail=str(chunks),
    )


def main() -> None:
    tests = [
        test_knowledge_type_definition,
        test_knowledge_type_what_this_means,
        test_knowledge_type_required_evidence,
        test_knowledge_type_merchant_liability,
        test_knowledge_type_timeline,
        test_knowledge_type_rebuttal_template,
        test_knowledge_type_winning_strategy,
        test_knowledge_type_pre_submission_checklist,
        test_knowledge_type_common_scenarios,
        test_knowledge_type_key_takeaways,
        test_knowledge_type_subsection_overrides_section,
        test_knowledge_type_unmatched_heading_is_none,
        test_knowledge_type_no_heading_is_none,
        test_actors_merchant_and_customer,
        test_actors_psp,
        test_actors_none_mentioned,
        test_evidence_tags_tracking_number,
        test_evidence_tags_none_mentioned,
        test_exception_short_section_not_merged,
        test_ordinary_short_section_still_merges,
        test_faq_chunk_tagged_faq,
        test_regular_chunk_carries_knowledge_type,
    ]

    print(f"\nRunning {len(tests)} chunking tests...\n")
    results = [t() for t in tests]
    passed  = sum(results)
    total   = len(results)

    print(f"\n{'='*60}")
    print(f"  Passed: {passed}/{total}")
    print(f"{'='*60}")

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
