"""
classifier.py — Rule-based classifiers for the chargeback pipeline.

Three functions replace LLM calls that were doing simple pattern matching:

  classify_query_type(text)      → "dispute" | "question" | "escalation" | "invalid"
  extract_network_and_code(text) → (card_network: str, reason_code: str)
  detect_settlement_issue(text)  → bool

All functions are pure Python with no external dependencies.
"""

import re
from typing import Tuple

# A specific UTR (UPI Transaction Reference) or NPCI case ID, e.g.
# "UTR20260802M002359516" / "NPCI20260818M002359516" (see merchant_db.py's
# ID format). Referencing an exact case is unambiguous dispute-agent intent
# on its own — "explain more on UTR..." has none of the usual dispute-
# incident language (no "chargeback", "refund", etc.) and would otherwise
# fall through to "invalid", even though naming a specific case is about as
# clear a signal as a query can give.
_CASE_REF_RE = re.compile(r'\b(?:UTR|NPCI)\d{6,}\w*\b', re.IGNORECASE)


# ---------------------------------------------------------------------------
# Query type classification
# ---------------------------------------------------------------------------

_ESCALATION_PHRASES = [
    # English
    "connect me", "speak to", "talk to", "talk with", "speak with",
    "human agent", "live agent", "real agent", "real person", "live person",
    "helpline", "support line", "phone number", "contact number",
    "customer care", "customer support", "call me", "call us",
    # Hinglish
    "kisi se baat", "agent se baat", "support se baat",
    "insan se", "human se", "baat karni hai",
]

_QUESTION_STARTERS = (
    "what", "how", "why", "when", "where", "which", "who",
    "can you", "do you", "could you", "is there", "are there",
    "explain", "tell me", "describe", "define",
    # Hinglish — can appear at the start of a query
    "kya hai", "kya hota", "kaise", "batao", "samjhao",
)

# Hinglish: "X kya hota hai" = "what is X" — question marker is mid-sentence
_MID_SENTENCE_QUESTION_MARKERS = (
    " kya ", " kaise ", " kyun ", " kab ",
    " kya hai", " kya hota", " kya hain", " ka matlab",
)

# Concept/informational patterns — "mastercard and its dispute types",
# "list of visa codes", "difference between 4853 and 4837".
# These phrases are essentially never in incident reports, so any one of them
# signals an informational query even without a traditional question starter.
_CONCEPT_QUERY_PATTERNS = (
    "types of", "kinds of", "list of", "overview of",
    "and its ", "and their ", "all codes", "all types", "all kinds",
    "how many", "what types", "what kinds", "categories of",
    "difference between", "compare ", "explain ",
)

# Payment-domain terms that qualify a question-form input as on-topic
_QUESTION_PAYMENT_TERMS = [
    "chargeback", "dispute", "reason code", "visa", "mastercard", "amex",
    "american express", "rupay", "npci", "representment", "acquirer", "issuer",
    "timelines", "timeline", "evidence", "rebuttal", "pre-arbitration",
    "arbitration", "process", "procedure", "policy", "fight", "refund",
    # Hinglish
    "chargeback kya", "kya hota hai",
]

# Concrete incident keywords — merchant describing a real problem
_DISPUTE_INCIDENT_TERMS = [
    "chargeback", "dispute", "transaction", "payment", "refund",
    "fraud", "unauthorized", "not received", "item not received",
    "never received", "bank reversed", "reversed my", "funds reversed",
    "settlement", "representment", "i got a", "i received a",
    "they filed", "customer filed", "reason code", "notification",
    "visa 1", "mastercard 4", "amex c", "rupay u",
    # Hinglish
    "paise nahi aaye", "paisa nahi aaya", "nahi mili raqam",
    "amount nahi aaya", "mera paisa", "meri payment", "bank ne wapas",
    "chargeback aaya", "dispute aaya",
]


def classify_query_type(query: str) -> str:
    """
    Rule-based query intent classification — no LLM call.

    Precedence: escalation → question → dispute → invalid.

    Args:
        query: PII-masked merchant input (any language, already length/injection checked).

    Returns:
        "dispute" | "question" | "escalation" | "invalid"
    """
    q = query.lower().strip()

    if any(phrase in q for phrase in _ESCALATION_PHRASES):
        return "escalation"

    # A specific UTR/case ID reference is checked before anything else below
    # — it's about as unambiguous dispute-agent intent as a query can carry,
    # and needs to win even when the ID happens to embed a substring that
    # would otherwise trigger a different classification. In particular,
    # "NPCI..." case IDs contain "npci" — itself one of _QUESTION_PAYMENT_TERMS
    # — which combined with a question-form opener like "explain" would
    # otherwise satisfy is_question_form and has_payment_topic below and
    # route to answer_question_node (generic knowledge-base search) instead
    # of planner_node (which looks the exact case up and grounds the answer
    # in it via chargeback_analysis.py).
    if _CASE_REF_RE.search(query):
        return "dispute"

    is_question_form    = (
        q.endswith("?")
        or any(q.startswith(w) for w in _QUESTION_STARTERS)
        or any(marker in q for marker in _MID_SENTENCE_QUESTION_MARKERS)
        or any(pattern in q for pattern in _CONCEPT_QUERY_PATTERNS)
    )
    # Also treat a query as payment-related when it contains a recognisable
    # card code (Visa decimal, Mastercard 4-digit, Amex letter+digit, RuPay U-code).
    _CODE_RE = re.compile(
        r'\b(1[0-9]\.\d{1,2}|4[0-9]{3}|[CF]\d{2,3}|FR\d|U\d{3})\b', re.IGNORECASE
    )
    has_payment_topic   = (
        any(kw in q for kw in _QUESTION_PAYMENT_TERMS)
        or bool(_CODE_RE.search(q))
    )
    has_dispute_incident = any(kw in q for kw in _DISPUTE_INCIDENT_TERMS)

    if is_question_form and has_payment_topic:
        return "question"

    if has_dispute_incident:
        return "dispute"

    # A recognisable chargeback reason code is strong enough on its own —
    # covers correction messages ("my bad it must be 4870"), bare-code retries
    # ("MC 4870"), and any phrasing where no incident keyword appears but the
    # specific code is present. extract_network_and_code already applies the
    # Mastercard allow-list, so arbitrary 4-digit amounts won't match.
    if extract_network_and_code(q)[1] != "Unknown":
        return "dispute"

    return "invalid"


# ---------------------------------------------------------------------------
# Reason code / network extraction
# ---------------------------------------------------------------------------

# Visa decimal codes: 10.1, 10.2, 10.3, 10.4, 12.6.1, 13.1–13.9 etc.
_VISA_CODE_RE   = re.compile(r'\b(1[0-9]\.\d{1,2}(?:\.\d)?)\b')

# Amex alpha-numeric codes (checked before MC to avoid 4-digit collision)
_AMEX_CODE_RE   = re.compile(r'\b(C\d{2,3}|F\d{2,3}|FR\d{1,2}|M\d{2,3})\b', re.IGNORECASE)

# Mastercard 4-digit codes (closed allow-list to exclude Visa BINs starting with 4)
# Sourced from chargeback-encyclopedia/05_Mastercard/ + load_chargeback_docs.py.
_MC_CODE_RE     = re.compile(r'\b(4[0-9]{3})\b')
_VALID_MC_CODES = {
    "4807", "4808", "4812", "4831", "4834", "4835", "4837", "4840", "4841",
    "4842", "4846", "4849", "4850", "4853", "4854", "4855", "4857", "4859",
    "4860", "4863", "4870", "4871",
}

# RuPay / NPCI codes: U001–U010
_RUPAY_CODE_RE  = re.compile(r'\b(U\d{3})\b', re.IGNORECASE)

# "mc" is a common Mastercard abbreviation but too short to substring-match
# safely (would false-positive inside unrelated words), so it gets its own
# word-boundary regex instead of joining the plain keyword lists below.
_MC_ABBREV_RE   = re.compile(r'\bmc\b', re.IGNORECASE)

_NETWORK_KEYWORDS: dict = {
    "Visa":       ["visa"],
    "Mastercard": ["mastercard", "master card", "master-card"],
    "Amex":       ["amex", "american express", "americanexpress"],
    "RuPay":      ["rupay", "ru pay", "ru-pay", "npci", "upi"],
}


def extract_network_and_code(text: str) -> Tuple[str, str]:
    """
    Extract card network and reason code from free text using regex.

    Tries explicit code patterns first (most precise), then falls back to
    network keyword matching (network known, code Unknown).

    Args:
        text: Any merchant text — query, additional_context, or doc excerpt.

    Returns:
        (card_network, reason_code) — "Unknown" for either when not found.
    """
    t = text.strip()

    m = _RUPAY_CODE_RE.search(t)
    if m:
        return "RuPay", m.group(1).upper()

    m = _AMEX_CODE_RE.search(t)
    if m:
        return "Amex", m.group(1).upper()

    m = _VISA_CODE_RE.search(t)
    if m:
        return "Visa", m.group(1)

    m = _MC_CODE_RE.search(t)
    if m and m.group(1) in _VALID_MC_CODES:
        return "Mastercard", m.group(1)

    t_lower = t.lower()
    for network, keywords in _NETWORK_KEYWORDS.items():
        if any(kw in t_lower for kw in keywords):
            return network, "Unknown"
    if _MC_ABBREV_RE.search(t):
        return "Mastercard", "Unknown"

    return "Unknown", "Unknown"


# ---------------------------------------------------------------------------
# Settlement issue detection
# ---------------------------------------------------------------------------

# Phrases that signal a SPECIFIC payment / settlement that never arrived
_SETTLEMENT_POSITIVE_PHRASES = [
    "never settled", "didn't settle", "did not settle",
    "not settled", "settlement failed", "settlement never",
    "money never arrived", "money didn't arrive", "money did not arrive",
    "funds never arrived", "funds didn't arrive", "funds did not arrive",
    "funds not received", "payment not received", "payment never received",
    "payment never arrived", "payment didn't arrive",
    "customer paid but", "was charged but never", "charged but not received",
    "charged but settlement", "settlement not received", "no settlement",
    "settled but not in my account", "transaction settled but",
    # Hinglish
    "paise nahi aaye", "paisa nahi aaya", "amount nahi aaya",
    "raqam nahi aayi", "payment nahi aayi",
    "customer ne pay kiya par", "par mujhe nahi mila",
]

# Phrases that signal a GENERIC low-balance complaint — NOT a settlement issue
_SETTLEMENT_NEGATIVE_PHRASES = [
    "balance khatam", "balance exhausted", "balance depleted", "balance finished",
    "account empty", "no money in account", "balance zero", "zero balance",
    "account mein paise nahi hain", "mera account khaali", "account khaali",
    "balance low", "low balance", "insufficient balance",
]


def detect_settlement_issue(text: str) -> bool:
    """
    Return True when the merchant is reporting a specific settlement that never
    arrived, as distinct from a generic low-balance or account-empty complaint.

    Args:
        text: Merchant's query (any language).

    Returns:
        True if a specific settlement/payment is reported as missing.
    """
    t = text.lower()
    if any(phrase in t for phrase in _SETTLEMENT_NEGATIVE_PHRASES):
        return False
    return any(phrase in t for phrase in _SETTLEMENT_POSITIVE_PHRASES)
