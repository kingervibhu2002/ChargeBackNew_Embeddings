"""
classifier.py — Rule-based classifiers for the chargeback pipeline.

Three functions replace LLM calls that were doing simple pattern matching:

  classify_query_type(text)      → "dispute" | "question" | "escalation" | "invalid"
  extract_network_and_code(text) → (card_network: str, reason_code: str)
  detect_settlement_issue(text)  → bool

All functions are pure Python with no external dependencies.
"""

import difflib
import re
from typing import Dict, List, Optional, Tuple

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
    # Hinglish list-request construction: "<topic> ki list chahiye" / "ki
    # list do" = "want/give a list of <topic>" — same imperative-list intent
    # as the English starters below, just a different sentence shape (the
    # list-word sits mid-sentence, not at the start).
    "ki list",
)

# Payment-domain terms that qualify a question-form input as on-topic.
# "upi" and "code"/"codes" were missing — a query naming only "UPI" (not
# "rupay"/"npci") or asking generically about "codes" (not a specific
# network) fell through to has_payment_topic=False and got misrouted or
# rejected even though it's squarely on-topic for this assistant.
_QUESTION_PAYMENT_TERMS = [
    "chargeback", "dispute", "reason code", "visa", "mastercard", "amex",
    "american express", "rupay", "npci", "upi", "representment", "acquirer",
    "issuer", "timelines", "timeline", "evidence", "rebuttal",
    "pre-arbitration", "arbitration", "process", "procedure", "policy",
    "fight", "refund", "code",
    # Also present in _DISPUTE_INCIDENT_TERMS below — deliberately duplicated,
    # same as "chargeback"/"dispute"/"refund" above, so a question-form query
    # naming one of these ("What is friendly fraud?", "What is an unauthorized
    # transaction?", "What is a settlement issue?") wins the is_question_form
    # check below before ever reaching has_dispute_incident. Confirmed live:
    # without these three, all three examples above were misclassified as
    # "dispute" and routed into the full evidence-gathering pipeline instead
    # of answer_question_node.
    "fraud", "unauthorized", "unauthorised", "settlement",
    # Same reasoning again: "how much is outstanding this month?" has no
    # other payment-domain term, so is_question_form was true but
    # has_payment_topic stayed false and the whole query was rejected as
    # "invalid" before it ever reached _answer_question_node's
    # personal_data_intent check (which was separately fixed to recognize
    # this exact phrasing — that fix alone wasn't sufficient, since
    # classify_query_type() runs first and never let it through).
    "outstanding", "owe", "owed",
    # Same reasoning a third time: "what is my win rate?" — added while
    # verifying the LLM-tool-calling replacement for personal_data_intent
    # (chargeback_agent.py's _resolve_data_lookup_intent) actually reaches
    # the model at all. "case"/"cases" added too — the other keyword in
    # that same tool-calling pre-filter (classifier.looks_like_data_lookup)
    # not already covered here, same failure mode waiting to happen for
    # any question naming only "case(s)" with no other payment term.
    "win rate", "case", "cases",
    # Hinglish
    "chargeback kya", "kya hota hai",
]

# Imperative list-request openers — "List X", "Show me X", "Give me X",
# "Enumerate X", "Display X". classify_query_type's question-detection
# previously only recognised interrogative phrasing (a "?", a wh-word, or a
# fixed concept pattern) and had no case for command-mood requests, which is
# the single most natural way to ask for a list in English. Confirmed live:
# even "List all Visa codes" — about as unambiguous a list request as any
# query can be — was rejected as invalid before this was added.
_IMPERATIVE_LIST_STARTERS = (
    "list ", "show me", "give me", "enumerate", "display all", "display the",
)

# Concrete incident keywords — merchant describing a real problem
_DISPUTE_INCIDENT_TERMS = [
    "chargeback", "dispute", "transaction", "payment", "refund",
    "fraud", "unauthorized", "not received", "item not received",
    "never received", "bank reversed", "reversed my", "funds reversed",
    "settlement", "representment", "i got a", "i received a",
    "they filed", "customer filed",
    # Note: "visa 1", "mastercard 4", "amex c", "rupay u" were removed here
    # deliberately — they were meant to catch genuine code mentions like
    # "Visa 13.1", but as loose substrings they also matched innocent phrases
    # like "Amex codes" or "RuPay users" (any word starting with the next
    # letter), forcing informational questions into the dispute evidence-
    # gathering flow. They were redundant anyway: extract_network_and_code()
    # below already catches every genuine code mention with an actual
    # decimal/digit-format regex, which these loose substrings can't validate.
    #
    # Same reasoning applies to "reason code" and "notification", removed
    # for the same fix: both are neutral domain vocabulary that appears
    # equally in informational lookups ("Visa reason code 13.2", "what's on
    # a chargeback notification") as in genuine incident reports — neither
    # implies an active dispute on its own. Confirmed live: "Visa reason
    # code 13.2" (no incident language, no question phrasing) matched
    # "reason code" here and got routed into the full dispute pipeline,
    # which then fabricated a complete evidence checklist and rebuttal
    # letter for a plain informational query.
    # Hinglish
    "paise nahi aaye", "paisa nahi aaya", "nahi mili raqam",
    "amount nahi aaya", "mera paisa", "meri payment", "bank ne wapas",
    "chargeback aaya", "dispute aaya",
]

# A bare "[network] [reason code] [code]" mention with nothing else —
# "Visa reason code 13.2", "Visa 13.2", "MC 4870", "RuPay U010" — reads as
# a search-engine-style topic lookup (the natural way to type a Q&A query
# without a "what is" prefix), not as someone describing an active dispute.
# Anchored to the whole (stripped) query — a genuine incident description
# that happens to name a code ("I received a Visa 13.1 chargeback") has
# other words around it and won't match, so it's unaffected and still
# falls through to has_dispute_incident / the code-presence check below.
_BARE_CODE_MENTION_RE = re.compile(
    r'^(visa|mastercard|mc|amex|american express|rupay)\s*'
    r'(reason\s*code)?\s*(is)?\s*'
    r'([\d.]+|[a-z]{1,2}\d{2,3}|u\d{3})\s*[?.]?$',
    re.IGNORECASE
)


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
        or any(q.startswith(w) for w in _IMPERATIVE_LIST_STARTERS)
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

    # A bare mention of just "[network] [reason code] [code]" — nothing
    # else in the query — reads as a topic lookup, not an incident report.
    # Checked before the code-presence fallback right below, which would
    # otherwise treat ANY bare code mention as a dispute purely because a
    # valid code pattern is present, regardless of whether the query has
    # any other word implying an actual incident. Confirmed live without
    # this: "Visa reason code 13.2" — a plain informational query — was
    # classified "dispute" and the full pipeline fabricated a complete
    # evidence checklist and rebuttal letter for it.
    if _BARE_CODE_MENTION_RE.match(q):
        return "question"

    # A recognisable chargeback reason code elsewhere in otherwise-unmatched
    # text is strong enough on its own to imply dispute intent — covers
    # phrasing where no incident keyword from _DISPUTE_INCIDENT_TERMS
    # appears but the specific code is present (e.g. a code embedded in a
    # longer sentence that doesn't match the bare-mention pattern above).
    # extract_network_and_code already applies the Mastercard allow-list,
    # so arbitrary 4-digit amounts won't match.
    if extract_network_and_code(q)[1] != "Unknown":
        return "dispute"

    return "invalid"


# ---------------------------------------------------------------------------
# Reason code / network extraction
# ---------------------------------------------------------------------------

# Visa decimal codes: 10.1, 10.2, 10.3, 10.4, 12.6.1, 13.1–13.9 etc.
#
# Each of these four code regexes has an optional network-name prefix
# ("visa", "mastercard"/"mc", "amex", "rupay"/"npci") glued directly onto
# the leading \b. A plain \b can't fire between the network name and an
# immediately-following code with no separator ("npciu001", "visa13.1",
# "mastercard4853") — both the last letter of the name and the first digit
# of the code are \w characters, so there's no boundary for \b to match at
# all, and the whole regex fails to match anywhere in the string. Confirmed
# live: a Q&A-tab query for "npciu001" (no space) returned classify_query_type
# "question" correctly (has_payment_topic already matches on "npci" as a
# keyword), but extract_network_and_code() came back completely empty
# ("Unknown", "Unknown") — so downstream domain-chunk selection had no code
# to key off, fell through to plain semantic search, and surfaced U010
# content instead of U001. The optional prefix lets the match start at the
# network name itself when the two are glued together, while a normal
# space/punctuation-separated mention ("NPCI U001", "Visa 13.1") still
# matches exactly as before via the same \b before the code.
_VISA_CODE_RE   = re.compile(r'\b(?:visa)?(1[0-9]\.\d{1,2}(?:\.\d)?)\b', re.IGNORECASE)

# Amex alpha-numeric codes (checked before MC to avoid 4-digit collision)
_AMEX_CODE_RE   = re.compile(r'\b(?:amex)?(C\d{2,3}|F\d{2,3}|FR\d{1,2}|M\d{2,3})\b', re.IGNORECASE)

# Mastercard 4-digit codes (closed allow-list to exclude Visa BINs starting with 4)
# Sourced from chargeback-encyclopedia/05_Mastercard/ + load_chargeback_docs.py.
_MC_CODE_RE     = re.compile(r'\b(?:mastercard|mc)?(4[0-9]{3})\b', re.IGNORECASE)
_VALID_MC_CODES = {
    "4807", "4808", "4812", "4831", "4834", "4835", "4837", "4840", "4841",
    "4842", "4846", "4849", "4850", "4853", "4854", "4855", "4857", "4859",
    "4860", "4863", "4870", "4871",
}

# RuPay / NPCI codes: U001–U010
_RUPAY_CODE_RE  = re.compile(r'\b(?:rupay|npci)?(U\d{3})\b', re.IGNORECASE)

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


# Generic filler/acknowledgement words that carry no dispute information on
# their own. A merchant replying "nice" or "ok" to "please share the reason
# code" is non-empty text — until this check existed, any non-empty
# additional_context was treated as a real answer and let the flow proceed
# straight into generate_node, once producing a fully-fabricated rebuttal
# letter grounded in nothing but the original dispute description. Only
# fires when the ENTIRE reply is built from these words (short filler plus
# trivial punctuation) — a real answer that happens to contain one, e.g.
# "no, it was a duplicate charge", is unaffected.
_JUNK_REPLY_WORDS = {
    "nice", "ok", "okay", "k", "kk", "fine", "cool", "sure", "alright",
    "yes", "no", "yep", "nope", "yeah", "nah", "maybe", "none", "na",
    "good", "great", "bad", "mad", "sad", "meh",
    "whatever", "idk", "dunno", "lol", "lmao", "haha",
    "fuck", "fuckyou", "fu", "wtf", "stfu", "shit", "damn", "hell",
}

# Real one-word dispute answers that must NOT be flagged as junk even
# though they're a single short token with no recognizable network/code of
# their own (extract_network_and_code doesn't know standalone reason words).
_KNOWN_DISPUTE_WORDS = {
    "fraud", "fraudulent", "duplicate", "duplicated", "refund", "refunded",
    "cancelled", "canceled", "defective", "damaged", "counterfeit",
    "unauthorized", "unauthorised", "unrecognized", "unrecognised",
    "chargeback", "undelivered", "delivered", "disputed", "return",
    "returned", "faulty", "incomplete", "late", "missing", "expired",
}


# A follow-up reply that echoes the original dispute description back
# verbatim (or near-verbatim) reads as substantive text — real words,
# often a real network name — but supplies literally nothing beyond what
# was already known before the question was asked. Ratio threshold is
# deliberately high: it must catch "retyped the same sentence", not
# penalize a real elaboration that happens to reuse some of the same
# domain words (e.g. repeating "Mastercard" and "fraud" while actually
# adding the reason code and evidence details).
_DUPLICATE_QUERY_SIMILARITY_THRESHOLD = 0.85


def _is_junk_segment(text: str, query: str) -> bool:
    """One turn's worth of reply — see is_junk_reply for the three checks."""
    stripped = re.sub(r'[^\w\s]', ' ', text).strip().lower()
    if not stripped:
        return True

    words = stripped.split()
    if all(w in _JUNK_REPLY_WORDS for w in words):
        return True

    if len(words) == 1:
        word = words[0]
        if (
            len(word) <= 20
            and not any(ch.isdigit() for ch in word)
            and word not in _KNOWN_DISPUTE_WORDS
        ):
            network, code = extract_network_and_code(text)
            if network == "Unknown" and code == "Unknown":
                return True

    if query:
        norm_query = re.sub(r'[^\w\s]', ' ', query).strip().lower()
        if norm_query:
            ratio = difflib.SequenceMatcher(None, stripped, norm_query).ratio()
            if ratio >= _DUPLICATE_QUERY_SIMILARITY_THRESHOLD:
                return True

    return False


def is_junk_reply(text: str, query: str = "") -> bool:
    """
    True if `text` carries no real dispute information beyond what was
    already known.

    additional_context can hold several turns' worth of replies joined by
    blank lines (chat.html appends each new reply onto the last while the
    agent keeps asking for more). The chat input is a single-line field, so
    a literal blank-line break can only be that join — never part of one
    reply — which makes it safe to split on and evaluate each turn on its
    own. This matters because checking the joined blob as one string lets
    a repeated junk/duplicate reply dilute itself: two or three copies of
    the same sentence pasted back to back drop the whole-string similarity
    ratio against the original query well below the threshold that catches
    a single copy, even though every individual turn is still exactly as
    uninformative. The whole context is junk only if EVERY turn is, by one
    of:

      1. every word in that turn is generic filler/acknowledgement (see
         _JUNK_REPLY_WORDS: "nice", "ok mad"), or
      2. it's a single short token that's neither a recognized network/code
         (extract_network_and_code) nor a known dispute word
         (_KNOWN_DISPUTE_WORDS) — i.e. likely gibberish such as a
         mashed-keyboard test string ("funckuou") rather than a real, if
         terse, answer, or
      3. `query` is given and that turn is a near-duplicate of it — the
         merchant retyped/echoed the original dispute description instead
         of actually answering the follow-up question, so despite being
         real, substantive-looking text it adds no new information.

    A single turn anywhere in the history that's genuinely informative
    (a real answer, even a terse one) makes the whole context non-junk —
    matching the flow's existing "ask once, use whatever you get" design.

    Branches 2 and 3 can false-positive on a genuine answer that happens to
    look similar (an unlisted one-word synonym, or a real elaboration that
    reuses a lot of the original wording) — an acceptable failure mode
    here since it only causes one more clarifying question, never a
    fabricated answer built from nothing.

    Args:
        text: A merchant's follow-up reply (additional_context) — may hold
              multiple turns joined by blank lines.
        query: The original dispute description, if available — used to
               catch a reply that just echoes it back.

    Returns:
        True if the reply carries no real dispute information.
    """
    segments = [s for s in text.split('\n\n') if s.strip()]
    if not segments:
        return True
    return all(_is_junk_segment(s, query) for s in segments)


def is_confidently_substantive(text: str) -> bool:
    """
    True if the regex layer already has high confidence `text` is a real,
    substantive reply — a recognized network/code (extract_network_and_code),
    or a single word from the curated dispute vocabulary
    (_KNOWN_DISPUTE_WORDS).

    Used to skip chargeback_agent.py's LLM backstop for cases the
    deterministic layer can already resolve with confidence. That backstop
    exists to judge genuinely ambiguous replies (is_junk_reply already let
    them through, but they could still be filler dressed as real text) — it
    was observed to be unreliable specifically on short, bare single-word
    answers ("fraud" alone, flakily rejected ~40% of the time across
    repeated identical calls) even though those are exactly the terse
    answers the follow-up question invites merchants to give. Routing this
    class of input around the LLM call entirely removes that flakiness
    where it matters most, since re-litigating an already-confident regex
    match through a model call adds risk without adding value.

    Args:
        text: A merchant's follow-up reply (a single turn, already known
              not to be junk).

    Returns:
        True if this reply is confidently real without needing an LLM call.
    """
    network, code = extract_network_and_code(text)
    if network != "Unknown" or code != "Unknown":
        return True
    stripped = re.sub(r'[^\w\s]', ' ', text).strip().lower()
    words = stripped.split()
    return len(words) == 1 and words[0] in _KNOWN_DISPUTE_WORDS


_QUESTION_STARTER_WORDS = (
    "how", "where", "what", "why", "which", "can i", "do i",
    "is there", "who",
)


def is_clarifying_question(text: str) -> bool:
    """
    True if the LATEST turn in `text` (accumulated follow-up replies are
    joined by blank lines — see is_junk_reply) reads as the merchant asking
    a question back, rather than answering one.

    Single source of truth for this heuristic — chargeback_agent.py's
    _detect_clarification_node uses this same check to decide whether to
    route to _answer_clarification_node, and _validate_node uses it to
    exempt a genuine clarifying question from the junk-reply/substantive-
    context filters below. Those filters only distinguish "real answer" vs
    "filler/gibberish/duplicate" — a clarifying question is neither, and
    both the regex layer and the LLM backstop were confirmed live to
    misjudge one as "not substantive" and silently discard it before
    _detect_clarification_node (which exists specifically to handle this
    case) ever saw it. Keeping this check first and authoritative avoids
    relying on the LLM to also learn a distinction it was shown not to
    make reliably.

    Args:
        text: additional_context — may hold multiple turns joined by
              blank lines; only the last one is checked, matching
              _detect_clarification_node's own semantics (only the
              merchant's most recent reply is a candidate for "this turn
              is a question").

    Returns:
        True if the latest turn looks like a question.
    """
    segments = [s.strip() for s in text.split('\n\n') if s.strip()]
    latest = segments[-1] if segments else text
    return bool(latest) and (
        latest.strip().endswith("?")
        or any(latest.lower().strip().startswith(w) for w in _QUESTION_STARTER_WORDS)
    )


# ---------------------------------------------------------------------------
# Case-list continuity: "show me my chargebacks" -> "tell me about the first
# one". detect_case_selection() resolves the second turn back to a real
# case_id so it can be rewritten into an explicit case reference and handed
# to the existing case-lookup path (chargeback_agent.py's _planner_node step
# 4b) — no new dispute-handling logic needed downstream of the resolution.
# ---------------------------------------------------------------------------

# Regex-guessing which phrasings mean "look up my own chargeback data" was
# abandoned after four distinct live failures in one session ("Give me all
# U002 cases" missed the filter; "how much is outstanding this month?"
# missed the intent entirely, in two separate places; "what all u002
# cases exist currently?" missed both) — each fix was a narrower patch
# that the next phrasing broke again. This is a genuinely open-ended
# natural-language surface, unlike reason-code extraction (U001-U010, a
# small closed vocabulary) where regex genuinely is the right tool.
# Replaced with real LLM tool-calling — see chargeback_agent.py's
# _resolve_data_lookup_intent(), confirmed live to correctly discriminate
# every phrasing that broke this regex, plus cases regex never covered at
# all ("what is my win rate?").
#
# looks_like_data_lookup() is NOT that accuracy-critical decision — it's
# a deliberately loose, over-inclusive pre-filter used only to skip the
# LLM tool-call on turns that obviously have nothing to do with the
# merchant's own case data (a plain evidence-gathering reply like "yes
# only one credit was issued", mid dispute-flow). False positives here
# just cost one extra (cheap, fast) LLM call; false negatives would
# silently break the feature the way the old regex did — so this errs
# toward matching too much, not too little.
_DATA_LOOKUP_HINT_RE = re.compile(
    r'\b(cases?|chargebacks?|disputes?|outstanding|owe|owed|win rate|how much)\b',
    re.IGNORECASE
)


def looks_like_data_lookup(query: str) -> bool:
    """
    Loose, over-inclusive check for whether `query` might be asking about
    the merchant's own chargeback data — a cost guard, not the actual
    intent decision (that's chargeback_agent.py's
    _resolve_data_lookup_intent(), via real LLM tool-calling). Errs toward
    false positives: matching too much just costs one extra LLM call,
    missing a genuine data-lookup query would silently break the feature.

    Args:
        query: The merchant's query (PII-masked).

    Returns:
        True if this might be worth an LLM tool-call check.
    """
    return bool(_DATA_LOOKUP_HINT_RE.search(query))


# Ordinal words a merchant might use to refer back to one of the cases
# just listed, mapped to a 0-based index into that list (in display order,
# i.e. the same order list_open_chargebacks() already returns — soonest
# deadline first). No such list existed anywhere in this codebase before
# this — built fresh, not adapted from an existing constant.
#
# Deliberately ordinals only ("first", "1st") — NOT bare cardinal numbers
# ("one", "two"). Confirmed live during testing: "the second one please"
# was matching "one" (index 0) before the loop ever reached "second"
# (index 1), because "one" is also the placeholder noun in "second one" /
# "third one" phrasing, not just a synonym for "first". A cardinal number
# word is too ambiguous to trust as an ordinal on its own.
_ORDINAL_WORDS = {
    "first": 0, "1st": 0,
    "second": 1, "2nd": 1,
    "third": 2, "3rd": 2,
    "fourth": 3, "4th": 3,
    "fifth": 4, "5th": 4,
}

_NUMBER_HASH_RE = re.compile(r'#\s*(\d+)|\bcase\s+(\d+)\b', re.IGNORECASE)

# Bare confirmation with no other specific content — only trustworthy as a
# case selection when exactly one case was shown (nothing else for "yes"
# to disambiguate between). Deliberately a small, literal set rather than
# reusing classifier._JUNK_REPLY_WORDS — that set exists to flag replies as
# uninformative, the opposite intent from "these specific words DO count
# as a valid selection when the context is unambiguous."
_BARE_CONFIRM_WORDS = {"yes", "yeah", "yep", "sure", "ok", "okay", "that one"}


def detect_case_selection(text: str, shown_cases: List[Dict]) -> Optional[str]:
    """
    Resolve a merchant's follow-up reply to one of the cases just listed
    back to a real case_id, or None if it doesn't unambiguously resolve.

    Deliberately conservative — every branch requires a specific, matched
    signal; there is no "just guess the first one" fallback. A merchant
    typing a genuinely new, unrelated question in this slot (e.g. "what
    does U002 mean?") must resolve to None here so it falls through to
    normal classification instead of being silently misread as a case
    pick.

    Args:
        text:        The merchant's reply (PII-masked). May be the latest
                     of several turns joined by blank lines, per this
                     module's usual multi-turn convention — only the
                     latest segment is checked, matching
                     is_clarifying_question's own semantics.
        shown_cases: The ordered list of case dicts (as returned by
                     merchant_db.list_open_chargebacks(), soonest deadline
                     first) that was actually rendered to the merchant —
                     order here must match what was displayed, since an
                     ordinal/number reference is resolved positionally.

    Returns:
        The resolved case_id, or None if nothing matched unambiguously.
    """
    if not shown_cases:
        return None

    segments = [s.strip() for s in text.split('\n\n') if s.strip()]
    latest = (segments[-1] if segments else text).strip()

    # A genuine question ("what does U002 mean?") is never a selection,
    # even when it happens to name one of the shown cases' reason codes —
    # confirmed live during testing: "what does U002 mean?" was matching
    # the U002 case via the reason-code check below before this existed.
    # Reuses the same check _validate_node already treats as authoritative
    # for "is the merchant asking a question" elsewhere in this module.
    if is_clarifying_question(latest):
        return None

    t = latest.lower()

    m = _NUMBER_HASH_RE.search(t)
    if m:
        idx = int(m.group(1) or m.group(2)) - 1
        if 0 <= idx < len(shown_cases):
            return shown_cases[idx]["case_id"]

    for word, idx in _ORDINAL_WORDS.items():
        if re.search(rf'\b{re.escape(word)}\b', t) and idx < len(shown_cases):
            return shown_cases[idx]["case_id"]

    # A bare reason-code substring match is too loose on its own — "can you
    # explain U001 to me" is a description request, not a selection, but
    # would still match "u001" as a substring. Require the code to sit next
    # to an actual selection cue (the/that/this before it, or one/case/
    # dispute after it) — "the U008 one" or "U001 case" qualify, "explain
    # U001" does not. Confirmed live: without this, "can you explain U001
    # to me" incorrectly resolved to the U001 case.
    matches = [
        c for c in shown_cases
        if c.get("reason_code") and re.search(
            rf'\b(the|that|this)\s+{re.escape(c["reason_code"].lower())}\b'
            rf'|\b{re.escape(c["reason_code"].lower())}\s+(one|case|dispute)\b',
            t,
        )
    ]
    if len(matches) == 1:
        return matches[0]["case_id"]

    if len(shown_cases) == 1 and t in _BARE_CONFIRM_WORDS:
        return shown_cases[0]["case_id"]

    return None
