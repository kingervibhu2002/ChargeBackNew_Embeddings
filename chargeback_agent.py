"""
chargeback_agent.py — LangGraph-based chargeback dispute agent.

Orchestrates a multi-step workflow of small, single-responsibility nodes:

  validate → planner → detect_settlement ─┬→ ask_user (END)
          ↘ answer_question (END)          ├→ decide → generate → reflect → END
          ↘ END                             ╰→ extract_code → detect_clarification ─┬→ answer_clarification → ask_user (END)
                                                                                       ╰→ extract_evidence ─┬→ ask_user (END)
                                                                                                              ╰→ decide → generate → reflect → END

Deterministic, regex/keyword-based classification (see classifier.py) and
rule-based fight/refund decisions (see decision_rules.py) replace LLM calls
wherever the task is simple pattern matching, not free-text reasoning.
Routing decisions live only in the `_route_after_*` conditional-edge
functions — node bodies never branch the graph themselves.

Guardrails applied at each stage:
  validate  — length check, prompt injection detection, PII masking
  search    — minimum result count, result diversity
  reflect   — groundedness check, confidence scoring, disclaimer, length cap
  LLM calls — automatic fallback to smaller model on primary failure

Design:
  Does NOT open its own VectorStore or embedding model. build_dispute_agent()
  accepts the store and embed_fn that api_server.py already owns, so only
  one Qdrant connection exists in the process (local mode allows only one).

Requires:
  An LLM provider configured via llm_provider.py — GROQ_API_KEY (default,
  free at https://console.groq.com) or LLM_PROVIDER=openai + OPENAI_API_KEY.
"""

import re
from typing import Callable, List, Literal, Optional, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field

import llm_provider
from guardrails import check_length, detect_prompt_injection, mask_pii, _parse_json_safe
from evidence_tags import EvidenceTag, EVIDENCE_TAG_LABELS, humanize_evidence
from network_detection import (
    DOMAIN_CANDIDATE_POOL_SIZE,
    NETWORK_KNOWLEDGE_DOMAINS,
    detect_knowledge_domain,
    detect_network_title_keys,
    is_upi_context,
    select_domain_chunk,
)
import classifier
import decision_rules
import retrieval_evaluator


# ---------------------------------------------------------------------------
# Data-lookup tools — bound to the LLM in _resolve_data_lookup_intent(),
# replacing what used to be classifier.is_case_list_request()'s regex
# guessing. Confirmed live (this session, before writing the plan this
# implements) that the model this deployment actually runs correctly
# discriminates all three cases these two tools + "call neither" cover,
# across phrasings that broke every version of the regex approach:
# "what all u002 cases exist currently?", "how much is outstanding this
# month?", "what is my win rate?", and more. The docstrings below are
# literally what the model reads to decide when to call them — verified
# wording, not placeholder text, and worth keeping close to as-is if
# edited later. Their bodies are never invoked by the framework; tool
# execution happens manually in _resolve_data_lookup_intent() against the
# real list_open_chargebacks()/query_chargebacks() functions, not these
# stubs — this project doesn't use LangGraph's ToolNode/agent-executor
# machinery anywhere else, and one decision point doesn't need it either.
# ---------------------------------------------------------------------------

@tool
def list_merchant_cases(reason_code: str = "", active_deadline_only: bool = False) -> str:
    """List the merchant's own open chargeback cases so they can be shown
    or picked from, optionally filtered to one reason code (e.g. U002).
    Pass empty string for no reason-code filter. Use this when the
    merchant wants to SEE or SELECT a case.
    Set active_deadline_only=True when the merchant's question asks to
    exclude cases whose response deadline has already passed/expired/
    elapsed/gone by, or to show only ones still within their deadline —
    however that's phrased (misspellings and synonyms included, e.g.
    "dealine not surpassed", "still has time left"). Leave False for a
    plain listing request with no such qualifier."""
    return ""


@tool
def query_chargeback_data(question: str) -> str:
    """Answer an analytical/aggregate question about the merchant's own
    chargeback data (totals, counts, win rate, amounts due) by running it
    against the database. Use this for computed numbers, not for listing
    individual cases."""
    return ""


# Used by _build_case_intro()'s multi-round tool loop, not
# _resolve_data_lookup_intent()'s single-round decision above. Originally
# verified live that a single round isn't enough here — given both tools
# at once, the model called only get_case_details first that time, then
# get_reason_code_info in a later round with the real reason code. NOT
# reliable, though: confirmed live in a LATER session that the model can
# also call BOTH tools in the SAME round, and when it does,
# get_reason_code_info gets no real reason code to work with yet — it was
# observed guessing one from the case_id string itself ("NPCI...M002006"
# -> reason_code="M002", not a real NPCI code at all), producing a
# confidently wrong answer grounded in the WRONG reason code's knowledge-
# base content. _build_case_intro() no longer trusts this tool call's own
# arguments for network/reason_code once the real values are known from
# get_case_details — see that method's own comments for the fix. Kept as
# a genuine multi-round loop regardless (rather than trying to force
# single-round-per-tool via prompting) since the model still sometimes
# needs the extra round, and the fix above makes same-round calls safe
# too.
@tool
def get_case_details(case_id: str) -> str:
    """Fetch the merchant's own chargeback case record by case ID —
    status, amount, deadline, reason code, and the recommended action if
    one has been determined."""
    return ""


@tool
def get_reason_code_info(network: str, reason_code: str) -> str:
    """Fetch reference knowledge-base information explaining what a
    specific chargeback reason code means and what evidence it typically
    requires from the merchant."""
    return ""


# ---------------------------------------------------------------------------
# Shared state
# ---------------------------------------------------------------------------

class ChargebackState(TypedDict):
    """
    Shared state passed between every node in the LangGraph workflow.

    Attributes:
        user_query            (str):        Merchant's original dispute (PII-masked after validate).
        additional_context    (str):        Follow-up info provided on a second call.
        is_valid_query        (bool):       False → validate_node rejected input; graph ends.
        query_type            (str):        "dispute" | "question" | "invalid" — set by validate_node.
        reason_code           (str):        e.g. "13.1" — set by planner_node / extract_code_node.
        card_network          (str):        "Visa" or "Mastercard" — set by planner_node / extract_code_node.
        retrieved_docs        (List[str]):  Policy doc contents — set by planner_node.
        retrieval_status      (str):        "good" | "ambiguous" | "bad" | "" (not assessed
                                             yet, e.g. network unknown) — set by planner_node.
                                             Signal only right now: see retrieval_evaluator.py's
                                             module docstring for why nothing routes on it yet.
        retrieval_issues      (str):        Human-readable explanation when retrieval_status
                                             isn't "good" — set by planner_node.
        is_settlement_issue   (bool):       True → set by detect_settlement_node.
        merchant_is_asking_question (bool): True → set by detect_clarification_node.
        evidence_present      (List[str]):  Evidence merchant mentioned — set by extract_evidence_node.
                                             Drawn from EvidenceTag vocabulary so
                                             decision_rules.py can match reliably.
        evidence_missing      (List[str]):  Evidence still needed — set by extract_evidence_node.
        needs_more_info       (bool):       True → routes to ask_user_node.
        missing_info_question (str):        Question to ask the merchant.
        clarification_round   (int):        How many clarification rounds have already been
                                             asked-and-answered in this conversation — computed
                                             fresh on every call by validate_node from
                                             additional_context via
                                             classifier.count_clarification_rounds() (this
                                             project's only cross-call memory; nothing here is
                                             actually incremented/persisted as running state —
                                             see that function's docstring for why re-deriving
                                             it from scratch each call is correct, not a
                                             workaround). Enforced by ask_user_node and three of
                                             validate_node's own early-return asks against
                                             MAX_CLARIFICATION_ROUNDS, so an unresolved back-
                                             and-forth escalates instead of asking forever.
        clarification_reason  (str):        Why the pending question (if any) was asked — one
                                             of the CLARIFICATION_REASON_* constants, or "" when
                                             nothing is pending. Set alongside
                                             missing_info_question by whichever node asked;
                                             purely for observability (e.g. "what fraction of
                                             merchants get stuck on X"), read by no routing
                                             logic.
        decision              (str):        "fight" or "refund" — set by decide_node.
        decision_reason       (str):        Explanation of the decision.
        decision_source       (str):        "" | "ledger" | "rules" | "llm" — HOW decide_node
                                             reached `decision`, set alongside it. Read by
                                             run() to tag a persisted recommendation
                                             (case_recommendations.py) with its provenance
                                             without re-deriving it later.
        case_intro_action     (str):        "fight" | "refund" | "" — set by validate_node's
                                             two case-intro early-return branches from
                                             _build_case_intro()'s analyze_chargeback() result.
                                             NOT the same signal as `decision` above — this is
                                             evidence-BLIND (CBS/ledger only), the same view
                                             the background pollers (auto_decision_poller.py,
                                             suggestion_poller.py) already act on/advise from,
                                             shown as a preview before any evidence-gathering
                                             happens. Read by run() to persist a
                                             case-intro-preview recommendation even though
                                             this path never reaches decide_node.
        case_intro_reason     (str):        Explanation paired with case_intro_action, copied
                                             verbatim from analyze_chargeback()'s reason text.
        case_intro_source     (str):        "cbs" | "ledger" | "rules" — chargeback_analysis.
                                             Analysis.source, paired with case_intro_action.
        draft_response        (str):        First version of letter/advice — set by generate_node.
        iteration             (int):        How many times generate_node has run.
        confidence_score      (int):        1-10 rating of answer quality — set by reflect_node.
        is_grounded           (bool):       True if answer is based only on retrieved docs.
        groundedness_issues   (str):        Description of any ungrounded claims found.
        reflection_feedback   (str):        What the peer-reviewer improved.
        final_answer          (str):        Polished final output — set by reflect_node.
        case_ref_not_found    (str):        A UTR/case_id the merchant named in free text that
                                             didn't resolve to a row scoped to their own
                                             merchant_id — set by planner_node, read by
                                             extract_code_node to give an accurate "no such case
                                             on your account" message instead of silently falling
                                             through to the generic new-dispute intake question.
                                             Deliberately worded identically whether the ID is
                                             simply wrong or belongs to another merchant — never
                                             confirms or denies another tenant's case exists.
        ledger_decision        (str):       "fight" | "refund" | "" — set by planner_node when a
                                             named case reference resolved to a row AND
                                             chargeback_analysis.analyze_chargeback() already
                                             produced a confident, bank-evidence-backed action for
                                             it (CBS refund record or U002 ledger/reconciliation).
                                             Read by extract_evidence_node and decide_node, both
                                             of which skip their own merchant-evidence gathering
                                             and LLM-based decision entirely when this is set —
                                             the bank's own posting records already settled the
                                             question, so re-asking the merchant to "confirm" the
                                             same fact the ledger already confirmed independently
                                             is redundant, and trusting decision_rules.decide()'s
                                             evidence-free default here could silently contradict
                                             what the ledger actually showed.
        ledger_decision_reason (str):       Explanation paired with ledger_decision, copied
                                             verbatim from analyze_chargeback()'s own reason text.
        ledger_no_decision_reason (str):    Set by planner_node instead of ledger_decision when
                                             analyze_chargeback() found a real bank-side blocker
                                             (a pending ledger entry, or a settlement
                                             reconciliation mismatch) but deliberately returned no
                                             confident action — equally authoritative as
                                             ledger_decision in the sense that no merchant-
                                             supplied evidence can resolve it either, so
                                             extract_evidence_node surfaces this reason directly
                                             instead of asking the merchant to "confirm" evidence
                                             that was never the actual blocker.
        resolved_case_id      (str):        Set by planner_node whenever a named UTR/case_id in
                                             the query resolved to a real row for this merchant —
                                             regardless of whether analyze_chargeback() reached a
                                             confident decision. Read by detect_clarification_node:
                                             a FIRST-turn query naming a real case can itself be a
                                             genuine question ("What exactly happened?", "Did you
                                             receive my evidence?") rather than a fresh incident
                                             description — but is_clarifying_question() otherwise
                                             only ever checks additional_context (a SECOND-turn
                                             reply), so a first-turn question was silently running
                                             straight through extract_evidence -> decide ->
                                             generate and getting a generic rebuttal/refund letter
                                             instead of an actual answer, confirmed live via
                                             agent_eval.py. This field is the signal that lets that
                                             first-turn question get recognized at all.
        resolved_utr          (str):        The same real case's UTR, set alongside
                                             resolved_case_id. Both are read by reflect_node to
                                             catch and deterministically correct a real, confirmed
                                             live failure mode: the LLM garbling a real case_id
                                             into a similar-looking wrong one inside the generated
                                             letter (e.g. "NPCI20260530M010" instead of the real
                                             "NPCI20260530M002010") — reflect_node's existing
                                             groundedness check only ever verified REASON CODE
                                             tokens, never case/UTR identifiers, so a wrong case ID
                                             in a letter meant to go to an actual bank passed
                                             through completely unnoticed.
    """
    user_query:            str
    additional_context:    str
    merchant_id:           str
    is_valid_query:        bool
    query_type:            str   # "dispute" | "question" | "invalid"
    reason_code:           str
    card_network:          str
    retrieved_docs:        List[str]
    retrieval_status:      str
    retrieval_issues:      str
    case_ref_not_found:    str
    ledger_decision:       str
    ledger_decision_reason: str
    ledger_no_decision_reason: str
    resolved_case_id:      str
    resolved_utr:          str
    evidence_present:      List[str]
    evidence_missing:      List[str]
    needs_more_info:            bool
    missing_info_question:      str
    clarification_round:        int
    clarification_reason:       str
    is_settlement_issue:        bool
    merchant_is_asking_question: bool
    decision:              str
    decision_reason:       str
    decision_source:       str
    case_intro_action:     str
    case_intro_reason:     str
    case_intro_source:     str
    draft_response:        str
    iteration:             int
    confidence_score:      int
    is_grounded:           bool
    groundedness_issues:   str
    reflection_feedback:   str
    final_answer:          str


# ---------------------------------------------------------------------------
# LLM factory
# ---------------------------------------------------------------------------

def _make_llms() -> tuple:
    """
    Create primary and fallback LLM clients for the configured provider.

    Delegates to llm_provider.py — the single source of truth for provider
    selection (LLM_PROVIDER=groq|openai), model names, and API-key
    resolution, shared with text_to_sql.py so the two callers can't drift
    on model names the way this project's Groq model choice already did
    once (Meta's llama-3.3-70b-versatile/llama-3.1-8b-instant were fully
    retired from Groq's catalog as of 2026-08-17 — see llm_provider.py's
    model table for whatever's currently configured).

    Returns:
        tuple: (primary_llm, fallback_llm)

    Raises:
        ValueError: If the configured provider's API key is not set.
    """
    return llm_provider.make_llms()


# classifier.py's extract_network_and_code() returns short canonical network
# names ("RuPay", "Amex") — the form used everywhere else in this project
# (state fields, decision_rules.RULES keys, evidence tag mappings). The
# encyclopedia's INDEXED network payload field doesn't always match that —
# but not in the single, uniform way an earlier version of this comment
# assumed ("RuPay docs are tagged 'RuPay / NPCI'", confirmed only via
# grep-ing the frontmatter TEXT, never against what actually landed in
# Qdrant). Verified directly against the real index
# (VectorStore.filter_by_payload({}, limit=300), grouped by network):
# RuPay documents are split across BOTH "RuPay" (5 docs) and "RuPay / NPCI"
# (6 docs); Amex across both "Amex" (9) and "American Express" (4) — a
# genuinely mixed, inconsistent index, not a single wrong spelling to
# correct. Root cause: chunking.py's derive_network() only uses a
# document's own frontmatter network: field when it parses as present and
# non-empty; it silently falls back to a short folder-based name
# otherwise, and that fallback fires for roughly half of each network's
# real documents. A translation to only ONE spelling (this dict's earlier
# form) meant _planner_node's step 3 payload filter matched only the other
# half — silently missing real documents and always falling through to
# the fuzzier hybrid-search fallback, and, once retrieval_evaluator.py
# started using this same mapping, produced false "bad" consistency
# verdicts for genuinely correct RuPay/Amex retrieval. Kept as a list per
# network (not a single string) so both call sites below can accept
# either real spelling as a match instead of assuming there's only one.
# Visa/Mastercard need no entry here — every indexed document for both is
# tagged with exactly the plain canonical name already.
_NETWORK_PAYLOAD_SPELLINGS = {
    "RuPay": ["RuPay", "RuPay / NPCI"],
    "Amex":  ["Amex", "American Express"],
}


# ---------------------------------------------------------------------------
# Structured-output schemas
# ---------------------------------------------------------------------------
# Real Pydantic schemas passed to _invoke_structured() (LangChain's
# .with_structured_output()) instead of hand-parsing free-form JSON text
# via guardrails._parse_json_safe(). The two approaches were producing the
# same DECISION SHAPE already (a "decision" field constrained to one of a
# few known values, checked with .get(..., default) after the fact) — the
# schema just makes that constraint real and enforced by the provider's
# own structured-output machinery, instead of a convention every call site
# has to individually get right. Started with _decide_node's fight/refund/
# uncertain output specifically (the fight-vs-refund recommendation) as
# the first, highest-value case to convert — not a wholesale rewrite of
# every _invoke() call site in this file at once.
class DecisionOutput(BaseModel):
    """decide_node's fight/refund/uncertain recommendation."""
    decision: Literal["fight", "refund", "uncertain"] = Field(
        description=(
            "fight — evidence is strong; representment likely to succeed. "
            "refund — evidence is weak or not worth contesting. "
            "uncertain — the available evidence genuinely isn't enough to "
            "confidently recommend either; use this rather than guessing "
            "when the case is a real toss-up."
        )
    )
    decision_reason: str = Field(
        description="One or two sentences explaining the recommendation."
    )


def _deadline_bucket(response_deadline: str) -> str:
    """
    Classify a case's response_deadline against today's date into
    "overdue" | "due_this_week" | "later" — used to give a merchant's
    open-case listing an urgency summary instead of a flat, undifferentiated
    list. status='Open' does NOT imply the deadline hasn't passed in this
    schema (see active_deadline_only elsewhere in this file) — a case can
    sit visually identical whether its deadline was weeks ago or is a
    month out, which a merchant scanning the list has no way to tell apart
    without this.
    """
    from datetime import date, timedelta
    deadline = date.fromisoformat(response_deadline)
    today = date.today()
    if deadline < today:
        return "overdue"
    if deadline <= today + timedelta(days=7):
        return "due_this_week"
    return "later"


# Hard cap on how many clarification rounds a single conversation can go
# through before the agent stops asking and escalates instead — every agent
# loop needs a termination guarantee (retrieval retries, tool retries,
# reflection all already have one; this was the one exception). Counted via
# classifier.count_clarification_rounds() from additional_context alone —
# this project's only cross-call memory, since chat.html never round-trips
# server-computed state (see looks_like_relative_case_reference()'s
# docstring). Enforced in _ask_user_node (the single funnel for the main
# pipeline's asks) and in the three of _validate_node's own early-return
# asks that bypass that funnel entirely.
MAX_CLARIFICATION_ROUNDS = 3

# clarification_reason values — set alongside missing_info_question at each
# site that asks the merchant something, purely for observability (e.g.
# "what fraction of merchants get stuck on a missing reason code vs.
# ambiguous case reference"). Deliberately scoped to sites that are actually
# part of the ask-merchant loop MAX_CLARIFICATION_ROUNDS bounds — a
# ledger-side blocker (ledger_no_decision_reason) isn't included here since
# no merchant reply can resolve it either way, so it was never a
# "clarification round" to begin with.
CLARIFICATION_REASON_AMBIGUOUS_CASE_REFERENCE = "ambiguous_case_reference"
CLARIFICATION_REASON_SETTLEMENT_AMBIGUITY     = "settlement_ambiguity"
CLARIFICATION_REASON_MISSING_REASON_CODE      = "missing_reason_code"
CLARIFICATION_REASON_MISSING_EVIDENCE         = "missing_evidence"


# ---------------------------------------------------------------------------
# DisputeAgent
# ---------------------------------------------------------------------------

class DisputeAgent:
    """
    Compiled LangGraph dispute agent with injected dependencies and guardrails.

    Instantiated once at server startup via build_dispute_agent().
    Reused for every /dispute request.
    """

    # Shared between _validate_node's first-turn escalation handling and
    # its follow-up-reply check (see that check's own comment for why a
    # second copy of this text is needed at all) — kept as one constant
    # so the two can never drift apart.
    _ESCALATION_MESSAGE = (
        "This is an AI assistant — I cannot connect you to a person directly.\n\n"
        "For human support, contact your:\n"
        "  • Acquiring bank or payment processor\n"
        "  • Visa merchant support: 1-800-VISA-911\n"
        "  • Mastercard merchant support: 1-800-999-0363\n\n"
        "I can still help you understand chargeback policies or draft a "
        "rebuttal letter. Just describe your dispute and I'll get started."
    )

    # Shown instead of yet another question once MAX_CLARIFICATION_ROUNDS is
    # hit — see that constant's own comment for why this exists at all.
    _CLARIFICATION_LIMIT_MESSAGE = (
        "I still don't have enough verified information to help with this "
        "after several rounds of questions. Please share the chargeback "
        "notice from your bank with the exact reason code, or contact your "
        "acquiring bank / Airtel Payments Bank support directly so they can "
        "pull the remaining case details."
    )

    def __init__(self, store, embed_fn: Callable[[str], list], rerank_fn=None, checkpointer=None):
        """
        Args:
            store:       VectorStore instance already connected to Qdrant.
            embed_fn:    Callable (str) → list[float] that embeds text.
            rerank_fn:   Optional callable (query: str, documents: list[str])
                         → list[float], a cross-encoder reranker (see
                         api_server.py's _rerank). None disables reranking —
                         _answer_question_node falls back to plain
                         vector-similarity selection, so this stays a
                         backward-compatible, purely additive parameter.
            checkpointer: Optional LangGraph checkpointer (e.g. SqliteSaver) for
                          session persistence across server restarts.
        """
        self._store         = store
        self._embed         = embed_fn
        self._rerank        = rerank_fn
        self._checkpointer  = checkpointer
        self._llm, self._fallback_llm = _make_llms()
        self._graph         = self._build_graph()
        self._list_cache: dict[str, str] = {}  # cache for list/compare responses

    # ── Shared "don't guess, ask" response builder ───────────────────────

    def _uncertain(self, message: str, needs_more_info: bool = True, **extra) -> dict:
        """
        Build a consistent "not confident enough to proceed" response —
        the one place a decision point in this graph goes when it can't
        confidently commit to an outcome, instead of each node inventing
        its own silent default guess.

        Found live in three separate places in this file, all the same
        underlying anti-pattern: an ambiguous or failed decision silently
        became one specific guess rather than surfacing the uncertainty.
          - _validate_node: a follow-up on an already-anchored case that
            matched none of the known patterns (data lookup, same-case
            reference, escalation, new request) used to be silently
            treated as evidence for that case — "help me with all open
            questions" got a full rebuttal letter for an unrelated case.
          - _decide_node: an unparseable LLM response defaulted to
            "fight" — the WRONG direction for a silent default, since
            this project's own decision_rules.py philosophy is "no
            evidence -> presumptively refund," the safe direction, not
            the aggressive one. The LLM also had no way to express
            genuine uncertainty at all — only a forced binary choice.
          - _extract_evidence_node: an unparseable LLM response defaulted
            to needs_more_info=False, silently letting an incomplete
            case proceed straight to a decision.
        Routing through one named, documented method — rather than three
        independent ad hoc fixes — means a future 4th instance of this
        same anti-pattern has an obvious tool to reach for.

        Args:
            message: The clarifying question or honest "not confident"
                     explanation to show the merchant.
            needs_more_info: Whether this genuinely expects a reply
                     (True — the default) or is a terminal, informational
                     answer for this turn (False — e.g. decide_node's
                     uncertain-decision case, which deliberately doesn't
                     reopen a second round of evidence-gathering; see
                     extract_evidence_node's own "one round, max" cap).
            **extra: Additional state fields the specific call site
                     needs merged in (e.g. decision="" for decide_node,
                     is_valid_query=True for validate_node's early return).

        Returns:
            dict with final_answer=message, needs_more_info, and sane
            confidence/groundedness defaults, plus **extra merged in.
        """
        return {
            "final_answer":        message,
            "needs_more_info":     needs_more_info,
            "confidence_score":    0,
            "is_grounded":         True,
            "groundedness_issues": "",
            **extra,
        }

    # ── LLM call with automatic fallback ─────────────────────────────────

    def _invoke(self, messages: list) -> object:
        """
        Invoke the primary LLM, falling back to the smaller model on failure.

        Implements the fallback chain:
          gpt-oss-120b → gpt-oss-20b → raise original error

        Args:
            messages (list): LangChain message list (SystemMessage + HumanMessage).

        Returns:
            AIMessage: The LLM's response.

        Raises:
            Exception: If both primary and fallback fail.
        """
        try:
            return self._llm.invoke(messages)
        except Exception as primary_err:
            try:
                return self._fallback_llm.invoke(messages)
            except Exception:
                raise primary_err

    def _invoke_with_tools(self, messages: list, tools: list) -> object:
        """
        Same primary→fallback contract as _invoke(), but with tools bound
        so the model can request a tool call instead of (or as well as)
        answering directly. Kept as a separate method rather than adding a
        tools=None param to _invoke() itself — every other call site in
        this file wants plain chat completion, and binding tools on every
        call for no reason would be wasted work.

        Args:
            messages: LangChain message list.
            tools:    @tool-decorated functions to bind.

        Returns:
            AIMessage: may have a non-empty .tool_calls list.

        Raises:
            Exception: If both primary and fallback fail.
        """
        try:
            return self._llm.bind_tools(tools).invoke(messages)
        except Exception as primary_err:
            try:
                return self._fallback_llm.bind_tools(tools).invoke(messages)
            except Exception:
                raise primary_err

    def _invoke_structured(self, messages: list, schema: type) -> BaseModel:
        """
        Same primary→fallback contract as _invoke(), but constrains the
        response to a typed Pydantic schema via LangChain's
        with_structured_output() instead of hand-parsing raw JSON text
        through guardrails._parse_json_safe(). Returns an instance of
        `schema`, not an AIMessage — different enough from _invoke()'s
        contract to be its own method, the same reasoning
        _invoke_with_tools() already uses for tool binding.

        A validation failure (the provider's own structured-output
        machinery couldn't produce something matching `schema`) counts
        as a failure for fallback purposes, same as a network error —
        it's caught by the same except Exception as a malformed
        _parse_json_safe() response used to be, just enforced by the
        provider/schema instead of ad hoc string parsing on this end.

        Args:
            messages: LangChain message list.
            schema:   A Pydantic BaseModel subclass describing the
                      expected response shape.

        Returns:
            An instance of `schema`.

        Raises:
            Exception: If both primary and fallback fail (including a
                       response that fails schema validation).
        """
        try:
            return self._llm.with_structured_output(schema).invoke(messages)
        except Exception as primary_err:
            try:
                return self._fallback_llm.with_structured_output(schema).invoke(messages)
            except Exception:
                raise primary_err

    # ── Nodes ─────────────────────────────────────────────────────────────

    def _filter_substantive_context(self, query: str, context: str) -> str:
        """
        LLM backstop for classifier.is_junk_reply's regex layer.

        Judges whether `context` (a merchant's follow-up reply, possibly
        several turns joined) actually answers the dispute follow-up
        question with real, new information — or is filler, gibberish, or
        an echo of the original description that the regex checks didn't
        happen to catch. Same contract as is_junk_reply: returns `context`
        unchanged if substantive, "" otherwise, so the caller doesn't need
        to know which layer made the call.

        Fails open (returns `context` unchanged) on any LLM error — the
        regex layer already ran and found nothing obviously wrong with this
        reply, so a transient LLM/network failure should not block a real
        merchant's answer.

        Args:
            query: The original dispute description (already PII-masked).
            context: additional_context that survived the regex pre-filter.

        Returns:
            `context` if substantive, "" otherwise.
        """
        try:
            response = self._invoke([
                SystemMessage(content=(
                    "You are a strict input-quality checker for a chargeback "
                    "dispute assistant. A merchant was asked a follow-up "
                    "question during an active dispute — this could be for a "
                    "reason code, a description of what happened, "
                    "confirmation of a specific fact (e.g. how many credits "
                    "or charges were actually received, whether a refund was "
                    "issued), or any other evidence needed to resolve the "
                    "case. Decide whether their reply provides real, specific "
                    "information relevant to the dispute — not whether it "
                    "happens to match one particular question type.\n\n"
                    "Counts as substantive: any real, new detail — even a "
                    "short confirmation or denial with specific content (e.g. "
                    "'confirmed only one credit was issued', 'we checked and "
                    "there was no duplicate', 'yes, only one payment went "
                    "through'), a reason code, a network name, or a word "
                    "describing what happened (e.g. 'fraud', 'wrong item').\n"
                    "Does NOT count: bare filler or acknowledgement words "
                    "with no specific content of their own (e.g. 'nice', "
                    "'ok', 'sure', a lone 'yes' with nothing else attached), "
                    "gibberish, or a reply that just repeats the original "
                    "dispute description back with no new detail added.\n\n"
                    'Respond ONLY with JSON: {"is_substantive": true or false}'
                )),
                HumanMessage(content=(
                    f"Original dispute description: {query}\n\n"
                    f"Merchant's reply: {context}"
                )),
            ])
            data = _parse_json_safe(response.content, {"is_substantive": True})
            if not data.get("is_substantive", True):
                return ""
        except Exception:
            pass
        return context

    def _filtered_open_cases(
        self, merchant_id: str, reason_code: str = "", active_deadline_only: bool = False,
    ) -> list:
        """
        The open-chargebacks list a case-list query should show/resolve
        against — shared by _answer_question_node (rendering the list) and
        _validate_node (resolving "the first one" on the next turn) so the
        two can never drift apart and render one list while resolving
        against a different one.

        Filtering by reason code is now decided upstream, by the LLM tool
        call in _resolve_data_lookup_intent() (originally this method did
        its own regex-based extraction from the query text via
        classifier.extract_network_and_code() — replaced because that
        extraction lived downstream of classifier.is_case_list_request(),
        itself removed for missing phrasings like "what all u002 cases
        exist currently?"). This method now just takes the already-decided
        code and applies it — one job, not two.

        Args:
            merchant_id: Server-resolved merchant scope.
            reason_code: An explicit code to filter to (e.g. "U002"), or
                        "" for no filter.
            active_deadline_only: When True, also drop any case whose
                        response_deadline has already passed. status='Open'
                        does NOT imply this in this schema — confirmed live
                        a merchant asking for open cases "with deadline not
                        passed" got every Open case regardless, including
                        several with a response_deadline weeks in the
                        past. Decided by classifier.
                        looks_like_active_deadline_filter() upstream, same
                        pattern as reason_code above — deterministic, not
                        an LLM tool-call judgment.

        Returns:
            list[dict]: rows from merchant_db.list_open_chargebacks(),
                       filtered to reason_code and/or an active deadline
                       if given.
        """
        from datetime import date
        from merchant_db import list_open_chargebacks
        cases = list_open_chargebacks(merchant_id, limit=100)
        if reason_code:
            cases = [c for c in cases if c["reason_code"] == reason_code]
        if active_deadline_only:
            today = date.today().isoformat()
            cases = [c for c in cases if c["response_deadline"] >= today]
        return cases

    def _resolve_data_lookup_intent(self, merchant_id: str, query: str) -> Optional[dict]:
        """
        Decide whether `query` is asking to see/list the merchant's own
        chargeback cases, asking an aggregate/analytic question about
        them, or neither — via real LLM tool-calling instead of regex.

        Replaces classifier.is_case_list_request()/personal_data_intent's
        old regex approach, which broke on a new phrasing roughly every
        other live test this session ("Give me all U002 cases" missed the
        filter; "how much is outstanding this month?" missed the intent
        entirely, in two separate places; "what all u002 cases exist
        currently?" missed both). Confirmed live, before this method was
        written, that the actually-configured model
        (ChatGroq/openai-gpt-oss-120b) correctly discriminates all of
        these via .bind_tools() — this is a working capability being used,
        not a hopeful redesign.

        Builds and maintains a real LangChain message history for this
        decision (SystemMessage, HumanMessage, the returned AIMessage with
        its tool_calls, and — when a tool was actually called — a
        ToolMessage carrying that tool's real result) rather than just
        returning a bare value, per standard LangChain tool-calling
        convention. The list_merchant_cases/query_chargeback_data
        functions bound here are never themselves executed — their
        job is only to describe a schema/docstring for the model to
        choose between; the real work (list_open_chargebacks() /
        text_to_sql.query_chargebacks()) happens below once we know which
        one, if any, was chosen.

        Args:
            merchant_id: Server-resolved merchant scope (never trusted
                        from the query text itself).
            query:       The query to classify — either the current turn's
                        user_query (first turn) or the resent pending
                        query (a continuity-resolution turn in
                        _validate_node), same as _filtered_open_cases()
                        already treats these interchangeably.

        Returns:
            {"type": "list", "reason_code": "U002" or ""}   — list intent
            {"type": "aggregate", "answer": "..."}            — already
                                                                 answered,
                                                                 via
                                                                 text_to_sql
            None                                               — not a
                                                                 data-lookup
                                                                 query
        """
        # Deterministic short-circuit for financial-balance-shaped
        # questions ("how much is outstanding", "what do I owe") —
        # bypasses the LLM tool-calling decision below entirely. Confirmed
        # live this was necessary: the identical query sent unchanged
        # non-deterministically produced three different outcomes across
        # repeated calls, one of which fell through to a plain KB search
        # that surfaced a Visa/Mastercard arbitration-fee document (wrong
        # card network, USD amounts) as the merchant's own account
        # balance. See classifier.looks_like_aggregate_question()'s
        # docstring for the full detail.
        if classifier.looks_like_aggregate_question(query):
            from text_to_sql import query_chargebacks
            result = query_chargebacks(question=query, role="merchant", merchant_id=merchant_id)
            answer = result.get("answer") or result.get("error") or "No matching data found."
            return {"type": "aggregate", "answer": answer}

        # Same deterministic short-circuit, same reasoning, for a status-
        # word question ("why is my chargeback pending") — see
        # classifier.looks_like_status_question()'s own docstring for why
        # this needed its own check: list_merchant_cases only ever shows
        # status='Open' rows (never 'Pending', a real, different status
        # in this schema), so even when the LLM tool-call correctly chose
        # the listing tool, it could never surface what was actually
        # asked about either way.
        if classifier.looks_like_status_question(query):
            from text_to_sql import query_chargebacks
            result = query_chargebacks(question=query, role="merchant", merchant_id=merchant_id)
            answer = result.get("answer") or result.get("error") or "No matching data found."
            return {"type": "aggregate", "answer": answer}

        # Same deterministic short-circuit, same reasoning again, for a
        # direct "show me/tell me about my own cases" request. Confirmed
        # live via a debug trace on ai_msg.tool_calls: for "Tell me about
        # my chargebacks." the LLM tool-call returned ZERO tool calls at
        # all — not a wrong tool, no tool — so this fell all the way
        # through to a plain knowledge-base search and answered with a
        # generic, US-centric explanation of what a chargeback is in
        # general (MATCH list, $15-$100 fees, none of it grounded in the
        # merchant's real data or even this platform's actual RuPay/UPI
        # domain), despite the tool's own docstring saying almost exactly
        # this phrasing should call it ("use this when the merchant wants
        # to SEE or SELECT a case"). Reuses looks_like_new_request() (built
        # earlier this session for a different purpose — recognizing a
        # fresh imperative ask on a case-anchored conversation) since it
        # already correctly distinguishes "tell me about/show me my X" (a
        # listing request) from "how many/how much" aggregate phrasing —
        # confirmed no overlap with either aggregate check above.
        if classifier.looks_like_new_request(query):
            return {
                "type": "list",
                "reason_code": "",
                "active_deadline_only": classifier.looks_like_active_deadline_filter(query),
            }

        messages = [
            SystemMessage(content=(
                "You are a chargeback assistant for a merchant. Decide "
                "whether this message needs a lookup against the "
                "merchant's own chargeback data, and if so, which tool."
            )),
            HumanMessage(content=query),
        ]
        ai_msg = self._invoke_with_tools(messages, [list_merchant_cases, query_chargeback_data])
        messages.append(ai_msg)

        if not ai_msg.tool_calls:
            return None

        tool_call = ai_msg.tool_calls[0]

        if tool_call["name"] == "list_merchant_cases":
            reason_code = (tool_call["args"].get("reason_code") or "").strip().upper()
            # OR'd with the model's own tool-call argument, not replaced by
            # it: this regex is a narrow keyword match (confirmed live it
            # misses typos/synonyms — "dealine ... surpassed" matched
            # neither "deadline" nor "passed" as whole words), while the
            # LLM argument handles arbitrary phrasing the way reason_code
            # already does above. Kept as a deterministic floor rather than
            # relying on the LLM alone, the same reasoning as
            # looks_like_data_lookup() below it in this file: a false
            # negative from the LLM on a genuinely non-deterministic call
            # shouldn't silently drop the filter when the keywords are
            # actually right there in the text.
            active_deadline_only = (
                classifier.looks_like_active_deadline_filter(query)
                or bool(tool_call["args"].get("active_deadline_only"))
            )
            cases = self._filtered_open_cases(merchant_id, reason_code, active_deadline_only)
            messages.append(ToolMessage(
                content=f"Found {len(cases)} matching case(s).",
                tool_call_id=tool_call["id"],
            ))
            return {
                "type": "list",
                "reason_code": reason_code,
                "active_deadline_only": active_deadline_only,
            }

        if tool_call["name"] == "query_chargeback_data":
            from text_to_sql import query_chargebacks
            # Deliberately the ORIGINAL query text, not tool_call["args"]
            # ["question"] (the model's own rephrasing of it) — found live
            # this regressed a case that worked before this redesign:
            # "how much is outstanding this month?" got correctly routed
            # here, but the model's rephrased version ("What is the total
            # outstanding chargeback amount for the current month?") hit
            # text_to_sql.py's own internal safety/question-answering logic
            # differently and got rejected, while the identical original
            # phrasing succeeds (confirmed directly, side by side).
            # text_to_sql.py does its own NL interpretation regardless —
            # the tool call's only job here is deciding to route to it,
            # not rewriting what gets asked.
            result = query_chargebacks(question=query, role="merchant", merchant_id=merchant_id)
            answer = result.get("answer") or result.get("error") or "No matching data found."
            messages.append(ToolMessage(content=answer, tool_call_id=tool_call["id"]))
            return {"type": "aggregate", "answer": answer}

        return None

    def _lookup_case_details(self, merchant_id: str, case_id: str) -> tuple:
        """
        Real execution behind a get_case_details tool call — same DB
        lookup _planner_node's step 4b already runs (scoped by case_id
        directly here since the case was already resolved via
        classifier.detect_case_selection(), not named in free text). Also
        folds in decision_rules.RULES' required evidence for this
        (network, reason_code) — the same deterministic lookup
        _extract_evidence_node uses — as authoritative content for the
        model to report verbatim, so the actual evidence ask stays
        deterministic even though the surrounding narrative in
        _build_case_intro() is LLM-synthesized.

        Returns:
            (content_for_tool_message, row_or_None)
        """
        from chargeback_analysis import analyze_chargeback
        from merchant_db import get_connection

        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM chargebacks WHERE merchant_id = ? AND case_id = ?",
            (merchant_id, case_id),
        ).fetchone()
        conn.close()

        if not row:
            return f"No case found with ID {case_id} for this merchant.", None

        analysis = analyze_chargeback(row, db_path="chargebacks.db")
        parts = [
            f"Case {row['case_id']} (UTR {row['utr']}): reason code {row['reason_code']} "
            f"({row['reason_description']}), amount {row['chargeback_amount']}, "
            f"status {row['status']}, response deadline {row['response_deadline']}."
        ]
        if analysis.action:
            parts.append(f"Recommended action: {analysis.action}. {analysis.reason}")

        rule = decision_rules.RULES.get(("RuPay", row["reason_code"]))
        if rule:
            needed = rule.required_any or rule.required_all
            if needed:
                labels = ", ".join(humanize_evidence(sorted(needed)))
                parts.append(f"Evidence typically required for this reason code: {labels}.")

        return " ".join(parts), row

    def _lookup_reason_code_info(self, network: str, reason_code: str) -> str:
        """
        Real execution behind a get_reason_code_info tool call — the same
        confident (network, reason_code)-known retrieval chain
        _answer_question_node uses for a strong domain match:
        NETWORK_KNOWLEDGE_DOMAINS → search_chunks(knowledge_domain=...) →
        select_domain_chunk() → full parent document on a strong hit.
        Reused rather than reimplemented so this stays consistent with
        what a direct question about the same code would already surface.
        """
        domain = NETWORK_KNOWLEDGE_DOMAINS.get((network or "").lower())
        if not domain:
            return f"No knowledge-base domain found for network '{network}'."

        embedding = self._embed(f"{network} {reason_code} evidence required")
        domain_hits = self._store.search_chunks(
            embedding, top_k=DOMAIN_CANDIDATE_POOL_SIZE, knowledge_domain=domain
        )
        tier, best = select_domain_chunk(domain_hits, reason_code)
        if not best:
            return f"No specific knowledge-base entry found for {network} {reason_code}."

        if tier == "strong":
            parent_doc = self._store.get_document_by_id(best["document_id"])
            if parent_doc:
                return parent_doc["content"][:4000]
        return best["content"]

    def _build_case_intro(self, merchant_id: str, case_id: str) -> Optional[dict]:
        """
        Called from _validate_node when a merchant's follow-up reply
        ("the first one") resolves to a real case_id — replaces the old
        flat "Help me with case <id>" rewrite with a real, capped
        multi-round tool-calling loop (get_case_details, then
        get_reason_code_info once the reason code is known) so the
        merchant sees a case summary + reason-code context before being
        asked for evidence.

        Verified live before writing this (see the module-level comment
        above get_case_details/get_reason_code_info) that a single round
        can be not enough here — the model doesn't always know
        get_reason_code_info's reason_code argument until it's seen
        get_case_details' result. It ALSO sometimes calls both tools in
        the same round anyway and guesses a reason_code for the second
        one (a real, observed failure — see the fix inside the loop
        below) — the multi-round shape stays, but nothing downstream
        trusts that guess once the real value is known. Capped at 4
        rounds — generous enough for both tools plus one retry, never
        truly unbounded; if the cap is hit without the model settling on
        a tool-call-free answer, one
        final call with no tools bound forces a synthesis so this can
        never return scaffolding-only content.

        Returns:
            {"final_answer": str, "reason_code": str, "card_network": str,
            "case_id": str, "case_intro_action": str, "case_intro_reason": str,
            "case_intro_source": str} or None if case_id doesn't resolve to
            a real row for this merchant — the caller falls through to
            today's existing "Help me with case <id>" rewrite in that case,
            never a dead end.
        """
        messages = [
            SystemMessage(content=(
                "You are a chargeback assistant. The merchant just selected "
                "one of their own open cases to learn more about. First look "
                "up the case's real details, then look up what its reason "
                "code means and what evidence it typically requires. Then "
                "write a short, friendly summary covering: what the case is "
                "(amount, status, deadline), what the reason code means, and "
                "what evidence is needed next. Use only facts returned by "
                "the tools — never invent a status, amount, or evidence "
                "requirement."
            )),
            HumanMessage(content=f"The merchant selected case {case_id}. Tell me about it."),
        ]

        case_row = None
        network, reason_code = "", ""
        final_ai = None

        for _ in range(4):
            ai_msg = self._invoke_with_tools(messages, [get_case_details, get_reason_code_info])
            messages.append(ai_msg)
            if not ai_msg.tool_calls:
                final_ai = ai_msg
                break
            # get_case_details processed first, regardless of the order the
            # model returned them in. Confirmed live this matters: the model
            # doesn't always call the two tools in separate rounds the way
            # the docstring above assumed — it sometimes calls BOTH in the
            # SAME round, and for get_reason_code_info it has no real reason
            # code to give yet, so it guesses one from the case_id string
            # itself (observed: "NPCI20260629M002006" -> reason_code="M002",
            # not a real code at all — NPCI codes are U001-U010). Sorting
            # get_case_details first, within this same round, means
            # `reason_code`/`network` below are already the REAL values by
            # the time get_reason_code_info's branch runs, whichever order
            # the model listed the two calls in.
            ordered_tool_calls = sorted(
                ai_msg.tool_calls, key=lambda tc: tc["name"] != "get_case_details"
            )
            for tc in ordered_tool_calls:
                if tc["name"] == "get_case_details":
                    content, case_row = self._lookup_case_details(
                        merchant_id, tc["args"].get("case_id") or case_id
                    )
                    if case_row:
                        network, reason_code = "RuPay", case_row["reason_code"]
                elif tc["name"] == "get_reason_code_info":
                    # Authoritative value (from get_case_details, this round
                    # or an earlier one) wins over the model's own guessed
                    # argument, not the other way around — the model has no
                    # way to know the real reason code better than the DB
                    # row already fetched, and any disagreement is by
                    # definition the model being wrong. Only falls back to
                    # the model's argument when get_case_details genuinely
                    # hasn't run yet (network/reason_code both still "").
                    content = self._lookup_reason_code_info(
                        network or tc["args"].get("network"),
                        reason_code or tc["args"].get("reason_code"),
                    )
                else:
                    content = ""
                messages.append(ToolMessage(content=content, tool_call_id=tc["id"]))
        else:
            final_ai = self._invoke(messages)

        if case_row is None:
            return None

        # A second, deliberately-accepted redundant analyze_chargeback()
        # call — _lookup_case_details() above already ran one internally to
        # build its tool-message text, but that method's return contract
        # is a plain 2-tuple (content, row) reused elsewhere as a live
        # tool-call executor; threading a third value through it isn't
        # worth it for a call this cheap (pure SQL via cbs.py, no LLM/
        # network I/O). Surfaced here so run() can persist this preview
        # recommendation (case_recommendations.py) even though this whole
        # path never reaches decide_node — see ChargebackState's
        # case_intro_action docstring for why this is evidence-BLIND,
        # not the same signal as decision_node's own decision.
        from chargeback_analysis import analyze_chargeback
        analysis = analyze_chargeback(case_row, db_path="chargebacks.db")

        return {
            "final_answer": (final_ai.content if final_ai else "").strip(),
            "reason_code":  reason_code,
            "card_network": network,
            "case_id":           case_row["case_id"],
            "case_intro_action": analysis.action or "",
            "case_intro_reason": analysis.reason,
            "case_intro_source": analysis.source,
        }

    def _validate_node(self, state: ChargebackState) -> dict:
        """
        Node 0 — Input guardrails + dispute intent check.

        Guardrails applied (in order, cheapest first):
          1. Length check           — no LLM call, immediate
          2. Prompt injection       — no LLM call, immediate
          3. PII masking            — mask before anything downstream sees it
          4. Intent classification  — no LLM call, regex/keyword (classifier.py)
          5. Junk-reply filtering   — regex pre-filter, then an LLM backstop
                                      only for replies the regex didn't
                                      already rule out (see Guard 5 below)

        Reads:  user_query, additional_context
        Writes: is_valid_query, user_query (PII-masked), final_answer,
                additional_context (junk-filtered)

        Args:
            state (ChargebackState): Current graph state.

        Returns:
            dict: is_valid_query, updated user_query, final_answer.
        """
        query = state["user_query"]

        # Guard 1 — length
        length_error = check_length(query, min_len=10, max_len=2000)
        if length_error:
            return {"is_valid_query": False, "final_answer": length_error}

        # Guard 2 — prompt injection
        if detect_prompt_injection(query):
            return {
                "is_valid_query": False,
                "final_answer": "Invalid input detected. Please describe your chargeback dispute.",
            }

        # Guard 3 — PII masking (mask before anything downstream sees it)
        masked_query = mask_pii(query)

        # Preserved separately from masked_query because the continuity
        # block right below may overwrite masked_query entirely (e.g. to
        # just the latest reply's bare text) — losing whatever case/
        # reason-code reference the ORIGINAL pendingQuery carried. Kept
        # around so the anaphoric follow-up fallback further down can
        # re-attach that reference instead of operating on a completely
        # contextless string. See that fallback's comment for the live
        # failure this fixes.
        original_masked_query = masked_query

        # A genuine "talk to a human agent" request in a FOLLOW-UP reply
        # must win outright, regardless of what a stale case-anchored
        # masked_query would otherwise resolve to. Confirmed live: on a
        # case-anchored conversation ("Help me with case NPCI...",
        # needs_more_info=True), classify_query_type() is only ever
        # called on masked_query (Guard 4, further below) — and a named
        # case ALWAYS classifies as "dispute" via _CASE_REF_RE's own
        # precedence, regardless of what the merchant's actual reply
        # said. additional_context does get a second chance via the
        # "invalid -> retry combined" rescue later in this function, but
        # that only fires when masked_query classifies as "invalid" —
        # never "dispute", which a case reference always does. Result:
        # "I have a chargeback and I want to talk to a human agent"
        # typed as a follow-up on an already-resolved U002 case silently
        # fell through the entire evidence -> decide -> generate pipeline
        # and produced a complete rebuttal letter, never once being
        # recognized as an escalation request. Checked here, before any
        # of the case-reference/list-continuity logic below gets a
        # chance to run, using only the LATEST reply segment (matching
        # every other latest-segment check in this function) — an escalation
        # phrase anywhere earlier in a multi-turn blob shouldn't override
        # what the merchant is actually saying right now.
        _raw_context_for_escalation = state.get("additional_context", "")
        if _raw_context_for_escalation:
            _segments = [s.strip() for s in _raw_context_for_escalation.split('\n\n') if s.strip()]
            _latest = _segments[-1] if _segments else _raw_context_for_escalation
            if classifier.classify_query_type(_latest) == "escalation":
                return {
                    "is_valid_query": False,
                    "final_answer":   self._ESCALATION_MESSAGE,
                }

        # Case-list continuity: chat.html always resends the ORIGINAL query
        # as pendingQuery on every follow-up turn (needs_more_info=True
        # keeps the same query in play until the conversation resolves) —
        # so on a genuine follow-up to "show me my open chargebacks", this
        # masked_query is still that same listing request, and
        # additional_context holds whatever the merchant just replied (e.g.
        # "the first one"). Re-derive the list fresh here — cheap,
        # deterministic, always current — rather than trying to remember it
        # from the prior turn, which the checkpointer can't yet do reliably
        # (run() still rebuilds a full blank initial_state on every call;
        # confirmed via a standalone test earlier this session that this
        # overwrites rather than merges with any prior checkpoint). If the
        # merchant's reply resolves to a specific case, rewrite the query to
        # an explicit case reference so classify_query_type() below routes
        # it as a normal dispute — _planner_node's existing step 4b case
        # lookup (merchant_id-scoped) picks it up from there, unchanged.
        #
        # Re-runs the SAME LLM tool-call decision _answer_question_node
        # used to decide turn 1 was a list request in the first place
        # (_resolve_data_lookup_intent, temperature=0 so this reproduces
        # reliably) rather than a regex gate — the regex gate this
        # replaced (classifier.is_case_list_request) was itself part of
        # why "what all u002 cases exist currently?" broke continuity: even
        # after fixing turn 1's rendering, turn 2 would never have resolved,
        # since the pending query wouldn't have matched the regex either.
        # Guarded by the loose, cheap looks_like_data_lookup() pre-filter
        # first so an unrelated follow-up (e.g. mid evidence-gathering)
        # doesn't cost an extra LLM call.
        raw_context_preview = state.get("additional_context", "")
        merchant_id_preview  = state.get("merchant_id", "")

        # Purely derived from raw_context_preview, not incremented/persisted
        # anywhere — see count_clarification_rounds()'s own docstring for
        # why re-deriving this fresh on every call is correct for this
        # project's stateless-per-call client, not a workaround. Read below
        # by three early-return asks and threaded through to ask_user_node
        # via the final return at the bottom of this function.
        clarification_round = classifier.count_clarification_rounds(raw_context_preview)

        # A case named DIRECTLY in a first-turn query ("Help me with case
        # NPCI20260530M002010", "explain more on UTR...") used to fall
        # straight through to the full dispute pipeline
        # (extract_evidence -> decide -> generate), which unconditionally
        # produces a complete fight/refund letter regardless of what was
        # actually asked — jumping straight to a conclusion instead of
        # retrieving the case, explaining the reason code, and evaluating
        # evidence first, the way the ordinal-selection continuity path
        # ("show me my cases" -> "tell me about the first one") already
        # does via _build_case_intro(). Confirmed live this was a real,
        # not cosmetic, gap: identical case, identical merchant, but a
        # completely different (and worse) experience purely because of
        # HOW the case was referenced. Fixed by giving a direct case
        # mention the exact same progressive introduction, on a TRUE
        # first turn only (no additional_context yet) — once the merchant
        # has replied with evidence/a follow-up, chat.html resends this
        # same masked_query with additional_context now set, this check
        # deliberately does not re-fire, and the normal pipeline (still
        # grounded via planner_node's own step 4b lookup) proceeds to a
        # real evidence evaluation and eventual decision instead of
        # repeating the intro forever.
        if not raw_context_preview and merchant_id_preview:
            case_ref_token = classifier.extract_case_reference(masked_query)
            if case_ref_token:
                from merchant_db import get_connection as _get_conn
                conn = _get_conn()
                row = conn.execute(
                    "SELECT case_id FROM chargebacks WHERE merchant_id = ? AND (utr = ? OR case_id = ?)",
                    (merchant_id_preview, case_ref_token, case_ref_token),
                ).fetchone()
                conn.close()
                if row:
                    intro = self._build_case_intro(merchant_id_preview, row["case_id"])
                    if intro:
                        return {
                            "is_valid_query": True,
                            "user_query":     masked_query,
                            "final_answer":   intro["final_answer"],
                            "reason_code":    intro["reason_code"],
                            "card_network":   intro["card_network"],
                            "needs_more_info": True,
                            "confidence_score": 8,
                            "is_grounded":      True,
                            "groundedness_issues": "",
                            # Not gated by MAX_CLARIFICATION_ROUNDS — a case
                            # WAS just resolved, this is forward progress
                            # (moving on to the evidence ask), not a stuck
                            # loop. clarification_reason is still set so
                            # telemetry can see what's being waited on next.
                            "clarification_reason": CLARIFICATION_REASON_MISSING_EVIDENCE,
                            "clarification_round":  clarification_round,
                            # This path returns straight to END, never
                            # reaching planner_node (the node that would
                            # normally set resolved_case_id) — set it here
                            # too, or run() has no case_id to persist
                            # case_intro_action against.
                            "resolved_case_id":  intro["case_id"],
                            "case_intro_action": intro["case_intro_action"],
                            "case_intro_reason": intro["case_intro_reason"],
                            "case_intro_source": intro["case_intro_source"],
                        }
                    # intro build failed (e.g. tool loop never resolved a
                    # row) — fall through to planner_node's step 4b, same
                    # never-a-dead-end guarantee the ordinal-selection path
                    # already relies on.
                # else: no row for this merchant — fall through too;
                # planner_node's step 4b + extract_code_node's
                # case_ref_not_found handling give the accurate
                # "no such case on your account" answer for that case.

        data_lookup_intent = None
        list_intent = None
        # A pendingQuery that ALREADY names one specific case (e.g. "Help
        # me with case NPCI20260530M002010" — itself the result of a
        # prior single-case lookup, not a list-then-select flow) must
        # skip this whole block rather than be handed to
        # _resolve_data_lookup_intent() below. Confirmed live: that LLM
        # tool-call misread exactly this query as a "list my cases"
        # request (its docstring says "use this when the merchant wants
        # to SEE or SELECT a case," which a specific case mention
        # loosely resembles) — list_intent then got set, the merchant's
        # real follow-up ("when was it raised, what's the reason code,
        # what evidence...") didn't look like an ordinal case selection
        # against the resulting list, and the code below fell through to
        # its "abandon and promote the latest reply" branch, discarding
        # the case reference in masked_query entirely and replacing it
        # with the follow-up text alone — which has no case ID, no
        # reason code, and no evidence-gathering context at all.
        if (
            raw_context_preview and merchant_id_preview
            and not classifier.has_case_reference(masked_query)
            and classifier.looks_like_data_lookup(masked_query)
        ):
            intent = self._resolve_data_lookup_intent(merchant_id_preview, masked_query)
            if intent:
                data_lookup_intent = intent
                if intent["type"] == "list":
                    list_intent = intent
        if list_intent is not None:
            shown = self._filtered_open_cases(
                merchant_id_preview, list_intent["reason_code"],
                list_intent.get("active_deadline_only", False),
            )
            resolved = classifier.detect_case_selection(raw_context_preview, shown)
            if resolved:
                # Rich case-intro: a real DB lookup + a real knowledge-base
                # lookup, both as genuine tool calls with maintained
                # AIMessage/ToolMessage history (_build_case_intro), rather
                # than just rewriting the query and falling through to the
                # normal pipeline — which, per a live trace, jumped straight
                # to an evidence question with no case summary or
                # reason-code context shown first. Early-return here mirrors
                # the length-check/prompt-injection guards above: no
                # query_type is set, so _route_after_validate falls through
                # to "end" with final_answer already populated. Falls
                # through to the old rewrite-and-continue behavior if the
                # lookup finds no matching row — never a dead end.
                intro = self._build_case_intro(merchant_id_preview, resolved)
                if intro:
                    # confidence_score/is_grounded: 8/True is the fixed
                    # convention _answer_question_node's own confident,
                    # tool-backed answers use to bypass reflect_node (which
                    # never runs on this early-return path) — not setting
                    # these left the API response defaulting to
                    # confidence_score=0, which reads as a low-confidence
                    # answer in chat.html's UI despite this being a
                    # grounded, real DB+KB-backed response.
                    #
                    # user_query is rewritten to reference the resolved
                    # case here too, matching the FAILURE branch just
                    # below which already does the same — for internal
                    # state consistency (this is what downstream nodes see
                    # if this dict's fields are ever read again within the
                    # same graph run). NOTE: this does NOT by itself fix
                    # cross-turn continuity — confirmed live that
                    # api_server.py never returns user_query in the HTTP
                    # response at all, and chat.html's pendingQuery is set
                    # once from the client's own first message and never
                    # updated from any server response. The actual fix for
                    # "what about the other one?" re-showing the full list
                    # is classifier.looks_like_relative_case_reference(),
                    # wired in below — it asks a clarifying question
                    # instead of relying on any state this project's
                    # stateless-per-call client never round-trips.
                    return {
                        "is_valid_query": True,
                        "user_query":     f"Help me with case {resolved}",
                        "final_answer":   intro["final_answer"],
                        "reason_code":    intro["reason_code"],
                        "card_network":   intro["card_network"],
                        "needs_more_info": True,
                        "confidence_score": 8,
                        "is_grounded":      True,
                        "groundedness_issues": "",
                        # Not gated by MAX_CLARIFICATION_ROUNDS — same
                        # reasoning as the direct-mention branch above: a
                        # case WAS just resolved, this is forward progress.
                        "clarification_reason": CLARIFICATION_REASON_MISSING_EVIDENCE,
                        "clarification_round":  clarification_round,
                        # Same reasoning as the direct-mention branch above:
                        # this path never reaches planner_node, so
                        # resolved_case_id must be set here too.
                        "resolved_case_id":  intro["case_id"],
                        "case_intro_action": intro["case_intro_action"],
                        "case_intro_reason": intro["case_intro_reason"],
                        "case_intro_source": intro["case_intro_source"],
                    }
                masked_query = f"Help me with case {resolved}"
            elif classifier.is_out_of_range_case_reference(raw_context_preview, shown):
                # Confirmed live: "what about third one?" when only 2 cases
                # were ever shown reached the promotion fallback below with
                # bare detect_case_selection()==None — indistinguishable
                # from "not a selection at all" — and got re-enriched with
                # whatever case the ORIGINAL pendingQuery happened to
                # reference, producing a confidently wrong answer ("Case
                # NPCI... is the third open chargeback") instead of telling
                # the merchant plainly that no third case exists. Caught
                # here, before that fallback ever runs, and answered with
                # the real count + the list again rather than guessing.
                case_label = (
                    f"open {list_intent['reason_code']} case(s)"
                    if list_intent["reason_code"] else "open chargeback case(s)"
                )
                if clarification_round >= MAX_CLARIFICATION_ROUNDS:
                    # Repeated out-of-range references, MAX_CLARIFICATION_
                    # ROUNDS worth of back-and-forth already spent — showing
                    # the list a fourth+ time isn't going to land any
                    # better than the first three. Escalate instead.
                    return {
                        "is_valid_query": True,
                        "user_query":     masked_query,
                        "final_answer":   self._CLARIFICATION_LIMIT_MESSAGE,
                        "needs_more_info": False,
                        "confidence_score": 8,
                        "is_grounded":      True,
                        "groundedness_issues": "",
                        "clarification_round": clarification_round,
                    }
                lines = [f"You only have {len(shown)} {case_label} right now — there's no case at that position. Here they are again:\n"]
                for i, c in enumerate(shown, 1):
                    lines.append(
                        f"{i}. {c['case_id']} — RuPay {c['reason_code']} "
                        f"({c['reason_description']}), ₹{c['chargeback_amount']:,.2f}, "
                        f"due {c['response_deadline']}"
                    )
                return {
                    "is_valid_query": True,
                    "user_query":     masked_query,
                    "final_answer":   "\n".join(lines),
                    "needs_more_info": True,
                    "confidence_score": 8,
                    "is_grounded":      True,
                    "groundedness_issues": "",
                    "clarification_reason": CLARIFICATION_REASON_AMBIGUOUS_CASE_REFERENCE,
                    "clarification_round":  clarification_round,
                }
            elif classifier.looks_like_relative_case_reference(raw_context_preview):
                # "What about the other one?" — refers to a specific case
                # RELATIVE to whatever was just discussed, but names no
                # ordinal/number for detect_case_selection() to resolve.
                # Confirmed live: this used to fall straight through to
                # the "abandon and promote" fallback below, which treated
                # the bare text as an unrelated new topic and — since
                # chat.html never round-trips which specific case a PRIOR
                # turn resolved to (nothing here can know "the second
                # one" from two turns ago was NPCI...M002008) — ended up
                # just re-showing the entire case list from scratch, with
                # no acknowledgment the merchant had already picked one.
                # Rather than guess which case "other" means (this
                # project's own state genuinely doesn't have that answer
                # to give), ask — the same "don't silently guess" principle
                # _uncertain() exists for elsewhere in this file.
                if clarification_round >= MAX_CLARIFICATION_ROUNDS:
                    return {
                        "is_valid_query": True,
                        "user_query":     masked_query,
                        **self._uncertain(
                            self._CLARIFICATION_LIMIT_MESSAGE,
                            needs_more_info=False,
                            clarification_round=clarification_round,
                        ),
                    }
                return {
                    "is_valid_query": True,
                    "user_query":     masked_query,
                    **self._uncertain(
                        "Do you mean a different case from the list I just showed? "
                        "Tell me which one (e.g. \"the first one\", \"#2\", or the case ID).",
                        clarification_reason=CLARIFICATION_REASON_AMBIGUOUS_CASE_REFERENCE,
                        clarification_round=clarification_round,
                    ),
                }
            elif not classifier.is_junk_reply(raw_context_preview, query=masked_query):
                # Confirmed live: a genuine new question typed here ("what
                # does U002 mean?", "how much is outstanding this month?")
                # was silently swallowed — since masked_query stayed the
                # stale "show me my open chargebacks" text, re-classifying
                # it just re-showed the identical list instead of answering
                # what was actually asked, with no visible sign anything
                # had gone wrong. A reply that isn't junk and isn't a
                # resolvable case selection is the merchant abandoning this
                # sub-topic for a new one — promote it to be this turn's
                # query so normal classification handles it exactly as if
                # it were a fresh message, the same as chat.html's own
                # client-side looksLikeNewTopic() already does for a
                # narrower set of patterns during evidence-gathering.
                #
                # Promote only the LATEST turn, not the whole (possibly
                # multi-turn) raw_context_preview blob — matching
                # detect_case_selection()'s own latest-segment convention
                # just above. Confirmed live this was a real bug: once a
                # sub-conversation ran three-plus turns deep (e.g. list ->
                # "the first one" -> a genuine new question), an EARLIER
                # segment still sitting in the blob (e.g. "show me my open
                # chargebacks") got promoted right alongside the real new
                # question. _answer_question_node re-runs its own
                # looks_like_data_lookup() check against whatever query it's
                # given, that earlier segment's "chargebacks" text was
                # enough to make it match again, and the tool-calling
                # decision saw a blob literally starting with a listing
                # request — so it re-showed the full case list instead of
                # answering the real, later question.
                segments = [s.strip() for s in raw_context_preview.split('\n\n') if s.strip()]
                latest_segment = segments[-1] if segments else raw_context_preview
                masked_query = mask_pii(latest_segment)
        elif data_lookup_intent is not None:
            # The original query resolved to a non-list data-lookup intent
            # (e.g. "aggregate" — a computed-number question like "how many
            # chargebacks do I currently have?"). There's no list to select
            # a position from, so only the "abandon and promote a genuine
            # new message" repair above applies — but it was never reached
            # for this intent type at all, since it lives inside the
            # list_intent branch. Confirmed live via agent_eval.py: a
            # session that opened with an aggregate question, then asked
            # two different genuine follow-ups ("how much is still open?",
            # "what are my most common reasons?"), got the exact same stale
            # first answer for all three turns — masked_query never
            # changed, so _answer_question_node reprocessed the identical
            # frozen query every time (and its own _list_cache, keyed on
            # query text alone, then reproduced the same cached response on
            # top of that). Same fix as the list branch: promote a
            # non-junk follow-up to be this turn's real query.
            if not classifier.is_junk_reply(raw_context_preview, query=masked_query):
                segments = [s.strip() for s in raw_context_preview.split('\n\n') if s.strip()]
                latest_segment = segments[-1] if segments else raw_context_preview
                masked_query = mask_pii(latest_segment)
        elif raw_context_preview and merchant_id_preview and classifier.has_case_reference(masked_query):
            # masked_query is anchored to one specific case (named
            # directly, or resolved earlier from a list) — but the
            # merchant's LATEST reply might be a genuinely different
            # question about their OWN data in aggregate ("which all
            # chargeback cases are currently open?"), not a reply about
            # THIS case at all. Confirmed live: this fell all the way
            # through to detect_clarification_node/answer_clarification_
            # node instead, whose own prompt says to "lead with" whatever
            # case-specific record sits in retrieved_docs[0] — which is
            # always THIS one case, no matter what was actually asked —
            # so the merchant got the same single case's details again
            # in answer to "which cases are open," with no listing at all.
            #
            # Reuses the same real LLM tool-call decision the list_intent
            # branch above already trusts (_resolve_data_lookup_intent) —
            # pointed at the FOLLOW-UP text specifically, never the stale
            # case-anchored masked_query (misreading THAT is exactly what
            # the has_case_reference guard above exists to prevent). A
            # loose regex check alone isn't safe here: "help me with step
            # by step info about THIS chargeback" (a genuine follow-up on
            # the SAME case, a real bug fixed earlier this session) also
            # contains the word "chargeback" and would wrongly trigger a
            # looser check — the real tool-call correctly distinguishes
            # "explain this one" (calls neither tool) from "show me my
            # other cases" (calls list_merchant_cases/query_chargeback_data).
            segments = [s.strip() for s in raw_context_preview.split('\n\n') if s.strip()]
            latest_segment = segments[-1] if segments else raw_context_preview
            not_same_case_and_not_junk = (
                not classifier.refers_to_current_case(latest_segment)
                and not classifier.is_junk_reply(raw_context_preview, query=masked_query)
            )
            if not not_same_case_and_not_junk:
                # Refers to the anchored case, or is junk filler — fall
                # through unchanged to the normal evidence-gathering flow
                # below, exactly as before any of this branch existed.
                pass
            elif classifier.looks_like_data_lookup(latest_segment):
                # refers_to_current_case() is checked BEFORE the LLM
                # tool-call, not just alongside it — confirmed live the
                # tool-call alone isn't reliable enough here: given
                # exactly this "explain THIS chargeback in detail" text,
                # it returned an intent anyway, which would have
                # re-triggered the exact case-losing bug this whole
                # elif branch was built to avoid fixing a DIFFERENT one.
                new_topic_intent = self._resolve_data_lookup_intent(merchant_id_preview, latest_segment)
                if new_topic_intent:
                    masked_query = mask_pii(latest_segment)
                else:
                    # Loose data-lookup keyword matched, but the real
                    # tool-call decided this ISN'T actually a list/
                    # aggregate request either — genuinely unclear what
                    # it is. Ask rather than silently falling through to
                    # "must be evidence," the same anti-pattern _uncertain()
                    # exists to close off everywhere in this file.
                    anchored_case = classifier.extract_case_reference(masked_query) or "this case"
                    if clarification_round >= MAX_CLARIFICATION_ROUNDS:
                        return {
                            "is_valid_query": True,
                            "user_query":     masked_query,
                            **self._uncertain(
                                self._CLARIFICATION_LIMIT_MESSAGE,
                                needs_more_info=False,
                                clarification_round=clarification_round,
                            ),
                        }
                    return {
                        "is_valid_query": True,
                        "user_query":     masked_query,
                        **self._uncertain(
                            f"I'm not sure if that's about case {anchored_case} or "
                            "something else — could you clarify, or ask your "
                            "question directly and I'll answer it?",
                            clarification_reason=CLARIFICATION_REASON_AMBIGUOUS_CASE_REFERENCE,
                            clarification_round=clarification_round,
                        ),
                    }
            elif classifier.looks_like_new_request(latest_segment):
                # Not data-lookup-shaped, but still clearly a fresh
                # imperative ask ("help me with all open questions"),
                # not an evidence answer for the anchored case at all.
                # Confirmed live: this phrasing matches NONE of the
                # other checks in this branch (no "case"/"chargeback"/
                # "dispute" keyword for looks_like_data_lookup, no
                # demonstrative reference, not an escalation phrase
                # either — that's checked separately, earlier in this
                # function) — so it fell all the way through to being
                # silently treated as evidence, and since this case's
                # ledger_decision was already set, extract_evidence_node
                # short-circuits straight past evidence-gathering
                # regardless of content, producing a complete rebuttal
                # letter for a message that never asked for one.
                # Promoted directly, no LLM confirmation needed — an
                # imperative opener is unambiguous enough on its own,
                # the same reasoning as refers_to_current_case()'s veto
                # just above needing no LLM confirmation either.
                masked_query = mask_pii(latest_segment)
            # else: no known pattern matched at all — deliberately falls
            # through unchanged to the normal evidence-gathering flow
            # below, same as before this branch existed. Tried an
            # unconditional "ask for clarification" catch-all here first
            # and reverted it live: it also caught genuine evidence
            # answers with no reason to be suspicious ("Yes, we confirmed
            # only one credit was issued for this transaction" matches
            # none of looks_like_data_lookup/looks_like_new_request/
            # refers_to_current_case either — it says "this transaction,"
            # not "this case"/"this chargeback" — so a blanket "ask when
            # nothing matches" rule asked for clarification INSTEAD OF
            # extracting real evidence that was right there, breaking the
            # single most common follow-up shape in this whole flow).
            # Evidence text is inherently unrecognizable by a positive
            # pattern — it's free-form "here's what I have," not a fixed
            # phrase — so there's no safe way to distinguish "confusingly
            # phrased evidence" from "genuinely unrelated message" without
            # more signal than a keyword/demonstrative check can give. The
            # narrower asks above (data-lookup keyword matched but the
            # LLM said no; an unambiguous imperative opener) stay, because
            # each already has a real, specific reason to be suspicious —
            # this bare fallback didn't.

        # Guard 4 — deterministic intent classification (no LLM call)
        query_type = classifier.classify_query_type(masked_query)

        # Guard 5 — junk-reply filtering. additional_context is a merchant's
        # follow-up answer to a question like "please share the reason code
        # or describe what happened" — until this check existed, ANY
        # non-empty reply (including "nice", "ok", "mad", or mashed-keyboard
        # gibberish) satisfied every downstream "not context" routing check
        # identically to a real answer, letting the flow proceed straight to
        # a confident generate step grounded in nothing. Normalized to ""
        # here, once, so every downstream node/route (_route_after_extract_code,
        # _route_after_detect_settlement, _extract_evidence_node's one-round
        # cap, etc.) treats a junk reply exactly like no reply at all,
        # without each needing its own check.
        # Masked immediately on read, same as user_query above — this is the
        # field a merchant is most likely to paste sensitive detail into
        # when asked "please provide evidence," and everything downstream
        # (junk-reply filter, clarifying-question check, every node that
        # reads state["additional_context"]) only ever sees the masked
        # value once it's applied here, once.
        raw_context = mask_pii(state.get("additional_context", ""))

        # A genuine clarifying question ("what is authorization evidence?")
        # is neither a real answer nor junk/filler — it's a third category
        # the checks below were never designed to recognize, and both were
        # confirmed live to misjudge one as "not substantive" and silently
        # discard it before _detect_clarification_node (which exists
        # specifically to handle this case, routing to
        # _answer_clarification_node) ever saw it — the merchant's question
        # vanished and the flow proceeded as if no reply had been given at
        # all. Checked first and treated as authoritative: a question is
        # never junk, full stop, so it skips both the regex filter and the
        # LLM backstop entirely rather than trusting either to also learn
        # this distinction.
        if classifier.is_clarifying_question(raw_context):
            context = raw_context
        else:
            # Guard 5 — junk-reply filtering. additional_context is a
            # merchant's follow-up answer to a question like "please share
            # the reason code or describe what happened" — until this check
            # existed, ANY non-empty reply (including "nice", "ok", "mad",
            # or mashed-keyboard gibberish) satisfied every downstream "not
            # context" routing check identically to a real answer, letting
            # the flow proceed straight to a confident generate step
            # grounded in nothing. Normalized to "" here, once, so every
            # downstream node/route (_route_after_extract_code,
            # _route_after_detect_settlement, _extract_evidence_node's
            # one-round cap, etc.) treats a junk reply exactly like no reply
            # at all, without each needing its own check.
            context = (
                "" if classifier.is_junk_reply(raw_context, query=masked_query)
                else raw_context
            )

            # Guard 5b — LLM backstop for whatever escapes the regex filter
            # above. "Is this reply actually informative" is an open-ended
            # judgment call — every adversarial round so far ("nice"/"ok"/"mad",
            # mashed-keyboard gibberish, retyping the original query once, then
            # retyping it multiple times) found a pattern the regex layer didn't
            # cover yet. Rather than keep enumerating patterns by hand, ask the
            # LLM once the cheap layer has already ruled out the obvious cases —
            # mirrors decision_rules.py's curated-table-first, LLM-fallback-for-
            # the-long-tail pattern. Skipped entirely when the regex layer is
            # already confident (is_confidently_substantive) — the LLM call was
            # observed to be flaky specifically on short, bare single-word
            # answers like "fraud", so those bypass it rather than risk a
            # coin-flip rejection of exactly the terse answer the follow-up
            # question invites.
            if context and not classifier.is_confidently_substantive(context):
                context = self._filter_substantive_context(masked_query, context)

        # Anaphoric follow-up fallback: a bare reference ("Are all of those
        # covered?", "What's the difference between those two?") carries no
        # payment-domain keyword of its own and classifies as "invalid" in
        # isolation — but on a genuine second turn, additional_context holds
        # the prior turn's question, which usually does. Retry classification
        # against query+context combined before giving up, so a real
        # follow-up isn't rejected purely because THIS turn's text alone is
        # context-free. Only rescues an "invalid" result — never overrides a
        # query that already classified as something else on its own, and
        # never fires on a genuine first turn (additional_context is always
        # empty there). Confirmed via live 2-turn test: without this,
        # "Are all of those covered?" was rejected even with the correct
        # prior-turn context already attached.
        # Confirmed live this rescue was incomplete: it fixed the
        # classification verdict but not what actually gets answered.
        # "what documentation is required for this?" (bare) is "invalid"
        # in isolation, correctly flips to "question" once combined with
        # context — but state["user_query"] stayed the bare text, so
        # _answer_question_node ran with zero case/reason-code reference,
        # its KB search matched a generic Visa/Mastercard/Amex/Discover
        # "retrieval request" document, and it answered confidently from
        # the wrong network entirely.
        #
        # Fix: when the rescue succeeds, also rewrite masked_query itself
        # to carry the recovered topic — using original_masked_query (the
        # untouched pendingQuery text, which may hold the real case/
        # reason-code reference the continuity block above already
        # discarded) plus only the LATEST segment of context, not the
        # full multi-turn blob. Using the full blob here would risk
        # reintroducing the case-list misrouting bug fixed earlier this
        # session: an earlier stale segment (e.g. "show me my open
        # chargebacks") would make _answer_question_node's own
        # looks_like_data_lookup() check fire again and re-trigger the
        # listing tool instead of answering the real question.
        if query_type == "invalid" and context:
            segments = [s.strip() for s in context.split('\n\n') if s.strip()]
            latest_context_segment = segments[-1] if segments else context
            combined = f"{original_masked_query} {latest_context_segment}"
            retried_type = classifier.classify_query_type(combined)
            if retried_type != "invalid":
                query_type = retried_type
                masked_query = combined

        is_valid   = query_type not in ("invalid", "escalation")

        # Build the rejection / escalation message
        if query_type == "escalation":
            final_answer = self._ESCALATION_MESSAGE
        elif query_type == "invalid":
            final_answer = (
                "Please describe a chargeback dispute — for example: "
                "'I received a Visa chargeback for $300, the customer claims "
                "they never received the order but I have delivery confirmation.'"
            )
        else:
            final_answer = ""

        return {
            "is_valid_query":    is_valid,
            "query_type":        query_type,
            "user_query":        masked_query,
            "final_answer":      final_answer,
            "additional_context": context,
            # Threaded through so ask_user_node can enforce
            # MAX_CLARIFICATION_ROUNDS for the rest of the main pipeline
            # (detect_settlement/extract_code/extract_evidence) — the same
            # cap already enforced inline above for the early-return asks
            # that bypass ask_user_node entirely.
            "clarification_round": clarification_round,
        }

    def _planner_node(self, state: ChargebackState) -> dict:
        """
        Node 1b — Deterministic retrieval + regex-based network/code extraction.

        Replaces the old tool-calling LLM loop (up to 4 LLM calls) with:
          1. Regex extraction of card_network / reason_code — 0 LLM calls.
          2. Hybrid vector+BM25 search — 0 LLM calls.
          3. Targeted payload-filtered search if code is known — 0 LLM calls.
          4. Merchant history lookup for RuPay disputes only — 0 LLM calls (SQL).
          5. LLM fallback ONLY when regex found neither network nor code — 1 call.

        Reads:  user_query, merchant_id
        Writes: card_network, reason_code, retrieved_docs, retrieval_status,
                retrieval_issues
        """
        query       = state["user_query"]
        merchant_id = state.get("merchant_id", "")
        case_ref_not_found = ""
        ledger_decision = ""
        ledger_decision_reason = ""
        ledger_no_decision_reason = ""
        resolved_case_id = ""
        resolved_utr = ""

        # 1. Deterministic code extraction — covers the majority of disputes
        network, code = classifier.extract_network_and_code(query)
        payload_networks = _NETWORK_PAYLOAD_SPELLINGS.get(network, [network])

        # 2. Broad hybrid search (no LLM needed to decide what to retrieve)
        embedding = self._embed(query)
        results   = self._store.hybrid_search(query, embedding, top_k=5)

        # Diversity: one result per document
        seen, diverse = set(), []
        for r in results:
            if r["id"] not in seen:
                seen.add(r["id"])
                diverse.append(r)
            if len(diverse) == 5:
                break

        # Retrieval-sufficiency check — does `diverse` actually look
        # applicable to the network just detected, or merely semantically
        # similar to it? Deliberately run on `diverse` (the STRUCTURED
        # results, still carrying their own `network` payload field)
        # before the next line flattens them to bare content strings that
        # carry no metadata at all. Signal only for now — nothing below
        # this reads or routes on it yet; see retrieval_evaluator.py's own
        # module docstring for why that's a deliberate, separate next step.
        assessment = retrieval_evaluator.evaluate_retrieval(payload_networks, diverse)

        retrieved_contents = [r["content"] for r in diverse]
        existing_set       = set(retrieved_contents)

        # 3. Targeted supplemental retrieval when code is known
        if code != "Unknown" and network != "Unknown":
            # Try every known real spelling for this network (see
            # _NETWORK_PAYLOAD_SPELLINGS) — the index is genuinely split
            # across more than one for RuPay/Amex, not just one to guess.
            targeted = []
            for payload_network in payload_networks:
                targeted = self._store.filter_by_payload(
                    {"network": payload_network, "reason_code": code}, limit=3
                )
                if targeted:
                    break
            if not targeted:
                focused_q = f"{network} {code} {query}"
                emb2      = self._embed(focused_q)
                targeted  = self._store.hybrid_search(focused_q, emb2, top_k=3)
            for r in targeted:
                if r["content"] not in existing_set:
                    retrieved_contents.append(r["content"])
                    existing_set.add(r["content"])

        # 4. Merchant history — RuPay/UPI disputes only (NL→SQL, no LLM)
        if merchant_id and network == "RuPay":
            try:
                from text_to_sql import query_chargebacks
                result = query_chargebacks(question=query, role="merchant", merchant_id=merchant_id)
                answer = result.get("answer", "")
                if answer:
                    retrieved_contents.append(f"Merchant history: {answer}")
            except Exception:
                pass

        # 4b. Specific case reference — if the merchant names an exact UTR or
        # case_id (e.g. "explain more on UTR20260802M002359516"), ground the
        # response in the same CBS + decision_rules analysis
        # auto_decision_poller.py / suggestion_poller.py already use, instead
        # of making the merchant repeat the question in the SQL query tool
        # (which can't narrate — "explain" is a conversational trigger there)
        # or wait for the next poller run. Scoped to merchant_id so a
        # merchant can't probe another merchant's case by guessing its ID —
        # same defense-in-depth pattern used everywhere else in this project.
        case_ref = re.search(r"\b(UTR\w+|NPCI\w+)\b", query, re.IGNORECASE)
        if case_ref and merchant_id:
            try:
                from chargeback_analysis import analyze_chargeback
                from merchant_db import get_connection

                conn = get_connection()
                row = conn.execute(
                    "SELECT * FROM chargebacks WHERE merchant_id = ? AND (utr = ? OR case_id = ?)",
                    (merchant_id, case_ref.group(1), case_ref.group(1)),
                ).fetchone()
                conn.close()

                if row:
                    # Set network/code directly from the real row instead of
                    # leaving them "Unknown" for step 5's LLM fallback to
                    # guess at — this schema is always RuPay by construction
                    # (see merchant_db.NPCI_REASON_CODES), and the exact
                    # reason_code is right here, not something to infer from
                    # free text. Without this, a query like "explain more on
                    # UTR..." (no reason-code keyword in the text itself)
                    # left both Unknown, triggering the "please provide a
                    # reason code" ask-user branch even though the case was
                    # already found and fully analyzed.
                    network = "RuPay"
                    code    = row["reason_code"]
                    resolved_case_id = row["case_id"]
                    resolved_utr     = row["utr"]

                    analysis = analyze_chargeback(row, db_path="chargebacks.db")
                    status_line = (
                        f"Current status: {row['status']}, "
                        f"resolution: {row['resolution'] or 'not yet resolved'}."
                    )
                    # insert(0, ...), not append(): downstream nodes only
                    # look at the first 1-2 retrieved_docs entries
                    # (_extract_evidence_node uses [:2], _decide_node's LLM
                    # fallback uses [:1] — see those nodes) to keep prompts
                    # small. This case's own DB-backed analysis is the single
                    # most relevant thing in retrieved_docs for THIS dispute
                    # — more so than any generic semantic-search hit — so it
                    # must survive that truncation. Appending put it after
                    # up to 8 generic hits from steps 2-3 above, meaning it
                    # was silently invisible to both of those nodes: the
                    # agent had already determined "Accept, no evidence can
                    # help" here, but asked the merchant for evidence anyway
                    # because neither node ever saw that determination.
                    if analysis.action:
                        retrieved_contents.insert(0,
                            f"Case {row['case_id']} ({row['utr']}), reason code "
                            f"{row['reason_code']} ({row['reason_description']}): "
                            f"recommended action = {analysis.action}. {analysis.reason} "
                            f"{status_line}"
                        )
                        # Authoritative, not just a hint for the LLM steps
                        # below to notice — see ChargebackState's own
                        # docstring for why extract_evidence_node/decide_node
                        # must short-circuit on this deterministically rather
                        # than rely on the LLM correctly re-deriving it from
                        # retrieved_docs text (observed flaky live: the exact
                        # RuPay U002 case this covers still asked the
                        # merchant to "confirm only one credit was issued"
                        # even with this analysis already inserted at [0]).
                        ledger_decision = analysis.action
                        ledger_decision_reason = analysis.reason
                    elif analysis.source in ("cbs", "ledger"):
                        # A real bank-side blocker (pending ledger entry, or
                        # a settlement reconciliation mismatch), not simply
                        # "no rule for this code." Equally authoritative as
                        # the analysis.action branch above — no amount of
                        # merchant-supplied evidence resolves a pending
                        # ledger entry or a settlement mismatch, so this
                        # must bypass extract_evidence_node's generic
                        # evidence ask the same way, not just the retrieved
                        # ledger text.
                        retrieved_contents.insert(0,
                            f"Case {row['case_id']} ({row['utr']}), reason code "
                            f"{row['reason_code']} ({row['reason_description']}): "
                            f"{analysis.reason} {status_line}"
                        )
                        ledger_no_decision_reason = (
                            f"{analysis.reason} {status_line}"
                        )
                    else:
                        retrieved_contents.insert(0,
                            f"Case {row['case_id']} ({row['utr']}), reason code "
                            f"{row['reason_code']} ({row['reason_description']}): "
                            f"no automated recommendation available for this reason "
                            f"code without more evidence. {status_line}"
                        )
                else:
                    # Matched a UTR/case_id-shaped token, but no row for THIS
                    # merchant — either a typo, or (just as likely, given the
                    # SQL scopes by merchant_id) a real case belonging to a
                    # different merchant. Recorded so extract_code_node can
                    # give an accurate answer instead of silently treating
                    # this as a brand-new, code-less dispute report — see
                    # extract_code_node for why that silent fallthrough was
                    # a real bug, not just a UX nicety.
                    case_ref_not_found = case_ref.group(1)
            except Exception:
                pass

        # 5. LLM fallback — only when regex found nothing at all
        if network == "Unknown" and code == "Unknown":
            doc_hints = "\n---\n".join(c[:200] for c in retrieved_contents[:3])
            response  = self._invoke([
                SystemMessage(content=(
                    "Extract the card network and reason code from this dispute.\n"
                    "Respond ONLY with JSON: "
                    "{\"card_network\": \"Visa\", \"reason_code\": \"13.1\"}\n"
                    "Use 'Unknown' if you cannot determine either value.\n\n"
                    f"Retrieved document excerpts:\n{doc_hints}"
                )),
                HumanMessage(content=query[:500]),
            ])
            data    = _parse_json_safe(
                response.content,
                {"card_network": "Unknown", "reason_code": "Unknown"},
            )
            network = data.get("card_network", "Unknown")
            code    = data.get("reason_code",  "Unknown")

        return {
            "card_network":       network,
            "reason_code":        code,
            "retrieved_docs":     retrieved_contents,
            "retrieval_status":   assessment.status,
            "retrieval_issues":   "; ".join(assessment.issues),
            "case_ref_not_found": case_ref_not_found,
            "ledger_decision":           ledger_decision,
            "ledger_decision_reason":    ledger_decision_reason,
            "ledger_no_decision_reason": ledger_no_decision_reason,
            "resolved_case_id":          resolved_case_id,
            "resolved_utr":              resolved_utr,
        }

    def _detect_settlement_node(self, state: ChargebackState) -> dict:
        """
        Node 3a — Is this a settlement failure rather than a chargeback?

        Single responsibility: keyword-check the original query and write the
        result. Pre-populates missing_info_question with the static settlement
        question so ask_user can display it if the router sends it there.

        Reads:  user_query
        Writes: is_settlement_issue, missing_info_question
        """
        is_settlement = classifier.detect_settlement_issue(state["user_query"])
        return {
            "is_settlement_issue": is_settlement,
            "missing_info_question": (
                "Before I can advise you, one critical question:\n\n"
                "Was the customer's card actually charged? "
                "Check your payment processor dashboard or statement.\n\n"
                "A) Yes — the customer was charged, but the funds never reached my account.\n\n"
                "B) No — the transaction appears to have failed at the bank or processor level. "
                "The customer may not have been charged at all.\n\n"
                "C) I am not sure — I cannot verify this right now.\n\n"
                "The answer changes everything: if the customer was not charged, there is no "
                "valid chargeback and you should ask them to retry payment. "
                "If they were charged, your recourse is against your payment processor — "
                "but whether to fight or accept any chargeback depends on whether you "
                "delivered the goods."
            ) if is_settlement else "",
            "clarification_reason": CLARIFICATION_REASON_SETTLEMENT_AMBIGUITY if is_settlement else "",
        }

    def _extract_code_node(self, state: ChargebackState) -> dict:
        """
        Node 3b — Do we know the card network and reason code?

        Single responsibility: supplement the planner's regex extraction with
        additional_context (the merchant's second-turn reply). Pre-populates
        missing_info_question with the static "please share the reason code"
        text if the code remains unknown and no context was provided — unless
        planner_node flagged that the merchant actually named a specific
        case reference that didn't resolve to their own account, in which
        case that takes priority: telling them "I need a reason code" is
        actively misleading when what actually happened is "that case ID
        isn't on your account" — a merchant reading the generic question
        has no way to tell those two situations apart, and would reasonably
        assume the system just failed to notice the case ID they gave.

        Reads:  reason_code, card_network, additional_context, case_ref_not_found
        Writes: reason_code, card_network, missing_info_question
        """
        reason_code  = state.get("reason_code",  "Unknown") or "Unknown"
        card_network = state.get("card_network", "Unknown") or "Unknown"
        context      = state.get("additional_context", "")
        not_found_id = state.get("case_ref_not_found", "")

        if reason_code == "Unknown" and context:
            n, c = classifier.extract_network_and_code(context)
            if c != "Unknown":
                reason_code, card_network = c, n
            elif n != "Unknown":
                card_network = n

        clarification_reason = ""
        if reason_code != "Unknown" or context:
            missing_info_question = ""
        elif not_found_id:
            missing_info_question = (
                f"I couldn't find a case matching '{not_found_id}' on your account. "
                "Please double-check the case ID, or ask me to list your open "
                "chargebacks and pick one from there."
            )
            clarification_reason = CLARIFICATION_REASON_AMBIGUOUS_CASE_REFERENCE
        else:
            missing_info_question = (
                "I still need one key detail to help you.\n\n"
                "Did a customer file a chargeback against you — meaning your bank "
                "sent you a chargeback notification and reversed funds from your account?\n\n"
                "If yes: please share the reason code or reason written on the "
                "chargeback notification (e.g. 'Visa 13.1', 'item not received', "
                "'fraud', '4853'). This tells us what the customer claimed and "
                "determines how to respond.\n\n"
                "If your balance dropped for a different reason (fees, a refund you "
                "issued, a processor deduction) — describe what happened and I can "
                "advise accordingly."
            )
            clarification_reason = CLARIFICATION_REASON_MISSING_REASON_CODE

        return {
            "reason_code":            reason_code,
            "card_network":           card_network,
            "missing_info_question":  missing_info_question,
            "clarification_reason":   clarification_reason,
        }

    def _detect_clarification_node(self, state: ChargebackState) -> dict:
        """
        Node 3c — Is the merchant's latest reply a question?

        Single responsibility: heuristic detection only, no LLM call.
        If yes, _answer_clarification_node answers it.
        If no, _extract_evidence_node extracts evidence tags.

        Delegates to classifier.is_clarifying_question() — the same check
        _validate_node uses to exempt a genuine clarifying question from
        the junk-reply/substantive-context filters, so the two can't drift
        on what counts as "the merchant is asking a question."

        On a FIRST turn (no additional_context yet), also checks the
        original user_query itself — but only when planner_node already
        resolved it to one specific, real case (resolved_case_id set).
        Without this, a first message like "What exactly happened?" or
        "Did you receive my evidence?" naming a real case ID never had any
        chance of being recognized as a question at all — this check only
        ever looked at additional_context, a SECOND-turn reply — so it ran
        straight through extract_evidence -> decide -> generate and got a
        generic rebuttal/refund letter instead of an actual answer.
        Confirmed live via agent_eval.py. Scoped to only fire when a real
        case was already resolved (not any first message) so a genuine new
        dispute description that happens to contain a question word isn't
        misrouted away from the normal evidence-gathering flow.

        Reads:  additional_context, user_query, resolved_case_id
        Writes: merchant_is_asking_question
        """
        context = state.get("additional_context", "")
        if not context and state.get("resolved_case_id"):
            return {"merchant_is_asking_question": classifier.is_clarifying_question(state.get("user_query", ""))}
        return {"merchant_is_asking_question": classifier.is_clarifying_question(context)}

    def _answer_clarification_node(self, state: ChargebackState) -> dict:
        """
        Node 3d — Answer the merchant's question, grounding in case-specific
        facts first when available, before falling back to generic policy
        guidance.

        Single responsibility: one LLM call that answers the merchant's LATEST
        question using retrieved docs. Router always sends the result to
        ask_user so the merchant can read the answer and reply with evidence.

        retrieved_docs[0] can be a case-specific fact string inserted by
        _planner_node's step 4b (e.g. "Case NPCI... : recommended action =
        refund. No proof on file that only one valid transaction occurred...
        Current status: Open...") when the merchant's query named a real
        case/UTR. Found live: with the old prompt ("answer practically —
        which dashboard/report/party holds that data"), the LLM defaulted to
        generic "go check your bank statement" procedural advice even when
        this exact case's real status/recommendation was sitting right there
        in the prompt — e.g. "can you check my transaction data and tell me
        if two amounts were credited?" got zero mention of the system's own
        on-file status, despite it being retrieved_docs[0] verbatim. Fixed by
        explicitly instructing the LLM to check for and lead with
        case-specific facts before falling back to procedural guidance for
        whatever those facts don't cover — and to say plainly when something
        asked isn't covered by what's on file, rather than answering as if
        it had been checked.

        Reads:  user_query, additional_context, reason_code, card_network,
                retrieved_docs
        Writes: missing_info_question
        """
        context      = state.get("additional_context", "")
        reason_code  = state.get("reason_code",  "Unknown")
        card_network = state.get("card_network", "Unknown")
        docs_text    = "\n\n".join(state.get("retrieved_docs", [])[:2])

        segments = [s.strip() for s in context.split("\n\n") if s.strip()]
        # Falls back to user_query itself when there's no additional_context
        # at all — the first-turn case detect_clarification_node now also
        # recognizes (see that node's docstring): the merchant's actual
        # question IS the original query, not a follow-up reply to one.
        latest   = segments[-1] if segments else (context or state.get("user_query", ""))

        # The closing reminder must point at whatever is ACTUALLY still
        # missing, not a hardcoded "come back with evidence" regardless of
        # stage. Confirmed live this was wrong: a merchant who asked "what
        # is a reason code?" before ever providing one — reason_code was
        # still "Unknown" — got told "please come back with the actual
        # evidence once you have it." The real blocker was the reason
        # code itself; there was no evidence stage to come back to yet,
        # and nothing tracked the ORIGINAL pending question once this
        # node's own answer overwrote missing_info_question. Reuses the
        # same deterministic signals extract_code_node/decide_node already
        # use to know what's actually missing, rather than leaving the
        # LLM to guess a generic closing line from context alone.
        if reason_code == "Unknown" or card_network == "Unknown":
            closing_instruction = (
                "End with one short sentence asking them to share the chargeback "
                "reason code (e.g. 'Visa 13.1', 'RuPay U002') so you can continue — "
                "that is the actual next thing needed, not evidence."
            )
        elif state.get("ledger_decision"):
            closing_instruction = (
                "Do NOT ask for evidence — this case's outcome is already "
                "determined from the bank's own ledger records, not merchant-"
                "supplied evidence. End with one short sentence letting them "
                "know you already have what's needed for this case."
            )
        else:
            closing_instruction = (
                "End with one short sentence reminding them to come back with the "
                "actual evidence once they have it."
            )

        response = self._invoke([
            SystemMessage(content=(
                "You are a chargeback evidence analyst. The merchant is asking a "
                "clarifying QUESTION about their dispute — they have NOT yet "
                "provided the evidence itself.\n"
                "First check whether the 'Relevant context' below includes a "
                "case-specific record (a line starting with \"Case <id>\" — the "
                "system's own on-file status/recommendation for this exact "
                "dispute) that answers or partially answers their question. If "
                "so, lead with those specific facts by name (status, recommended "
                "action, what evidence is or isn't on file) — the merchant is "
                "often asking you to check something the system already knows, "
                "not asking how to look it up themselves.\n"
                "Only fall back to generic procedural guidance (which dashboard, "
                "report, or party holds that data) for whatever the case record "
                "does NOT cover. Never imply you checked something the record "
                "doesn't actually contain — if what they're asking is outside "
                "what's on file (e.g. no full transaction ledger exists to "
                "verify a duplicate charge from the payment side), say that "
                "plainly rather than answering as if you looked it up.\n"
                f"{closing_instruction}\n"
                "Respond ONLY with JSON: {\"answer\": \"...\"}"
            )),
            HumanMessage(content=(
                f"Dispute: {state['user_query']}\n"
                f"Earlier conversation: {context}\n"
                f"Merchant's LATEST question: {latest}\n"
                f"Reason code: {card_network} {reason_code}\n\n"
                f"Relevant context:\n{docs_text}"
            )),
        ])
        answer = _parse_json_safe(response.content, {"answer": ""}).get("answer", "").strip()
        return {"missing_info_question": answer or latest}

    def _extract_evidence_node(self, state: ChargebackState) -> dict:
        """
        Node 3e — What evidence does the merchant have / still need?

        Single responsibility: map the merchant's free-text description to the
        closed EvidenceTag vocabulary. Sets needs_more_info=True only when a
        critical tag is completely absent (routing is handled by the edge
        function, not inside this node).

        Reads:  user_query, additional_context, reason_code, card_network,
                retrieved_docs, ledger_decision
        Writes: evidence_present, evidence_missing, needs_more_info,
                missing_info_question
        """
        # planner_node already got a confident, bank-evidence-backed decision
        # for this exact case (CBS refund record, or U002 ledger/settlement
        # reconciliation) — skip the merchant-evidence gathering entirely
        # rather than asking them to "confirm" a fact the bank's own records
        # already settled. decide_node uses ledger_decision directly, so no
        # evidence_present/missing is needed downstream either.
        if state.get("ledger_decision"):
            return {
                "evidence_present":      [],
                "evidence_missing":      [],
                "needs_more_info":       False,
                "missing_info_question": "",
            }

        # A real bank-side blocker (pending entry / reconciliation mismatch)
        # already explains why no recommendation can be made yet — surface
        # that directly rather than asking the merchant for evidence that
        # was never the actual blocker.
        no_decision_reason = state.get("ledger_no_decision_reason", "")
        if no_decision_reason:
            return {
                "evidence_present":      [],
                "evidence_missing":      [],
                "needs_more_info":       True,
                "missing_info_question": no_decision_reason,
            }

        docs_text    = "\n\n".join(state.get("retrieved_docs", [])[:2])
        context      = state.get("additional_context", "")
        reason_code  = state.get("reason_code",  "Unknown")
        card_network = state.get("card_network", "Unknown")

        # Looked up BEFORE the LLM call (not just after, as before) — when a
        # deterministic rule exists, it tells us exactly which of the ~30
        # tags in EVIDENCE_TAG_LABELS are actually relevant to this reason
        # code, which the LLM can be given directly instead of guessing from
        # tag names alone against the full flat list. Confirmed live this
        # was needed: for RuPay U002, a clear but terse merchant answer ("i
        # checked i was credited only once") wasn't being recognized as
        # single_credit_confirmed at all — evidence_present came back empty
        # even though the rule already fully specifies that single-vs-
        # duplicate credit is the only evidence category that matters here.
        rule = decision_rules.RULES.get((card_network, reason_code))
        if rule is None and reason_code == "4853":
            subtype = decision_rules._detect_mc_4853_subtype(
                f"{state.get('user_query', '')} {context}"
            )
            if subtype:
                rule = decision_rules.RULES.get((card_network, f"4853#{subtype}"))

        rule_guidance = ""
        if rule is not None:
            relevant_tags = sorted(set(rule.required_any) | set(rule.required_all))
            if relevant_tags:
                labeled = "; ".join(f"{t} ({EVIDENCE_TAG_LABELS.get(t, t)})" for t in relevant_tags)
                rule_guidance = (
                    "\n\nFor this specific reason code, ONLY these evidence tags "
                    "actually matter — check the merchant's text carefully for "
                    "anything matching them, even a short or informal statement "
                    "(e.g. 'we checked and only one credit was received', 'yes, "
                    "just the one payment went through' both count as "
                    f"single_credit_confirmed): {labeled}"
                )

        response = self._invoke([
            SystemMessage(content=(
                "You are a chargeback evidence analyst.\n"
                "Based on the dispute and policy, identify evidence present and missing.\n\n"
                "IMPORTANT RULES for needs_more_info:\n"
                "  Set needs_more_info=TRUE only when ALL of these apply:\n"
                "    1. A piece of CRITICAL evidence is completely absent\n"
                "    2. Without it, a representment cannot possibly succeed\n"
                "    3. The merchant has provided fewer than 3 pieces of evidence\n"
                "  Set needs_more_info=FALSE when:\n"
                "    - The merchant has provided 3 or more evidence items, OR\n"
                "    - Delivery proof OR authorization proof is confirmed\n\n"
                "Critical evidence (reason to ask):\n"
                "  - Zero proof of delivery for physical goods disputes\n"
                "  - Zero proof of authorization for fraud disputes\n"
                "Nice-to-have (do NOT ask for these):\n"
                "  - Type of goods, cardholder communication, order date\n\n"
                "evidence_present and evidence_missing MUST use ONLY these tags:\n"
                f"  {', '.join(EVIDENCE_TAG_LABELS.keys())}"
                f"{rule_guidance}\n\n"
                "Respond ONLY with JSON:\n"
                '{"evidence_present": ["tag", "..."], "evidence_missing": ["tag", "..."],\n'
                ' "needs_more_info": false, "missing_info_question": ""}'
            )),
            HumanMessage(content=(
                f"Dispute: {state['user_query']}\n"
                + (f"Additional context: {context}\n" if context else "")
                + f"Reason code: {card_network} {reason_code}\n\n"
                f"Relevant policy:\n{docs_text}"
            )),
        ])

        # needs_more_info=True on parse failure, not False — a genuinely
        # failed LLM response used to silently mean "no evidence needed,
        # proceed to a decision," letting an incomplete case reach
        # decide_node with empty evidence_present/missing and no one ever
        # having actually asked. See _uncertain()'s own docstring for the
        # other two places this exact anti-pattern lived in this file.
        # Only bites on a genuine parse failure — the surrounding
        # "one evidence round max" cap a few lines below (needs_more_info
        # = ... and not context) still suppresses this on a later turn,
        # same as it already does for the LLM's own (successfully parsed)
        # needs_more_info field.
        fallback = {
            "evidence_present": [], "evidence_missing": [],
            "needs_more_info": True,
            "missing_info_question": (
                "I wasn't able to process that clearly — could you describe "
                "what evidence you have for this dispute?"
            ),
        }
        data = _parse_json_safe(response.content, fallback)

        evidence_present = data.get("evidence_present", [])

        # Replace the LLM's evidence_missing with only the tags the rule
        # actually requires — prevents the LLM from flagging irrelevant tags
        # (e.g. AVS/CVV/3DS as "missing" on a 4870 chip dispute where only
        # emv_chip_data matters).
        if rule is not None:
            required = set(rule.required_any) | set(rule.required_all)
            present_set = set(evidence_present)
            evidence_missing = [t for t in required if t not in present_set]
            # Whether the rule's own required_any is satisfied by what's
            # present so far — used below to force needs_more_info=True
            # deterministically rather than trusting the LLM's own guess.
            rule_evidence_satisfied = bool(rule.required_any) and bool(rule.required_any & present_set)
        else:
            evidence_missing = data.get("evidence_missing", [])
            rule_evidence_satisfied = True  # no rule to be unsatisfied by

        # Deterministic cap: one evidence follow-up round, max. The LLM has no
        # memory of having asked before, so on a follow-up turn (context already
        # present) it can re-derive the same "still missing" conclusion from the
        # merchant's answer and re-ask forever. Once the merchant has replied,
        # proceed to decide_node with whatever evidence was found instead of
        # looping — mirrors the turn-1-ask/turn-2-decide pattern already used
        # for settlement detection.
        needs_more_info = data.get("needs_more_info", False) and not context

        # always_refund rules (e.g. RuPay U010) mean no evidence changes the
        # outcome — decision_rules already knows that deterministically, so
        # don't let the LLM's needs_more_info guess override it. Without
        # this, evidence_missing correctly comes back empty (via the rule
        # lookup above) but needs_more_info was still whatever the LLM's raw
        # JSON said — observed asking for unrelated "refund transaction ID"
        # evidence in roughly 2 of 3 identical live runs for U010, despite
        # there being nothing to actually ask for.
        if rule is not None and rule.always_refund:
            needs_more_info = False
        elif rule is not None and not rule_evidence_satisfied and not context:
            # First turn, a real evidence-based rule matched, and current
            # evidence doesn't satisfy it — force the ask rather than
            # trusting the LLM's own needs_more_info guess, which was
            # observed flaky here too: for the identical first-turn RuPay
            # U002 query with zero evidence supplied, roughly 1 in 3 live
            # runs skipped straight to a full "recommend accepting the
            # refund" generated letter instead of asking for the evidence
            # this rule actually requires — purely because the LLM's own
            # needs_more_info field came back False that time despite there
            # being nothing on file to decide with. decide()'s own
            # no-evidence-present fallback would still correctly land on
            # "refund" as the eventual outcome either way — this only
            # ensures the merchant actually gets the one chance to provide
            # evidence first, same as every other evidence-gathering step
            # in this graph already guarantees.
            needs_more_info = True

        # The LLM authors missing_info_question freely regardless of
        # whether a deterministic rule matched. Originally this deterministic
        # override only stepped in when the LLM's text came back completely
        # blank (observed live for RuPay U005, no rule at the time), on the
        # assumption its phrasing is "usually fine when present." That
        # assumption didn't hold: the U010 comment above already documents
        # the LLM asking for unrelated "refund transaction ID" evidence in
        # ~2 of 3 identical live runs despite there being nothing to ask for
        # — and the same hallucination was confirmed live for U002 too, this
        # time with NON-empty text ("Can you provide the UPI refund
        # transaction ID or UTR... to demonstrate that the refund was
        # processed?") for a case whose actual required evidence is whether
        # one or two credits were received, nothing about a refund UTR. A
        # non-empty answer isn't the same as a correct one. Whenever a rule
        # matched and evidence_missing is already known deterministically,
        # that always wins now — no reason to trust the LLM to also guess
        # correctly a second time for information the rule table already has.
        missing_info_question = data.get("missing_info_question", "") if needs_more_info else ""
        if needs_more_info and rule is not None and evidence_missing:
            missing_info_question = (
                "Please provide: " + ", ".join(humanize_evidence(evidence_missing)) + "."
            )

        return {
            "evidence_present":      evidence_present,
            "evidence_missing":      evidence_missing,
            "needs_more_info":       needs_more_info,
            "missing_info_question": missing_info_question,
            "clarification_reason":  CLARIFICATION_REASON_MISSING_EVIDENCE if needs_more_info else "",
        }

    def _ask_user_node(self, state: ChargebackState) -> dict:
        """
        Node 4 — Return a follow-up question (terminal for this turn).

        The single funnel for every ask in the main pipeline (detect_
        settlement, extract_code, extract_evidence, and answer_clarification
        — which always edges here too, re-presenting the same pending
        question after answering a merchant's meta-question). This is also
        where MAX_CLARIFICATION_ROUNDS is enforced for all of them at once —
        the three early-return asks inside validate_node's list-continuity
        block bypass this node entirely (no query_type set, so they route
        straight to END), so they enforce the same cap inline themselves.

        Reads:  missing_info_question, clarification_round
        Writes: final_answer, needs_more_info

        Args:
            state (ChargebackState): Current graph state.

        Returns:
            dict: final_answer set to the follow-up question, or the
            escalation message if MAX_CLARIFICATION_ROUNDS is already spent.
        """
        if state.get("clarification_round", 0) >= MAX_CLARIFICATION_ROUNDS:
            return {"final_answer": self._CLARIFICATION_LIMIT_MESSAGE, "needs_more_info": False}

        # `or`, not `.get(key, default)`: the fallback must also cover an
        # EMPTY string, not just a missing key. missing_info_question is
        # always set by the upstream node (never actually absent), but its
        # value can come from the LLM's own raw JSON output (e.g.
        # _extract_evidence_node's evidence-gathering step) — when that
        # field comes back blank on a given call, needs_more_info is still
        # True, and .get(key, default) returns the stored "" rather than
        # falling back, leaving the merchant with only the static "I need a
        # bit more information" banner and no actual question underneath it.
        question = state.get("missing_info_question") or "Could you provide more details about the dispute?"
        return {"final_answer": question, "needs_more_info": True}

    def _answer_question_node(self, state: ChargebackState) -> dict:
        """
        Node 4b — Answer a general chargeback question using the knowledge base.

        Used when validate_node classifies the input as query_type="question"
        rather than a specific dispute. Searches Qdrant directly and asks the
        LLM to answer using retrieved documents — skipping classify, evaluate,
        decide, generate, and reflect entirely.

        Reads:  user_query
        Writes: final_answer, retrieved_docs, confidence_score, is_grounded

        Args:
            state (ChargebackState): Current graph state.

        Returns:
            dict: Plain answer drawn from knowledge base documents.
        """
        import re as _re
        query = state["user_query"]
        cache_key = query.lower().strip()

        # Personal-data intent: "list my open chargebacks", "what all U002
        # cases exist currently?", "how much is outstanding this month?" —
        # this asks for the caller's OWN chargeback records, not general
        # policy. This node otherwise only does semantic search over
        # chargeback-encyclopedia/ (policy documents) — it has no
        # connection to the merchant's actual chargebacks.db rows on its
        # own. Without this check, a query phrased this way matched
        # list_intent below and got routed into the generic KB-listing
        # path, where the LLM — having nothing relevant retrieved —
        # fabricated a plausible-looking table of chargebacks (case IDs
        # like "CB001") that don't exist anywhere in this project's real
        # schema. Checked first, ahead of stage_intent/list_intent, so a
        # data-lookup question can never be misrouted into the
        # fabrication-prone generic path.
        #
        # The intent+filter decision itself is real LLM tool-calling
        # (_resolve_data_lookup_intent), not regex — regex here went
        # through four rounds of live-reported phrasing gaps in one
        # session ("Give me all U002 cases" missed the filter; "how much
        # is outstanding" missed the intent entirely, twice; "what all
        # u002 cases exist currently?" missed both) before being replaced.
        # looks_like_data_lookup() is only a loose, cheap pre-filter to
        # skip the LLM call on turns obviously unrelated to the merchant's
        # own data — the actual accuracy-critical decision is the model's.
        merchant_id = state.get("merchant_id", "")
        # Without a merchant_id (the Q&A tab, unauthenticated), the loose
        # looks_like_data_lookup() hint alone isn't enough to conclude this
        # needs an identity — "what is chargeback" contains the word
        # "chargeback" and would otherwise be rejected outright with a
        # "select your merchant identity" message despite needing no
        # identity at all. Require an actual first-person/possessive
        # signal in that specific case; a logged-in caller keeps the
        # original, looser behavior (a false positive there just costs one
        # cheap, self-correcting LLM tool-call, not a wrongly rejected
        # general question).
        is_data_lookup = classifier.looks_like_data_lookup(query) and (
            bool(merchant_id) or classifier.looks_like_personal_data_lookup(query)
        )
        if is_data_lookup:
            if not merchant_id:
                return {
                    "final_answer": (
                        "I don't have access to your specific chargeback "
                        "records here. Select your merchant identity above "
                        "(the same login used on the \"My Chargebacks\" tab) "
                        "and ask again, or describe a specific case and I "
                        "can help with that."
                    ),
                    "retrieved_docs":      [],
                    "confidence_score":    0,
                    "is_grounded":         True,
                    "groundedness_issues": "",
                }
            intent = self._resolve_data_lookup_intent(merchant_id, query)

            if intent and intent["type"] == "list":
                # A plain "show me my open chargebacks" gets a deterministic
                # rendering here instead of text_to_sql.py's free-form
                # NL->SQL — that path has no guaranteed row order, and a
                # follow-up like "tell me about the first one" needs
                # "first" to mean the same case it meant when the list was
                # rendered. _filtered_open_cases() is shared with
                # _validate_node's continuity-resolution step, filtered by
                # the same reason_code the tool call just decided — never
                # a differently-filtered set than what's actually shown.
                # needs_more_info=True (not the default False every other
                # branch in this node relies on) is what makes chat.html's
                # existing handleDispute treat this as an ongoing
                # conversation — it already resends the original query as
                # pendingQuery plus the merchant's reply as
                # additional_context for any needs_more_info=True response,
                # no frontend changes needed.
                reason_code = intent["reason_code"]
                cases = self._filtered_open_cases(
                    merchant_id, reason_code, intent.get("active_deadline_only", False),
                )
                case_label = f"open {reason_code} case(s)" if reason_code else "open chargeback case(s)"
                if not cases:
                    no_match = (
                        f"You have no open {reason_code} cases right now."
                        if reason_code else
                        "You have no open chargeback cases right now."
                    )
                    return {
                        "final_answer":        no_match,
                        "retrieved_docs":      [],
                        "confidence_score":    8,
                        "is_grounded":         True,
                        "groundedness_issues": "",
                        "needs_more_info":     False,
                    }
                # Urgency summary + per-case tag, requested live: a flat
                # list gave no sense of which cases actually need
                # attention now — e.g. a case with a response_deadline
                # weeks in the past (status='Open' doesn't imply the
                # deadline hasn't passed in this schema — see
                # active_deadline_only above) sat visually identical to
                # one due next month. _filtered_open_cases() already
                # returns cases sorted by response_deadline ASC, which is
                # already overdue-first/soonest-first — bucketing for
                # display doesn't reorder anything, so ordinal references
                # ("the first one") on the next turn still resolve against
                # the exact same list in the exact same order.
                buckets = [_deadline_bucket(c["response_deadline"]) for c in cases]
                overdue_n      = buckets.count("overdue")
                due_week_n     = buckets.count("due_this_week")
                later_n        = buckets.count("later")
                bucket_tag = {
                    "overdue":       " — DEADLINE PASSED",
                    "due_this_week": " — due within a week",
                    "later":         "",
                }
                lines = [
                    f"I found {len(cases)} {case_label} for your account:\n",
                    f"Summary: {overdue_n} deadline already passed, "
                    f"{due_week_n} due within the next week, "
                    f"{later_n} with more than a week remaining.\n",
                ]
                for i, (c, bucket) in enumerate(zip(cases, buckets), 1):
                    lines.append(
                        f"{i}. {c['case_id']} — RuPay {c['reason_code']} "
                        f"({c['reason_description']}), ₹{c['chargeback_amount']:,.2f}, "
                        f"due {c['response_deadline']}{bucket_tag[bucket]}"
                    )
                if len(cases) > 1:
                    # cases[0] is the chronologically-earliest deadline
                    # overall, not necessarily an ACTIONABLE one — reported
                    # live: with 5 of 7 cases already past deadline, this
                    # used to suggest "start with" the most-overdue case
                    # (the earliest deadline of all, but a passed one),
                    # which makes no sense as a "here's where to begin"
                    # recommendation. Suggest the earliest deadline that
                    # HASN'T passed instead — that's the one actually
                    # actionable today.
                    upcoming = [c for c, b in zip(cases, buckets) if b != "overdue"]
                    if upcoming:
                        lines.append(
                            f"\nThe {upcoming[0]['case_id']} case has the earliest "
                            f"deadline that hasn't passed yet "
                            f"({upcoming[0]['response_deadline']}) — want to start "
                            "with that one? Tell me which case (e.g. \"the first "
                            "one\", \"#2\", or the case ID)."
                        )
                    else:
                        lines.append(
                            f"\nAll {len(cases)} of these are already past their "
                            "response deadline — tell me which one you'd like to "
                            "look at (e.g. \"the first one\", \"#2\", or the case ID)."
                        )
                else:
                    lines.append("\nWant me to walk you through this one?")
                return {
                    "final_answer":        "\n".join(lines),
                    "retrieved_docs":      [],
                    "confidence_score":    8,
                    "is_grounded":         True,
                    "groundedness_issues": "",
                    "needs_more_info":     True,
                }

            if intent and intent["type"] == "aggregate":
                # Already executed and synthesized inside
                # _resolve_data_lookup_intent() via text_to_sql.py's
                # existing, separately-tested query_chargebacks() —
                # nothing left to do here but return it.
                return {
                    "final_answer":        intent["answer"],
                    "retrieved_docs":      [],
                    "confidence_score":    8,
                    "is_grounded":         True,
                    "groundedness_issues": "",
                }

            # looks_like_data_lookup() fired (loose pre-filter) but the
            # model decided neither tool actually applies — e.g. "what
            # does U002 mean?" contains "case"-adjacent vocabulary in the
            # KB sense, not a request for the merchant's own records. Falls
            # through to the normal KB-search path below, unchanged.

        # Dispute-lifecycle questions ("which codes are at pre-arbitration stage?")
        # must NOT be routed into the generic list handler — codes don't map to
        # stages, every code can pass through any stage. Checked first so it
        # takes priority over the "codes" keyword inside list_intent.
        stage_intent = any(kw in query.lower() for kw in [
            "pre-arbitration", "prearbitration", "arbitration", "escalation",
            "dispute stage", "dispute stages", "lifecycle",
        ])

        # Bare "all" is deliberately excluded from the keyword list below —
        # "what all proofs do I need" (Indian English for "what proofs") is not
        # an enumeration request, but a naive substring check on "all" would
        # catch it and misroute an evidence question into the list-dump path.
        # It's only treated as list intent when paired with a list-type noun
        # ("all codes", "list all the reasons", "every dispute type", etc.).
        list_intent = (not stage_intent) and (
            any(kw in query.lower() for kw in [
                "list", "every", "enumerate", "what are", "show all",
                "types of", "kinds of", "codes", "categories", "types",
                "compare", "difference between", "vs", "versus",
            ])
            or bool(_re.search(
                r'\ball\b.{0,15}\b(codes?|types?|reasons?|categories|networks?|disputes?)\b',
                query.lower()
            ))
        )

        # "are all codes covered?" / "is that the complete list?" — the user
        # is asking us to CONFIRM completeness, not asking for the list again.
        # Without this, it matches list_intent's "all" keyword and just
        # re-dumps the same list it already gave, ignoring the actual question.
        coverage_intent = bool(_re.search(
            r'\b(are all\b.*\b(covered|listed|included)|'
            r'is (everything|that|this|it)\b.*\b(all|complete|covered|listed|included)|'
            r'all covered|fully covered|all listed|all included|'
            r'anything missing|did i miss|complete list|list complete)\b',
            query, _re.IGNORECASE
        ))

        # Detect explicit reason codes mentioned in the query (e.g. U008, C02, FR2, 4853)
        mentioned_codes = _re.findall(
            r'\b(U\d{3}|C\d{2,3}|F\d{2,3}|FR\d|M\d{2,3}|\d{4})\b',
            query, flags=_re.IGNORECASE
        )
        mentioned_codes = [c.upper() for c in mentioned_codes]

        embedding = self._embed(query)

        # Network/app detection factored into network_detection.py — shared
        # with api_server.py's /search endpoint so both surfaces recognize
        # the same consumer app names (PhonePe, Google Pay, etc.), not just
        # technical terms ("UPI", "NPCI"). Falls back to additional_context
        # (the previous turn's question, sent by the frontend) when this
        # turn names no network itself — e.g. a bare follow-up like "are all
        # dispute types covered?" has nothing to match on its own and would
        # otherwise fall through to an unrelated semantic search across
        # every network in the knowledge base.
        network_title_keys, detected_networks = detect_network_title_keys(
            query, state.get("additional_context", "")
        )

        if stage_intent:
            # Ground the lifecycle explanation in whichever network's docs are
            # relevant (timelines/escalation rules differ by network), or fall
            # back to general semantic search if no network was named.
            if network_title_keys:
                results = self._store.filter_by_title(network_title_keys)[:6]
            else:
                results = self._store.search(embedding, top_k=4)
        elif mentioned_codes:
            # Fetch every doc whose title contains one of the mentioned codes.
            # This guarantees U008, U009, U010 are all retrieved for "compare U008 U009 U010".
            results = self._store.filter_by_title(mentioned_codes)
            # Supplement with semantic search in case some codes weren't title-matched
            sem = self._store.search(embedding, top_k=6)
            seen_ids = {r["id"] for r in results}
            for r in sem:
                if r["id"] not in seen_ids:
                    results.append(r)
                    seen_ids.add(r["id"])
        elif (list_intent or coverage_intent) and network_title_keys:
            # Title-based scan guarantees ALL codes for a specific network
            # regardless of semantic ranking position. coverage_intent needs
            # this same exhaustive set to actually verify completeness —
            # without it, "did I miss anything?" (no "all"/"list" keyword)
            # would fall through to a plain top-4 semantic search.
            results = self._store.filter_by_title(network_title_keys)
            if not results:
                results = self._store.search(embedding, top_k=10)
        elif list_intent or coverage_intent:
            # Generic list — semantic search with extra breadth + overview boost
            results = self._store.search(embedding, top_k=8)
            ov_emb = self._embed(query + " overview all codes summary")
            ov_results = self._store.search(ov_emb, top_k=3)
            seen_ids = {r["id"] for r in results}
            for r in ov_results:
                if r["id"] not in seen_ids:
                    results.append(r)
                    seen_ids.add(r["id"])
        else:
            # Plain single-question path — the one branch that moves to the
            # chunk collection. list_intent/stage_intent/coverage_intent/
            # mentioned_codes above all genuinely want exhaustive whole-doc
            # breadth via filter_by_title() and stay on the whole-doc
            # collection unchanged; only an open-ended question benefits from
            # chunk-level precision.
            # Cross-encoder rerank when available: widen the candidate pool
            # (cosine similarity alone is the weakest link for an open-ended
            # question with no specific code named — a generic FAQ chunk
            # phrased as a question can outscore a topically-correct but more
            # narrative chunk on similarity alone, regardless of topic) and
            # let the reranker — which jointly reads query+chunk rather than
            # comparing independent embeddings — pick the real top 6.
            # rerank_score is a NEW field, kept separate from `score` (raw
            # unbounded cross-encoder logits, e.g. ~+11/-11 — not a 0-1 value
            # comparable to cosine similarity): nothing below this block
            # reads rerank_score, so the domain-boost/promoted/parent-doc
            # logic that follows is completely unaffected either way.
            # Falls back to plain top-6-by-similarity (today's behavior) if
            # no rerank_fn was configured, or if reranking itself errors.
            wide_candidates = self._store.search_chunks(embedding, top_k=DOMAIN_CANDIDATE_POOL_SIZE)
            chunk_hits = None
            if wide_candidates and self._rerank is not None:
                try:
                    docs   = [c["content"] for c in wide_candidates]
                    scores = self._rerank(query, docs)
                    for c, s in zip(wide_candidates, scores):
                        c["rerank_score"] = s
                    wide_candidates.sort(key=lambda c: c["rerank_score"], reverse=True)
                    chunk_hits = wide_candidates[:6]
                except Exception:
                    chunk_hits = None
            if chunk_hits is None:
                chunk_hits = [r for r in wide_candidates[:6] if r["score"] >= 0.65]

            domain = detect_knowledge_domain(query, state.get("additional_context", ""))
            promoted = None
            parent_entry = None
            if domain:
                domain_hits = self._store.search_chunks(
                    embedding, top_k=DOMAIN_CANDIDATE_POOL_SIZE, knowledge_domain=domain
                )
                seen = {r["chunk_id"] for r in chunk_hits}

                # select_domain_chunk() prefers the domain's Overview
                # document for a general query rather than whatever scores
                # marginally highest — a narrow reason-code page's denser
                # vocabulary routinely outscores genuinely general content on
                # raw similarity within one domain (see network_detection.py
                # for the measurement that showed this: for a broad "what
                # happens" query, the RuPay Overview's best chunk ranked 9th
                # of 10 domain candidates, behind several single-scenario
                # pages like "Technical Root Causes of Multi-Debit Events").
                _, detected_code = classifier.extract_network_and_code(query)
                tier, best = select_domain_chunk(domain_hits, "" if detected_code == "Unknown" else detected_code)

                if best and best["chunk_id"] not in seen:
                    if tier == "strong":
                        # Leads the retrieved context, not just present in it
                        # — same reasoning as api_server.py's
                        # search_documents(): a plain score-sort undoes any
                        # "guaranteed slot" positioning, so the promotion has
                        # to survive past that sort explicitly.
                        promoted = best
                        seen.add(best["chunk_id"])
                    else:
                        chunk_hits = chunk_hits[:5] + [best]
                        seen.add(best["chunk_id"])

                for r in domain_hits:
                    if r["score"] >= 0.65 and r["chunk_id"] not in seen:
                        chunk_hits.append(r)
                        seen.add(r["chunk_id"])

                chunk_hits.sort(key=lambda r: r["score"], reverse=True)
                if promoted:
                    chunk_hits = [promoted] + [r for r in chunk_hits if r["chunk_id"] != promoted["chunk_id"]]

                # Parent-document retrieval: fires whenever select_domain_chunk()
                # is confident which single document the query is about — its
                # "strong" tier (score >= 0.65), matched against that chunk's
                # own reason_code payload field when a code was detected.
                # Deliberately keyed off `tier`/`best` directly rather than
                # `promoted`: promoted only gets set when best["chunk_id"]
                # wasn't already present in the plain (non-domain-scoped)
                # search above — a highly relevant document routinely turns
                # up there too, in which case `promoted` stays None even
                # though `tier` is still "strong". Using `tier`/`best`
                # catches that case too, since the confidence signal itself
                # doesn't depend on which search first happened to surface it.
                #
                # Rather than trust one chunk (+radius-1 neighbors) to
                # contain "enough" of the answer, fetch the whole document —
                # removes the need for that guess entirely once the document
                # itself is no longer in doubt. Falls through to the existing
                # chunk+neighbor behavior if the lookup finds nothing, so
                # this can only improve the confident case, never regress
                # the general one.
                if tier == "strong" and best and detected_code != "Unknown":
                    parent_doc = self._store.get_document_by_id(best["document_id"])
                    if parent_doc:
                        # Drop every chunk_hits entry from this same document
                        # (not just `best`/`promoted` specifically) — the
                        # full document supersedes all of them, and leaving
                        # others in would duplicate content already covered.
                        chunk_hits = [r for r in chunk_hits if r["document_id"] != best["document_id"]]
                        parent_entry = {
                            "chunk_id":       f"parent:{parent_doc['id']}",
                            "document_id":    parent_doc["id"],
                            "document_title": parent_doc["title"],
                            "content":        parent_doc["content"][:4000],
                            "network":        parent_doc.get("network", ""),
                            "reason_code":    parent_doc.get("reason_code", ""),
                            "chunk_index":    -1,
                            "score":          best["score"],
                        }

            # Narrow expansion: pull each matched chunk's immediate document-
            # local neighbors so the LLM prompt gets a fuller section of
            # context than one isolated chunk, without pulling in the whole
            # document — small-to-big retrieval, not small-then-everything.
            # Skipped for parent_entry (added back in below) since it
            # already carries the whole document.
            seen_chunk_ids = {r["chunk_id"] for r in chunk_hits}
            expanded = list(chunk_hits)
            for r in chunk_hits:
                for n in self._store.get_neighbor_chunks(r["document_id"], r["chunk_index"], radius=1):
                    if n["chunk_id"] not in seen_chunk_ids:
                        expanded.append(n)
                        seen_chunk_ids.add(n["chunk_id"])
            if parent_entry:
                expanded = [parent_entry] + expanded
            results = expanded

        # Deduplicate by title (encyclopedia indexed twice with different
        # title formats). Skipped for chunk-shaped results (the `else` branch
        # above) — those are already deduplicated by chunk_id as they're
        # assembled, and multiple chunks legitimately share the same
        # document_title (different sections of the same document, not
        # duplicate indexing the way this check was written to catch).
        if results and "chunk_id" not in results[0]:
            seen_titles: set = set()
            unique_results = []
            for r in results:
                norm = r["title"].lower().strip()
                if norm not in seen_titles:
                    seen_titles.add(norm)
                    unique_results.append(r)
            results = unique_results

        compare_intent = any(kw in query.lower() for kw in [
            "compare", "difference between", "vs", "versus", "differ",
        ])

        # Cache hit — return immediately without calling the LLM
        # (stage_intent is excluded: its answer depends on conceptual framing,
        # not document content, so caching by raw query text is unreliable)
        if (not stage_intent) and (list_intent or mentioned_codes or coverage_intent) and cache_key in self._list_cache:
            return {
                "final_answer":        self._list_cache[cache_key],
                "retrieved_docs":      [],
                "confidence_score":    8,
                "is_grounded":         True,
                "groundedness_issues": "",
            }

        # Build the docs_text to pass to the LLM.
        # For specific-code queries: full summary + some content (800 chars).
        # For broad lists: use stored summary field if available (the ## Overview
        #   paragraph extracted at index time) — avoids the 200-char truncation hack.
        # For detail queries: full content of top results.
        if stage_intent:
            doc_parts = []
            for r in results[:6]:
                summary = r.get("summary", "").strip()
                excerpt = summary if summary else r["content"][:600]
                doc_parts.append(f"### {r['title']}\n{excerpt}")
            docs_text = "\n\n".join(doc_parts)
        elif mentioned_codes:
            doc_parts = []
            for r in results[:10]:
                summary = r.get("summary", "").strip()
                excerpt = summary if summary else r["content"][:800]
                doc_parts.append(f"### {r['title']}\n{excerpt}")
            docs_text = "\n\n".join(doc_parts)
        elif list_intent or coverage_intent:
            # Cap high enough to cover a multi-network comparison without
            # silently truncating it — Amex (~13 titled docs) + Mastercard
            # (~13) alone is ~26, which used to overflow a 25-doc cap and
            # drop codes off the tail before the LLM ever saw them.
            results = results[:50]
            doc_parts = []
            for r in results:
                summary = r.get("summary", "").strip()
                if summary:
                    doc_parts.append(f"### {r['title']}\n{summary}")
                else:
                    # Fallback for older docs without summary field
                    excerpt = r["content"].strip()[:300].rsplit(" ", 1)[0]
                    doc_parts.append(f"### {r['title']}\n{excerpt}…")
            docs_text = "\n\n".join(doc_parts)
        else:
            # Label each chunk's network explicitly rather than relying on
            # the model to infer it from prose alone — confirmed this
            # matters: without a label, the LLM cited a Visa/Mastercard-
            # specific "$15-$50 chargeback fee" figure as if it applied to a
            # UPI/NPCI question, hedged as "the knowledge base says" (true)
            # but presented as directly applicable (false — the RuPay/NPCI
            # docs never mention a merchant-paid dispute fee at all). A
            # structural signal the model can act on beats a stronger prose
            # instruction alone for this failure mode — it still has to
            # read every source's prose to catch a cross-network fact, a
            # label lets it filter before it ever starts reasoning about content.
            doc_parts = []
            for r in results:
                network_label = r.get("network") or "general / not network-specific"
                # A parent-document entry (chunk_id prefixed "parent:") was
                # already capped to its own, larger budget when assembled
                # above — re-truncating it to [:1000] here would silently
                # undo the whole point of fetching the full document instead
                # of a chunk.
                is_parent = r.get("chunk_id", "").startswith("parent:")
                content   = r["content"] if is_parent else r["content"][:1000]
                label     = "Full document" if is_parent else "Source"
                doc_parts.append(f"[{label}: {r.get('document_title', '')} — network: {network_label}]\n{content}")
            docs_text = "\n\n".join(doc_parts)

        if not results:
            return {
                "final_answer":        "I don't have specific information about that in my knowledge base. Try asking about chargeback reason codes, timelines, evidence requirements, or dispute processes.",
                "retrieved_docs":      [],
                "confidence_score":    0,
                "is_grounded":         True,
                "groundedness_issues": "",
            }

        if stage_intent:
            system_prompt = (
                "You are a chargeback expert. The user is asking about dispute LIFECYCLE STAGES "
                "(chargeback / pre-arbitration / arbitration), not asking for a list of codes. "
                "IMPORTANT: reason codes are not assigned to a specific stage — every reason code "
                "can be raised at the initial chargeback stage, and ANY of them can escalate to "
                "pre-arbitration or arbitration if the dispute remains unresolved. There is no "
                "fixed subset of codes that only apply at pre-arbitration or arbitration. "
                "Explain this clearly, then describe what happens at each stage using the provided "
                "knowledge base documents (timelines, who can escalate, costs/risk of arbitration). "
                "Do not produce a per-code list — answer in terms of the three stages."
            )
        elif coverage_intent:
            system_prompt = (
                "You are a chargeback expert. The user is asking you to CONFIRM whether "
                "a list of dispute codes is complete — they are NOT asking you to repeat "
                "the list, they likely already saw it in a previous message.\n"
                "Using the knowledge base documents provided, count how many reason codes "
                "appear per network (e.g. 'Amex: 12 codes, Mastercard: 10 codes') and confirm "
                "that this is everything currently in the knowledge base for those networks. "
                "Do NOT re-print the full numbered list. Keep it to 2-4 sentences. "
                "If a network's count looks unusually low or you're not confident it's "
                "complete, say so plainly instead of asserting completeness."
            )
        elif compare_intent and len(detected_networks) >= 2:
            system_prompt = (
                "You are a chargeback expert. The user wants a network-level comparison. "
                "Using the knowledge base documents, summarize how each payment network handles "
                "disputes: total number of codes, main categories (fraud / fulfillment / billing / "
                "technical), key differences in timelines or liability rules, and any unique codes "
                "one network has that the other doesn't. Use clear sections per network.\n\n"
                "IMPORTANT: the question may name more than two things to compare (e.g. "
                "\"how RuPay, Cashfree, NPCI differ\"), but this knowledge base only documents "
                "card networks (Visa, Mastercard, Amex, RuPay) and NPCI/UPI — it does NOT cover "
                "payment gateways/aggregators (Cashfree, Razorpay, PayU, and similar) at all, "
                "since those are a fundamentally different kind of entity (a merchant-facing "
                "payment processor, not a card network or dispute-arbitrating body). Before "
                "answering, check the question against what's actually in the knowledge base "
                "documents below: if it names something that ISN'T represented there, say so "
                "explicitly and plainly (e.g. \"I don't have documentation on Cashfree — it's a "
                "payment gateway, not a card network or UPI system this knowledge base covers\") "
                "before answering the part you can. Never silently answer only the covered part "
                "as if the full question had been addressed."
            )
        elif compare_intent and mentioned_codes:
            system_prompt = (
                "You are a chargeback expert. The user wants a comparison. "
                "Using the knowledge base documents, produce a clear side-by-side comparison. "
                "Use a table or structured sections: for each code show — what triggers it, "
                "who is liable, and key difference from the others. Be concise.\n\n"
                "IMPORTANT: if the question names a code or system not represented in the "
                "documents below, say so explicitly rather than silently comparing only the "
                "ones you have information on."
            )
        elif list_intent:
            system_prompt = (
                "You are a chargeback expert. The user wants a list. "
                "Using the knowledge base documents provided, produce a clean numbered list. "
                "For each item: code/name on one line, then one sentence describing it. "
                "Be concise — no long paragraphs. Do not repeat information."
            )
        else:
            system_prompt = (
                "You are a chargeback expert. Answer the question clearly and "
                "concisely using only the provided knowledge base documents. "
                "Explain in plain English. Do not use jargon without explaining it.\n\n"
                "If the retrieved documents cover more than one card network, "
                "attribute network-specific facts (fees, deadlines, thresholds) to the "
                "network they actually describe — do not present one network's "
                "documented figure as if it applies to a different network the "
                "question is actually about."
            )

        # UPI/NPCI transactions don't route through Visa/Mastercard at all —
        # but the retrieved docs for an informational question are often a
        # MIX of generic card-ecosystem docs (issuing bank/card network/
        # acquiring bank framing) and, when detected, the NPCI-specific doc
        # (a different model: NPCI is both network AND arbitrator, disputes
        # are primarily bank-to-bank, merchant involvement is indirect).
        # Originally only applied in the generic fallback branch above — but
        # a lifecycle-STAGE question ("will this go to pre-arbitration?")
        # hits stage_intent instead, which had zero protection against the
        # same blending. Confirmed live: asked about escalation for a real
        # UPI case, the answer described generic card-network chargeback →
        # representment → pre-arbitration → arbitration terminology with no
        # indication of whether NPCI's actual dispute workflow works the
        # same way. Applied here, after all five branches, so every one of
        # them gets this protection instead of duplicating it five times.
        if is_upi_context(detected_networks):
            system_prompt += (
                "\n\nIMPORTANT: this question is about a UPI/NPCI transaction, NOT a Visa/"
                "Mastercard one — UPI does not route through a card network at all. If "
                "the knowledge base documents include an NPCI/UPI-specific document, "
                "its model is authoritative here: NPCI itself is both the network AND "
                "the dispute arbitrator (unlike Visa/Mastercard, where these are "
                "separate), the dispute is primarily between the customer's bank "
                "(remitter bank) and the recipient's/merchant's bank (beneficiary "
                "bank), and the merchant's involvement is indirect. Do NOT use Visa/"
                "Mastercard terminology (issuing bank, card network, acquiring bank, "
                "representment, pre-arbitration, arbitration) even if other, more "
                "generic retrieved documents use that framing — those describe a "
                "different payment rail and do not apply here unless the NPCI-specific "
                "documents explicitly confirm the same process/terminology applies.\n\n"
                "This same caution applies to SPECIFIC FACTS and PROCESS CLAIMS, not "
                "just terminology. A dollar/rupee figure, a percentage, a day-count, or "
                "an escalation rule (e.g. what happens if a customer disputes again) "
                "from a generic or Visa/Mastercard-specific document does not "
                "automatically apply to UPI/NPCI — for example, a card-network "
                "'chargeback fee' is not evidence that NPCI charges merchants an "
                "equivalent fee, and a card network's representment/pre-arbitration "
                "escalation trigger is not evidence NPCI's UPI dispute process has an "
                "equivalent trigger.\n\n"
                "Each source below is labeled with its network. Before stating any "
                "specific number or process claim, check which source it came from: if "
                "the ONLY source is labeled a different network or 'general / not "
                "network-specific', do not present it as a UPI/NPCI fact. Say plainly "
                "that the knowledge base doesn't document a UPI-specific answer for "
                "that point, rather than substituting the other network's process or "
                "figure — presenting another network's fact as if it were UPI-specific "
                "is a factual error, not a reasonable generalization, even if you name "
                "the source honestly."
            )
        elif not detected_networks:
            # A genuinely network-agnostic question ("how do I prevent
            # chargebacks?", "what evidence should I keep?") with no
            # network named at all — is_upi_context() above only fires
            # when the query text ITSELF names UPI/RuPay/NPCI, so a query
            # naming no network gets neither guard. But every real
            # merchant transaction this platform actually has on file is
            # RuPay/NPCI UPI (merchant_db.py's schema is RuPay by
            # construction) — and the knowledge base's cross-network
            # "best practices" content (e.g. 14_Best_Practices/
            # 001_Prevention_Best_Practices.md) freely mixes in card-
            # network-only mechanisms (3-D Secure, AVS, CVV, PSD2 SCA)
            # that have no UPI equivalent at all (UPI authenticates via
            # PIN/device binding, not card verification data). Confirmed
            # live: "How to prevent chargebacks?" retrieved that exact
            # doc and presented AVS/CVV/3DS as directly actionable advice
            # with no indication that a RuPay/UPI merchant's transactions
            # don't go through card verification at all. Not wrong per
            # se (the docs are real, not hallucinated) — but presented
            # without the one caveat that actually matters for this
            # platform's real users.
            system_prompt += (
                "\n\nNote: every real merchant transaction this platform actually "
                "processes is a RuPay/NPCI UPI transaction — not a Visa/Mastercard "
                "card transaction. Some retrieved best-practice content may describe "
                "card-network-specific mechanisms (3-D Secure, AVS, CVV, PSD2 SCA) "
                "that have no UPI equivalent (UPI authenticates via PIN and device "
                "binding, not card verification data). When recommending a specific "
                "technical control, say plainly whether it's directly applicable to "
                "UPI/RuPay transactions or is a card-network-only practice included "
                "for general context — do not present every retrieved recommendation "
                "as uniformly actionable for this merchant's actual transactions."
            )

        # Shared across every branch above: found live that a question about
        # evidence/proof for a specific reason code got answered from the
        # WRONG side of the dispute — asked "what proofs do I need to submit
        # at all three stages for U002" mid-way through actually defending a
        # real U002 case, the answer listed "the customer's bank statements
        # showing the duplicate debits... support the customer's claim for a
        # refund" — evidence that argues FOR the customer, not the merchant
        # this whole assistant exists to help. None of the branches above
        # establish whose side evidence advice should be framed from, so the
        # LLM defaulted to a neutral "how would you prove a duplicate
        # transaction happened" framing instead. This tool's whole purpose
        # (a chargeback dispute assistant for merchants) makes the answer
        # unambiguous regardless of which branch fired, so it's appended
        # once here rather than duplicated into every branch above.
        system_prompt += (
            "\n\nIMPORTANT: whenever evidence, proof, or documentation is "
            "discussed for a reason code, frame it from the MERCHANT'S "
            "defensive perspective — what the merchant should gather to "
            "rebut/defend against the dispute — never from the perspective "
            "of proving the underlying claim against the merchant. For "
            "example, for a duplicate-transaction code, the relevant "
            "evidence is the merchant's own settlement/transaction records "
            "confirming only one credit was received (or a refund record if "
            "a duplicate credit did occur) — not the customer's bank "
            "statement showing they were debited twice, which supports the "
            "customer's claim, not the merchant's defense."
        )

        response = self._invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=(
                f"Question: {state['user_query']}\n\n"
                f"Knowledge base:\n{docs_text}"
            )),
        ])

        # Cache list and compare responses — they don't change between requests
        if (not stage_intent) and (list_intent or mentioned_codes or coverage_intent):
            self._list_cache[cache_key] = response.content

        return {
            "final_answer":        response.content,
            "retrieved_docs":      [r["content"] for r in results],
            "confidence_score":    8,
            "is_grounded":         True,
            "groundedness_issues": "",
        }

    def _decide_node(self, state: ChargebackState) -> dict:
        """
        Node 5 — Recommend fight or refund.

        Reads:  user_query, reason_code, card_network, evidence_present,
                evidence_missing, retrieved_docs, ledger_decision
        Writes: decision, decision_reason

        Args:
            state (ChargebackState): Current graph state.

        Returns:
            dict: {"decision": str, "decision_reason": str}
        """
        # planner_node already resolved this exact case against the bank's
        # own CBS/ledger records — use that directly instead of falling
        # through to decision_rules.decide()'s evidence-free default, which
        # could silently contradict it (e.g. U002's no-evidence default is
        # "refund," but the ledger may have already confirmed "fight").
        ledger_decision = state.get("ledger_decision", "")
        if ledger_decision:
            return {
                "decision":        ledger_decision,
                "decision_reason": state.get("ledger_decision_reason", ""),
                "decision_source": "ledger",
            }

        # Settlement scenario — merchant answered the "was customer charged?" question.
        # is_settlement_issue flag was set by detect_settlement_node (rule-based, classifier.py).
        context            = state.get("additional_context", "").lower()
        is_settlement_case = state.get("is_settlement_issue", False)

        if is_settlement_case and context:
            customer_charged = any(w in context for w in ["yes", "charged", "a)", "option a", "was charged", "customer was charged"])
            customer_not_charged = any(w in context for w in ["no", "not charged", "b)", "option b", "failed", "never charged", "bank issue"])

            if customer_not_charged:
                return {
                    "decision":        "",
                    "decision_reason": "Transaction failed — customer was not charged",
                    "final_answer": (
                        "Since the customer was not actually charged, there is no valid chargeback.\n\n"
                        "What to do:\n\n"
                        "1. Do not ship anything — no payment has been received.\n\n"
                        "2. Contact the customer and ask them to retry the payment. "
                        "The transaction likely failed at their bank or during processing.\n\n"
                        "3. If a chargeback was filed despite no charge, dispute it with your "
                        "bank — attach your processor's confirmation that the transaction never "
                        "completed. A chargeback on a transaction that never settled is invalid.\n\n"
                        "4. Check your payment processor dashboard to confirm the transaction "
                        "status (failed / declined / not captured) and save that record."
                    ),
                }
            elif customer_charged:
                return {
                    "decision":        "",
                    "decision_reason": "Settlement failure — customer was charged but merchant not settled",
                    "final_answer": (
                        "The customer was charged but the funds never reached you — "
                        "this is a settlement failure by your payment processor.\n\n"
                        "What to do:\n\n"
                        "1. Do not ship — you have not received payment.\n\n"
                        "2. Contact your payment processor urgently:\n"
                        "   \"Transaction [ID] on [date] for $[amount] was charged to the customer "
                        "but never settled to my merchant account. Please investigate and transfer "
                        "the funds or reverse the transaction.\"\n\n"
                        "3. On the chargeback (if one was filed for non-delivery):\n"
                        "   - The customer's claim is technically valid — they paid and got nothing.\n"
                        "   - Do NOT fight the chargeback on the card scheme level.\n"
                        "   - Accept it AND simultaneously pursue the processor for the lost funds.\n"
                        "   - You cannot recover from both paths — your recourse is with the processor.\n\n"
                        "4. If the customer also filed a chargeback claiming FRAUD "
                        "(they deny making the purchase entirely) — that is a different matter. "
                        "Paste the chargeback notification letter with the reason code and I can help."
                    ),
                }
            else:
                # Unclear answer — ask more specifically
                return {
                    "decision":        "",
                    "decision_reason": "Settlement status unclear",
                    "final_answer": (
                        "I need one clear answer: was the customer's card actually charged?\n\n"
                        "Log into your payment processor dashboard and look up the transaction. "
                        "It will show one of: Completed / Settled / Captured (charged) "
                        "or Failed / Declined / Voided (not charged).\n\n"
                        "Reply with what you see and I will give you the correct next steps."
                    ),
                }

        # Deterministic rule engine — skip the LLM entirely for reason codes
        # we have a hand-curated evidence rule for. Falls through to the LLM
        # below for anything not in decision_rules.RULES.
        rule_result = decision_rules.decide(
            card_network=state.get("card_network", ""),
            reason_code=state.get("reason_code", ""),
            evidence_present=state.get("evidence_present", []),
            evidence_missing=state.get("evidence_missing", []),
            context_text=f"{state.get('user_query', '')} {state.get('additional_context', '')}",
        )
        if rule_result is not None:
            decision, decision_reason = rule_result
            return {"decision": decision, "decision_reason": decision_reason, "decision_source": "rules"}

        docs_text = "\n\n".join(state.get("retrieved_docs", [])[:1])

        messages = [
            SystemMessage(content=(
                "You are a chargeback strategy consultant.\n"
                "Decide whether the merchant should fight or accept this chargeback."
            )),
            HumanMessage(content=(
                f"Reason code: {state.get('card_network', '')} {state.get('reason_code', '')}\n"
                f"Evidence present: {humanize_evidence(state.get('evidence_present', []))}\n"
                f"Evidence missing: {humanize_evidence(state.get('evidence_missing', []))}\n"
                f"Original dispute: {state['user_query']}\n\n"
                f"Relevant policy:\n{docs_text}"
            )),
        ]

        # DecisionOutput's own schema is the enforcement mechanism now —
        # decision is a real Literal["fight", "refund", "uncertain"], not
        # a string this code has to defensively .get(..., default) after
        # hand-parsing JSON text. A schema-validation failure (provider
        # couldn't produce something matching the type) is caught the
        # same way a network error is — see _invoke_structured()'s own
        # docstring — and lands on "uncertain" as the fallback, NOT
        # "fight": this project's own decision_rules.py philosophy is "no
        # evidence -> presumptively refund," the safe direction. The old
        # hand-parsed version defaulted an unparseable response to
        # "fight" — the wrong direction for a silent guess, and had no
        # schema option for the LLM to express genuine uncertainty with
        # at all, only a forced binary choice.
        try:
            result = self._invoke_structured(messages, DecisionOutput)
            decision, decision_reason = result.decision, result.decision_reason
        except Exception:
            decision, decision_reason = "uncertain", ""

        if decision == "uncertain":
            # needs_more_info=False deliberately — this is the FINAL word
            # for this turn, not a request the merchant is expected to
            # reply to. extract_evidence_node already caps evidence-
            # gathering at one round; reopening a second round here would
            # contradict that established design instead of extending it.
            return self._uncertain(
                "The available evidence doesn't clearly support recommending "
                "either fight or refund with confidence."
                + (f" {decision_reason}" if decision_reason else "")
                + " You may want to gather stronger documentation before "
                "proceeding, or consult your acquiring bank directly.",
                needs_more_info=False,
                decision="",
                decision_reason=decision_reason or "Insufficient evidence to decide confidently",
            )

        return {
            "decision":        decision,
            "decision_reason": decision_reason,
            "decision_source": "llm",
        }

    def _generate_node(self, state: ChargebackState) -> dict:
        """
        Node 6 — Generate the rebuttal letter or refund advice.

        Guardrail: Appends a legal disclaimer to all fight responses reminding
        the merchant to verify with their payment processor.

        Reads:  decision, user_query, reason_code, card_network, evidence_present,
                evidence_missing, decision_reason, retrieved_docs, iteration
        Writes: draft_response, iteration

        Args:
            state (ChargebackState): Current graph state.

        Returns:
            dict: {"draft_response": str, "iteration": int}
        """
        decision     = state.get("decision", "fight")
        card_network = state.get("card_network", "")
        reason_code  = state.get("reason_code",  "")
        base_docs    = state.get("retrieved_docs", [])

        # For fight decisions, supplement the base docs with rebuttal-library
        # examples retrieved via payload filter — these are templated letters
        # that provide concrete structure for the draft.
        if decision == "fight":
            rebuttal_docs = self._store.filter_by_payload({"knowledge_domain": "10_Rebuttal_Library"}, limit=3)
            rebuttal_contents = [r["content"] for r in rebuttal_docs]
            all_docs = base_docs + [c for c in rebuttal_contents if c not in base_docs]
        else:
            all_docs = base_docs

        docs_text = "\n\n".join(all_docs)

        # Built-in reason code definitions — used when KB docs don't cover the code.
        # This lets generate write a confident, accurate letter without needing the
        # specific code to be in the vector store.
        REASON_CODE_DEFINITIONS = {
            # Visa
            "13.1": "Visa 13.1 — Merchandise / Services Not Received: Cardholder claims goods or services paid for were not received. Merchant defence requires proof of delivery (tracking, signature, or digital delivery confirmation).",
            "13.2": "Visa 13.2 — Cancelled Recurring: Cardholder cancelled a recurring charge. Merchant defence requires proof subscription was not cancelled before the charge.",
            "13.3": "Visa 13.3 — Not as Described / Defective: Cardholder claims goods were significantly different from description. Merchant defence requires product description evidence.",
            "10.4": "Visa 10.4 — Other Fraud – Card Absent: Cardholder denies the transaction. Merchant defence requires AVS/CVV match, 3DS authentication, or IP/device match.",
            "10.1": "Visa 10.1 — EMV Liability Shift Counterfeit Fraud: Card-present counterfeit transaction. Merchant defence requires EMV chip data.",
            "12.6": "Visa 12.6.1 — Duplicate Processing: Same transaction processed more than once. Merchant defence requires records confirming only one valid charge.",
            # Mastercard
            "4808": "Mastercard 4808 — Required Authorization Not Obtained: Transaction processed without valid authorisation. Merchant defence requires the authorisation code from the original approval.",
            "4812": "Mastercard 4812 — Account Number Not on File: Issuer has no record of the account. Typically unwinnable — issuer error or account closed.",
            "4831": "Mastercard 4831 — Transaction Amount Differs: Cardholder charged incorrect amount. Merchant defence requires original signed receipt showing the agreed amount.",
            "4834": "Mastercard 4834 — Duplicate Processing: Same transaction processed more than once. Merchant defence requires transaction records showing only one charge.",
            "4837": "Mastercard 4837 — No Cardholder Authorization: Cardholder denies authorising the transaction. Merchant defence requires AVS/CVV match, 3DS authentication, or signed authorisation.",
            "4840": "Mastercard 4840 — Fraudulent Processing of Transactions: Issuer alleges merchant is the source of card compromise or fraud pattern. Merchant defence requires full transaction records and security audit cooperation.",
            "4842": "Mastercard 4842 — Late Presentment: Transaction submitted for settlement after the permitted timeframe. Usually unwinnable; prevent by processing transactions within the required window.",
            "4846": "Mastercard 4846 — Correct Transaction Currency Code Not Provided: Wrong currency code on the transaction. Merchant defence requires records showing correct currency was disclosed and used.",
            "4849": "Mastercard 4849 — Questionable Merchant Activity: Issuer flags the merchant for suspicious transaction patterns (excessive chargebacks, MATCH-listed activity). Merchant defence requires full cooperation with the acquirer's risk review.",
            "4853": "Mastercard 4853 — Cardholder Dispute: Covers multiple subtypes — goods/services not received, not as described, credit not processed, or cancelled merchandise. Merchant defence depends on the specific subtype: delivery proof, refund records, or cancellation policy documentation.",
            "4855": "Mastercard 4855 — Goods or Services Not Provided: Cardholder did not receive what was purchased. Merchant defence requires proof of delivery or service completion.",
            "4860": "Mastercard 4860 — Credit Not Processed: Cardholder was promised a refund that never appeared. Merchant defence requires proof the credit was issued to the same card within the required timeframe.",
            "4863": "Mastercard 4863 — Cardholder Does Not Recognize — Potential Fraud: Cardholder does not recognise the charge; may escalate to fraud. Merchant defence requires AVS/CVV match, 3DS, or other proof the genuine cardholder authorised the transaction.",
            "4870": "Mastercard 4870 — Chip Liability Shift (Counterfeit Fraud): A chip-enabled card was processed via magnetic stripe instead of the EMV chip, enabling counterfeit fraud. Merchant defence requires the authorization record showing POS Entry Mode 05 (contact chip) or 07 (contactless tap) and the EMV Application Cryptogram — proving the chip was read and counterfeit data cannot be replayed. If the terminal swiped the card, the merchant bears the liability.",
            "4871": "Mastercard 4871 — Chip and PIN Liability Shift (Lost/Stolen Fraud): A chip-and-PIN card was used at a terminal that accepted signature instead of requiring PIN entry, enabling lost/stolen card fraud. Merchant defence requires the authorization record showing PIN was verified (CVM result = PIN), or that the card does not support PIN, or that the transaction was below the CVM floor limit.",
            # Amex
            "C08": "Amex C08 — Goods / Services Not Received: Cardholder claims goods or services were not received. Merchant defence requires proof of delivery (tracking, signature, or carrier confirmation).",
            "F29": "Amex F29 — Card Not Present Fraud: Cardholder denies making the card-not-present transaction. Merchant defence requires AVS/CVV match or 3DS authentication.",
            # RuPay
            # Both entries below were previously wrong — confirmed live: a
            # U002 rebuttal letter cited "RuPay U002 — Credit Not Processed"
            # and argued about "a refund promised but not credited," neither
            # of which is what U002 means. That definition is actually
            # U009's ("Merchant Not Providing Refund") — U002 is a duplicate-
            # DEBIT dispute, the opposite direction: the customer was charged
            # twice, not promised a refund that never arrived. U001 had the
            # same class of error, holding U008's definition ("Goods/
            # Services Not Provided") instead of its own — U001 is
            # "Transaction Not Done by Customer (Fraud)," an unauthorized-
            # transaction dispute (OTP vishing, SIM swap, screen-sharing
            # fraud), not a delivery dispute at all. Corrected against
            # decision_rules.py's own RULES comments and
            # chargeback-encyclopedia/07_RuPay/NPCI_U001.md /
            # NPCI_U002.md — this dict has no automated check tying it back
            # to either source, so a mismatch like this can sit
            # undetected indefinitely; worth periodically spot-checking
            # the rest of this table against the same sources.
            "U001": "RuPay U001 — Transaction Not Done by Customer (Fraud): Cardholder claims they did not initiate the transaction — an unauthorized UPI transaction (OTP vishing, SIM swap, screen-sharing fraud, or a compromised collect request). Merchant defence requires proof the UPI PIN was correctly authenticated, or delivery to the customer's own registered address.",
            "U002": "RuPay U002 — Duplicate Transaction: Cardholder's account was debited twice for the same UPI payment (system retry, network timeout, or bank-side processing duplication). Merchant defence requires proof only one valid credit was received; if the merchant actually received two credits, the duplicate must be refunded rather than contested.",
        }

        # Find definition for this reason code if available
        rc_definition = ""
        for code_key, definition in REASON_CODE_DEFINITIONS.items():
            if code_key in reason_code:
                rc_definition = definition
                break

        if decision == "fight":
            # rc_definition empty means no built-in definition matched this
            # reason_code — most often because it's genuinely "Unknown" (the
            # merchant's reply never resolved to a real code, e.g. "Visa 13"
            # instead of "Visa 13.1"). The old unconditional instruction here
            # ("Do NOT say the reason code is unknown... use the definition
            # provided above") still fired even when there was no definition
            # to use, which pressured the model to fabricate a plausible-
            # looking code — confirmed live: reason_code showed "Unknown" in
            # the API response, but the generated letter confidently cited
            # "Visa reason code 13.1" throughout. Both the opening-line
            # instruction and the closing instruction now branch on whether
            # a real definition actually exists.
            if rc_definition:
                opening_instruction = "Opening: state you are disputing this chargeback under the reason code above."
                code_guidance = (
                    "Write confidently and authoritatively. Do NOT say the reason code is "
                    "unknown or undefined — use the definition provided above."
                )
            else:
                opening_instruction = (
                    "Opening: state you are disputing this chargeback based on the claim "
                    "described below. Do NOT cite a specific reason code number — none was "
                    "confirmed for this dispute."
                )
                code_guidance = (
                    "IMPORTANT: no specific reason code number was confirmed for this dispute "
                    "— do NOT invent or assert one (e.g. do not write '13.1' or any other "
                    "specific code you were not actually given). State plainly, once, that the "
                    "exact code wasn't confirmed on the notification, and build the rebuttal "
                    "around the facts and evidence described instead — a delivery-evidence "
                    "rebuttal doesn't need a code number to be substantive."
                )
            evidence_list = humanize_evidence(state.get("evidence_present", []))
            evidence_str  = ", ".join(evidence_list) if evidence_list else "None confirmed"

            # Evidence discipline: confirmed live, separately from the
            # reason-code fabrication above, that this prompt also let the
            # model invent things beyond evidence_present — a "3-D Secure
            # authentication" evidence tag (which only means authentication
            # occurred) turned into a fabricated, specific "ECI 02 code"
            # claim, and the letter invented two entirely new evidence
            # categories (IP address matching, order-confirmation-email
            # records) that were never in evidence_present at all. The old
            # prompt's only guardrail was step 2's placeholder pattern
            # ("[Date of Transaction]... if not specified"), which the model
            # over-generalized from "placeholder for a basic transactional
            # fact" to "placeholder for an entire invented evidence type."
            # This instruction draws that line explicitly.
            evidence_discipline = (
                "EVIDENCE DISCIPLINE: only reference evidence types listed in 'Evidence "
                "available' above — do NOT invent, assume, or add any other evidence "
                "category (e.g. do not mention IP address matching, order confirmation "
                "emails, or communication records unless they appear in that list, even "
                "if they're a common, plausible thing to include in this kind of letter). "
                "For each listed evidence item, describe only what its label states — do "
                "NOT invent a specific technical detail beyond it (e.g. '3-D Secure "
                "authentication' means authentication occurred; do NOT invent a specific "
                "ECI/CAVV value, protocol version, or similar detail that was never "
                "provided). [Date of Transaction], [Transaction Amount], and [Transaction "
                "ID] are the only fill-in-later placeholders allowed, for basic "
                "transaction facts — that's different from inventing evidence.\n\n"
                "SCOPE OF EVIDENCE: the merchant's evidence describes the merchant's OWN "
                "records only — do not claim it demonstrates something only the "
                "customer's own bank account records could show. For example, 'confirmed "
                "only one credit was issued' means the merchant's settlement/transaction "
                "records show a single credit on the merchant's side — do NOT write that "
                "this 'demonstrates the cardholder's account was not debited twice' (the "
                "merchant has no visibility into the customer's bank account). Write "
                "instead that the merchant's records show only one valid credit was "
                "received for this transaction, and let the applicable rule/policy "
                "establish what that means for the dispute — don't assert the underlying "
                "customer-side fact directly."
            )

            prompt = (
                f"Write a professional chargeback rebuttal letter for submission to the acquiring bank.\n\n"
                f"Merchant dispute context: {state['user_query']}\n"
                f"Additional context: {state.get('additional_context', '')}\n"
                f"Reason code: {card_network} {reason_code}\n"
                + (f"Reason code definition: {rc_definition}\n" if rc_definition else "")
                + f"Evidence available: {evidence_str}\n\n"
                f"Relevant policy:\n{docs_text[:1500]}\n\n"
                "Structure:\n"
                f"1. {opening_instruction}\n"
                "2. Transaction summary: refer to [Date of Transaction] and [Transaction Amount] as placeholders if not specified\n"
                "3. Evidence: each listed item and exactly what it proves in relation to the claim — see EVIDENCE DISCIPLINE below\n"
                "4. Closing: formally request reversal citing the evidence\n\n"
                f"{code_guidance}\n\n"
                f"{evidence_discipline}"
            )
        else:
            prompt = (
                f"The merchant has decided to accept this chargeback.\n\n"
                f"Reason code: {state.get('card_network', '')} {state.get('reason_code', '')}\n"
                f"Missing evidence: {', '.join(humanize_evidence(state.get('evidence_missing', [])))}\n"
                f"Decision reason: {state.get('decision_reason', '')}\n\n"
                "Write actionable advice covering:\n"
                "1. Why fighting is not recommended\n"
                "2. Immediate next steps to process the refund\n"
                "3. Process improvements to prevent recurrence\n"
                "4. Thresholds to monitor (MATCH / monitoring programs)"
            )

        response = self._invoke([
            SystemMessage(content="You are an expert chargeback specialist helping merchants."),
            HumanMessage(content=prompt),
        ])

        draft = response.content

        # Disclaimer guardrail — appended to all fight letters
        if decision == "fight":
            draft += (
                "\n\n---\n"
                "⚠️  Disclaimer: This letter is AI-generated guidance only. "
                "Verify all details and consult your acquiring bank or payment "
                "processor before submitting a representment."
            )

        return {
            "draft_response": draft,
            "iteration":      state.get("iteration", 0) + 1,
        }

    # Regex that picks reason-code-like tokens out of free text:
    # covers Visa-style decimals (13.1, 10.4), Mastercard 4-digit codes (4853),
    # Amex alpha-numeric (C08, F29), RuPay U-codes (U002), and FR-codes (FR2).
    _RC_PATTERN = re.compile(
        r'\b(\d{1,2}\.\d{1,4}|4[0-9]{3}|[A-Z]\d{2,3}|U\d{3}|FR\d)\b'
    )

    def _reflect_node(self, state: ChargebackState) -> dict:
        """
        Node 7 — Deterministic groundedness check and confidence scoring.

        Replaces the LLM peer-review call with a rule-based validator:
          - Extracts reason-code tokens from the draft and cross-checks them
            against retrieved docs and the RULES table. Codes that appear in
            the draft but nowhere in either source are flagged as ungrounded.
          - When a specific case was resolved (resolved_case_id/resolved_utr
            set), deterministically corrects any garbled case_id/UTR the LLM
            wrote in the draft — this is a letter that may actually get
            submitted to a bank, so a wrong case reference in it is worse
            than a merely-worded-oddly answer.
          - Computes confidence from a formula (evidence count + rule-table
            coverage + doc match) rather than LLM self-rating.
          - Length-caps final_answer to 3000 characters.
          - Does NOT otherwise rewrite the draft — _generate_node already
            produced a complete, disclaimer-appended response.

        Reads:  draft_response, reason_code, card_network, evidence_present,
                retrieved_docs, resolved_case_id, resolved_utr
        Writes: final_answer, reflection_feedback, confidence_score,
                is_grounded, groundedness_issues
        """
        draft        = state.get("draft_response", "")
        reason_code  = (state.get("reason_code",  "") or "").strip()
        card_network = (state.get("card_network", "") or "").strip()
        evidence_present = state.get("evidence_present", [])

        # ------------------------------------------------------------------
        # Case-ID/UTR correction — deterministic, not a groundedness flag.
        # Confirmed live: a fully-grounded letter (real ledger evidence,
        # correct reason code, correct UTR) still cited the wrong case_id
        # in its "Re:" line — "NPCI20260530M010" instead of the real
        # "NPCI20260530M002010" (a dropped "002"). reflect_node's
        # groundedness check only ever verified reason-code tokens; a
        # garbled case/UTR reference passed through completely unnoticed,
        # into a letter meant to actually go to a bank. Since there's only
        # ever one real case being discussed here, any NPCI.../UTR...-shaped
        # token in the draft that doesn't match the one real,
        # deterministically-known value is corrected outright rather than
        # merely flagged — a lower confidence score is easy to miss buried
        # in a long letter; a wrong case ID sent to a bank is a real
        # consequence, and there is nothing ambiguous to preserve by
        # leaving it wrong.
        # ------------------------------------------------------------------
        id_corrected = False
        resolved_case_id = state.get("resolved_case_id", "")
        resolved_utr      = state.get("resolved_utr", "")
        if resolved_case_id:
            for found in set(re.findall(r"\bNPCI\w+\b", draft, re.IGNORECASE)):
                if found.upper() != resolved_case_id.upper():
                    draft = draft.replace(found, resolved_case_id)
                    id_corrected = True
        if resolved_utr:
            for found in set(re.findall(r"\bUTR\w+\b", draft, re.IGNORECASE)):
                if found.upper() != resolved_utr.upper():
                    draft = draft.replace(found, resolved_utr)
                    id_corrected = True

        # ------------------------------------------------------------------
        # Groundedness check
        # Extract reason-code tokens from the draft and verify each one
        # appears in retrieved docs OR in the RULES table. A code that's
        # in the draft but in neither source is a hallucination signal.
        # ------------------------------------------------------------------
        draft_codes = set(self._RC_PATTERN.findall(draft))

        is_grounded        = True
        groundedness_issues = ""

        # A code cited in the draft but appearing SOMEWHERE in the retrieved
        # policy text is not the same thing as a code confirmed for THIS
        # case — retrieved_docs is general reference material pulled for
        # semantic relevance, not proof this specific dispute's code was
        # ever established. When the case's own reason_code is still
        # "Unknown"/unconfirmed, ANY specific code cited in the draft is a
        # case-level fabrication regardless of whether that code exists in
        # the reference material — confirmed live: a Visa non-receipt query
        # retrieved the real 13.1 policy doc for background, the merchant's
        # own code was never confirmed (reason_code stayed "Unknown"), and
        # the old check below missed it because "13.1" legitimately existed
        # in retrieved_docs, just not as THIS case's confirmed code.
        if draft_codes and reason_code in ("", "Unknown"):
            is_grounded = False
            groundedness_issues = (
                f"Draft cites specific code(s) {', '.join(sorted(draft_codes))} but this "
                f"case's own reason code was never confirmed (still 'Unknown') — the draft "
                f"is asserting a code number that was not actually established for this dispute."
            )
        elif draft_codes:
            known_codes: set = set()
            for doc in state.get("retrieved_docs", []):
                known_codes.update(self._RC_PATTERN.findall(doc))
            for (_, code) in decision_rules.RULES:
                known_codes.add(code.split("#")[0])
            if reason_code:
                known_codes.add(reason_code)

            unknown = draft_codes - known_codes
            if unknown:
                is_grounded = False
                groundedness_issues = (
                    f"Draft cites codes not found in retrieved docs or rule table: "
                    f"{', '.join(sorted(unknown))}"
                )

        # ------------------------------------------------------------------
        # Confidence score (formula-based, 1-10)
        # ------------------------------------------------------------------
        docs_joined  = " ".join(state.get("retrieved_docs", []))
        evidence_tag_count = len([t for t in evidence_present if t in EVIDENCE_TAG_LABELS])
        doc_match    = bool(reason_code and reason_code in docs_joined)
        in_rule_table = any(
            k[0] == card_network and k[1].split("#")[0] == reason_code
            for k in decision_rules.RULES
        )

        confidence  = 5
        confidence += min(evidence_tag_count, 2)   # +0..+2 for evidence tags
        confidence += 2 if in_rule_table else 0    # +2 for deterministic decision
        confidence += 1 if doc_match    else 0     # +1 if code found in retrieved docs
        confidence -= 2 if not is_grounded else 0  # -2 for ungrounded citations
        confidence -= 1 if id_corrected  else 0     # -1 for a corrected case_id/UTR
        confidence -= 2 if len(draft) < 150 else 0 # -2 if draft suspiciously short
        confidence  = max(1, min(10, confidence))

        # Length cap — applied to the (possibly case-ID-corrected) draft
        final = draft[:2997] + "…" if len(draft) > 3000 else draft

        feedback = (
            "Grounded — all cited codes found in docs/rule table."
            if is_grounded else
            f"Groundedness issues detected: {groundedness_issues}"
        )
        if id_corrected:
            feedback += (
                f" Corrected a mismatched case_id/UTR in the draft to the "
                f"confirmed value (case {resolved_case_id or '(n/a)'}, "
                f"UTR {resolved_utr or '(n/a)'})."
            )

        return {
            "reflection_feedback": feedback,
            "final_answer":        final,
            "confidence_score":    confidence,
            "is_grounded":         is_grounded,
            "groundedness_issues": groundedness_issues,
        }

    # ── Routing ───────────────────────────────────────────────────────────

    @staticmethod
    def _route_after_validate(state: ChargebackState) -> Literal["classify", "answer_question", "end"]:
        """
        Route based on query_type set by validate_node.

          dispute    → classify (full dispute pipeline)
          question   → answer_question (direct knowledge base lookup)
          escalation → end (human handoff message already in final_answer)
          invalid    → end (rejection message already in final_answer)
        """
        qt = state.get("query_type", "invalid")
        if qt == "dispute":
            return "classify"
        if qt == "question":
            return "answer_question"
        return "end"

    @staticmethod
    def _route_after_detect_settlement(
        state: ChargebackState,
    ) -> Literal["ask_user", "decide", "extract_code"]:
        is_settlement = state.get("is_settlement_issue", False)
        context       = state.get("additional_context", "")
        if is_settlement and not context:
            return "ask_user"    # turn 1: ask "was customer charged?"
        if is_settlement and context:
            return "decide"      # turn 2: go straight to settlement resolution
        return "extract_code"

    @staticmethod
    def _route_after_extract_code(
        state: ChargebackState,
    ) -> Literal["ask_user", "detect_clarification"]:
        reason_code = state.get("reason_code", "Unknown") or "Unknown"
        context     = state.get("additional_context", "")
        if reason_code == "Unknown" and not context:
            return "ask_user"    # first turn with no code yet
        return "detect_clarification"

    @staticmethod
    def _route_after_detect_clarification(
        state: ChargebackState,
    ) -> Literal["answer_clarification", "extract_evidence"]:
        if state.get("merchant_is_asking_question"):
            return "answer_clarification"
        return "extract_evidence"

    @staticmethod
    def _route_after_extract_evidence(
        state: ChargebackState,
    ) -> Literal["ask_user", "decide"]:
        if state.get("needs_more_info"):
            return "ask_user"
        return "decide"

    @staticmethod
    def _route_after_decide(state: ChargebackState) -> Literal["generate", "end"]:
        """
        Skip generate+reflect when decide_node already wrote final_answer directly.

        This happens for special cases (settlement advice, transaction-not-charged,
        unclear status) where decide_node returns a complete answer instead of
        a fight/refund decision for generate_node to draft.
        """
        if state.get("final_answer"):
            return "end"
        return "generate"

    # ── Graph construction ────────────────────────────────────────────────

    def _build_graph(self):
        """
        Assemble and compile the LangGraph StateGraph.

        Flow:
          validate → planner → detect_settlement ─┬→ ask_user (END)
                  ↘ answer_question (END)          ├→ decide → generate → reflect → END
                  ↘ END                             ╰→ extract_code → detect_clarification ─┬→ answer_clarification → ask_user (END)
                                                                                               ╰→ extract_evidence ─┬→ ask_user (END)
                                                                                                                     ╰→ decide → generate → reflect → END

        Each node has a single responsibility (detect settlement, extract code,
        detect a clarifying question, answer it, or extract evidence); all
        branching decisions live in the `_route_after_*` conditional-edge
        functions, not inside the nodes themselves.

        Returns:
            CompiledStateGraph: A compiled, runnable graph.
        """
        graph = StateGraph(ChargebackState)

        # ── Nodes ─────────────────────────────────────────────────────────
        graph.add_node("validate",             self._validate_node)
        graph.add_node("planner",              self._planner_node)
        graph.add_node("detect_settlement",    self._detect_settlement_node)
        graph.add_node("extract_code",         self._extract_code_node)
        graph.add_node("detect_clarification", self._detect_clarification_node)
        graph.add_node("answer_clarification", self._answer_clarification_node)
        graph.add_node("extract_evidence",     self._extract_evidence_node)
        graph.add_node("ask_user",             self._ask_user_node)
        graph.add_node("answer_question",      self._answer_question_node)
        graph.add_node("decide",               self._decide_node)
        graph.add_node("generate",             self._generate_node)
        graph.add_node("reflect",              self._reflect_node)

        graph.set_entry_point("validate")

        # ── Edges ─────────────────────────────────────────────────────────
        graph.add_conditional_edges(
            "validate", self._route_after_validate,
            {"classify": "planner", "answer_question": "answer_question", "end": END},
        )
        graph.add_edge("answer_question", END)

        # Dispute path: planner → one focused node per question
        graph.add_edge("planner", "detect_settlement")

        graph.add_conditional_edges(
            "detect_settlement", self._route_after_detect_settlement,
            {"ask_user": "ask_user", "decide": "decide", "extract_code": "extract_code"},
        )
        graph.add_conditional_edges(
            "extract_code", self._route_after_extract_code,
            {"ask_user": "ask_user", "detect_clarification": "detect_clarification"},
        )
        graph.add_conditional_edges(
            "detect_clarification", self._route_after_detect_clarification,
            {"answer_clarification": "answer_clarification", "extract_evidence": "extract_evidence"},
        )
        graph.add_edge("answer_clarification", "ask_user")
        graph.add_conditional_edges(
            "extract_evidence", self._route_after_extract_evidence,
            {"ask_user": "ask_user", "decide": "decide"},
        )

        graph.add_edge("ask_user", END)

        graph.add_conditional_edges(
            "decide", self._route_after_decide,
            {"generate": "generate", "end": END},
        )
        graph.add_edge("generate", "reflect")
        graph.add_edge("reflect",  END)

        return graph.compile(checkpointer=self._checkpointer)

    # ── Recommendation persistence ──────────────────────────────────────────

    def _persist_recommendation(
        self,
        case_id: str,
        merchant_id: str,
        action: str,
        reason: str,
        source: str,
        confidence_score: int,
        origin: str,
        thread_id: str = "",
    ) -> None:
        """
        Single funnel run() routes both persistence call sites through
        (the main pipeline's evidence-informed decision, and
        _build_case_intro()'s evidence-blind preview) — see
        case_recommendations.py's module docstring for the full design
        and the HARD CONSTRAINT this never touches chargebacks.status/
        resolution/resolution_date, only the advisory suggested_action/
        suggestion_reason columns plus the new case_recommendations
        history table.

        Best-effort: a persistence failure must never break the merchant-
        facing answer already computed and returned — same swallow-and-
        continue convention this file already uses for non-critical
        enrichment elsewhere (e.g. _planner_node's own case-reference
        lookup).

        Args:
            case_id, merchant_id: identify which row to update/log against.
            action:   "fight" | "refund" — anything else is a no-op (never
                      a genuine decision to persist; covers empty-string
                      "uncertain"/settlement-branch/ask_user turns).
            reason, source, confidence_score, origin, thread_id: passed
                      straight through to case_recommendations.record_
                      recommendation() — see that function's own docstring.
        """
        if action not in ("fight", "refund") or not case_id or not merchant_id:
            return
        try:
            from case_recommendations import record_recommendation
            record_recommendation(
                case_id=case_id,
                merchant_id=merchant_id,
                action=action,
                reason=reason,
                source=source or "rules",
                origin=origin,
                confidence_score=confidence_score,
                thread_id=thread_id,
            )
        except Exception:
            pass

    # ── Public interface ──────────────────────────────────────────────────

    def run(
        self,
        query: str,
        additional_context: str = "",
        merchant_id: str = "",
        thread_id: str = "",
    ) -> dict:
        """
        Run the dispute agent for a merchant's chargeback description.

        Args:
            query              (str): Merchant's dispute description.
            additional_context (str): Merchant's answer to the follow-up question.
            merchant_id        (str): Authenticated merchant ID for merchant_tool access.
            thread_id          (str): UUID that identifies this conversation session.
                                      Passed to the checkpointer so the agent can resume
                                      across server restarts. A new UUID is created if empty.

        Returns:
            dict including thread_id so the client can resume the conversation.
        """
        import uuid
        if not thread_id:
            thread_id = str(uuid.uuid4())

        initial_state: ChargebackState = {
            "user_query":            query,
            "additional_context":    additional_context,
            "merchant_id":           merchant_id,
            "is_valid_query":        False,
            "query_type":            "",
            "reason_code":           "",
            "card_network":          "",
            "retrieved_docs":        [],
            "retrieval_status":      "",
            "retrieval_issues":      "",
            "case_ref_not_found":    "",
            "ledger_decision":       "",
            "ledger_decision_reason": "",
            "ledger_no_decision_reason": "",
            "resolved_case_id":      "",
            "resolved_utr":          "",
            "evidence_present":      [],
            "evidence_missing":      [],
            "needs_more_info":            False,
            "missing_info_question":      "",
            "clarification_round":        0,
            "clarification_reason":       "",
            "is_settlement_issue":        False,
            "merchant_is_asking_question": False,
            "decision":              "",
            "decision_reason":       "",
            "decision_source":       "",
            "case_intro_action":     "",
            "case_intro_reason":     "",
            "case_intro_source":     "",
            "draft_response":        "",
            "iteration":             0,
            "confidence_score":      0,
            "is_grounded":           True,
            "groundedness_issues":   "",
            "reflection_feedback":   "",
            "final_answer":          "",
        }

        # Thread config enables checkpointer to persist/resume this session.
        config = {"configurable": {"thread_id": thread_id}} if self._checkpointer else {}
        result = self._graph.invoke(initial_state, config=config)

        # Persist whichever recommendation this turn actually reached, for
        # whichever case it was actually about — see case_recommendations.py
        # and _persist_recommendation()'s own docstrings. The two branches
        # are mutually exclusive by construction: the case-intro preview
        # path (case_intro_action) never reaches decide_node, so `decision`
        # stays at its "" initial_state default whenever case_intro_action
        # is set, and vice versa.
        resolved_case_id = result.get("resolved_case_id", "")
        if resolved_case_id and merchant_id:
            if result.get("decision") in ("fight", "refund"):
                self._persist_recommendation(
                    case_id=resolved_case_id, merchant_id=merchant_id,
                    action=result["decision"], reason=result.get("decision_reason", ""),
                    source=result.get("decision_source", ""),
                    confidence_score=result.get("confidence_score", 0),
                    origin="live_chat", thread_id=thread_id,
                )
            elif result.get("case_intro_action") in ("fight", "refund"):
                self._persist_recommendation(
                    case_id=resolved_case_id, merchant_id=merchant_id,
                    action=result["case_intro_action"], reason=result.get("case_intro_reason", ""),
                    source=result.get("case_intro_source", ""),
                    confidence_score=result.get("confidence_score", 0),
                    origin="live_chat_preview", thread_id=thread_id,
                )

        card   = result.get("card_network", "")
        code   = result.get("reason_code",  "")
        rc_str = f"{card} {code}".strip() or "Unknown"

        return {
            "final_answer":        result.get("final_answer",        ""),
            "decision":            result.get("decision",            ""),
            "reason_code":         rc_str,
            "evidence_present":    humanize_evidence(result.get("evidence_present", [])),
            "evidence_missing":    humanize_evidence(result.get("evidence_missing", [])),
            "needs_more_info":     result.get("needs_more_info",     False),
            "is_valid_query":      result.get("is_valid_query",      False),
            "confidence_score":    result.get("confidence_score",    0),
            "is_grounded":         result.get("is_grounded",         True),
            "groundedness_issues": result.get("groundedness_issues", ""),
            # Deliberately separate from confidence_score/is_grounded above,
            # not folded into them — this is a RETRIEVAL-quality signal
            # (were the docs we fetched actually applicable to the detected
            # network?), computed by planner_node before generation ever
            # runs. is_grounded is an ANSWER-quality signal, computed by
            # reflect_node after generation, checking whether the DRAFT's
            # own citations trace back to what was retrieved. Two different
            # questions; conflating them would hide which one, if either,
            # actually failed.
            "retrieval_status":    result.get("retrieval_status",    ""),
            "retrieval_issues":    result.get("retrieval_issues",    ""),
            "thread_id":           thread_id,
            "clarification_round":  result.get("clarification_round",  0),
            "clarification_reason": result.get("clarification_reason", ""),
            "case_id":               resolved_case_id,
        }


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_dispute_agent(store, embed_fn: Callable[[str], list], rerank_fn=None,
                         checkpointer=None) -> DisputeAgent:
    """
    Create a DisputeAgent sharing the given store and embed function.

    Call once at server startup. Passing the existing singletons avoids
    opening a second Qdrant connection (local mode allows only one).

    Args:
        store:        A VectorStore already connected to Qdrant.
        embed_fn:     A callable (str) → list[float].
        rerank_fn:    Optional callable (query: str, documents: list[str]) →
                      list[float] — see DisputeAgent.__init__. Defaults to
                      None (no reranking) so existing callers (e.g.
                      test_qa_stress.py) that don't pass this keep working
                      unmodified.
        checkpointer: Optional LangGraph checkpointer (e.g. SqliteSaver) for
                      resuming a conversation via thread_id across calls.
                      Defaults to None (today's stateless-per-call behavior)
                      so existing callers keep working unmodified.

    Returns:
        DisputeAgent: Compiled and ready to process disputes.

    Raises:
        ValueError: If the configured LLM provider's API key is not set
                   (see llm_provider.py).
    """
    return DisputeAgent(store=store, embed_fn=embed_fn, rerank_fn=rerank_fn,
                         checkpointer=checkpointer)
