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

from chunking import ACTOR_KEYWORDS

# A specific UTR (UPI Transaction Reference) or NPCI case ID, e.g.
# "UTR20260802M002359516" / "NPCI20260818M002359516" (see merchant_db.py's
# ID format). Referencing an exact case is unambiguous dispute-agent intent
# on its own — "explain more on UTR..." has none of the usual dispute-
# incident language (no "chargeback", "refund", etc.) and would otherwise
# fall through to "invalid", even though naming a specific case is about as
# clear a signal as a query can give.
_CASE_REF_RE = re.compile(r'\b(?:UTR|NPCI)\d{6,}\w*\b', re.IGNORECASE)


def has_case_reference(query: str) -> bool:
    """True if `query` names a specific UTR/case ID directly (e.g.
    "NPCI20260530M002010") rather than describing a dispute in general
    terms. Used both by classify_query_type() below (a named case wins
    "dispute" classification outright) and by chargeback_agent.py's
    _validate_node, which must NOT run its list-then-select continuity
    logic (asking the LLM "is this a request to list cases?") against a
    query that already names one exact case — confirmed live that the
    LLM tool-call there misread "Help me with case NPCI..." as a listing
    request, which then discarded the case reference entirely as if it
    were stale pendingQuery text to be replaced by the newest message.
    """
    return bool(_CASE_REF_RE.search(query))


def extract_case_reference(query: str) -> Optional[str]:
    """The literal UTR/case_id token named in `query`, or None if none is
    present. Same underlying pattern as has_case_reference() above — used
    by _validate_node to look the token up directly (by utr OR case_id;
    the merchant may name either) rather than just knowing one exists.
    """
    match = _CASE_REF_RE.search(query)
    return match.group(0) if match else None


_SAME_CASE_DEMONSTRATIVE_RE = re.compile(
    r"\b(this|that|the)\s+(case|chargeback|dispute)\b", re.IGNORECASE
)


def refers_to_current_case(text: str) -> bool:
    """
    True if `text` uses a demonstrative reference ("this case," "this
    chargeback," "that dispute," "the case") pointing back at a case
    already anchored in the conversation, rather than asking about the
    merchant's OTHER/ALL cases.

    Used by _validate_node as a deterministic veto: when a follow-up on
    an already-case-anchored masked_query ALSO looks like a data lookup
    (contains "chargeback"/"cases"), the LLM tool-call deciding whether
    to abandon the case anchor was confirmed live to be unreliable for
    exactly this ambiguity — "help me with step by step info about THIS
    chargeback" (clearly still about the one case) was misread as wanting
    to see other cases, discarding the case reference. This demonstrative
    check overrides that judgment call outright rather than trusting it:
    a "this case"/"this chargeback" reference is unambiguous enough that
    no LLM confirmation is needed to know it means the anchored case.
    """
    return bool(_SAME_CASE_DEMONSTRATIVE_RE.search(text))


_CASE_INSTANCE_FACT_RE = re.compile(
    r'\b(how much|amount|deadline|due\s*date|due\s*by|resolved|resolution|'
    r'case\s*status|current\s*status)\b',
    re.IGNORECASE,
)


def asks_about_case_instance_fact(text: str) -> bool:
    """
    True if `text` is asking for a specific, only-this-case-can-answer-it
    fact (the amount, the deadline, whether it's resolved) rather than a
    conceptual/definitional question about a reason code in general.

    Distinct from refers_to_current_case() above: that function only
    catches an EXPLICIT demonstrative ("this case," "that dispute"). A bare
    follow-up like "what is the amount?" / "amount buddy?" carries no
    demonstrative and no case ID of its own, so refers_to_current_case()
    alone marks it as a generic/conceptual question — wrongly, since "the
    amount" has no generic, case-less answer at all; it can only mean the
    amount of whichever case is already anchored. Confirmed live: three
    consecutive rephrasings of "what is the amount?" during a single-case-
    anchored conversation all got a generic "the amount that was
    duplicated" non-answer instead of the real, on-file figure, because
    chargeback_agent.py's _answer_clarification_node gated its case-facts
    lookup on refers_to_current_case()/extract_case_reference() alone,
    neither of which any of the three phrasings satisfied. Meant to be
    combined with a check that a case IS already anchored (never used
    alone to decide WHICH case a fact-seeking question is about) — see
    that node's own is_case_specific_question for how the two combine.
    """
    return bool(_CASE_INSTANCE_FACT_RE.search(text))


# Section-A-style "case discovery" questions ("what is the case ID?", "is
# the case still open?") each have exactly one crisp, deterministic answer
# drawn straight from the DB row — no LLM judgment call needed, and letting
# an LLM answer them was confirmed live to produce the wrong shape twice
# over: a narrow single-fact question ("What is the case ID?") got the
# ENTIRE case status/resolution/recommendation dumped back regardless of
# what was actually asked, because _answer_clarification_node's prompt
# unconditionally instructed the model to "lead with" every fact by name.
# Checked in this priority order (most specific literal phrase first) so a
# question naming more than one keyword resolves to the single field it's
# actually asking about, not whichever pattern happens to be scanned first.
_CASE_FACT_PATTERNS = (
    ("case_id",           re.compile(r"\bcase\s*id\b", re.IGNORECASE)),
    ("amount",            re.compile(r"\b(chargeback\s+)?amount\b|\bhow\s+much\b", re.IGNORECASE)),
    ("reason_code",       re.compile(r"\breason\s*code\b|\b(which|what)\s+code\b", re.IGNORECASE)),
    ("network",           re.compile(r"\bnetwork\b", re.IGNORECASE)),
    ("can_respond",       re.compile(
        r"\bcan\s+i\s+(still\s+)?(respond|reply|submit|fight|dispute)\b|\btoo\s+late\b",
        re.IGNORECASE,
    )),
    # Checked BEFORE the bare deadline_date bucket below — "why...deadline"
    # and "deadline...mean...lost" both contain "deadline" too, and would
    # otherwise be swallowed by that bucket's bare \bdeadline\b match,
    # returning just the date to a question that was never asking for the
    # date at all (confirmed live: "Why are you saying the deadline
    # passed?" and "Does deadline passed mean I automatically lost?" both
    # got the same bare "The response deadline was June 29, 2026." non-answer).
    ("deadline_explanation", re.compile(r"\bwhy\b.*\bdeadline\b", re.IGNORECASE)),
    ("deadline_implication", re.compile(
        r"\bdeadline\b.*\b(mean|means|imply|implies)\b.*\b(lost|lose|losing|automatic)\b",
        re.IGNORECASE,
    )),
    ("deadline_date",     re.compile(
        r"\bdeadline\b|\bdue\s*date\b|\bdue\s*by\b|\brespond\s+by\b|\bwhen\b.*\brespond\b",
        re.IGNORECASE,
    )),
    ("resolution_status", re.compile(r"\bresolut(ion|ved)\b", re.IGNORECASE)),
    ("case_status",       re.compile(
        r"\bis\s+(it|the\s+case)\s+(still\s+)?(open|closed)\b|\bcase\s+status\b|"
        r"\bcurrent\s+status\b|\bstill\s+open\b",
        re.IGNORECASE,
    )),
    # Section-B-style evidence questions — "what do I have/need," "does my
    # ledger prove X" — all resolve to the SAME underlying fact this project
    # already computes per case (chargeback_analysis.ledger_decision_reason /
    # ledger_no_decision_reason): what the bank's own records do and don't
    # establish. Checked as distinct intents so the answer can be framed to
    # match what was actually asked (a yes/no "does this prove..." reads
    # differently from an open "what do I have"), even though both draw on
    # the same underlying reason text.
    ("ledger_proof",      re.compile(
        r"\b(does|doesn.?t|what\s+does)\s+.*\bledger\b.*\bprove\b|"
        r"\bprove\s+i.?m\s+innocent\b|\bproves?\s+(i\s+)?wasn.?t\b",
        re.IGNORECASE,
    )),
    ("missing_evidence",  re.compile(
        r"\bevidence\s+is\s+missing\b|\bwhat\s+evidence\s+(do\s+i\s+)?(still\s+)?need\b|"
        r"\bwhat.?s\s+missing\b|\bwhat\s+should\s+i\s+collect\b",
        re.IGNORECASE,
    )),
    # Checked BEFORE current_evidence — "do I have enough evidence to
    # fight?" needs a direct yes/not-yet answer (derived from the same
    # 5-way assessment the Section-E intents below use), not a bare
    # restatement of the evidence narrative with no framing at all.
    ("sufficiency",       re.compile(
        r"\benough\s+evidence\s+to\s+fight\b|\bdo\s+i\s+have\s+enough\s+evidence\b",
        re.IGNORECASE,
    )),
    ("current_evidence",  re.compile(
        r"\bwhat\s+evidence\s+do\s+i\s+(currently\s+)?have\b|\bcurrent\s+evidence\b",
        re.IGNORECASE,
    )),
    # Section-E-style assessment/recommendation questions — map directly
    # onto _derive_assessment()'s own 5-way output (CONTEST/ACCEPT/
    # INVESTIGATE/INSUFFICIENT_EVIDENCE/NO_ACTION_AVAILABLE), computed from
    # the same case_context fields the fact intents above already read —
    # not a new decision, just a different question about the same state.
    ("who_is_right",      re.compile(
        r"\bwho\s+is\s+right\b|\bwho.?s\s+right\b|\bcustomer\s+or\s+merchant\b|"
        r"\bmerchant\s+or\s+customer\b",
        re.IGNORECASE,
    )),
    ("final_answer",      re.compile(r"\bfinal\s+answer\b", re.IGNORECASE)),
    ("assessment",        re.compile(
        r"\bshould\s+i\s+fight\b|\bwhat\s+is\s+your\s+recommendation\b|"
        r"\bwhat.?s\s+your\s+recommendation\b|\bwhat\s+should\s+i\s+do\b",
        re.IGNORECASE,
    )),
)


def classify_case_fact_intent(text: str) -> str:
    """
    Which single, on-file case fact `text` is asking about, or "case_summary"
    for a broad case-view request ("show me this case," "tell me about this
    case") with no narrower target, or "" if neither.

    Only meaningful once a real case is already anchored (case_context.
    case_id set) — callers must gate on that themselves, same as
    asks_about_case_instance_fact() above; this function has no way to know
    whether a case is anchored on its own.

    Deliberately NOT used to decide whether something IS a question at all
    (that's is_clarifying_question(), which already requires a "?" or a
    question-starter word for every one of these narrow buckets in
    practice) — this only decides WHICH fact to answer, once a caller has
    already established the turn is a question. The one exception is the
    "case_summary" bucket, checked via refers_to_current_case() below,
    which a caller may also use as a routing signal for a genuine but
    question-mark-free case-view imperative like "Show me this case." (see
    _detect_clarification_node's own use of this).
    """
    if not text:
        return ""
    for label, pattern in _CASE_FACT_PATTERNS:
        if pattern.search(text):
            return label
    if refers_to_current_case(text):
        return "case_summary"
    return ""


def detect_case_fact_ambiguity(
    latest: str, previous_segment: str, anchored_reason_code: str,
) -> Optional[str]:
    """
    Returns the OTHER reason code `previous_segment` named, if a bare
    case-fact follow-up in `latest` (resolved to the anchored case only
    because asks_about_case_instance_fact() has no other case-less
    interpretation — see classify_case_fact_intent()'s caller) might
    actually be about a DIFFERENT case the merchant just brought up in
    passing. None when there's no such signal — the overwhelmingly common
    case, where the bare follow-up genuinely does mean the long-anchored
    case.

    Reported live: mid-conversation about an anchored U002 case, the
    merchant asked "ohhh i have U003 also?" (correctly answered as a
    generic definitional aside, NOT a case switch — detect_case_selection()
    already deliberately refuses to hijack the anchor for a genuine
    question like this, see that function's own docstring) and then asked
    "what is its amount?" — which silently resolved to the still-anchored
    U002 case's amount, not the U003 case that was actually just discussed.
    Deliberately conservative, same philosophy as detect_case_selection():
    fires only when `previous_segment` named a specific different code AND
    was NOT itself already an explicit case reference (has_case_reference/
    refers_to_current_case) — that case is upstream anchor-switching logic's
    job, not this function's. A caller finding this returns non-None should
    ask which case is meant rather than guess.
    """
    if not previous_segment:
        return None
    _, code = extract_network_and_code(previous_segment)
    if code == "Unknown" or code == anchored_reason_code:
        return None
    if has_case_reference(previous_segment) or refers_to_current_case(previous_segment):
        return None
    return code


_NEW_REQUEST_STARTER_RE = re.compile(
    r"^\s*(help me( with| to)?|please help|can you help|i need help|"
    r"show me|tell me|list |give me|explain( to me)?)\b",
    re.IGNORECASE,
)

# "help me with it"/"help me with this"/"help me with is" (the last one a
# common no-space typo for "help me with this") carry no concrete new
# subject at all — they're the merchant pointing back at whatever's already
# anchored, not asking about something else. Scoped to the "help me..."
# family specifically (not show/tell/list/give/explain) since that's the
# reported failure shape: a bare pronoun/typo remainder after "help me"
# still satisfied _NEW_REQUEST_STARTER_RE, so a case-anchored "help me with
# it" discarded the case reference from masked_query exactly like "help me
# with all open questions" (a genuinely different, broader ask) correctly
# does — the two are opposite in meaning but were being treated identically.
_VAGUE_ANAPHORIC_HELP_RE = re.compile(
    r"^\s*(help me|please help|can you help|i need help)"
    r"\s*(with|to)?\s*(it|this|that|is)?\s*[.!?]*\s*$",
    re.IGNORECASE,
)


def looks_like_new_request(text: str) -> bool:
    """
    True if `text` opens with an imperative request pattern ("help me
    with...", "show me...", "list...") rather than reading as a direct
    answer to a question. Confirmed live: "help me with all open
    questions" — typed as a follow-up on an already-case-anchored
    conversation, matching none of looks_like_data_lookup() (no "case"/
    "chargeback"/"dispute" keyword), refers_to_current_case(), or an
    escalation phrase — fell through every existing check and got
    silently treated as evidence for the anchored case, producing a
    complete rebuttal letter regardless of what was actually asked.

    Deliberately checked only at the START of the text (re.match, not
    re.search) — a genuine evidence answer ("we have the tracking
    number and the customer's delivery confirmation") can legitimately
    contain phrases like "show" or "tell" mid-sentence without being a
    new request; what actually distinguishes a fresh ask is opening
    with one.

    EXCEPT a vague, subject-free "help me with it/this/that" (see
    _VAGUE_ANAPHORIC_HELP_RE) — confirmed live this was misread as a new,
    unrelated request on an already-case-anchored conversation, discarding
    the case reference from masked_query entirely. classify_query_type()
    on the resulting bare "help me with it" then returned "invalid", and
    because masked_query itself (not just additional_context) was now this
    same vague text, the LLM substantive-context backstop judged the
    context non-substantive too — defeating _validate_node's own "invalid
    + context" rescue and producing the generic "please describe a
    chargeback dispute" rejection for what was actually a continuation of
    the case just discussed.
    """
    stripped = text.strip()
    if not _NEW_REQUEST_STARTER_RE.match(stripped):
        return False
    if _VAGUE_ANAPHORIC_HELP_RE.match(stripped):
        return False
    return True


_EXPLICIT_RESOLUTION_RE = re.compile(
    r"\b(give me (a |the )?resolution|need (a |the )?resolution|resolution please|"
    r"draft (the |a )?(letter|rebuttal|response)|write (the |a )?(letter|rebuttal|response)|"
    r"generate (the |a )?(letter|rebuttal|response)|send (the |a )?(letter|rebuttal)|"
    r"go ahead|proceed( with)?|let'?s fight|please fight|fight it|"
    r"yes,? fight|draft it|write it up|prepare (the |a )?(letter|rebuttal|response))\b",
    re.IGNORECASE,
)


def looks_like_explicit_resolution_request(text: str) -> bool:
    """
    True if `text` unambiguously asks the system to proceed straight to a
    decision/rebuttal letter now ("give me a resolution", "go ahead and
    draft it", "fight it") — as opposed to a vague continuation ("help me
    with it", "ok", "sure") that doesn't actually say what kind of help is
    wanted.

    Reported live: once a case's ledger_decision is already known,
    _extract_evidence_node used to treat ANY non-question follow-up as
    permission to skip straight to decide_node/generate_node — a vague
    "help me with it" (the merchant confirming they want to continue, not
    specifying HOW) produced the exact same complete, formal rebuttal
    letter as an explicit "give me a resolution" would. This check is what
    lets that shortcut require an actual, specific ask rather than just
    "not obviously a question" — see _extract_evidence_node's own comment
    for how it's used to gate the shortcut instead of removing it outright.
    """
    return bool(_EXPLICIT_RESOLUTION_RE.search(text))


_HELP_SCOPE_EXPLAIN_RE = re.compile(
    r"\b(explain|more detail|in detail|better way|elaborate|walk me through|"
    r"break(it| it)? down|breakdown|tell me more|clarify)\b",
    re.IGNORECASE,
)

_HELP_SCOPE_BARE_AFFIRMATIVE_RE = re.compile(
    r"^(yes|yeah|yep|sure|ok|okay|please do)[.!]?$", re.IGNORECASE,
)


def resolve_help_scope_reply(text: str) -> Optional[str]:
    """
    Resolves a reply to extract_evidence_node's binary scoping question
    ("Want me to explain the evidence in more detail, or should I go ahead
    and draft the response now?") into "explain", "draft", or None if the
    reply picks neither.

    Reported live: nothing consumed the answer to this question at all —
    "yes" and "explain it in a better way" both fell through every existing
    check (is_junk_reply blanks "yes" outright; is_clarifying_question
    doesn't recognize "explain ..." as an answer; and neither
    looks_like_explicit_resolution_request nor anything else had an
    "explain" branch), so the scoping question was re-asked verbatim on
    every single reply, forever — with no cap, since this clarification_reason
    is deliberately exempted from MAX_CLARIFICATION_ROUNDS (see
    chargeback_agent.py's _ask_user_node comment on
    CLARIFICATION_REASON_UNCLEAR_HELP_SCOPE) on the assumption something
    downstream would eventually resolve it.

    "explain" signals are checked first and win over an explicit-resolution
    match — "go ahead and explain it in more detail" mentions both "go
    ahead" and "explain", and the merchant is clearly asking to see the
    evidence explained, not for the letter.

    A bare affirmative ("yes", "sure", "ok") is treated as "draft": this
    question is the one place in the graph that already offers the
    merchant an explicit choice, so an unqualified "yes" reads as "yes,
    proceed" (the last, and only actionable, option this specific question
    poses) — different from the vague "help me with it" case
    looks_like_explicit_resolution_request's own docstring describes, which
    isn't a reply to a two-option question at all.

    Args:
        text: The merchant's latest raw reply segment.

    Returns:
        "explain", "draft", or None if the reply resolves to neither.
    """
    if _HELP_SCOPE_EXPLAIN_RE.search(text):
        return "explain"
    if looks_like_explicit_resolution_request(text):
        return "draft"
    if _HELP_SCOPE_BARE_AFFIRMATIVE_RE.match(text.strip()):
        return "draft"
    return None


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

# A merchant asking to see their OWN existing cases in aggregate — "help me
# with all open u002 chargebacks", "what about all my pending disputes" —
# reads as a listing/data-lookup request, not a single new incident being
# reported. Checked separately from _CONCEPT_QUERY_PATTERNS above (mid-
# sentence, same as that list) because "all"/"my" + a status word here
# signals "show me the list" specifically, distinct from a general
# informational question. Without this, "help me with all open u002
# chargebacks" doesn't start with an _IMPERATIVE_LIST_STARTERS phrase and
# contains "chargebacks" (a _DISPUTE_INCIDENT_TERMS word), so it fell
# through to "dispute" — the single-incident evidence-gathering pipeline —
# and asked the merchant to "confirm only one credit was issued" for a
# request that was never describing one specific transaction at all.
#
# Requires the status word to sit directly next to the case-noun (an
# optional reason code allowed in between, e.g. "open u002 chargebacks") —
# a plain "all open"/"my open" substring match was tried first and wrongly
# fired on "they filed a U002 dispute against my open store", where "open"
# describes the store, not the case count.
_OWN_CASES_STATUS_NOUN_RE = re.compile(
    r"\b(open|pending)\s+(?:u\d{3}\s+)?(chargebacks?|disputes?|cases?)\b",
    re.IGNORECASE,
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
    if has_case_reference(query):
        return "dispute"

    is_question_form    = (
        q.endswith("?")
        or any(q.startswith(w) for w in _QUESTION_STARTERS)
        or any(q.startswith(w) for w in _IMPERATIVE_LIST_STARTERS)
        or any(marker in q for marker in _MID_SENTENCE_QUESTION_MARKERS)
        or any(pattern in q for pattern in _CONCEPT_QUERY_PATTERNS)
        or (
            ("all " in q or "my " in q)
            and _OWN_CASES_STATUS_NOUN_RE.search(q)
        )
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

# A merchant can ask several real questions in one imperative-shaped
# sentence — "help me with step by step info, when was it raised, what
# is the reason code, what evidence..." — with no "?" at all and no
# question word at the very start. Each clause after a comma/semicolon
# starting with a question word is itself a clarifying question, even
# though the sentence as a whole opens with "help me with." Checked
# separately from the start/end-anchored check above (which alone missed
# exactly this phrasing live) rather than folding into it, since this one
# looks for a clause boundary, not just a word position.
_MID_SENTENCE_CLARIFYING_RE = re.compile(
    r'[,;]\s*(how|where|what|why|which|who)\b', re.IGNORECASE
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
        or bool(_MID_SENTENCE_CLARIFYING_RE.search(latest))
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


# _DATA_LOOKUP_HINT_RE above is deliberately loose ("cases", "chargebacks",
# "disputes" alone are enough) — fine when a merchant_id is available,
# since a false positive there just costs one extra, cheap LLM tool-call
# that correctly says "not actually a personal lookup" and moves on. But
# chargeback_agent.py's _answer_question_node also uses this same loose
# check to gate its ANONYMOUS (no merchant_id, e.g. the Q&A tab with no
# login) branch — and there, a false positive has no LLM call to correct
# it: it goes straight to "select your merchant identity," full stop.
# Confirmed live: "what is chargeback" — a plain definitional question,
# not a request for the caller's own records — matches the loose hint
# regex (it contains the word "chargeback") and got rejected outright,
# even though it needs no identity at all. This tighter check requires an
# actual first-person/possessive signal before treating a query as a
# genuine "show me MY data" request in the no-identity case specifically.
_PERSONAL_DATA_SIGNAL_RE = re.compile(
    r"\b(my|mine|i've|i have|i currently|i owe|do i have|do i owe|show me my|"
    r"give me my|list my|tell me my)\b",
    re.IGNORECASE,
)


def looks_like_personal_data_lookup(query: str) -> bool:
    """
    Tighter than looks_like_data_lookup() — requires an explicit first-
    person/possessive signal ("my", "I owe", "do I", ...), not just a
    topic word like "chargeback". Used only to gate the ANONYMOUS branch
    of _answer_question_node's data-lookup check (see that regex's own
    comment above for why the loose version isn't safe to use alone
    there) — the logged-in branch keeps using looks_like_data_lookup()
    unchanged, since a false positive there is cheap to correct.

    Also true for looks_like_aggregate_question() ("how much is
    outstanding," "what do I owe") even without an explicit "my"/"I" —
    that phrasing is unambiguously a personal-balance question by
    convention in this app (see that function's own module comment),
    not a definitional one, even when phrased impersonally.
    """
    return bool(_PERSONAL_DATA_SIGNAL_RE.search(query)) or looks_like_aggregate_question(query)


# Narrow, deterministic pre-check for financial-balance-shaped questions —
# "how much is outstanding", "what do I owe" — that routes straight to the
# aggregate SQL tool in chargeback_agent.py's _resolve_data_lookup_intent()
# instead of relying on the LLM's own tool-calling judgment call for this
# keyword set. Confirmed live this was necessary, not hypothetical: the
# same exact query ("how much is outstanding this case?"), sent
# unchanged, non-deterministically produced three different outcomes
# across repeated calls even at temperature=0 (Groq's MoE routing/batching
# introduces real run-to-run variance) — sometimes correctly calling the
# aggregate tool, sometimes the listing tool, and sometimes neither,
# falling through to a plain knowledge-base search that surfaced a
# Visa/Mastercard arbitration-fee document (wrong card network entirely,
# USD example amounts) as if it answered the merchant's own NPCI/UPI
# account balance. "outstanding"/"owe"/"owed" is unambiguous enough here
# that there's no upside to leaving it to the LLM's judgment at all.
_AGGREGATE_QUESTION_RE = re.compile(
    r'\b(outstanding|owe|owed|amount due|total due)\b',
    re.IGNORECASE
)


def looks_like_aggregate_question(query: str) -> bool:
    """
    True if `query` is a financial-balance-shaped question that should
    bypass the LLM tool-calling decision entirely and go straight to the
    aggregate SQL tool. See _AGGREGATE_QUESTION_RE for why this specific
    keyword set is deterministic rather than left to the LLM.

    Args:
        query: The merchant's query (PII-masked).

    Returns:
        True if this should skip straight to the aggregate data lookup.
    """
    return bool(_AGGREGATE_QUESTION_RE.search(query))


# Deterministic, same reasoning as _AGGREGATE_QUESTION_RE above — "why is
# my chargeback pending" is unambiguous enough that there's no upside to
# leaving it to the LLM tool-call's judgment. Confirmed live: the
# identical query, sent unchanged across repeated calls, non-
# deterministically produced three different outcomes — the real
# list_merchant_cases tool (which only ever shows status='Open' rows,
# never 'Pending' — a different, real status value in this schema, so
# even that "correct" outcome never actually surfaced the merchant's real
# Pending cases), or a fabricated, ungrounded generic explanation from a
# plain knowledge-base search with no connection to the merchant's real
# case data at all. Calling text_to_sql.query_chargebacks() directly (the
# aggregate/query_chargeback_data path) was confirmed to correctly
# generate `WHERE status = 'Pending'` and return the real matching cases
# every time — the underlying capability already works; only the routing
# to it was unreliable. Requires a personal reference ("my"/"our"), not a
# bare status word alone — "what does pending mean" (a general knowledge
# question, not about the caller's own data) must NOT match this.
_STATUS_WORD_RE = re.compile(r"\b(pending|expired)\b", re.IGNORECASE)
_PERSONAL_REFERENCE_RE = re.compile(r"\b(my|our)\b", re.IGNORECASE)


def looks_like_status_question(query: str) -> bool:
    """
    True if `query` is asking about the status of the CALLER'S OWN
    chargeback(s) using a real status value this schema has ("pending,"
    "expired") — should bypass the LLM tool-calling decision entirely
    and go straight to the aggregate SQL tool, same as
    looks_like_aggregate_question() above. See _STATUS_WORD_RE's own
    comment for why this is deterministic rather than left to the LLM.

    Args:
        query: The merchant's query (PII-masked).

    Returns:
        True if this should skip straight to the aggregate data lookup.
    """
    return bool(_STATUS_WORD_RE.search(query) and _PERSONAL_REFERENCE_RE.search(query))


# Deterministic, not left to the LLM tool-call — matches this project's
# general pattern (see looks_like_aggregate_question above) of pulling a
# reliably keyword-detectable filter out of the LLM's judgment entirely
# rather than trusting it to notice every time. Requires BOTH a deadline
# word AND a temporal-status word somewhere in the query, not either
# alone — "deadline" alone appears in plenty of questions that aren't
# asking to exclude expired cases (e.g. "what's the deadline for
# NPCI...").
_DEADLINE_WORD_RE = re.compile(r"\b(deadline|due date)\b", re.IGNORECASE)
_DEADLINE_STATUS_WORD_RE = re.compile(
    r"\b(passed|expired|remaining|left|still|not over|not due|not passed|active)\b",
    re.IGNORECASE,
)


def looks_like_active_deadline_filter(query: str) -> bool:
    """
    True if `query` is asking to list/filter cases to ones whose response
    deadline hasn't passed yet ("deadline is also due not passed,"
    "still has time left," "deadline not expired") — as opposed to a
    plain listing request with no deadline qualifier at all.

    _filtered_open_cases() (chargeback_agent.py) only ever filters by
    status='Open' — status='Open' does NOT imply the deadline hasn't
    passed in this schema (that's a separate field, and this demo data
    doesn't guarantee the two stay in sync). Confirmed live: "which all
    chargeback cases are currently open and deadline is also due not
    passed?" returned every Open case regardless of whether its deadline
    had already passed, silently dropping the second half of the
    question — text_to_sql.py's own NL->SQL path already handles this
    correctly (its rule 7 for "due in N days"/"expiring soon" phrasing),
    but the deterministic list_merchant_cases path chargeback_agent.py
    uses for case-selection continuity had no equivalent at all.
    """
    return bool(_DEADLINE_WORD_RE.search(query) and _DEADLINE_STATUS_WORD_RE.search(query))


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
    "fourth": 3, "4th": 3, "forth": 3,  # "forth" is a common misspelling of
                                        # "fourth" — confirmed live typed
                                        # exactly this way ("what about
                                        # forth one?"); without this alias
                                        # it doesn't match any ordinal at
                                        # all, falling through as if it
                                        # weren't a selection attempt.
    "fifth": 4, "5th": 4,
}

_NUMBER_HASH_RE = re.compile(r'#\s*(\d+)|\bcase\s+(\d+)\b', re.IGNORECASE)

# "the last one"/"last case" — unlike "the other one" (looks_like_relative_
# case_reference, genuinely ambiguous — which other one?), "last" is fully,
# unambiguously resolvable: it always means the highest-index case in
# whatever list was just shown. Confirmed live this was a real gap, not
# hypothetical: with 7 cases shown, "last one" matched neither
# _ORDINAL_WORDS (no entry past "fifth") nor
# looks_like_relative_case_reference()'s pattern (doesn't say "other" or
# "different") — it fell all the way through detect_case_selection()
# returning None, past is_out_of_range_case_reference() (also ordinal-
# word-based, so also None), past looks_like_relative_case_reference()
# (no match), straight into the "abandon and promote" fallback, which
# treated the bare text "last one" as a new topic and got rejected by the
# generic invalid-query guard ("Please describe a chargeback dispute...")
# — a confusing, unrelated-looking answer for what was actually a
# perfectly resolvable case reference.
_LAST_ONE_RE = re.compile(r'\b(the\s+)?last\s+(one|case|chargeback|dispute)\b', re.IGNORECASE)

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
    t = latest.lower()

    # Strong, unambiguous selection signals — checked BEFORE the
    # clarifying-question guard below, deliberately. An ordinal/number
    # reference is a real selection even when phrased as a question:
    # "what about the second one?", "what's #2?" both unambiguously mean
    # "show me case index 1", not a genuine request for information.
    # Confirmed live this ordering matters, not just in theory: with the
    # question-guard checked first (this function's original order),
    # "what about second one?" — sent as a follow-up right after a
    # 2-case list was shown — was rejected as "just a question" before
    # this ordinal check ever ran, so it fell through to normal
    # classification instead of resolving to the second case, and ended
    # up answered from the FIRST case's own details instead (wrong case
    # entirely, not just a missed selection).
    m = _NUMBER_HASH_RE.search(t)
    if m:
        idx = int(m.group(1) or m.group(2)) - 1
        if 0 <= idx < len(shown_cases):
            return shown_cases[idx]["case_id"]

    if _LAST_ONE_RE.search(t):
        return shown_cases[-1]["case_id"]

    for word, idx in _ORDINAL_WORDS.items():
        if re.search(rf'\b{re.escape(word)}\b', t) and idx < len(shown_cases):
            return shown_cases[idx]["case_id"]

    # A genuine question ("what does U002 mean?") is never a selection via
    # the WEAKER reason-code-mention signal below, even when it happens to
    # name one of the shown cases' reason codes — confirmed live during
    # testing: "what does U002 mean?" was matching the U002 case via the
    # reason-code check below before this guard existed. Checked only
    # here, after the strong ordinal/number signals above have already had
    # their chance — a question-PHRASED selection still resolves via
    # those, while a genuine informational question about a reason code
    # (naming no ordinal/number at all) still correctly falls through to
    # None. Reuses the same check _validate_node already treats as
    # authoritative for "is the merchant asking a question" elsewhere in
    # this module.
    if is_clarifying_question(latest):
        return None

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


def is_out_of_range_case_reference(text: str, shown_cases: List[Dict]) -> bool:
    """
    True if the latest turn in `text` looks like an ordinal/number case
    reference ("the third one", "#5") whose index does NOT exist in
    shown_cases — i.e. detect_case_selection() returned None specifically
    BECAUSE the position was out of range, not because the text wasn't a
    selection attempt at all. The two situations need different handling
    from the caller: a genuinely unrelated follow-up question should fall
    through to normal classification, but an out-of-range selection
    attempt should be told plainly there's no such case, not silently
    reinterpreted as something else.

    Confirmed live this distinction is necessary, not defensive
    programming: with only detect_case_selection()'s plain None to go on,
    _validate_node's existing fallback (promote this turn's text, re-
    enriched with whatever case reference the ORIGINAL pendingQuery
    happened to carry) reattached the FIRST case's id to "what about
    third one?" when only two cases had ever been shown — producing a
    confidently wrong answer ("Case NPCI... is the third open
    chargeback...") for a case that was never third anything, rather
    than surfacing that no third case exists.

    Args:
        text:        The merchant's reply — same latest-segment
                     convention as detect_case_selection().
        shown_cases: The cases actually shown, same as
                     detect_case_selection().

    Returns:
        True only if an ordinal/number was named and it's out of range;
        False for a reference that resolves fine, or for text with no
        ordinal/number in it at all (that's just "not a selection",
        detect_case_selection()'s job to say so).
    """
    if not shown_cases:
        return False

    segments = [s.strip() for s in text.split('\n\n') if s.strip()]
    latest = (segments[-1] if segments else text).strip()
    t = latest.lower()

    m = _NUMBER_HASH_RE.search(t)
    if m:
        idx = int(m.group(1) or m.group(2)) - 1
        if idx < 0 or idx >= len(shown_cases):
            return True

    for word, idx in _ORDINAL_WORDS.items():
        if re.search(rf'\b{re.escape(word)}\b', t) and idx >= len(shown_cases):
            return True

    return False


_RELATIVE_CASE_REFERENCE_RE = re.compile(
    r"\b(the other one|another one|the other case|the other chargeback|"
    r"a different one|the previous one)\b",
    re.IGNORECASE,
)


def looks_like_relative_case_reference(text: str) -> bool:
    """
    True if the latest turn in `text` refers to "some other case" relative
    to whatever was just discussed ("what about the other one?", "and the
    previous one?") WITHOUT naming a resolvable ordinal/number/case ID —
    detect_case_selection() correctly returns None for this (it's not an
    ordinal), but None here means something different from "not a
    selection attempt at all": the merchant IS trying to reference a
    specific case, just relative to conversational context this project's
    stateless-per-call design (chat.html never round-trips which case a
    PRIOR turn resolved to) has no way to reconstruct reliably.

    Confirmed live: after resolving "the second one" to a specific case,
    "What about the other one?" on the very next turn re-showed the
    entire case list from scratch — because nothing tracks that a
    specific case was just discussed, "the other one" has no ordinal for
    detect_case_selection() to match, and the existing "abandon and
    promote" fallback just treated the bare text as an unrelated new
    topic. Used by _validate_node to ask a clarifying question instead of
    guessing or restarting from the full list — same reasoning as
    is_out_of_range_case_reference() one level up: a specific class of
    "not a resolvable selection" deserves different handling than a
    genuinely unrelated follow-up.

    Args:
        text: The merchant's reply — same latest-segment convention as
              detect_case_selection().

    Returns:
        True if the latest turn names a relative "other case" reference.
    """
    segments = [s.strip() for s in text.split('\n\n') if s.strip()]
    latest = segments[-1] if segments else text
    return bool(_RELATIVE_CASE_REFERENCE_RE.search(latest))


def count_clarification_rounds(additional_context: str) -> int:
    """
    Approximates how many clarification rounds have already happened in
    this conversation, purely from additional_context — this project's only
    cross-call memory (chat.html never round-trips anything the server
    computed; see looks_like_relative_case_reference()'s docstring for the
    same constraint biting a different bug). Every non-empty reply segment
    counts as one round.

    Deliberately does NOT try to exclude "clarification about the
    question" replies (is_clarifying_question()'s job elsewhere) — tried
    that first and reverted it, confirmed live it was actively wrong: a
    real, unresolved PRIMARY reply like "what about the other one?" also
    ends in "?", so is_clarifying_question() matches it too, and excluding
    it meant a merchant could repeat exactly that phrase forever with the
    round count stuck at 0 — silently defeating the cap for precisely the
    ambiguous-case-reference scenario it most needs to bound.
    is_clarifying_question() only knows "is this phrased as a question,"
    not "is this asking about the SYSTEM rather than attempting to answer
    it" — too blunt an instrument to reuse here safely.

    Net effect: a genuine meta-question ("where do I find the reason
    code?") also consumes one of MAX_CLARIFICATION_ROUNDS, even though it
    didn't get a real chance to resolve anything. Accepted deliberately —
    a slightly conservative cap that reliably triggers beats a precise one
    that can be talked past indefinitely just by phrasing replies as
    questions. Likewise, a junk filler reply ("ok", "thanks") counts as a
    round too, even though validate_node's own junk-reply filtering may
    later strip it from what downstream nodes actually see — same
    trade-off, same reasoning.

    Args:
        additional_context: The full accumulated conversation text, same
                             '\\n\\n'-joined convention as every other
                             function in this module.

    Returns:
        Number of prior rounds, 0 on a true first turn.
    """
    segments = [s.strip() for s in additional_context.split('\n\n') if s.strip()]
    return len(segments)


def count_consecutive_matches(additional_context: str, predicate) -> int:
    """
    How many of the MOST RECENT reply segments consecutively satisfy
    `predicate`, walking backward from the latest and stopping at the
    first segment that doesn't — the narrower counterpart to
    count_clarification_rounds() for the several places in this file that
    check "has THIS SPECIFIC kind of ambiguity recurred," not "how long
    has the conversation been in total."

    Reported live: a merchant had a long, healthy, wide-ranging U002 Q&A
    conversation (five turns — none of them an ambiguous case reference)
    before asking "Can I win a U002 case?" as their 3rd... no, their
    FIRST-EVER instance of this specific ambiguity (does "case" here mean
    THIS anchored case, or something else?). _validate_node's own inline
    round-cap check used count_clarification_rounds() — the conversation's
    TOTAL segment count, already 3+ from unrelated exchanges — and
    escalated on the very first occurrence, having never actually
    repeated. This function fixes that class of bug at its root: a
    predicate-specific streak count is 1 the first time a pattern occurs,
    not however long the conversation happens to already be.

    Args:
        additional_context: Full accumulated conversation text, same
                             '\\n\\n'-joined convention as everywhere else
                             in this module.
        predicate:           Callable(segment: str) -> bool, evaluated
                             against one segment at a time (same
                             latest-segment convention every other
                             function here uses when given the full text).

    Returns:
        Length of the streak ending at (and including) the latest
        segment. 0 if there are no segments, or the latest one doesn't
        match at all.
    """
    segments = [s.strip() for s in additional_context.split('\n\n') if s.strip()]
    count = 0
    for seg in reversed(segments):
        if not predicate(seg):
            break
        count += 1
    return count


# ---------------------------------------------------------------------------
# Knowledge-type / actor intent detection
#
# Query-side counterpart to chunking.py's index-side derive_knowledge_type()/
# derive_actors() — maps question phrasing to the same KnowledgeType/Actor
# vocabulary so _answer_question_node can filter/boost chunk retrieval by
# the KIND of knowledge a question wants, not just its network/reason code.
# Checked in order below, most specific first, so e.g. "what's the deadline
# to submit evidence?" resolves to DEADLINE rather than the broader EVIDENCE
# match later in the list.
# ---------------------------------------------------------------------------

_KNOWLEDGE_TYPE_INTENT_PATTERNS = [
    (re.compile(r'\b(deadline|due date|time limit|time frame|how (many|long)\b.{0,15}\bdays?\b)\b', re.IGNORECASE), "DEADLINE"),
    (re.compile(r'\b(exception|exempt|waiv(e|er|ed)|caveat)\b', re.IGNORECASE), "EXCEPTION"),
    (re.compile(r'\b(rebuttal|represent(ment)?|how (do|can) i (fight|win|contest|dispute))\b', re.IGNORECASE), "REBUTTAL"),
    (re.compile(r'\b(evidence|proofs?|documents?|documentation)\b', re.IGNORECASE), "EVIDENCE"),
    (re.compile(r'\b(who is responsible|whose fault|who.?s liable|liability|liable)\b', re.IGNORECASE), "RESPONSIBILITY"),
    (re.compile(r'\b(what if|what happens if|can i still)\b', re.IGNORECASE), "SCENARIO"),
    (re.compile(r'\b(what does\b.{0,30}\bmean|meaning of|what is\b.{0,20}\b(code|reason))\b', re.IGNORECASE), "DEFINITION"),
]


def detect_knowledge_type_intent(query: str) -> Optional[str]:
    """
    Classify a question's phrasing into the KnowledgeType vocabulary
    (chunking.derive_knowledge_type's DEFINITION/EVIDENCE/PROCEDURE/
    RESPONSIBILITY/OUTCOME/DEADLINE/EXCEPTION/FAQ/SCENARIO/REBUTTAL/SUMMARY),
    or None if nothing matches. Callers should treat None the same as any
    other "no signal" case in this module — fall back to unfiltered
    retrieval rather than erroring.
    """
    for pattern, ktype in _KNOWLEDGE_TYPE_INTENT_PATTERNS:
        if pattern.search(query):
            return ktype
    return None


# A scenario question naming a specific intermediary ("what if the PSP
# charged the customer twice?") almost always also names "customer" or
# "merchant" as the transaction's two parties regardless of which party is
# actually at fault — those two are checked LAST so a more specific,
# diagnostic actor (psp/issuer/acquirer/network) wins when both appear.
_ACTOR_INTENT_PRIORITY = ["psp", "issuer", "acquirer", "network", "customer", "merchant"]


def detect_actor_intent(query: str) -> Optional[str]:
    """
    Classify a question's phrasing into the Actor vocabulary
    (chunking.derive_actors' merchant/customer/issuer/acquirer/psp/network),
    or None if no actor is named. Shares chunking.ACTOR_KEYWORDS with the
    content-side detector so query-side and content-side actor detection
    can't drift apart — but checks it in _ACTOR_INTENT_PRIORITY order
    (specific intermediary before generic transaction party), not
    ACTOR_KEYWORDS' own dict order, since a query can legitimately name
    both. Word-boundary matched (not a naive substring check) for the same
    reason _answer_question_node's other intent checks are — see this
    module's other detect_*/looks_like_* functions.
    """
    lowered = query.lower()
    for actor in _ACTOR_INTENT_PRIORITY:
        for kw in ACTOR_KEYWORDS[actor]:
            if re.search(r'\b' + re.escape(kw) + r'\b', lowered):
                return actor
    return None
