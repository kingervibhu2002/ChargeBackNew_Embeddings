# `chargeback_agent.py`, Explained

`chargeback_agent.py` is the largest, most complex file in this project — around 2,800 lines, one class, twelve steps, and every LLM call the Dispute Assistant makes. This document explains what it's actually *for*, in plain language first, then walks through every piece of how it achieves that — written so a reader with no prior context on the project, LangGraph, or even chargebacks can follow it end to end.

If you already know LangChain/LangGraph mechanics and just want the "how tool calling works" or "what's a node/edge" explanation, that lives in [`LANGCHAIN_LANGGRAPH_GUIDE.md`](LANGCHAIN_LANGGRAPH_GUIDE.md) — this document assumes nothing and re-teaches nothing; it focuses on *this file specifically*: why each piece exists, what real-world problem it solves, and how they fit together.

---

## Table of contents

1. [What problem is this file actually solving?](#what-problem-is-this-file-actually-solving)
2. [The one-paragraph mental model](#the-one-paragraph-mental-model)
3. [`DisputeAgent` — what the class actually holds](#disputeagent--what-the-class-actually-holds)
4. [`ChargebackState` — the shared notebook](#chargebackstate--the-shared-notebook)
5. [The graph, step by step, in plain language](#the-graph-step-by-step-in-plain-language)
6. [The conversational layer: listing cases, picking one, asking follow-ups](#the-conversational-layer-listing-cases-picking-one-asking-follow-ups)
7. [Cross-cutting concerns that show up everywhere](#cross-cutting-concerns-that-show-up-everywhere)
8. [Two full traces, from the merchant's first message to the final answer](#two-full-traces-from-the-merchants-first-message-to-the-final-answer)
9. [Design philosophy — why it's built this way](#design-philosophy--why-its-built-this-way)
10. [Where to look in the code](#where-to-look-in-the-code)

---

## What problem is this file actually solving?

Picture a small online merchant. A customer disputes a payment with their bank — maybe they say "I never got this," maybe "I never agreed to this charge." The bank claws the money back from the merchant immediately, before anyone has proven anything. The merchant now has a limited window to either **fight** (submit evidence arguing the claim is wrong) or **accept the refund** (let it go). Getting this decision wrong costs real money either way — fighting a case you'll lose wastes an evidence filing fee and time; accepting a case you could have won means giving away money you didn't have to.

Most merchants aren't chargeback specialists. They don't know that a Visa "13.1" claim needs delivery proof, that a RuPay "U002" claim needs proof of a single credit (not delivery proof at all), or that some dispute codes can never be won no matter what evidence exists. `chargeback_agent.py` is the part of this project that stands in for that expertise — a conversation partner that asks the right follow-up questions, checks the merchant's evidence against what actually matters for *their specific* dispute code, and either drafts a rebuttal letter or explains clearly why accepting the refund is the right call.

## The one-paragraph mental model

Instead of one giant "figure everything out at once" AI call, this file breaks the job into **small, single-purpose steps** — extract the reason code, check what evidence exists, decide fight-or-refund, write the letter, double-check the letter isn't making things up — and only calls an AI model for the steps that genuinely need judgment. Steps that are really just "look this up" (deciding fight-vs-refund for a *known* reason code, extracting a reason code that's spelled out in the text, checking whether a claim is even a valid chargeback) are answered with plain Python logic instead — faster, free, and, crucially, **consistent**: the same evidence for the same code always produces the same answer, which an AI model asked to reason about it fresh every time cannot promise. Where a step genuinely needs to understand free-form human language — "did the merchant actually answer the question," "what is this reason code's evidence requirement," "write a persuasive rebuttal letter" — that's exactly where an AI call is used, and used narrowly, for one job at a time.

## `DisputeAgent` — what the class actually holds

Everything in this file lives on one class, `DisputeAgent`, created once when the server starts and reused for every request (creating it fresh per request would mean reconnecting to the vector database and rebuilding the whole graph on every single message — wasteful and unnecessary, since none of what it holds is request-specific).

```python
class DisputeAgent:
    def __init__(self, store, embed_fn, rerank_fn=None, checkpointer=None):
        self._store         = store          # the shared connection to the knowledge base
        self._embed         = embed_fn       # turns text into a vector for similarity search
        self._rerank        = rerank_fn      # optional: re-scores search results for better ordering
        self._checkpointer  = checkpointer   # optional: LangGraph's save/resume mechanism (see §7)
        self._llm, self._fallback_llm = _make_llms()   # primary + backup AI model
        self._graph         = self._build_graph()      # the actual step-by-step workflow (§5)
        self._list_cache    = {}             # remembers recent list/compare answers, cheaply
```

Nothing here is specific to one conversation — `store`, `embed_fn`, and the two LLM clients are shared infrastructure, injected in from `api_server.py` rather than created inside this class, specifically so the whole app only ever opens **one** connection to the vector database (its storage format only allows one process/connection at a time — see `README.md`'s Running section).

**Why two LLM clients (`_llm` and `_fallback_llm`)?** Real API calls sometimes fail — a rate limit, a timeout, a model temporarily overloaded. Every call in this file goes through `_invoke()` (or `_invoke_with_tools()` for the tool-calling paths in §6), which tries the primary model first and silently falls back to a second, smaller model if it fails:

```python
def _invoke(self, messages: list) -> object:
    try:
        return self._llm.invoke(messages)
    except Exception as primary_err:
        try:
            return self._fallback_llm.invoke(messages)
        except Exception:
            raise primary_err
```
Every node that needs the AI calls this one method instead of touching a model directly, so this safety net is automatic everywhere — no individual step has to remember to implement its own retry logic.

## `ChargebackState` — the shared notebook

Every step in this file's workflow reads from and writes to one shared piece of data — `ChargebackState`, a Python `TypedDict` (a dictionary with a fixed, documented set of keys). Think of it as a form that starts almost entirely blank and gets filled in, one field at a time, as the conversation progresses — no single step ever sees or fills in the whole thing at once.

| Field | What it holds | Filled in by |
|---|---|---|
| `user_query` | The merchant's message, with any personal data masked out | Set at the start; occasionally rewritten by the conversational layer (§6) |
| `additional_context` | Whatever the merchant said on a follow-up turn | Passed in from the previous response |
| `merchant_id` | Who's asking, resolved server-side — never trusted from the message itself | `api_server.py`, before the graph even starts |
| `query_type` | `"dispute"` / `"question"` / `"escalation"` / `"invalid"` | The first step, `validate_node` |
| `reason_code` / `card_network` | e.g. `"13.1"` / `"Visa"` — which specific claim this is | `planner_node`, refined later if still unknown |
| `retrieved_docs` | Relevant policy text pulled from the knowledge base | `planner_node` |
| `retrieval_status` / `retrieval_issues` | `"good"` / `"ambiguous"` / `"bad"` / `""` — were the retrieved documents actually consistent with the detected network, or just semantically similar to it? Signal only right now; nothing yet retries retrieval or blocks generation when this comes back `"bad"` | `planner_node`, via `retrieval_evaluator.py` |
| `is_settlement_issue` | Is this actually a missing-payment problem, not a real chargeback? | `detect_settlement_node` |
| `evidence_present` / `evidence_missing` | What the merchant has, mapped to a fixed vocabulary (see [`DECISION_RULES_GUIDE.md`](DECISION_RULES_GUIDE.md)) | `extract_evidence_node` |
| `needs_more_info` | Should the graph stop and ask the merchant something? | Several nodes |
| `decision` / `decision_reason` | `"fight"` or `"refund"`, and why | `decide_node` |
| `draft_response` | The letter or refund guidance, before final polish | `generate_node` |
| `confidence_score` / `is_grounded` / `groundedness_issues` | A trustworthiness check on the final answer | `reflect_node` |
| `final_answer` | What actually gets shown to the merchant | Whichever node ends the conversation |

A step never returns the *whole* state — it returns only the fields it wants to change, and the framework merges that on top of everything already there. (No step in this file uses anything fancier than plain overwrite-on-write for that merge — see `LANGCHAIN_LANGGRAPH_GUIDE.md`'s concept-coverage section for the precise mechanics of why that matters.)

## The graph, step by step, in plain language

```
validate → planner → detect_settlement ─┬→ ask_user (END)
        ↘ answer_question (END)          ├→ decide → generate → reflect → END
        ↘ END                             ╰→ extract_code → detect_clarification ─┬→ answer_clarification → ask_user (END)
                                                                                     ╰→ extract_evidence ─┬→ ask_user (END)
                                                                                                            ╰→ decide → generate → reflect → END
```

Twelve steps, each doing exactly one job. Reading left to right is reading the actual order a real dispute gets handled in:

**1. `validate` — is this even a real dispute, and is it safe to process?**
Before anything else: is the message a reasonable length (not empty, not a 5,000-word essay)? Does it look like an attempt to manipulate the AI rather than describe a real problem (a "prompt injection" check)? Any personal data (card numbers, phone numbers) gets masked out before any further processing sees it. Then: is this actually describing a dispute, asking a general question, asking to talk to a human, or nonsense? This step also houses the entire conversational continuity feature described in §6 — case listing, case selection, and follow-up questions are all resolved *here*, before the rest of the pipeline below ever runs, because a resolved conversation can skip straight to a full answer without needing any of the following steps.

**2. `planner` — what is this dispute, and what does policy say about it?**
Pulls out the card network and reason code if they're spelled out in the text (plain pattern-matching — "Visa 13.1" is unambiguous, no AI judgment needed), then searches the knowledge base for relevant policy. If the merchant names a real case ID they've filed before, this step looks up the actual database row and grounds everything downstream in the real facts of that case instead of guessing from free text. Only if none of that works — no code, no network, nothing usable extracted — does this step ask an AI model to take a guess from the raw text. It also runs a quick, deterministic sanity check on what it just retrieved — do these documents actually belong to the network just detected, or did they just happen to score well on similarity? (See `retrieval_evaluator.py`, below.) A high similarity score doesn't guarantee policy applicability — a Visa document about "unauthorized transactions" can score well against a UPI fraud question while being the wrong network's rules entirely.

**3. `detect_settlement` — wait, is this even a real chargeback?**
A surprisingly common confusion: a merchant sees money missing and assumes it's a chargeback, when actually the customer's payment simply never went through (a "settlement failure," a completely different problem with a completely different fix). This step is a single keyword check — no AI call — that flags this case so `decide_node` can hand back the right advice instead of chargeback-fighting advice for a chargeback that never happened.

**4. `extract_code` — do we actually know what claim we're dealing with?**
If the previous step didn't find a reason code, this one gives the merchant's follow-up reply a second chance to supply it. If it's still unknown, the conversation pauses here and asks for it — there's no way to give correct advice about "some unspecified dispute."

**5. `detect_clarification` — is the merchant answering, or asking something back?**
A one-line check (not an AI call): does the merchant's reply *look like a question* ("what does that mean?") rather than an answer ("yes, we have delivery proof")? This decides whether the next step is *answering* them or *extracting evidence from* them — two very different things that would otherwise get confused.

**6a. `answer_clarification` — answer the merchant's actual question.**
If they asked something, this step answers it — and specifically checks whether the case's own real, on-file facts (pulled in step 2, if a real case was named) already answer part of the question, leading with those before falling back to generic advice. A live bug this fixed: a merchant asking "can you check my data and tell me if two amounts were credited?" was getting told *how* to go check their own bank statement, even when the system already had that exact case's status sitting right there — this step now checks for and uses that first.

**6b. `extract_evidence` — what does the merchant actually have?**
Reads the merchant's free-text answer and maps it onto a fixed, closed vocabulary of evidence types ("tracking number," "AVS match," "confirmed only one credit was issued," etc. — see [`DECISION_RULES_GUIDE.md`](DECISION_RULES_GUIDE.md) for the full list and why it's closed rather than free text). When a deterministic rule already exists for this exact reason code, this step tells the AI model *exactly* which evidence types matter for this specific case — instead of making it guess from a flat list of thirty possibilities, most of which are irrelevant to any one dispute.

**7. `decide` — fight or refund?**
For a settlement-failure case (step 3), this returns settlement-specific advice, not a fight/refund call at all. Otherwise: check the hand-curated rule table first (`decision_rules.py`, its own full write-up) — if this exact reason code has a documented evidence requirement, the answer is computed by a plain lookup, no AI judgment involved, and it's *always* the same answer for the same evidence. Only reason codes with no such rule fall through to an AI model's judgment call.

**8. `generate` — write the actual letter (or refund guidance).**
Drafts the rebuttal letter for a "fight" decision (pulling in real example rebuttal letters from the knowledge base as structural templates) or clear refund guidance otherwise. A fight response always gets a legal disclaimer appended, reminding the merchant this is guidance, not a guarantee, and to verify with their actual payment processor.

**9. `reflect` — is this letter actually trustworthy before we show it to anyone?**
The last step before the merchant sees anything. Scans the draft for any reason code it mentions and checks that code actually appears in the retrieved policy documents or the rule table — a code mentioned in the letter that traces back to *neither* is a strong signal the AI invented something. Computes a 1–10 confidence score from a plain formula (how much real evidence was found, whether a deterministic rule existed, whether the code was actually confirmed) rather than asking the model to rate its own answer. This step calls no AI model at all — it's pure verification logic, on purpose: you don't want the same kind of system that might hallucinate a fact to also be the one certifying that it didn't.

Two more steps sit outside this main flow: **`ask_user`** simply packages up whatever question the current step needs answered and ends the conversation for this turn, waiting for the merchant's reply. **`answer_question`** is a separate, lighter path entirely — for a merchant who's just asking a general knowledge-base question ("what's the difference between Visa 10.4 and 13.1?") rather than describing an actual dispute, this step searches the knowledge base directly and answers in one AI call, skipping the whole fight/refund pipeline above since there's no specific case to evaluate.

## The conversational layer: listing cases, picking one, asking follow-ups

Everything above assumes the conversation is a straightforward "describe your dispute → answer follow-ups → get a letter" exchange. Real usage is messier: a merchant might say "show me my open chargebacks," then "tell me about the first one," then ask an unrelated question, then come back to the case they were just discussing. All of that is handled inside `validate_node` — the very first step — using a genuinely different technique from everything described above: **the AI model itself decides what the merchant means**, via real tool calling, rather than pattern-matching their words.

**Why this needed a different approach.** Detecting "does this message want to see the merchant's own cases" started as plain keyword matching, like everything else in this file — and kept breaking. "What all U002 cases exist currently?" would slip past one version of the check; "how much is outstanding this month?" would slip past another. Every fix caught one phrasing and missed the next, because natural language for "show me my stuff" genuinely has no fixed, enumerable pattern the way a reason code (`U002`, `13.1`) does. So this one decision point hands the judgment to the model instead: it's given two tool "options" — *list my cases* or *look up a computed number* — with a plain-English description of when to use each, and it picks (or picks neither, if the message isn't actually about the merchant's own data at all). Full mechanics of how this works — `@tool`, `.bind_tools()`, the multi-round loop needed for the richer case-detail feature below — are in [`LANGCHAIN_LANGGRAPH_GUIDE.md`'s tool-calling section](LANGCHAIN_LANGGRAPH_GUIDE.md#16-tool-calling--letting-the-model-ask-for-real-data).

**Picking a case gets a real, grounded introduction, not a bare evidence question.** When a merchant picks a case ("the first one," "#2," a case ID), the system doesn't just jump straight to asking for evidence. `_build_case_intro()` runs a real, multi-step lookup — fetch the case's actual database row (amount, status, deadline, reason code), then fetch what that reason code actually means and requires from the knowledge base — and stitches both together into one grounded, natural-language introduction before asking for anything. This needs *two* rounds of AI decision-making, not one, because the second lookup (what does this reason code require) can't happen until the first one (what is the reason code) has already returned an answer — verified live before this was built: given both options at once, the model correctly refuses to guess the second one early.

**A real gap, found live and fixed, worth knowing about even though it's closed now:** this conversational memory lives entirely in the browser, which resends the whole exchange on every turn (see §7's checkpointer note for why). The browser used to fully reset that memory the moment ANY single question in the conversation got a complete, standalone answer — so a case you were discussing could drop out of context a few turns later, even mid-topic, the moment a fully-answered tangent came in between. Reported live with a real 6-turn transcript (list cases → select one → two follow-up questions → an aggregate question → "what about the second one?") that ended in a flat rejection by the last turn, with nothing left server-side to resolve "second one" against. Fixed in `chat.html`: conversation memory now persists across a completed answer too, capped to the most recent turns rather than growing without bound, and is only actually cleared by a genuine topic change (the existing `looksLikeNewTopic()` check, now applied regardless of whether the agent is mid-follow-up) or switching merchant/tab. Fixing this surfaced a second, deeper bug in the same trace: `classifier.detect_case_selection()`'s clarifying-question guard (added to stop "what does U002 mean?" from false-matching a case by reason code alone) was firing before the ordinal-word check ever ran, so "what about the second one?" — a real selection, just phrased as a question — was being rejected as "just a question" and answered from the wrong (first) case entirely. Fixed by reordering: strong ordinal/number signals are checked first, and the clarifying-question guard now only protects the weaker reason-code-mention match it was actually built for.

Fixing *that* surfaced a third bug, one step further into the same conversation: asking about a case position that doesn't exist ("what about the third one?" with only two cases ever shown) has no case to resolve to at all — `detect_case_selection()` correctly recognized "third" as an ordinal and correctly refused to guess (bounds-checked: index 2 isn't `< len(shown_cases)==2`), returning `None`. But `None` here was indistinguishable from "not a selection attempt at all," so `_validate_node`'s fallback treated it the same way — re-enriching the query with whatever case the *original* `pendingQuery` happened to reference, and confidently answering as if that case were "the third one." A merchant would read a real, fluent-sounding answer about a real case, for a question that should have gotten "you only have 2 cases, there's no third." Fixed with a new `classifier.is_out_of_range_case_reference()` — checked as its own branch in `_validate_node`, before the reattach-and-guess fallback ever runs — so an out-of-range ordinal reference now gets told the truth (the real count, the real list again) instead of a hallucinated-sounding substitution. A smaller, related find in the same pass: `_ORDINAL_WORDS` didn't recognize "forth" (a common misspelling of "fourth") as an ordinal at all, so it hit the same wrong-case bug through a different gap — missing vocabulary rather than a missing bounds check. Added as an alias.

This whole chain is also the clearest real illustration of a structural point worth knowing on its own: `reflect_node` — the only verification step anywhere in this graph — never ran for any of these three bugs. All of them happen inside `_validate_node`'s early-return continuity logic, which (by design, for speed) routes straight to `END` without ever touching `decide → generate → reflect`. Confirmed live, not assumed: none of the resulting answers were checked for correctness by anything in the graph before reaching the merchant. Even a hypothetically universal `reflect_node` wouldn't have caught the second bug specifically — its check is "does this reason code trace back to real docs/rules," and U002 genuinely does; it was just attached to the wrong case. Verifying *conversational reference correctness* is a different problem than verifying *reason-code groundedness*, and nothing in this graph currently does the former at all.

## Cross-cutting concerns that show up everywhere

A few things aren't tied to any one step — they run underneath most of the file:

- **Guardrails, applied early and often.** Length checks, prompt-injection detection, and PII masking all happen in `validate_node`, before any other logic sees the raw message. A follow-up reply gets its own filter — `is_junk_reply()`'s cheap pattern check first, then (only if that's inconclusive) an AI backstop (`_filter_substantive_context`) that judges whether a reply is a real, substantive answer or just filler ("nice," "ok," a repeated echo of the original question). Both exist because a merchant's reply that carries no real information should never be silently treated as if it answered the question.
- **The primary/fallback pattern**, described in §3, wraps every single AI call in this file — no step has to think about API reliability itself.
- **A real, wired LangGraph checkpointer that doesn't actually do anything yet.** `DisputeAgent` accepts one and compiles the graph with it (`self._graph.invoke(initial_state, config=config)`), and `api_server.py` does construct a real one on startup. But the browser never resends the `thread_id` needed to resume from it — every call effectively starts a brand-new conversation from the checkpointer's point of view. Multi-turn memory in this app comes entirely from the browser re-sending the accumulated conversation text as `additional_context`, not from anything this file persists on its own. Full detail in `LANGCHAIN_LANGGRAPH_GUIDE.md` §2.7.
- **A simple response cache** (`self._list_cache`) remembers recent list/comparison-style answers by their exact query text, so asking the identical question twice in a row doesn't re-run a full search-and-generate cycle.

## Two full traces, from the merchant's first message to the final answer

**Trace 1 — a straightforward new dispute:** *"Mastercard chargeback, customer says the charge is fraudulent, but they placed the order through our 3D Secure checkout."*

1. `validate` — passes the safety checks, no prior conversation context, classified as `"dispute"`.
2. `planner` — pattern-matching finds `"Mastercard"` but no specific 4-digit code in the text; retrieves relevant Mastercard fraud policy anyway via similarity search.
3. `detect_settlement` — not a settlement issue; this is a real dispute.
4. `extract_code` — still no code known, and no follow-up reply yet to check → the conversation pauses here, asking for the specific reason code.
5. `ask_user` — returns the question. **Turn ends.**

Second message: *"4837, and yes we have 3DS authentication logs."*

6. `extract_code` — now finds `"Mastercard 4837"` in the reply.
7. `detect_clarification` — this isn't a question, it's an answer → proceeds to evidence extraction, not clarification.
8. `extract_evidence` — the rule table already knows 4837 needs `avs_match`/`cvv_match`/`three_ds_authentication`; recognizes "3DS authentication logs" as exactly that.
9. `decide` — the rule table has a direct answer for Mastercard 4837 with 3DS confirmed: **fight**, no AI judgment call needed.
10. `generate` — drafts the rebuttal letter, pulling in a real example rebuttal structure from the knowledge base, appends the standard disclaimer.
11. `reflect` — checks the draft only cites "4837," which is both the case's own confirmed code and present in the retrieved docs → grounded. Computes a high confidence score (a matched rule-table entry plus real evidence tags). **Turn ends — merchant sees the finished letter.**

**Trace 2 — a conversational case exploration:** *"show me my open chargebacks"* → *"tell me about the first one"*

1. `validate` — first turn, no prior context, classified as `"question"` (a data-lookup request, not a specific dispute description).
2. Routes to `answer_question` — recognizes this as asking about the merchant's *own* data, and the tool-calling decision (§6) picks "list my cases." Renders the real open cases from the database, soonest deadline first, and asks which one to discuss. **Turn ends.**

Second message, same conversation:

3. `validate` runs again — this time `additional_context` holds "tell me about the first one." The continuity logic (§6) resolves "first one" against the case list, positively identifies a real case, and calls `_build_case_intro()` — which itself makes two rounds of real database + knowledge-base lookups (case details, then that reason code's requirements) before synthesizing one grounded answer.
4. `validate_node` returns **immediately** with that full answer — `planner`, `decide`, `generate`, and every other step in the main pipeline never run for this turn. **Turn ends — merchant sees a real case summary, what the reason code means, and what evidence is needed, all in one response.**

## Design philosophy — why it's built this way

A few decisions repeat throughout this file, worth naming explicitly:

- **Deterministic before AI, wherever the task allows it.** Reason-code pattern matching, fight/refund decisions for known codes, and "is this a settlement issue" are all plain Python — faster, free, and testable with an ordinary assertion, not just "looks reasonable." AI calls are reserved for genuinely open-ended judgment (does this reply actually answer the question, what does this specific reason code's evidence requirement look like in this merchant's own words, write a persuasive letter) — and even there, the model is given as much structure as possible (a closed evidence vocabulary, rule-scoped guidance, JSON-only responses) rather than being asked to freelance.
- **One job per step, routing kept completely separate from logic.** No step in this file decides what runs next — that decision lives only in dedicated `_route_after_*` functions. This means you can read any one step in isolation and know exactly what it does, without needing to also trace where control might jump afterward.
- **Every AI-calling step gets its own narrow persona.** "Chargeback evidence analyst" here, "chargeback strategy consultant" there — never one general-purpose assistant character carried across the whole file. A narrowly-scoped job is both easier for the model to do reliably and easier for a human reviewing the prompt to reason about.
- **Verification is deterministic, deliberately.** `reflect_node` — the step whose entire job is "can we trust this answer" — calls no AI model at all. Using the same kind of system that might make something up to also certify that it didn't would defeat the point.
- **Known limitations are documented, not hidden.** The inert checkpointer (§7) and the conversational-memory gap (§6) are both real, current limitations of this file's design — recorded here and in the related guides specifically so a future reader doesn't have to rediscover them the hard way.

## Where to look in the code

- **`chargeback_agent.py`** — everything described in this document. Search `_build_graph` for the full wiring in one place, any `_route_after_*` for a routing decision, `self._invoke(` for a plain AI call, `self._invoke_with_tools(` for a tool-calling one.
- **[`LANGCHAIN_LANGGRAPH_GUIDE.md`](LANGCHAIN_LANGGRAPH_GUIDE.md)** — the LangChain/LangGraph *mechanics* this file uses (nodes, edges, state, tool calling), taught from first principles using this file as the running example, plus a concept-by-concept coverage map of what this project does and doesn't use.
- **[`DECISION_RULES_GUIDE.md`](DECISION_RULES_GUIDE.md)** — the fight/refund rule table `decide_node` and `extract_evidence_node` both depend on, in full detail.
- **`classifier.py`** — the plain-Python text classification this file leans on constantly: `classify_query_type()`, `extract_network_and_code()`, `detect_settlement_issue()`, `is_junk_reply()`, `detect_case_selection()`, and more.
- **`evidence_tags.py`** — the closed evidence vocabulary referenced throughout §5 and §6.
- **`guardrails.py`** — the length/injection/PII-masking checks `validate_node` runs first.
- **`retrieval_evaluator.py`** — the deterministic network-consistency check `planner_node` runs right after retrieval, before generation.
- **`api_server.py`** — the one caller of this file's public entry point, `DisputeAgent.run()` — read it to see how a `/dispute` HTTP request actually becomes a call into this graph, and how the returned dict becomes the JSON response the browser sees.
- **`README.md`** — this file's place in the overall project architecture, one level up from this document's `chargeback_agent.py`-specific focus.
