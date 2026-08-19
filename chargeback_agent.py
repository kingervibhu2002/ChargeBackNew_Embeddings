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
from typing import Callable, List, Literal, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph

import llm_provider
from guardrails import check_length, detect_prompt_injection, mask_pii, _parse_json_safe
from evidence_tags import EvidenceTag, EVIDENCE_TAG_LABELS, humanize_evidence
from network_detection import (
    DOMAIN_CANDIDATE_POOL_SIZE,
    detect_knowledge_domain,
    detect_network_title_keys,
    is_upi_context,
    select_domain_chunk,
)
import classifier
import decision_rules


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
        is_settlement_issue   (bool):       True → set by detect_settlement_node.
        merchant_is_asking_question (bool): True → set by detect_clarification_node.
        evidence_present      (List[str]):  Evidence merchant mentioned — set by extract_evidence_node.
                                             Drawn from EvidenceTag vocabulary so
                                             decision_rules.py can match reliably.
        evidence_missing      (List[str]):  Evidence still needed — set by extract_evidence_node.
        needs_more_info       (bool):       True → routes to ask_user_node.
        missing_info_question (str):        Question to ask the merchant.
        decision              (str):        "fight" or "refund" — set by decide_node.
        decision_reason       (str):        Explanation of the decision.
        draft_response        (str):        First version of letter/advice — set by generate_node.
        iteration             (int):        How many times generate_node has run.
        confidence_score      (int):        1-10 rating of answer quality — set by reflect_node.
        is_grounded           (bool):       True if answer is based only on retrieved docs.
        groundedness_issues   (str):        Description of any ungrounded claims found.
        reflection_feedback   (str):        What the peer-reviewer improved.
        final_answer          (str):        Polished final output — set by reflect_node.
    """
    user_query:            str
    additional_context:    str
    merchant_id:           str
    is_valid_query:        bool
    query_type:            str   # "dispute" | "question" | "invalid"
    reason_code:           str
    card_network:          str
    retrieved_docs:        List[str]
    evidence_present:      List[str]
    evidence_missing:      List[str]
    needs_more_info:            bool
    missing_info_question:      str
    is_settlement_issue:        bool
    merchant_is_asking_question: bool
    decision:              str
    decision_reason:       str
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


# ---------------------------------------------------------------------------
# DisputeAgent
# ---------------------------------------------------------------------------

class DisputeAgent:
    """
    Compiled LangGraph dispute agent with injected dependencies and guardrails.

    Instantiated once at server startup via build_dispute_agent().
    Reused for every /dispute request.
    """

    def __init__(self, store, embed_fn: Callable[[str], list], checkpointer=None):
        """
        Args:
            store:       VectorStore instance already connected to Qdrant.
            embed_fn:    Callable (str) → list[float] that embeds text.
            checkpointer: Optional LangGraph checkpointer (e.g. SqliteSaver) for
                          session persistence across server restarts.
        """
        self._store         = store
        self._embed         = embed_fn
        self._checkpointer  = checkpointer
        self._llm, self._fallback_llm = _make_llms()
        self._graph         = self._build_graph()
        self._list_cache: dict[str, str] = {}  # cache for list/compare responses

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

    # ── Nodes ─────────────────────────────────────────────────────────────

    def _validate_node(self, state: ChargebackState) -> dict:
        """
        Node 0 — Input guardrails + dispute intent check.

        Guardrails applied (in order, cheapest first):
          1. Length check         — no LLM call, immediate
          2. Prompt injection     — no LLM call, immediate
          3. PII masking          — mask before LLM sees the text
          4. Dispute intent check — one LLM call to verify it's a real dispute

        Reads:  user_query
        Writes: is_valid_query, user_query (PII-masked), final_answer

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

        # Guard 4 — deterministic intent classification (no LLM call)
        query_type = classifier.classify_query_type(masked_query)

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
        context = state.get("additional_context", "")
        if query_type == "invalid" and context:
            query_type = classifier.classify_query_type(f"{masked_query} {context}")

        is_valid   = query_type not in ("invalid", "escalation")

        # Build the rejection / escalation message
        if query_type == "escalation":
            final_answer = (
                "This is an AI assistant — I cannot connect you to a person directly.\n\n"
                "For human support, contact your:\n"
                "  • Acquiring bank or payment processor\n"
                "  • Visa merchant support: 1-800-VISA-911\n"
                "  • Mastercard merchant support: 1-800-999-0363\n\n"
                "I can still help you understand chargeback policies or draft a "
                "rebuttal letter. Just describe your dispute and I'll get started."
            )
        elif query_type == "invalid":
            final_answer = (
                "Please describe a chargeback dispute — for example: "
                "'I received a Visa chargeback for $300, the customer claims "
                "they never received the order but I have delivery confirmation.'"
            )
        else:
            final_answer = ""

        return {
            "is_valid_query": is_valid,
            "query_type":     query_type,
            "user_query":     masked_query,
            "final_answer":   final_answer,
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
        Writes: card_network, reason_code, retrieved_docs
        """
        query       = state["user_query"]
        merchant_id = state.get("merchant_id", "")

        # 1. Deterministic code extraction — covers the majority of disputes
        network, code = classifier.extract_network_and_code(query)

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

        retrieved_contents = [r["content"] for r in diverse]
        existing_set       = set(retrieved_contents)

        # 3. Targeted supplemental retrieval when code is known
        if code != "Unknown" and network != "Unknown":
            targeted = self._store.filter_by_payload(
                {"network": network, "reason_code": code}, limit=3
            )
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

                    analysis = analyze_chargeback(row, db_path="chargebacks.db")
                    status_line = (
                        f"Current status: {row['status']}, "
                        f"resolution: {row['resolution'] or 'not yet resolved'}."
                    )
                    if analysis.action:
                        retrieved_contents.append(
                            f"Case {row['case_id']} ({row['utr']}), reason code "
                            f"{row['reason_code']} ({row['reason_description']}): "
                            f"recommended action = {analysis.action}. {analysis.reason} "
                            f"{status_line}"
                        )
                    else:
                        retrieved_contents.append(
                            f"Case {row['case_id']} ({row['utr']}), reason code "
                            f"{row['reason_code']} ({row['reason_description']}): "
                            f"no automated recommendation available for this reason "
                            f"code without more evidence. {status_line}"
                        )
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
            "card_network":   network,
            "reason_code":    code,
            "retrieved_docs": retrieved_contents,
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
        }

    def _extract_code_node(self, state: ChargebackState) -> dict:
        """
        Node 3b — Do we know the card network and reason code?

        Single responsibility: supplement the planner's regex extraction with
        additional_context (the merchant's second-turn reply). Pre-populates
        missing_info_question with the static "please share the reason code"
        text if the code remains unknown and no context was provided.

        Reads:  reason_code, card_network, additional_context
        Writes: reason_code, card_network, missing_info_question
        """
        reason_code  = state.get("reason_code",  "Unknown") or "Unknown"
        card_network = state.get("card_network", "Unknown") or "Unknown"
        context      = state.get("additional_context", "")

        if reason_code == "Unknown" and context:
            n, c = classifier.extract_network_and_code(context)
            if c != "Unknown":
                reason_code, card_network = c, n
            elif n != "Unknown":
                card_network = n

        return {
            "reason_code":  reason_code,
            "card_network": card_network,
            "missing_info_question": (
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
            ) if reason_code == "Unknown" and not context else "",
        }

    def _detect_clarification_node(self, state: ChargebackState) -> dict:
        """
        Node 3c — Is the merchant's latest reply a question?

        Single responsibility: heuristic detection only, no LLM call.
        If yes, _answer_clarification_node answers it.
        If no, _extract_evidence_node extracts evidence tags.

        Reads:  additional_context
        Writes: merchant_is_asking_question
        """
        context  = state.get("additional_context", "")
        segments = [s.strip() for s in context.split("\n\n") if s.strip()]
        latest   = segments[-1] if segments else context

        is_question = bool(latest) and (
            latest.strip().endswith("?")
            or any(latest.lower().strip().startswith(w) for w in [
                "how", "where", "what", "why", "which", "can i", "do i",
                "is there", "who",
            ])
        )
        return {"merchant_is_asking_question": is_question}

    def _answer_clarification_node(self, state: ChargebackState) -> dict:
        """
        Node 3d — Answer the merchant's question about how/where to get evidence.

        Single responsibility: one LLM call that answers the merchant's LATEST
        question using retrieved policy docs. Router always sends the result
        to ask_user so the merchant can read the answer and reply with evidence.

        Reads:  user_query, additional_context, reason_code, card_network,
                retrieved_docs
        Writes: missing_info_question
        """
        context      = state.get("additional_context", "")
        reason_code  = state.get("reason_code",  "Unknown")
        card_network = state.get("card_network", "Unknown")
        docs_text    = "\n\n".join(state.get("retrieved_docs", [])[:2])

        segments = [s.strip() for s in context.split("\n\n") if s.strip()]
        latest   = segments[-1] if segments else context

        response = self._invoke([
            SystemMessage(content=(
                "You are a chargeback evidence analyst. The merchant is asking a "
                "clarifying QUESTION about how or where to obtain a piece of evidence "
                "— they have NOT yet provided the evidence itself.\n"
                "Answer ONLY their LATEST question directly and practically (e.g. which "
                "dashboard, report, or party holds that data), using the policy context "
                "provided. Use the earlier conversation only as background.\n"
                "End with one short sentence reminding them to come back with the "
                "actual evidence once they have it.\n"
                "Respond ONLY with JSON: {\"answer\": \"...\"}"
            )),
            HumanMessage(content=(
                f"Dispute: {state['user_query']}\n"
                f"Earlier conversation: {context}\n"
                f"Merchant's LATEST question: {latest}\n"
                f"Reason code: {card_network} {reason_code}\n\n"
                f"Relevant policy:\n{docs_text}"
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
                retrieved_docs
        Writes: evidence_present, evidence_missing, needs_more_info,
                missing_info_question
        """
        docs_text    = "\n\n".join(state.get("retrieved_docs", [])[:2])
        context      = state.get("additional_context", "")
        reason_code  = state.get("reason_code",  "Unknown")
        card_network = state.get("card_network", "Unknown")

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
                f"  {', '.join(EVIDENCE_TAG_LABELS.keys())}\n\n"
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

        fallback = {"evidence_present": [], "evidence_missing": [],
                    "needs_more_info": False, "missing_info_question": ""}
        data = _parse_json_safe(response.content, fallback)

        evidence_present = data.get("evidence_present", [])

        # If a deterministic rule exists for this code, replace the LLM's
        # evidence_missing with only the tags that rule actually requires —
        # prevents the LLM from flagging irrelevant tags (e.g. AVS/CVV/3DS
        # as "missing" on a 4870 chip dispute where only emv_chip_data matters).
        rule = decision_rules.RULES.get((card_network, reason_code))
        if rule is None and reason_code == "4853":
            subtype = decision_rules._detect_mc_4853_subtype(
                f"{state.get('user_query', '')} {context}"
            )
            if subtype:
                rule = decision_rules.RULES.get((card_network, f"4853#{subtype}"))
        if rule is not None:
            required = set(rule.required_any) | set(rule.required_all)
            present_set = set(evidence_present)
            evidence_missing = [t for t in required if t not in present_set]
        else:
            evidence_missing = data.get("evidence_missing", [])

        # Deterministic cap: one evidence follow-up round, max. The LLM has no
        # memory of having asked before, so on a follow-up turn (context already
        # present) it can re-derive the same "still missing" conclusion from the
        # merchant's answer and re-ask forever. Once the merchant has replied,
        # proceed to decide_node with whatever evidence was found instead of
        # looping — mirrors the turn-1-ask/turn-2-decide pattern already used
        # for settlement detection.
        needs_more_info = data.get("needs_more_info", False) and not context

        return {
            "evidence_present":      evidence_present,
            "evidence_missing":      evidence_missing,
            "needs_more_info":       needs_more_info,
            "missing_info_question": data.get("missing_info_question",  "") if needs_more_info else "",
        }

    def _ask_user_node(self, state: ChargebackState) -> dict:
        """
        Node 4 — Return a follow-up question (terminal for this turn).

        Reads:  missing_info_question
        Writes: final_answer, needs_more_info

        Args:
            state (ChargebackState): Current graph state.

        Returns:
            dict: final_answer set to the follow-up question.
        """
        question = state.get(
            "missing_info_question",
            "Could you provide more details about the dispute?",
        )
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
            chunk_hits = self._store.search_chunks(embedding, top_k=6)

            # Domain boost — chunking substantially reduced the old whole-doc
            # dilution problem (the RuPay/NPCI overview doc's best section
            # rose from a 0.554 whole-document score to 0.670 once split out)
            # but didn't eliminate the need for this entirely: a generic FAQ
            # chunk phrased as a question ("What happens if I don't
            # respond...") can still outscore a topically-correct but more
            # narrative chunk on question-form similarity alone, regardless
            # of topic — confirmed for the exact query that motivated this
            # migration (~0.80 for the generic FAQ vs 0.67 for the correct
            # NPCI chunk). Unlike the old whole-doc title-boost, this is
            # ranked by real cosine similarity throughout at chunk
            # granularity, so it can't resurface the old bug of an arbitrary
            # wrong-code chunk winning by luck — it just gives the right
            # network's genuinely-best chunks a chance to be seen at all.
            chunk_hits = [r for r in chunk_hits if r["score"] >= 0.65]

            domain = detect_knowledge_domain(query, state.get("additional_context", ""))
            promoted = None
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

            # Narrow expansion: pull each matched chunk's immediate document-
            # local neighbors so the LLM prompt gets a fuller section of
            # context than one isolated chunk, without pulling in the whole
            # document — small-to-big retrieval, not small-then-everything.
            seen_chunk_ids = {r["chunk_id"] for r in chunk_hits}
            expanded = list(chunk_hits)
            for r in chunk_hits:
                for n in self._store.get_neighbor_chunks(r["document_id"], r["chunk_index"], radius=1):
                    if n["chunk_id"] not in seen_chunk_ids:
                        expanded.append(n)
                        seen_chunk_ids.add(n["chunk_id"])
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
                doc_parts.append(
                    f"[Source: {r.get('document_title', '')} — network: {network_label}]\n"
                    f"{r['content'][:1000]}"
                )
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
                "one network has that the other doesn't. Use clear sections per network."
            )
        elif compare_intent and mentioned_codes:
            system_prompt = (
                "You are a chargeback expert. The user wants a comparison. "
                "Using the knowledge base documents, produce a clear side-by-side comparison. "
                "Use a table or structured sections: for each code show — what triggers it, "
                "who is liable, and key difference from the others. Be concise."
            )
        elif list_intent:
            system_prompt = (
                "You are a chargeback expert. The user wants a list. "
                "Using the knowledge base documents provided, produce a clean numbered list. "
                "For each item: code/name on one line, then one sentence describing it. "
                "Be concise — no long paragraphs. Do not repeat information."
            )
        else:
            # UPI/NPCI transactions don't route through Visa/Mastercard at
            # all — but the retrieved docs for a plain informational question
            # are a MIX of generic card-ecosystem docs (which use issuing
            # bank/card network/acquiring bank framing) and, when detected,
            # the NPCI-specific doc (which explicitly has a different model:
            # NPCI is both network AND arbitrator, disputes are primarily
            # bank-to-bank, merchant involvement is indirect). Without this
            # instruction the LLM tends to blend both framings into an
            # incorrect hybrid — verified: it previously mislabeled a
            # merchant's bank as the "issuing bank" by defaulting to the
            # card model's roles instead of UPI's remitter/beneficiary model.
            if is_upi_context(detected_networks):
                system_prompt = (
                    "You are a chargeback expert. Answer the question clearly and "
                    "concisely using only the provided knowledge base documents. "
                    "Explain in plain English. Do not use jargon without explaining it.\n\n"
                    "IMPORTANT: this question is about a UPI/NPCI transaction, NOT a Visa/"
                    "Mastercard one — UPI does not route through a card network at all. If "
                    "the knowledge base documents include an NPCI/UPI-specific document, "
                    "its model is authoritative here: NPCI itself is both the network AND "
                    "the dispute arbitrator (unlike Visa/Mastercard, where these are "
                    "separate), the dispute is primarily between the customer's bank "
                    "(remitter bank) and the recipient's/merchant's bank (beneficiary "
                    "bank), and the merchant's involvement is indirect. Do NOT use Visa/"
                    "Mastercard terminology (issuing bank, card network, acquiring bank) "
                    "even if other, more generic retrieved documents use that framing — "
                    "those describe a different payment rail and do not apply here.\n\n"
                    "This same caution applies to SPECIFIC FACTS, not just terminology. A "
                    "dollar/rupee figure, a percentage, or a day-count from a generic or "
                    "Visa/Mastercard-specific document does not automatically apply to UPI/"
                    "NPCI — for example, a card-network 'chargeback fee' is not evidence "
                    "that NPCI charges merchants an equivalent fee for a UPI dispute.\n\n"
                    "Each source below is labeled with its network. Before stating any "
                    "specific number, check which source it came from: if the ONLY source "
                    "for that number is labeled a different network or 'general / not "
                    "network-specific', do not present it as a UPI/NPCI fact. Say plainly "
                    "that the knowledge base doesn't document a UPI-specific figure for "
                    "that point, rather than substituting the other network's number — "
                    "presenting another network's fact as if it were UPI-specific is a "
                    "factual error, not a reasonable generalization, even if you name the "
                    "source honestly."
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
                evidence_missing, retrieved_docs
        Writes: decision, decision_reason

        Args:
            state (ChargebackState): Current graph state.

        Returns:
            dict: {"decision": str, "decision_reason": str}
        """
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
            return {"decision": decision, "decision_reason": decision_reason}

        docs_text = "\n\n".join(state.get("retrieved_docs", [])[:1])

        response = self._invoke([
            SystemMessage(content=(
                "You are a chargeback strategy consultant.\n"
                "Decide whether the merchant should fight or accept this chargeback.\n"
                "  fight  — evidence is strong; representment likely to succeed.\n"
                "  refund — evidence is weak or not worth contesting.\n\n"
                "Respond ONLY with JSON:\n"
                '{"decision": "fight", "decision_reason": "Strong delivery proof"}'
            )),
            HumanMessage(content=(
                f"Reason code: {state.get('card_network', '')} {state.get('reason_code', '')}\n"
                f"Evidence present: {humanize_evidence(state.get('evidence_present', []))}\n"
                f"Evidence missing: {humanize_evidence(state.get('evidence_missing', []))}\n"
                f"Original dispute: {state['user_query']}\n\n"
                f"Relevant policy:\n{docs_text}"
            )),
        ])

        data = _parse_json_safe(response.content, {
            "decision":        "fight",
            "decision_reason": "Review evidence manually",
        })
        return {
            "decision":        data.get("decision",        "fight"),
            "decision_reason": data.get("decision_reason", ""),
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
            "U001": "RuPay U001 — Goods / Services Not Provided: Cardholder did not receive purchased goods or services. Merchant defence requires delivery proof or cardholder acknowledgement.",
            "U002": "RuPay U002 — Credit Not Processed: Refund promised but not credited to the cardholder. Merchant defence requires the refund transaction record.",
        }

        # Find definition for this reason code if available
        rc_definition = ""
        for code_key, definition in REASON_CODE_DEFINITIONS.items():
            if code_key in reason_code:
                rc_definition = definition
                break

        if decision == "fight":
            prompt = (
                f"Write a professional chargeback rebuttal letter for submission to the acquiring bank.\n\n"
                f"Merchant dispute context: {state['user_query']}\n"
                f"Additional context: {state.get('additional_context', '')}\n"
                f"Reason code: {card_network} {reason_code}\n"
                + (f"Reason code definition: {rc_definition}\n" if rc_definition else "")
                + f"Evidence available: {', '.join(humanize_evidence(state.get('evidence_present', [])))}\n\n"
                f"Relevant policy:\n{docs_text[:1500]}\n\n"
                "Structure:\n"
                "1. Opening: state you are disputing this chargeback with the reason code\n"
                "2. Transaction summary: refer to [Date of Transaction] and [Transaction Amount] as placeholders if not specified\n"
                "3. Evidence: each item and exactly what it proves in relation to the reason code\n"
                "4. Closing: formally request reversal citing the evidence\n\n"
                "Write confidently and authoritatively. Do NOT say the reason code is "
                "unknown or undefined — use the definition provided above."
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
          - Computes confidence from a formula (evidence count + rule-table
            coverage + doc match) rather than LLM self-rating.
          - Length-caps final_answer to 3000 characters.
          - Does NOT rewrite the draft — _generate_node already produced a
            complete, disclaimer-appended response.

        Reads:  draft_response, reason_code, card_network, evidence_present,
                retrieved_docs
        Writes: final_answer, reflection_feedback, confidence_score,
                is_grounded, groundedness_issues
        """
        draft        = state.get("draft_response", "")
        reason_code  = (state.get("reason_code",  "") or "").strip()
        card_network = (state.get("card_network", "") or "").strip()
        evidence_present = state.get("evidence_present", [])

        # ------------------------------------------------------------------
        # Groundedness check
        # Extract reason-code tokens from the draft and verify each one
        # appears in retrieved docs OR in the RULES table. A code that's
        # in the draft but in neither source is a hallucination signal.
        # ------------------------------------------------------------------
        draft_codes = set(self._RC_PATTERN.findall(draft))

        is_grounded        = True
        groundedness_issues = ""

        if draft_codes:
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
        confidence -= 2 if len(draft) < 150 else 0 # -2 if draft suspiciously short
        confidence  = max(1, min(10, confidence))

        # Length cap
        final = draft[:2997] + "…" if len(draft) > 3000 else draft

        return {
            "reflection_feedback": (
                "Grounded — all cited codes found in docs/rule table."
                if is_grounded else
                f"Groundedness issues detected: {groundedness_issues}"
            ),
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
            "evidence_present":      [],
            "evidence_missing":      [],
            "needs_more_info":            False,
            "missing_info_question":      "",
            "is_settlement_issue":        False,
            "merchant_is_asking_question": False,
            "decision":              "",
            "decision_reason":       "",
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
            "thread_id":           thread_id,
        }


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_dispute_agent(store, embed_fn: Callable[[str], list]) -> DisputeAgent:
    """
    Create a DisputeAgent sharing the given store and embed function.

    Call once at server startup. Passing the existing singletons avoids
    opening a second Qdrant connection (local mode allows only one).

    Args:
        store:    A VectorStore already connected to Qdrant.
        embed_fn: A callable (str) → list[float].

    Returns:
        DisputeAgent: Compiled and ready to process disputes.

    Raises:
        ValueError: If the configured LLM provider's API key is not set
                   (see llm_provider.py).
    """
    return DisputeAgent(store=store, embed_fn=embed_fn)
