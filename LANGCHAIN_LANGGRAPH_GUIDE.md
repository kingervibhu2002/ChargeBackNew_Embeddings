# LangChain & LangGraph, Explained Through This Project

This document explains what LangChain and LangGraph actually *do* — not in the abstract, but by pointing at the real code in `chargeback_agent.py` that uses them. If you've never touched either library before, read this top to bottom. If you already know them, skip to [Part 3](#part-3-walking-through-one-real-request) for the concrete trace, or the [glossary](#quick-glossary) for a fast lookup.

No prior LangChain/LangGraph knowledge assumed. Basic Python (functions, dictionaries, classes) is enough.

---

## Table of contents

1. [The big picture](#the-big-picture)
2. [Part 1: LangChain — talking to a model](#part-1-langchain--talking-to-a-model)
3. [Part 2: LangGraph — orchestrating many steps](#part-2-langgraph--orchestrating-many-steps)
4. [Part 3: Walking through one real request](#part-3-walking-through-one-real-request)
5. [Quick glossary](#quick-glossary)
6. [Where to look in the code](#where-to-look-in-the-code)

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

### 2.7 Checkpointers — an honest note

LangGraph supports an optional **checkpointer**: a way to save the state after each node runs, so a *later* `.invoke()` call with the same `thread_id` can resume mid-conversation instead of starting over. `DisputeAgent` accepts one (`checkpointer=None` by default) and passes it into `.compile(checkpointer=self._checkpointer)`.

Worth knowing as a real-world lesson: this project's API layer (`api_server.py`) doesn't currently wire a `thread_id` through from the browser, so every `/dispute` call effectively starts a fresh graph run regardless. Multi-turn conversations still work — but through a *simpler* mechanism: the browser (`chat.html`) itself remembers the original question and re-sends it, along with the merchant's follow-up reply, as the `additional_context` field on the next call. The checkpointer machinery is there and correctly wired, but this particular app doesn't currently lean on it. A good reminder that a library offering a feature doesn't mean every project built with it uses that feature.

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
| Checkpointer | Optional: save/resume state across separate `.invoke()` calls | Accepted by `DisputeAgent`, not currently exercised by `api_server.py` |

## Where to look in the code

- **`chargeback_agent.py`** — everything described in this document lives here. Search for `_build_graph` to see the whole graph wired up in one place; search for any `_route_after_*` function to see a routing decision; search for `self._invoke(` to find every LLM call in the project.
- **`llm_provider.py`** — the LangChain chat-model construction (`ChatGroq`/`ChatOpenAI`), and the provider-switching logic from Part 1.
- **`guardrails.py`** — `_parse_json_safe()`, the safe-JSON-parsing helper from Part 1.5.
- **`classifier.py`** / **`decision_rules.py`** — the plain-Python (no LangChain, no LangGraph, no LLM) logic that several nodes call into, worth reading side-by-side with the nodes that use them to see the "rule-based over LLM-based" split in action.
- **`README.md`** — the full project architecture and every module's purpose, one level up from this document's LangChain/LangGraph-specific focus.
