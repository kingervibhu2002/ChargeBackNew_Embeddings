"""
chunking.py — Heading-based document splitting for the chunk-level Qdrant
collection, shared by load_encyclopedia.py and load_chargeback_docs.py.

Lives in its own module for the same reason network_detection.py does: two
loader call sites need the exact same splitting rules, and factoring it out
here is the only way they can't silently diverge.

Why heading-based rather than fixed-size or LLM-based chunking: the corpus
already has real, meaningful ## / ### structure (confirmed: 106/149 docs use
###) — splitting on it uses structure that's already there instead of paying
algorithmic or LLM cost to rediscover boundaries the author already marked.
The one recurring exception is a "## FAQs" / "## Frequently Asked Questions"
section, which is itself a bundle of several unrelated **Q: ... ** / answer
pairs under one heading (confirmed via direct inspection of NPCI_U005.md,
NPCI_U001.md, and Visa_10_1.md — all three use the identical **Q: ... **
marker pattern) — treated as one chunk, it would dilute an embedding across
several unrelated questions, so it gets its own split rule.
"""

import re
from typing import Dict, List, Optional

from evidence_tags import EVIDENCE_TAG_LABELS

# A ## or ### heading line, capturing its level and text.
_HEADING_RE = re.compile(r'^(#{2,3})\s+(.+?)\s*$', re.MULTILINE)

_FAQ_HEADING_RE = re.compile(r'^(frequently asked questions|faqs?)$', re.IGNORECASE)

# Splits a FAQ section's body right before each "**Q:" marker.
_QA_SPLIT_RE = re.compile(r'\n(?=\*\*Q:)')

_QUESTION_TEXT_RE = re.compile(r'\*\*Q:\s*(.+?)\*\*')

# Sections shorter than this aren't worth their own vector (e.g. a bare
# "## Related Codes" heading with one line) — merged into the preceding chunk.
_MIN_SECTION_WORDS = 40
# Sections longer than this get split further on paragraph boundaries so one
# embedding doesn't have to represent an oversized block of unrelated content.
_MAX_SECTION_WORDS = 350

# Folder → network fallback for the ~50% of docs (confirmed: 18/36 in
# Visa+RuPay) whose frontmatter has no explicit `network:` field. Mirrors the
# existing fallback pattern load_encyclopedia.py already uses for `section`.
_FOLDER_NETWORK = {
    "04_Visa": "Visa",
    "05_Mastercard": "Mastercard",
    "06_Amex": "Amex",
    "07_RuPay": "RuPay",
}


def derive_network(meta: dict, file_path: str) -> str:
    """Frontmatter network field if present, else inferred from the folder."""
    network = (meta.get("network") or "").strip()
    if network:
        return network
    folder = file_path.split("/")[0] if "/" in file_path else ""
    return _FOLDER_NETWORK.get(folder, "")


# ---------------------------------------------------------------------------
# Knowledge-type / actor / evidence-tag taxonomy
#
# Deterministic, keyword-driven — no LLM call, matching this repo's
# rule-based-over-LLM-based philosophy (classifier.py, decision_rules.py).
# The KnowledgeType vocabulary and keyword map below were derived from the
# actual corpus (`grep -rh '^## ' chargeback-encyclopedia/`), not invented:
# a small set of canonical, high-frequency headings (Definition, Required
# Evidence, Winning Strategy/Losing Mistakes, Merchant Liability, Timeline,
# Rebuttal Letter Template, FAQs, Common Scenarios, Summary/Key Takeaways)
# covers most of the corpus. The long tail of one-off narrative headings
# ("Why Merchants Cannot Fight 10.5 Chargebacks Directly") either falls into
# one of these buckets via a keyword hit or maps to nothing — every consumer
# of this field already treats a missing value as "no signal", the same way
# a missing section/subsection is handled today.
# ---------------------------------------------------------------------------

KnowledgeType = str  # DEFINITION / EVIDENCE / PROCEDURE / RESPONSIBILITY /
                     # OUTCOME / DEADLINE / EXCEPTION / FAQ / SCENARIO /
                     # REBUTTAL / SUMMARY

# Checked against heading text (lowercased) in order; first match wins.
# Ordered so more specific keywords are checked before the generic
# definition/overview fallback.
_KNOWLEDGE_TYPE_KEYWORDS = [
    ("exception",      "EXCEPTION"),
    ("exempt",         "EXCEPTION"),
    ("waiv",           "EXCEPTION"),
    ("caveat",         "EXCEPTION"),
    ("evidence",       "EVIDENCE"),
    ("proof",          "EVIDENCE"),
    ("liability",      "RESPONSIBILITY"),
    ("responsib",      "RESPONSIBILITY"),
    ("rebuttal",       "REBUTTAL"),
    ("timeline",       "DEADLINE"),
    ("deadline",       "DEADLINE"),
    ("wait period",    "DEADLINE"),
    ("day rule",       "DEADLINE"),
    ("checklist",      "PROCEDURE"),
    ("prevention",     "PROCEDURE"),
    ("correction step", "PROCEDURE"),
    ("winning",        "OUTCOME"),
    ("losing",         "OUTCOME"),
    ("mistake",        "OUTCOME"),
    ("strategy",       "OUTCOME"),
    ("win rate",       "OUTCOME"),
    ("scenario",       "SCENARIO"),
    ("worked example", "SCENARIO"),
    ("summary",        "SUMMARY"),
    ("key takeaway",   "SUMMARY"),
    ("merchant notes", "SUMMARY"),
    ("definition",     "DEFINITION"),
    ("overview",       "DEFINITION"),
    ("what this",      "DEFINITION"),
    ("about this",     "DEFINITION"),
    ("applies",        "DEFINITION"),
    ("means",          "DEFINITION"),
]


def derive_knowledge_type(section: Optional[str], subsection: Optional[str]) -> Optional[str]:
    """
    Classify a chunk's ## section / ### subsection heading into the
    KnowledgeType vocabulary via keyword match. Subsection is checked first
    (more specific than the enclosing section) then section. Returns None
    when nothing matches — callers already treat a missing section/
    subsection as "no signal" today, so this is consistent with that.
    """
    for heading in (subsection, section):
        if not heading:
            continue
        lowered = heading.lower()
        for keyword, ktype in _KNOWLEDGE_TYPE_KEYWORDS:
            if keyword in lowered:
                return ktype
    return None


# Canonical actor -> keywords that imply it, scanned against chunk content
# (headings rarely name a role explicitly, unlike knowledge_type). Shared
# with classifier.py's detect_actor_intent() so query-side and content-side
# actor detection can't drift apart.
ACTOR_KEYWORDS = {
    "merchant": ["merchant"],
    "customer": ["customer", "cardholder"],
    "issuer":   ["issuer", "issuing bank"],
    "acquirer": ["acquirer", "acquiring bank"],
    "psp":      ["psp", "payment service provider", "payment gateway", "aggregator"],
    "network":  ["npci", "network reconciliation", "card network"],
}


def derive_actors(content: str) -> List[str]:
    """
    Scan chunk content for actor-role mentions. Returns canonical actor
    names in first-seen order (a chunk can legitimately discuss several
    roles — e.g. a PSP-vs-issuer scenario — so this is a list, not a
    single value, unlike knowledge_type).
    """
    lowered = content.lower()
    found = []
    for actor, keywords in ACTOR_KEYWORDS.items():
        if any(kw in lowered for kw in keywords):
            found.append(actor)
    return found


def derive_evidence_tags(content: str) -> List[str]:
    """
    Scan chunk content for mentions of the closed EvidenceTag vocabulary
    (evidence_tags.py) — reused rather than reinventing a second evidence
    taxonomy, so KB content ties directly to the same tags decision_rules.py
    matches against. Matches on either the tag's human-readable label or its
    raw underscored name (as spaces), case-insensitively.
    """
    lowered = content.lower()
    found = []
    for tag, label in EVIDENCE_TAG_LABELS.items():
        tag_as_words = tag.replace("_", " ")
        if label.lower() in lowered or tag_as_words in lowered:
            found.append(tag)
    return found


def _word_count(text: str) -> int:
    return len(text.split())


def _split_faq_section(body: str) -> List[str]:
    parts = [p.strip() for p in _QA_SPLIT_RE.split(body) if p.strip()]
    return parts if parts else ([body.strip()] if body.strip() else [])


def _split_paragraphs(text: str, max_words: int = _MAX_SECTION_WORDS) -> List[str]:
    """Group paragraphs up to max_words per chunk. Used both as the oversized-
    section splitter and as the whole-document fallback when there's no
    heading structure at all (load_chargeback_docs.py's 10 curated docs have
    zero ## markup)."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks, current, current_words = [], [], 0
    for p in paragraphs:
        w = _word_count(p)
        if current and current_words + w > max_words:
            chunks.append("\n\n".join(current))
            current, current_words = [], 0
        current.append(p)
        current_words += w
    if current:
        chunks.append("\n\n".join(current))
    return chunks or ([text.strip()] if text.strip() else [])


def _first_question_slug(qa_text: str) -> str:
    m = _QUESTION_TEXT_RE.match(qa_text)
    if not m:
        return ""
    q = m.group(1).strip()
    return q[:80] + ("…" if len(q) > 80 else "")


_EXCEPTION_HEADING_KEYWORDS = ("exception", "exempt", "waiv", "caveat", "warning")


def _is_exception_heading(heading: Optional[str]) -> bool:
    """Whether a heading names an exception/caveat — these should stay their
    own chunk even under _MIN_SECTION_WORDS rather than being merged into the
    preceding chunk (see split_into_chunks()'s short-section merge): a short
    'no evidence required if...' exception carries outsized retrieval value
    for a chargeback KB, and merging it into e.g. the preceding Evidence
    chunk blurs both."""
    return bool(heading) and any(kw in heading.lower() for kw in _EXCEPTION_HEADING_KEYWORDS)


def split_into_chunks(body: str) -> List[Dict]:
    """
    Split one document's body into chunks along its ## / ### structure.

    Args:
        body: Document body text (frontmatter already stripped by the caller).

    Returns:
        List of {chunk_index, section, subsection, content, knowledge_type,
        actors, evidence_tags} dicts. `section` is the enclosing ## heading
        text (or None for pre-heading intro text or a headingless document);
        `subsection` is the enclosing ### heading text, or — inside a split
        FAQ section — a short slug of the question. `knowledge_type` is a
        deterministic classification of section/subsection into the
        KnowledgeType vocabulary (see derive_knowledge_type()), or None if
        nothing matched. `actors`/`evidence_tags` are content-derived (see
        derive_actors()/derive_evidence_tags()).
    """
    matches = list(_HEADING_RE.finditer(body))

    if not matches:
        raw_chunks = _split_paragraphs(body)
        return [
            {
                "chunk_index": i, "section": None, "subsection": None, "content": c,
                "knowledge_type": None,
                "actors": derive_actors(c),
                "evidence_tags": derive_evidence_tags(c),
            }
            for i, c in enumerate(raw_chunks)
        ]

    raw_sections = []
    for i, m in enumerate(matches):
        level = len(m.group(1))
        heading_text = m.group(2).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        raw_sections.append((level, heading_text, body[start:end].strip()))

    intro = body[:matches[0].start()].strip()

    chunks: List[Dict] = []
    if intro and _word_count(intro) >= _MIN_SECTION_WORDS:
        chunks.append({
            "section": None, "subsection": None, "content": intro,
            "knowledge_type": None,
            "actors": derive_actors(intro),
            "evidence_tags": derive_evidence_tags(intro),
        })

    current_section: Optional[str] = None

    for level, heading_text, section_body in raw_sections:
        if level == 2:
            current_section = heading_text
            subsection = None
        else:
            subsection = heading_text

        if not section_body:
            continue

        if _FAQ_HEADING_RE.match(current_section or ""):
            for qa in _split_faq_section(section_body):
                chunks.append({
                    "section": current_section,
                    "subsection": _first_question_slug(qa),
                    "content": qa,
                    "knowledge_type": "FAQ",
                    "actors": derive_actors(qa),
                    "evidence_tags": derive_evidence_tags(qa),
                })
            continue

        pieces = (
            _split_paragraphs(section_body)
            if _word_count(section_body) > _MAX_SECTION_WORDS
            else [section_body]
        )
        for piece in pieces:
            heading_for_piece = subsection or current_section
            if (
                _word_count(piece) < _MIN_SECTION_WORDS
                and chunks
                and not _is_exception_heading(heading_for_piece)
            ):
                chunks[-1]["content"] += "\n\n" + piece
                chunks[-1]["actors"] = derive_actors(chunks[-1]["content"])
                chunks[-1]["evidence_tags"] = derive_evidence_tags(chunks[-1]["content"])
            else:
                chunks.append({
                    "section": current_section,
                    "subsection": subsection,
                    "content": piece,
                    "knowledge_type": derive_knowledge_type(current_section, subsection),
                    "actors": derive_actors(piece),
                    "evidence_tags": derive_evidence_tags(piece),
                })

    for i, c in enumerate(chunks):
        c["chunk_index"] = i
    return chunks


def build_contextual_prefix(
    document_title: str,
    network: str,
    reason_code: str,
    section: Optional[str],
    subsection: Optional[str],
) -> str:
    """
    Deterministic per-chunk context prefix, built purely from metadata already
    known at index time — no LLM call, unlike Anthropic's published Contextual
    Retrieval technique this is modeled on. Prepended to a chunk's content
    only for the text that gets embedded; never stored in the payload itself
    (the raw content field stays clean for display/citation). Without this, a
    chunk like "The merchant should provide delivery records." has weak
    semantic identity on its own — prefixing it with which document, code,
    and section it's from gives the embedding model something to anchor to.
    """
    parts = [document_title]
    code_bits = " ".join(b for b in (network, reason_code) if b)
    if code_bits:
        parts.append(code_bits)
    if section:
        parts.append(section)
    if subsection:
        parts.append(subsection)
    return " — ".join(parts) + "\n\n"


def chunk_id(document_id: str, chunk_index: int) -> str:
    """Stable, positional chunk identifier — deliberately never derived from
    heading text, which isn't stable across re-indexes (headings repeat
    across documents and can be reworded without notice)."""
    return f"{document_id}_{chunk_index:03d}"
