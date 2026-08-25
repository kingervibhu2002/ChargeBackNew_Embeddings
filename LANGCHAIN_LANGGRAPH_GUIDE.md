# LangChain & LangGraph, Explained Through This Project

This document explains what LangChain and LangGraph actually *do* — not in the abstract, but by pointing at the real code in `chargeback_agent.py` that uses them. If you've never touched either library before, read this top to bottom. If you already know them, skip to [Part 3](#part-3-walking-through-one-real-request) for the concrete trace, or the [glossary](#quick-glossary) for a fast lookup.

No prior LangChain/LangGraph knowledge assumed. Basic Python (functions, dictionaries, classes) is enough.

---

## Table of contents

1. [The big picture](#the-big-picture)
2. [Part 1: LangChain — talking to a model](#part-1-langchain--talking-to-a-model)
3. [Part 2: LangGraph — orchestrating many steps](#part-2-langgraph--orchestrating-many-steps)
4. [Part 3: Walking through one real request](#part-3-walking-through-one-real-request)
5. [Concept coverage: what this project uses, and what it doesn't](#concept-coverage-what-this-project-uses-and-what-it-doesnt)
6. [Quick glossary](#quick-glossary)
7. [Where to look in the code](#where-to-look-in-the-code)

---

## The big picture

**LangChain** is a library for talking to an LLM (like GPT or Llama) in a structured way — building a prompt, sending it, getting a response back — without hand-rolling raw HTTP calls to whichever provider you're using. It gives you a common "shape" (chat models, messages) that works whether the model is from OpenAI, Groq, Anthropic, or someone else.

**LangGraph** is a *separate* library, built on top of LangChain, for a different problem: what happens when answering a question takes more than one LLM call, and the steps in between involve real logic — branching, looping back, deciding to stop early? LangGraph lets you describe that as a **graph**: a set of steps ("nodes") connected by rules about which step runs next ("edges"), sharing one common notebook of information ("state") as they go.

Here's the analogy this project actually follows:

- **LangChain** = the phone. It's how you have *one* conversation with an AI.
- **LangGraph** = the flowchart on the wall behind the customer-service desk. It's what tells the person which phone call to make next, based on what they just learned, and when to stop and hand you an answer.

The Dispute Assistant needs the flowchart, not just the phone: describing a chargeback isn't one question-and-answer, it's *extract the reason code → check what evidence exists → decide fight or refund → write the letter → double-check the letter isn't making things up* — a sequence of steps, several of which might not even need the phone at all (this project's whole "rule-based over LLM-based" philosophy — see `CLAUDE.md` — is about skipping the phone call whenever plain code can decide something just as well).

## Part 1: LangChain — talking to a model

### 1.1 Chat models — the "phone line" to the AI

A **chat model** object in LangChain represents one specific AI model you can send messages to. This project uses two: `ChatGroq` and `ChatOpenAI`, both from LangChain's provider packages. They look almost identical to use — that's the entire point of LangChain's abstraction: swap which one you construct, and every other line of code that *uses* it stays the same.

```python
# llm_provider.py — this project's actual provider-switching code
from langchain_groq import ChatGroq
primary = ChatGroq(model="openai/gpt-oss-120b", temperature=0, api_key=key)

# or, if LLM_PROVIDER=openai instead:
from langchain_openai import ChatOpenAI
primary = ChatOpenAI(model="gpt-4o", temperature=0, api_key=key)
```

`temperature=0` means "be as deterministic as possible" — good for a business tool where you want the same input to reliably produce a similar answer, as opposed to `temperature=1`-ish settings tuned for creative variety.

### 1.2 Messages — how you structure a conversation

You don't send a chat model a plain string. You send it a **list of messages**, each tagged with a role. This project uses two message types from `langchain_core.messages`:

- **`SystemMessage`** — instructions for how the model should behave. Never shown to the end user; it's the model's "job description" for this call.
- **`HumanMessage`** — the actual thing being asked, as if a person typed it.

```python
# A simplified version of what _extract_evidence_node in chargeback_agent.py sends
from langchain_core.messages import SystemMessage, HumanMessage

messages = [
    SystemMessage(content=(
        "You are a chargeback evidence analyst.\n"
        "Based on the dispute and policy, identify evidence present and missing.\n"
        "Respond ONLY with JSON: "
        '{"evidence_present": [...], "evidence_missing": [...], "needs_more_info": false}'
    )),
    HumanMessage(content=(
        "Dispute: Customer says the charge is fraudulent, but they used our "
        "3D Secure checkout.\nReason code: Mastercard 4837"
    )),
]
```

Notice the **system prompt is narrow and single-purpose** — "you are a chargeback evidence analyst," nothing more. This project deliberately gives each LLM-calling step its own tightly-scoped persona (evidence analyst here, "chargeback strategy consultant" in `_decide_node`, and so on) instead of one big general-purpose assistant character carried across the whole conversation. A narrow job is easier for the model to do reliably, and easier for a human reviewing the prompt to reason about.

### 1.3 Actually calling the model — `.invoke()`

Once you have a chat model and a message list, you call `.invoke()`:

```python
response = primary.invoke(messages)
print(response.content)   # the model's reply, as a plain string
```

That's the entire core LangChain interaction loop: build messages → `.invoke()` → read `.content` off the result. Everything else in this project layered on top of that is *this project's own code*, not LangChain — LangChain's job stops at "send this, get that back."

### 1.4 The primary/fallback pattern

Real API calls sometimes fail — rate limits, timeouts, a model being temporarily overloaded. This project wraps every `.invoke()` call in a small helper that tries a second, cheaper model if the first one fails:

```python
# chargeback_agent.py's DisputeAgent._invoke() — the real code
def _invoke(self, messages: list) -> object:
    try:
        return self._llm.invoke(messages)
    except Exception as primary_err:
        try:
            return self._fallback_llm.invoke(messages)
        except Exception:
            raise primary_err
```

Every node in the graph that needs the LLM calls `self._invoke(messages)` instead of touching a chat model directly — so this fallback behavior is automatic everywhere, not something each node has to remember to implement itself.

### 1.5 Getting structured data back, safely

An LLM's raw output is text. When you actually need *data* — a list of evidence tags, a yes/no flag — you ask the model to reply in JSON (as in the system prompt example above) and then parse that string. But LLMs occasionally wrap JSON in markdown fences, add a stray sentence before it, or otherwise produce something `json.loads()` chokes on. This project never lets a parse failure crash a request — `guardrails.py`'s `_parse_json_safe()` tries to parse, and returns a safe fallback value if it can't:

```python
# The real pattern, used throughout chargeback_agent.py
response = self._invoke([...])
fallback = {"evidence_present": [], "evidence_missing": [], "needs_more_info": False}
data = _parse_json_safe(response.content, fallback)
evidence_present = data.get("evidence_present", [])
```

If the model's JSON is malformed, the merchant sees "no evidence identified yet" instead of the whole request crashing with a Python exception. Small detail, but it's the difference between a graceful degradation and a 500 error in production.

### 1.6 Tool calling — letting the model ask for real data

Everything above (`SystemMessage`/`HumanMessage`/JSON-parsing) is how most of this project's LLM calls work — but it has a real limit: the model can only reason about text you already put in front of it. It cannot look anything up itself.

**Tool calling** solves that. You describe a set of functions to the model (name, arguments, a docstring explaining when to use it) via `.bind_tools([...])`. The model doesn't run those functions — it can't; it has no code execution ability — it can only reply "please call `get_case_details` with `case_id="NPCI2026..."`" and hand that decision back to you as structured data. Your own code then actually runs the real function, and feeds the result back to the model as a new message so it can continue reasoning with real information instead of guessing.

This project added this pattern for exactly one class of problem: deciding what a merchant means by a message like *"what all U002 cases exist currently?"* or *"tell me about the first one."* Regex-based intent detection (`classifier.is_case_list_request()`, since removed) kept breaking on new phrasings — every fix caught one pattern and missed the next. Tool calling lets the model itself decide, in natural language, which real lookup (if any) a message is asking for.

```python
# chargeback_agent.py — the actual tool definitions
from langchain_core.tools import tool

@tool
def list_merchant_cases(reason_code: str = "") -> str:
    """List the merchant's own open chargeback cases so they can be shown
    or picked from, optionally filtered to one reason code (e.g. U002).
    Use this when the merchant wants to SEE or SELECT a case."""
    return ""   # never executed — see below for why

@tool
def query_chargeback_data(question: str) -> str:
    """Answer an analytical/aggregate question about the merchant's own
    chargeback data (totals, counts, amounts due) by running it against
    the database. Use this for computed numbers, not for listing cases."""
    return ""
```

Notice the function **bodies are empty** and never run. `@tool` only uses the function's name, argument types, and docstring to build a schema the model reads — the docstring is literally the instructions the model uses to decide *when* to call this tool, so wording it precisely matters as much as wording a `SystemMessage` does. The real logic lives in this project's own code, dispatched manually once the model's decision comes back:

```python
# A trimmed version of _resolve_data_lookup_intent()
ai_msg = self._invoke_with_tools(messages, [list_merchant_cases, query_chargeback_data])
messages.append(ai_msg)

if not ai_msg.tool_calls:
    return None   # the model decided neither tool applies — not a data-lookup query

tool_call = ai_msg.tool_calls[0]   # {"name": "list_merchant_cases", "args": {...}, "id": "..."}

if tool_call["name"] == "list_merchant_cases":
    reason_code = tool_call["args"].get("reason_code", "")
    cases = self._filtered_open_cases(merchant_id, reason_code)   # the REAL lookup
    messages.append(ToolMessage(
        content=f"Found {len(cases)} matching case(s).",
        tool_call_id=tool_call["id"],   # links this result back to that specific call
    ))
```

Three new pieces beyond what Part 1 already covered:

- **`.bind_tools([...])`** — attaches the tool schemas to a chat model before `.invoke()`. `_invoke_with_tools()` is this project's own thin wrapper mirroring `_invoke()`'s primary/fallback pattern, just with tools bound on both models.
- **`AIMessage.tool_calls`** — when the model decides to use a tool instead of (or before) answering directly, its response (`ai_msg` above) carries a `tool_calls` list instead of, or alongside, plain text content. Each entry has the tool's `name`, the `args` the model chose to pass, and an `id`.
- **`ToolMessage`** — the message type you append *after* actually running the real function, carrying the result back into the conversation and referencing which `tool_call_id` it's answering. This is what makes the model's next `.invoke()` call (if there is one) aware of what the tool actually returned.

**Multi-round tool calling.** One case in this project needs more than one round: `_build_case_intro()` (built for "tell me about the first one" landing on a real case) gives the model two tools, `get_case_details` and `get_reason_code_info` — but `get_reason_code_info` needs a `reason_code` argument the model can't know until it's seen `get_case_details`' result. Confirmed live before writing this: given both tools in a single round, the model correctly calls only `get_case_details` first, rather than guessing. The fix is a capped loop, not a single call:

```python
# A trimmed version of _build_case_intro()'s loop
for _ in range(4):                                            # capped, never unbounded
    ai_msg = self._invoke_with_tools(messages, [get_case_details, get_reason_code_info])
    messages.append(ai_msg)
    if not ai_msg.tool_calls:
        break                                                  # model is done — has its final answer
    for tc in ai_msg.tool_calls:
        result = <run the real function for tc["name"]>
        messages.append(ToolMessage(content=result, tool_call_id=tc["id"]))
# messages now holds: SystemMessage, HumanMessage, AIMessage(tool_calls=[get_case_details]),
#                      ToolMessage(case details), AIMessage(tool_calls=[get_reason_code_info]),
#                      ToolMessage(reason-code info), AIMessage(final prose answer, no more tool_calls)
```

Each iteration re-invokes the model with everything learned so far appended to the message list — invoke → execute whatever it asked for → append the result → invoke again — until it stops asking for tools (or the cap is hit, at which point one final tool-free call forces a synthesis rather than returning empty scaffolding).

**Where this fits the project's "rule-based over LLM-based" philosophy** (see `README.md`'s Design principles): tool calling is still the *expensive, judgment-call* option, reserved for genuinely open-ended intent detection. It is not automatically trusted for every phrasing, either — a later fix added a narrow, deterministic **short-circuit** ahead of the tool-calling decision for financial-balance questions ("how much is outstanding," "what do I owe"), after live testing showed the model's tool-calling choice for that exact phrasing wasn't perfectly reproducible run to run (`classifier.looks_like_aggregate_question()`, checked before `_invoke_with_tools()` is ever called). The lesson generalizes: even inside an LLM-decision layer, carve out the well-defined slices back into plain code wherever you can — reserve the model's judgment for the genuinely ambiguous remainder.

## Part 2: LangGraph — orchestrating many steps

### 2.1 Why not just one big prompt?

You *could* try to solve the whole dispute flow with one giant prompt: "here's the merchant's message, figure out the network, the code, the evidence, the decision, and write a letter, all in one shot." Two problems with that:

1. **The model has to be right about everything at once.** One bad guess early (wrong reason code) corrupts everything downstream, and you have no way to catch it mid-stream.
2. **You lose the ability to skip the model entirely for parts that don't need it.** Deciding fight-vs-refund for a well-known reason code is a lookup-table problem (`decision_rules.py`), not a reasoning problem — no need to spend an LLM call on it.

LangGraph solves this by making the process explicit: a sequence of small, independently-testable steps, some of which call an LLM and some of which don't, with real Python logic deciding what happens next.

### 2.2 State — the shared notebook

Every LangGraph workflow has one **state** shape — a dictionary-like object that every node can read from and write to. This project defines it as a `TypedDict` (a Python type that says "this dict will have exactly these keys, with these types" — useful for editor autocomplete and catching typos, though Python doesn't enforce it at runtime):

```python
# A trimmed version of chargeback_agent.py's real ChargebackState
class ChargebackState(TypedDict):
    user_query:            str          # the merchant's original message
    additional_context:    str          # their reply to a follow-up question
    reason_code:           str          # e.g. "13.1" — filled in partway through
    card_network:          str          # e.g. "Visa"
    evidence_present:      List[str]    # filled in partway through
    decision:               str         # "fight" or "refund" — filled in partway through
    final_answer:            str        # the finished output
    # ...and more — see the real file for the full ~20-field shape
```

Think of it as a form that starts almost entirely blank and gets filled in, field by field, as it passes through the graph — never all at once.

### 2.3 Nodes — one job each, no branching inside

A **node** is just a Python function (or, here, a method) that takes the current state and returns a dictionary of the fields it wants to *update*. It does NOT return the whole state — LangGraph merges whatever you return on top of the existing state automatically.

```python
# A simplified version of _detect_settlement_node
def _detect_settlement_node(self, state: ChargebackState) -> dict:
    query = state["user_query"]
    is_settlement = classifier.detect_settlement_issue(query)   # plain regex — no LLM
    return {"is_settlement_issue": is_settlement}
```

Notice this particular node doesn't call an LLM at all — it just runs a regex check from `classifier.py` and hands back one field. Compare that to `_extract_evidence_node` from Part 1, which *does* call the LLM. Both are equally valid nodes; LangGraph doesn't care what happens inside one, only that it's a function taking state and returning a partial update.

**Rule this project follows strictly:** a node never decides what runs next. That decision lives entirely in separate routing functions (next section) — so you can look at one node and know exactly what it does, without also having to trace where control flow might jump.

### 2.4 Edges — plain vs. conditional

An **edge** connects two nodes: "after node A finishes, run node B." There are two kinds:

**Plain edges** — always go to the same next node, no decision involved:

```python
graph.add_edge("generate", "reflect")   # after generate, always run reflect
```

**Conditional edges** — a separate routing function looks at the current state and returns the *name* of whichever node should run next:

```python
# The real routing function that decides what happens after extract_code
@staticmethod
def _route_after_extract_code(state: ChargebackState) -> Literal["ask_user", "detect_clarification"]:
    reason_code = state.get("reason_code", "Unknown") or "Unknown"
    context     = state.get("additional_context", "")
    if reason_code == "Unknown" and not context:
        return "ask_user"              # we still don't know the code — ask for it
    return "detect_clarification"      # we have enough — move on

# Wiring it into the graph:
graph.add_conditional_edges(
    "extract_code", self._route_after_extract_code,
    {"ask_user": "ask_user", "detect_clarification": "detect_clarification"},
)
```

The third argument to `add_conditional_edges` is a mapping from the routing function's possible return values to actual node names — it's how LangGraph knows `"ask_user"` (the string) means "go run the node registered under the name `"ask_user"`."

This is also where this project's non-LLM, rule-based checks earn their keep the most: `_route_after_extract_code` is pure Python — no model call, no cost, instant — deciding something that genuinely needs deciding every single turn.

### 2.5 Entry point and `END`

Every graph needs a starting node and a way to say "we're done":

```python
graph.set_entry_point("validate")   # every run starts here

graph.add_edge("ask_user", END)     # END is a special LangGraph sentinel —
                                     # reaching it means this run is finished
```

`END` isn't a real node with logic in it — it's a marker LangGraph recognizes to stop executing and return whatever the state looks like at that point.

### 2.6 Compiling and running

Before a `StateGraph` can actually run, you call `.compile()` on it, which validates the whole wiring (every node reachable, every conditional edge's possible outputs actually mapped to a real node) and returns a runnable object:

```python
graph = StateGraph(ChargebackState)
graph.add_node("validate", self._validate_node)
# ...register every other node...
graph.set_entry_point("validate")
# ...wire every edge...
compiled = graph.compile()
```

Running it is one call — `.invoke()`, same name as the chat-model method from Part 1, but this is LangGraph's own `.invoke()` on the *compiled graph*, not on a model:

```python
# A simplified version of DisputeAgent.run()
initial_state = {"user_query": query, "additional_context": additional_context, ...}
result = self._graph.invoke(initial_state)
# result is the final state — read result["final_answer"], result["decision"], etc.
```

You hand it a starting state (usually mostly blank), and LangGraph runs node after node — following plain edges automatically, calling routing functions wherever there's a conditional edge — until execution reaches `END`, then hands you back whatever the state looks like at that point.

### 2.7 Checkpointers — an honest note, updated

LangGraph supports an optional **checkpointer**: a way to save the state after each node runs, so a *later* `.invoke()` call with the same `thread_id` can resume mid-conversation instead of starting over. `DisputeAgent` accepts one and passes it into `.compile(checkpointer=self._checkpointer)`.

This is a real, live piece of infrastructure now, not a hypothetical: `api_server.py` constructs an actual `SqliteSaver` on startup (`checkpoints.db`, in local file mode — see `.gitignore`, which excludes it and its WAL sidecar files as regenerable/runtime state) and passes it into `build_dispute_agent(checkpointer=_checkpointer)`. Every `/dispute` response includes a `thread_id`, generated server-side and scoped to the caller's identity (`{merchant_id}:{uuid4}` — checked on the way back in, so one merchant can't resume a session that belongs to another).

**But it still isn't what makes multi-turn conversations work in this app.** Confirmed by reading `chat.html`: the browser never reads or resends the `thread_id` the server returns. Since `run()` generates a brand-new UUID whenever no `thread_id` is supplied (`if not thread_id: thread_id = str(uuid.uuid4())`), and the browser never supplies one, every single `/dispute` call is, from the checkpointer's point of view, the *first* message of a brand-new thread — there is never a second `.invoke()` call on the same `thread_id` for it to resume. The checkpointer faithfully writes a fresh entry to `checkpoints.db` on every call and none of them are ever read back.

Multi-turn conversations work anyway, through a *completely separate*, simpler mechanism: `chat.html` itself remembers the original question (`pendingQuery`, set once and never touched again while the agent keeps asking follow-ups) and re-sends it verbatim on every subsequent call, along with every follow-up reply joined together as `additional_context`. `_validate_node` re-derives whatever it needs (which case was being discussed, whether a reply resolves to a specific case selection, etc.) fresh from that resent text on every single call — there is no persisted memory across calls at all, LangGraph-native or otherwise.

Why this matters in practice: it's the reason a case-selection sub-conversation can lose context after several turns (see `README.md`'s note on the Dispute Assistant's known limitation) — nothing is actually "remembered" server-side; everything downstream is re-derived from whatever text the browser happens to resend, and that resending logic has its own edge cases (e.g. a "complete" answer resets `chat.html`'s state entirely, discarding `pendingQuery` even mid-topic).

Two honest takeaways: (1) a library offering a feature doesn't mean a project actually exercises it — the checkpointer here is correctly wired but functionally inert; (2) `thread_id` earns its keep anyway, just for a different reason than resumption — it's a security-scoping token (so a guessed/leaked `thread_id` can't be replayed against another merchant's identity), independent of whether anything ever actually resumes on it.

## Part 3: Walking through one real request

Let's trace an actual message end-to-end: **"Mastercard chargeback — customer says the charge is fraudulent but they placed the order using our 3D Secure checkout."**

```
1. graph.invoke({"user_query": "Mastercard chargeback...", "additional_context": "", ...})

2. validate_node runs:
   - length check, prompt-injection check — both pass
   - classifier.classify_query_type(...) → "dispute" (not just a policy question)
   - returns {"is_valid_query": True, "query_type": "dispute", ...}

3. _route_after_validate looks at query_type="dispute" → returns "classify"
   → LangGraph runs the node registered under "planner"

4. planner_node runs:
   - classifier.extract_network_and_code(...) → ("Mastercard", "Unknown")
     (no explicit code number in the text, so code stays Unknown for now)
   - runs a Qdrant similarity search for relevant Mastercard fraud policy docs
   - returns {"card_network": "Mastercard", "reason_code": "Unknown",
              "retrieved_docs": [...]}

5. planner → detect_settlement (plain edge, always runs next)

6. detect_settlement_node runs:
   - classifier.detect_settlement_issue(...) → False (this is a real dispute,
     not a missing-payment complaint)
   - returns {"is_settlement_issue": False}

7. _route_after_detect_settlement: not a settlement issue → "extract_code"

8. extract_code_node runs:
   - reason_code is still "Unknown", additional_context is still empty
   - sets missing_info_question to "please share the reason code..."
   - returns {"reason_code": "Unknown", "missing_info_question": "..."}

9. _route_after_extract_code: reason_code=="Unknown" and no context → "ask_user"

10. ask_user_node runs:
    - returns {"final_answer": "I still need one key detail...", "needs_more_info": True}

11. edge to END — this run stops here.
```

`api_server.py` sends that `final_answer` back to the browser as the follow-up question. When the merchant replies (say, "fraud, and yes we have 3DS authentication"), the browser calls `/dispute` *again* — a brand-new `graph.invoke()` — but this time with `additional_context` filled in, so at step 8, `extract_code_node` finds a real code this time, `_route_after_extract_code` sends it to `"detect_clarification"` instead of back to `"ask_user"`, and the graph continues on into evidence extraction, the fight/refund decision, and (if fighting) drafting the actual letter — each of those exactly as described in Parts 1 and 2 above.

### 3.1 A second trace: tool calling across several turns

This one covers a different, newer path — the case-listing/case-intro conversation, entirely inside `_validate_node`, using the tool-calling pattern from Part 1.6. It never reaches `planner_node`/`decide_node` at all when it resolves cleanly.

```
Turn 1 — "show me my open chargebacks"

1. validate_node runs. additional_context is empty (first turn), so the
   continuity block is skipped entirely — nothing to resolve yet.
2. classify_query_type(...) → "question"
3. _route_after_validate → "answer_question" → _answer_question_node runs
4. classifier.looks_like_data_lookup(query) → True (matches "chargebacks")
5. _resolve_data_lookup_intent(merchant_id, query) runs:
     - builds [SystemMessage(...), HumanMessage("show me my open chargebacks")]
     - self._invoke_with_tools(messages, [list_merchant_cases, query_chargeback_data])
     - model's AIMessage comes back with tool_calls=[{"name": "list_merchant_cases",
       "args": {"reason_code": ""}, "id": "call_1"}]
     - real function runs: merchant_db.list_open_chargebacks(merchant_id)
     - ToolMessage(content="Found 7 matching case(s).", tool_call_id="call_1") appended
     - returns {"type": "list", "reason_code": ""}
6. _answer_question_node deterministically renders the 7 cases (soonest
   deadline first) and asks which one — {"needs_more_info": True, ...}
7. edge to END. api_server.py returns final_answer + needs_more_info=True.

Turn 2 — chat.html resends {query: "show me my open chargebacks",
          additional_context: "tell me about the first one"}

1. validate_node runs. additional_context is non-empty this time, so the
   continuity block DOES run:
     - looks_like_data_lookup(masked_query) → True
     - _resolve_data_lookup_intent(merchant_id, masked_query) → same
       list-tool-call decision as turn 1 (this masked_query is still the
       "show me my open chargebacks" text) → {"type": "list", "reason_code": ""}
     - classifier.detect_case_selection("tell me about the first one",
       shown_cases) → resolves to the real case_id (ordinal "first" +
       shown_cases sorted soonest-deadline-first)
2. _build_case_intro(merchant_id, resolved_case_id) runs — the
   multi-round loop from Part 1.6: get_case_details, then
   get_reason_code_info once the reason code is known, then a final
   prose synthesis with no more tool_calls.
3. _validate_node returns EARLY (mirrors the length-check/prompt-
   injection guards from Part 2's step 2) with final_answer already set,
   no query_type — so _route_after_validate sees query_type="" (the
   TypedDict default), falls through its if/if chain, and returns "end".
4. edge to END. The merchant sees a case summary + reason-code
   explanation + evidence ask, in one turn — no separate trip through
   planner_node/extract_evidence_node needed for this landing turn.
```

The interesting LangGraph point here: none of this needed a new node, edge, or state field. `_validate_node` — already the very first node in the graph — is where all of it lives, because an early `return {...}` with no `query_type` set is a pattern the graph already understood (`_route_after_validate` already treats a missing/empty `query_type` as "route to end"). The tool-calling loop itself is plain Python inside that one node's method body, not graph structure.

## Concept coverage: what this project uses, and what it doesn't

LangChain and LangGraph offer a lot more than what's used here. This section is an honest map — verified against the real code (greps, not memory) rather than assumed — of which parts of a broader LangGraph curriculum this project actually demonstrates, which it only approximates with hand-written code, and which it doesn't touch at all. Useful if you're learning LangGraph and want to know which of this codebase's patterns are "the real primitive" versus "a project-specific workaround that looks similar."

**Solidly used, the real primitive:**

- **Core graph mechanics** — `StateGraph`, `add_node`, `add_edge`, `add_conditional_edges`, `set_entry_point`, `END` (Part 2 above, in full).
- **Messages** — `SystemMessage`, `HumanMessage`, `AIMessage`, `ToolMessage` (Parts 1 and 1.6). Not `MessagesState`, though — state here is a custom `TypedDict` (`ChargebackState`), not LangGraph's prebuilt message-list state shape.
- **Conditional routing** — every `_route_after_*` function (§2.4).
- **Tool calling** — `@tool`, `.bind_tools()`, `AIMessage.tool_calls` (§1.6) — via raw LangChain, not LangGraph's prebuilt `ToolNode`/agent-executor. A code comment right above the tool definitions in `chargeback_agent.py` says so explicitly: this project dispatches tool calls by hand because it only has two decision points that need it, not enough to justify the prebuilt machinery.
- **RAG as graph nodes** — `planner_node` and `_answer_question_node` both do real vector retrieval as part of node logic (Part 3's first trace).
- **Hybrid retrieval + reranking** — `vector_store.hybrid_search()` (vector + BM25) and a cross-encoder rerank step, both real, both load-bearing for retrieval quality.
- **Fallback models** — `_invoke()`'s primary→fallback pattern (§1.4) — a genuine reliability mechanism, not just described.
- **A hand-rolled agentic loop** — `_build_case_intro()`'s capped multi-round tool-calling loop (§1.6) is a real invoke → act → observe → repeat pattern with a stopping condition, just written directly rather than via `create_react_agent`.
- **Guardrails** — prompt-injection detection, PII masking, rate limiting, a cost circuit breaker, role-based SQL scoping (`guardrails.py`, `auth.py`, `text_to_sql.py`) — all real, all enforced in code, not just prompted for.

**Present as infrastructure, but not actually exercised:**

- **Checkpointing** — a real `SqliteSaver` is wired up and every response carries a `thread_id` (§2.7), but `chat.html` never resends that `thread_id`, so nothing ever resumes from a saved checkpoint. Verified by grepping `chat.html` for `thread_id` — zero hits. `thread_id`'s actual job today is security scoping, not resumption.

**Approximated with project-specific code, not the LangGraph-native version:**

- **"Pause and resume" conversations** — real and working, but achieved by the graph run ending (`needs_more_info: True`) and the *browser* re-sending accumulated text on the next call — not LangGraph's `interrupt()`/`NodeInterrupt` primitive, which this project doesn't use at all.
- **Query routing** — `classify_query_type()` plus the tool-calling intent decision act as a router, but as conditional edges inside one graph, not a "supervisor agent" orchestrating separate sub-agents.
- **Human-in-the-loop, at the business level** — `auto_decision_poller.py` (auto-applies a recommendation) versus `suggestion_poller.py` (advisory only, a human decides) is a genuine HITL *pattern*, and there's a canned "talk to a human" escalation response — but neither uses LangGraph's interrupt/approval/resume primitives.

**Not used at all, verified by direct inspection:**

- **Custom reducers** — zero uses of `Annotated`/`operator.add`/`add_messages` anywhere in `chargeback_agent.py`. Every state field is plain last-write-wins overwrite, described precisely in §2.7's surrounding discussion of LangGraph's merge behavior.
- **In-graph cycles/loops** — the graph is a DAG; no edge ever routes back to an earlier node. The 4-round loop in `_build_case_intro()` is a plain Python `for` loop inside one node's method body, not a graph-level cycle.
- **Self-correcting retry loops** — `reflect_node` scores groundedness and confidence but has only one outgoing edge, straight to `END`. A low-confidence or ungrounded result is reported, never fed back into another retrieval/generation attempt. `planner_node` now does compute a real retrieval-sufficiency SIGNAL (`retrieval_evaluator.evaluate_retrieval()` — checks whether the retrieved documents' own `network` payload field actually matches the network just detected for the query, not just whether they scored well on similarity) and writes it to `retrieval_status`/`retrieval_issues` — but nothing yet routes on it or retries retrieval when it comes back "bad." That's a deliberate first step (an evaluator with no corrective action wired to it yet), not the same thing as a correction loop.
- **Subgraphs** — exactly one `StateGraph(ChargebackState)` exists in the whole file; no nested or composed graphs.
- **Multi-agent architectures** — one agent (`DisputeAgent`), many nodes. No agent-to-agent handoff, no separate policy/evidence/transaction agents collaborating.
- **Formal query rewriting** — the closest is `planner_node`'s step 3, which concatenates `f"{network} {code} {query}"` for a supplemental search; there's no LLM-driven query expansion/rewrite step.
- **Tracing/observability tooling** — `AuditLogger` logs query, decision, and latency per request (real, but simple), but there's no LangSmith or comparable tracing integration anywhere in the repo.

If you're using this project to practice LangGraph concepts you haven't built yet, the gaps above — subgraphs, multi-agent collaboration, real `interrupt()`-based HITL, a self-correcting RAG retry loop, custom reducers — are the genuinely open territory; everything else on this list is already a working, real example to read.

## Quick glossary

| Term | Plain-English meaning | Where in this project |
|---|---|---|
| Chat model | An object representing one specific AI model you can send messages to | `ChatGroq`/`ChatOpenAI` in `llm_provider.py` |
| `SystemMessage` | Instructions for how the model should behave this call | Every LLM-calling node in `chargeback_agent.py` |
| `HumanMessage` | The actual question/content being sent | Same |
| `.invoke()` (on a model) | Send the messages, get a response back | `DisputeAgent._invoke()` |
| State | The shared dict every node reads from and writes to | `ChargebackState` (a `TypedDict`) |
| Node | One step — a function taking state, returning a partial update | `_validate_node`, `_planner_node`, etc. |
| Edge | "After this node, run that node" | `graph.add_edge(...)` |
| Conditional edge | "After this node, run whichever node this function says to" | `graph.add_conditional_edges(...)`, the `_route_after_*` functions |
| Entry point | The node a graph run always starts at | `graph.set_entry_point("validate")` |
| `END` | A sentinel meaning "this run is finished" | Used throughout `_build_graph()` |
| `.compile()` | Validates the graph's wiring, returns a runnable object | `_build_graph()`'s last line |
| `.invoke()` (on a graph) | Run the whole graph from the entry point to `END` | `DisputeAgent.run()` |
| Checkpointer | Save/resume state across separate `.invoke()` calls, keyed by `thread_id` | Real `SqliteSaver` wired in `api_server.py` (`checkpoints.db`) — but functionally inert, since `chat.html` never resends the `thread_id` needed to resume (see §2.7) |
| `@tool` | Decorator that turns a Python function into a tool schema the model can request — its body is never executed by the framework | `list_merchant_cases`, `query_chargeback_data`, `get_case_details`, `get_reason_code_info` in `chargeback_agent.py` |
| `.bind_tools([...])` | Attaches tool schemas to a chat model before `.invoke()` | `DisputeAgent._invoke_with_tools()` |
| `AIMessage.tool_calls` | The model's response, when it chooses to request a tool instead of/alongside answering directly — a list of `{name, args, id}` | Read in `_resolve_data_lookup_intent()` and `_build_case_intro()` |
| `ToolMessage` | The message you append after actually running the real function, carrying its result back to the model, linked via `tool_call_id` | Same two methods |

## Where to look in the code

- **`chargeback_agent.py`** — everything described in this document lives here. Search for `_build_graph` to see the whole graph wired up in one place; search for any `_route_after_*` function to see a routing decision; search for `self._invoke(` to find every plain LLM call, and `self._invoke_with_tools(` for every tool-calling one.
- **`llm_provider.py`** — the LangChain chat-model construction (`ChatGroq`/`ChatOpenAI`), and the provider-switching logic from Part 1.
- **`guardrails.py`** — `_parse_json_safe()`, the safe-JSON-parsing helper from Part 1.5.
- **`classifier.py`** / **`decision_rules.py`** — the plain-Python (no LangChain, no LangGraph, no LLM) logic that several nodes call into, worth reading side-by-side with the nodes that use them to see the "rule-based over LLM-based" split in action — including `looks_like_data_lookup()` (a cheap pre-filter before spending a tool-calling round) and `looks_like_aggregate_question()` (a deterministic short-circuit that skips tool calling entirely for one narrow, well-defined phrasing — see Part 1.6's closing note).
- **`_resolve_data_lookup_intent()`** and **`_build_case_intro()`** — the two real tool-calling call sites, single-round and multi-round respectively; read them side-by-side with Part 1.6.
- **`README.md`** — the full project architecture and every module's purpose, one level up from this document's LangChain/LangGraph-specific focus.
