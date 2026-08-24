# `decision_rules.py`, Explained

`decision_rules.py` answers exactly one question, for exactly one class of chargeback: **given a card network, a reason code, and whatever evidence the merchant has, should they fight this dispute or accept the refund?** This document explains how it answers that question, why it's shaped the way it is, and the real bugs its current shape was built to fix.

No prior context assumed beyond basic Python (dataclasses, sets, dicts).

---

## Table of contents

1. [Why a lookup table instead of an LLM call](#why-a-lookup-table-instead-of-an-llm-call)
2. [The `DecisionRule` shape](#the-decisionrule-shape)
3. [Reading the table: four representative entries](#reading-the-table-four-representative-entries)
4. [The Mastercard 4853 problem: one code, six disputes](#the-mastercard-4853-problem-one-code-six-disputes)
5. [`decide()`: the precedence order, step by step](#decide-the-precedence-order-step-by-step)
6. [The evidence-free quirk: why background automation can never "fight"](#the-evidence-free-quirk-why-background-automation-can-never-fight)
7. [Where this gets called from](#where-this-gets-called-from)
8. [Real bugs this table's current shape was built to fix](#real-bugs-this-tables-current-shape-was-built-to-fix)
9. [Adding a new rule](#adding-a-new-rule)
10. [Testing](#testing)
11. [Where to look in the code](#where-to-look-in-the-code)

---

## Why a lookup table instead of an LLM call

For a *known* reason code, "should the merchant fight this" isn't actually a reasoning problem — it's "does the merchant have tag X, Y, or Z." A Visa `13.1` (item not received) dispute is winnable with delivery proof and isn't without it. That's a fact about how Visa's dispute process works, not something that benefits from being re-derived by an LLM on every single case.

So this project encodes that fact once, by hand, as data — a `Dict[(network, reason_code), DecisionRule]` — and looks it up instead of asking a model to figure it out fresh each time. This buys three things an LLM call can't:

- **Determinism.** The same evidence for the same code always produces the same decision. An LLM asked "should this merchant fight?" can (and, per the real incidents in [§8](#real-bugs-this-tables-current-shape-was-built-to-fix), did) waffle between runs on identical input.
- **Zero cost, zero latency.** A dict lookup, not an API call.
- **Testability.** `test_decision_rules.py` asserts exact outcomes for exact inputs — you cannot write that kind of test against a model's free-text judgment.

This isn't a claim that *every* reason code can be reduced to a lookup table — the module docstring is explicit that unmapped codes "fall through to the existing LLM call in `chargeback_agent.py`," and `decide()` returns `None` rather than guessing when a code isn't in `RULES`. The table only covers codes someone has actually sat down and worked out the real evidence requirements for. It's additive, not a replacement for the LLM path — and deliberately *not* derived automatically from the 149-document knowledge base, because those documents use two incompatible YAML frontmatter schemas (some carry `network`/`reason_code` fields, others carry `description`/`chargeback_type`/`win_rate` with neither) — an automated extraction pass would need its own normalization layer first, which was out of scope when this table was built.

## The `DecisionRule` shape

```python
@dataclass(frozen=True)
class DecisionRule:
    required_any:  Set[str] = field(default_factory=set)
    required_all:  Set[str] = field(default_factory=set)
    disqualifying: Set[str] = field(default_factory=set)
    always_refund: bool = False
    fight_reason:  str = ""
    refund_reason: str = ""
```

Each field answers a different question about one `(network, reason_code)` pair:

| Field | Question it answers | Example |
|---|---|---|
| `required_any` | Is **at least one** of these evidence tags present? If so, that alone is enough to fight. | Visa `13.1`: any one of tracking number, delivery confirmation, signature, or door photo. |
| `required_all` | Are **every one** of these tags present? Used *alongside* `required_any` for an "and" condition — leave empty if there's no such requirement. | Not currently used by any entry in the table, but exists for a future code that genuinely needs two independent proofs together. |
| `disqualifying` | Is **any** of these tags present? If so, always refund — **regardless of `required_any`/`required_all`.** | Visa `13.1`: if `refund_already_issued` is present, the dispute is moot no matter what delivery evidence also exists. |
| `always_refund` | Does the merchant's own evidence even matter here? If `True`, skip evidence-checking entirely. | RuPay `U010` (technical/system failure) — liability is NPCI's/the bank's by the reason code's own definition, not a function of anything the merchant could prove. |
| `fight_reason` / `refund_reason` | The human-readable explanation shown to the merchant for whichever outcome was reached. | — |

The `frozen=True` on the dataclass means a `DecisionRule` instance can't be mutated after construction — appropriate for something that's meant to be static configuration data, not runtime state.

**The `always_refund` field deserves its own note**, because it's easy to assume it's redundant with just leaving `required_any` empty. It isn't — and this distinction is load-bearing. `decide()` treats an *empty* `required_any` as "trivially satisfied" (see [§5](#decide-the-precedence-order-step-by-step)), which resolves to **fight**. `always_refund=True` means the opposite: no evidence changes anything, full stop. These represent two genuinely different real-world situations — "we haven't bothered specifying evidence requirements for this code" (a gap to fill in) versus "there is no evidence requirement, by design, because liability doesn't depend on the merchant's evidence at all" (a fact about the code). Conflating them would have meant every `always_refund` code silently defaulting to "fight" instead.

## Reading the table: four representative entries

**A simple `required_any` + `disqualifying` case** — Visa `13.1`, "item not received":

```python
("Visa", "13.1"): DecisionRule(
    required_any={"tracking_number", "delivery_confirmation", "signature_confirmation", "photo_at_door"},
    disqualifying={"refund_already_issued"},
    fight_reason="Proof of delivery (tracking, signature, or photo) directly rebuts an item-not-received claim.",
    refund_reason="No delivery evidence on file — a 13.1 claim cannot be rebutted without proof the item reached the customer.",
),
```
Any one delivery-proof tag → fight. But if the merchant already refunded the customer (whether or not delivery proof also exists) → refund anyway, because fighting a dispute you've already resolved makes no sense.

**An `always_refund` case** — RuPay `U010`, "technical error / system failure":

```python
("RuPay", "U010"): DecisionRule(
    always_refund=True,
    refund_reason="U010 is a technical/system failure — NPCI attributes liability to the bank or PSP whose system failed, not the merchant. No evidence the merchant can supply changes that; the customer should be made whole via auto-reversal or manual credit.",
),
```
No `required_any` at all — there's genuinely nothing in this project's evidence-tag vocabulary that bears on a technical failure the merchant wasn't party to. `always_refund=True` skips evidence-gathering entirely rather than asking the merchant for evidence that could never matter.

**A case where `disqualifying` carries the *entire* real-world meaning** — RuPay `U002`, "duplicate transaction":

```python
("RuPay", "U002"): DecisionRule(
    required_any={"single_credit_confirmed"},
    disqualifying={"refund_already_issued", "duplicate_charge_proof"},
    fight_reason="Records show only a single valid charge — the duplicate-transaction claim doesn't hold.",
    refund_reason="No proof on file that only one valid transaction occurred — a U002 claim cannot be rebutted without evidence the customer wasn't actually charged twice.",
),
```
Notice `duplicate_charge_proof` sits in `disqualifying`, not `required_any` — that's not an arbitrary choice, it's the whole point of the rule. `duplicate_charge_proof` means "we have proof a duplicate charge really did happen." That's evidence *for* the customer's claim, not evidence against it — so its presence should force a refund, never a fight. See [§8](#real-bugs-this-tables-current-shape-was-built-to-fix) for the real bug this was fixing.

**A rule that deliberately *doesn't* reuse another network's evidence tags** — RuPay `U005`, UPI-specific fraud:

```python
("RuPay", "U005"): DecisionRule(
    required_any={
        "beneficiary_vpa_confirmed", "merchant_kyc_verified",
        "delivery_confirmation", "service_completion_record",
    },
    fight_reason="The receiving VPA is confirmed to belong to a genuine, KYC-compliant merchant and the order was fulfilled...",
    refund_reason="No proof on file that the beneficiary VPA belongs to this registered merchant, or that the order was fulfilled...",
),
```
Every other fraud-adjacent rule in this table (Visa `10.4`, Mastercard `4837`, Amex `F29`) uses `avs_match`/`cvv_match`/`three_ds_authentication` — card-network authentication concepts. U005 deliberately does *not* reuse those, because UPI has no AVS, CVV, or 3-D Secure at all — they're card-scheme concepts that don't exist in NPCI's world. The comment above this rule in the actual source notes that the LLM fallback path was observed live suggesting exactly those card-scheme tags for a UPI dispute, before this rule existed to preempt it.

## The Mastercard 4853 problem: one code, six disputes

Every other code in this table maps one `(network, reason_code)` pair to one evidence requirement. Mastercard `4853` breaks that assumption — it's Mastercard's general-purpose "cardholder dispute" code, and covers six practically unrelated dispute types (fraud/no-authorization, credit-not-processed, not-as-described, cancelled-merchandise, digital-goods, and others) with *completely different* evidence requirements. A single `("Mastercard", "4853")` entry couldn't represent any of that correctly.

The fix: `_detect_mc_4853_subtype()` scans the dispute's free text for keyword patterns and maps `4853` to a synthetic sub-key (`"4853#credit_not_processed"`, `"4853#not_as_described"`, etc.) *before* the table lookup happens:

```python
_MC_4853_SUBTYPE_HINT_GROUPS: Dict[str, List[List[str]]] = {
    "no_cardholder_authorization": [
        ["fraud", "fraudulent", "unauthorized", "didn't authorize", ...],
    ],
    "credit_not_processed": [
        ["credit", "refund"],
        ["not processed", "never processed", "never refunded", ...],
    ],
    # ...
}

def _detect_mc_4853_subtype(context_text: str) -> Optional[str]:
    text = context_text.lower()
    for subtype, groups in _MC_4853_SUBTYPE_HINT_GROUPS.items():
        if all(any(kw in text for kw in group) for group in groups):
            return subtype
    return None
```

Each subtype's hint is a **list of groups**, and matching requires *one keyword from every group* (AND across groups) but *any* keyword within a group (OR within a group). `credit_not_processed` needs one word from `{"credit", "refund"}` *and* one phrase from `{"not processed", "never refunded", ...}` — a merchant who says "never got my refund" and one who says "credit was never processed" both match, without needing every possible phrasing spelled out as a literal string. A flat phrase list was tried first and missed common rewordings during testing — this two-group AND/OR structure is what replaced it.

`no_cardholder_authorization` is checked first in dict iteration order deliberately — a fraud claim under `4853` is handled identically to Mastercard's dedicated fraud code `4837` (authentication evidence shifts liability), so it needs first refusal before the other, more specific subtypes get a chance to match on overlapping vocabulary.

If no subtype's hint groups all match, `_detect_mc_4853_subtype()` returns `None`, and `decide()` returns `None` too — falling through to the LLM, same as any other unmapped code. A `4853` dispute the keyword groups can't classify is not silently forced into the wrong subtype's evidence requirements.

## `decide()`: the precedence order, step by step

```python
def decide(card_network, reason_code, evidence_present, evidence_missing, context_text="") -> Optional[Tuple[str, str]]:
```

1. **Resolve the lookup key.** Normally just `(network, code)`. For Mastercard `4853` specifically, first run `_detect_mc_4853_subtype()` on `context_text` and rewrite the key to `(network, "4853#<subtype>")` — or return `None` immediately if no subtype matched.
2. **Look up the rule.** `rule = RULES.get(lookup_key)`. If there's no entry at all, **return `None`** — this is the single signal the caller (`chargeback_agent.py`'s `_decide_node`) uses to know "fall through to the LLM instead."
3. **`always_refund` check, first.** If set, return `("refund", rule.refund_reason)` immediately — before even looking at what evidence was supplied. This has to be checked before the `required_any`/`required_all` logic below, because an *empty* `required_any` would otherwise be read as "trivially satisfied" and resolve to fight — exactly backwards from what `always_refund` means.
4. **`disqualifying` check, second.** If any disqualifying tag is present, return `("refund", rule.refund_reason)` — this overrides everything below it, including evidence that would otherwise be enough to fight. A merchant can have perfect delivery proof *and* have already refunded the customer; the refund wins.
5. **`required_any` / `required_all` check.** `has_any` is `True` if `required_any` is empty (nothing to satisfy) or if at least one required tag is present. `has_all` is `True` if every tag in `required_all` is present (using Python's `<=` set-subset operator). Both must hold. If so: return `("fight", ...)`, with the reason string annotated with exactly which tags matched (`humanize_evidence()` turns the raw tag names into merchant-facing labels for this).
6. **Default: refund.** If evidence didn't satisfy the rule, `decide()` doesn't return `None` and fall through to the LLM — it returns a real `("refund", rule.refund_reason)` decision. A *matched* code with insufficient evidence is a confident "not enough to fight," not an "I don't know."

The precedence is strict and intentional: `always_refund` beats `disqualifying` beats `required_any`/`required_all` beats the refund default. Reordering any of these would change real outcomes — e.g. checking `required_any` before `disqualifying` would let strong delivery evidence override a disqualifying "already refunded" tag, letting a merchant "win" a dispute they'd already resolved.

## The evidence-free quirk: why background automation can never "fight"

`decide()` has exactly one required-evidence input: `evidence_present`. Two very different callers pass very different things into it — and that difference has a real, non-obvious consequence.

- **The live chat path** (`_decide_node` in `chargeback_agent.py`) calls `decide()` with `evidence_present` built from an actual conversation — whatever the merchant told the agent they have. This can genuinely produce `"fight"`.
- **The background automation path** (`chargeback_analysis.py`'s `analyze_chargeback()`, shared by both `auto_decision_poller.py` and `suggestion_poller.py`) calls `decide()` with `evidence_present=[]` — always. There is no evidence-capture mechanism outside a live chat session; the pollers run unattended against every open case, with nobody there to ask a follow-up question.

Walk that through `decide()`'s logic: with `evidence_present` empty, `has_any` can only be `True` if `required_any` is itself empty — and no rule in the table currently leaves it empty (aside from the `always_refund` rules, which short-circuit before this check ever runs). So for **every** evidence-based rule in `RULES`, an evidence-free call falls straight through to the default: `refund`. Combined with `always_refund` rules *also* always resolving to `refund`, this means **`decision_rules.decide()` can never return `"fight"` when called with no evidence — which is exactly and only how the background pollers ever call it.**

This is documented explicitly in `chargeback_analysis.py`'s own docstring, and it's the correct behavior, not a bug: unattended automation shouldn't be deciding to fight a dispute on a merchant's behalf without any evidence to back that decision — "refund" (or `None`, for a code with no rule at all) are the only two outcomes that make sense without a human in the loop. The one exception, `analyze_chargeback()`'s CBS check (`cbs.py`'s `find_refund_for_utr()`), runs *before* `decision_rules.decide()` and can produce `"fight"` on its own — a confirmed prior refund on the exact transaction is real, database-verified evidence that doesn't require a merchant to have said anything.

## Where this gets called from

`decision_rules.py` has no callers of its own — everything below reaches into it from elsewhere:

| Call site | What it uses | Why |
|---|---|---|
| `chargeback_agent.py`'s `_extract_evidence_node` | `RULES.get((network, code))`, read-only | Looks up the rule *before* the LLM evidence-extraction call, so the LLM can be told exactly which of the ~30 possible evidence tags actually matter for this code, instead of guessing from the full flat list. Also used afterward to rewrite the LLM's own `evidence_missing` guess down to only the tags the rule actually cares about, and to deterministically force `needs_more_info=True` on the first turn if the rule's requirement isn't yet satisfied — see [§8](#real-bugs-this-tables-current-shape-was-built-to-fix) for why the LLM's own judgment on this specific question proved unreliable. |
| `chargeback_agent.py`'s `_decide_node` | `decide()` | The actual fight/refund decision for a live conversation. `None` means "fall through to the LLM judgment call" — see the code snippet in [§1](#why-a-lookup-table-instead-of-an-llm-call). |
| `chargeback_agent.py`'s `_reflect_node` | `RULES` keys, read-only, as a groundedness/confidence signal | Two uses: (1) treats reason codes found as *keys* in `RULES` as "known," alongside codes found in retrieved documents, when checking whether the drafted letter cites a code that was never actually established for this dispute; (2) adds +2 to the formula-based confidence score when the case's `(network, code)` is a rule-table entry, since a deterministic decision is inherently more trustworthy than an LLM's free-form judgment. |
| `chargeback_analysis.py`'s `analyze_chargeback()` | `decide()`, evidence-free | Shared by both background pollers — see [§6](#the-evidence-free-quirk-why-background-automation-can-never-fight) above. |

## Real bugs this table's current shape was built to fix

Two of the same *class* of bug, found and fixed independently in two different rules, are worth knowing about — because the pattern is easy to reintroduce if a future rule is added carelessly:

**`duplicate_charge_proof` pointed the wrong way, twice** (Visa `12.6.1` and RuPay `U002`). Both codes are "duplicate processing" disputes, and both originally had `duplicate_charge_proof` sitting in `required_any` — implying that *proof a duplicate charge occurred* was evidence the merchant could use to **fight**. That's backwards: proof of a duplicate charge is proof the customer's claim is *correct*, and per each code's own encyclopedia documentation ("If the Merchant Received Two Credits... must refund the duplicate"), it should force a **refund**, unconditionally. Both were fixed the same way — moved from `required_any` into `disqualifying`, alongside `refund_already_issued`. The correct tag for the *fight* side of these codes is `single_credit_confirmed` — evidence that only one valid transaction happened, i.e. evidence *against* the duplicate claim.

**RuPay `U001` and `U002` originally had evidence tags copied from an unrelated code**, before their current rules were written — `U001` (pure unauthorized-access fraud) had `client_acknowledgement`/`cardholder_communication` (evidence for a "goods matched what was offered" dispute), and `U002` (duplicate transaction, a billing dispute) had `delivery_confirmation`/`tracking_number` (evidence for a *delivery* dispute). Neither tag set had anything to do with what a merchant could actually supply to defend against the real claim, so neither code could ever correctly resolve through this table — every real case silently fell through to free-form LLM reasoning regardless of what rule *looked* like it existed. Both were corrected against `merchant_db.NPCI_REASON_CODES`'s actual definitions and the corresponding encyclopedia documents (`NPCI_U001.md`, `NPCI_U002.md`).

**RuPay `U010` had no rule at all before `always_refund` existed**, and fell through to the LLM for both evidence-gathering and the fight/refund call. Observed live: it asked the merchant for a "refund transaction ID" — evidence that belongs to a *different* code (`U009`, "merchant not providing refund") — in roughly 2 of 3 identical live runs. The reason code's own definition ("no party acted incorrectly — the failure is in the technology stack... the bank or PSP whose system failed bears the liability") makes this a case where no merchant-supplied evidence was ever going to be relevant, which is exactly what `always_refund` exists to express deterministically.

The common thread across all of these: a rule that's merely *present* in the table isn't automatically correct — the evidence tags actually have to correspond to the *real* defense for that *specific* reason code, checked against what the code's own documentation says the dispute is actually about, not assumed by analogy to a superficially similar code.

## Adding a new rule

1. Read the reason code's actual definition — `merchant_db.NPCI_REASON_CODES` for RuPay codes, or the matching `chargeback-encyclopedia/` document for any network. Identify what a merchant would *really* need to prove, not what a similar-sounding code needs.
2. Check `evidence_tags.py`'s `EvidenceTag` vocabulary for a tag that already represents that evidence. Only add a new tag if nothing existing fits — and if you do, add its human-readable label to `EVIDENCE_TAG_LABELS` in the same file.
3. Decide which shape applies: a normal `required_any` (optionally with `required_all` for an "and" condition), a `disqualifying`-only override, or `always_refund=True` if no evidence could ever matter for this code.
4. Write both `fight_reason` and `refund_reason` as complete, merchant-facing sentences — these are shown directly to the merchant, not just used internally.
5. Add the entry to `RULES`, then add tests to `test_decision_rules.py` covering at minimum: the fight path with matching evidence, the refund path with no evidence, and (if applicable) the disqualifying-override path.

## Testing

```bash
pytest test_decision_rules.py -q
```

Pure-Python, no external dependencies, no API keys, no LLM calls — every test asserts an exact `(decision, reason)` tuple (or `None`) for exact inputs. Coverage includes a per-rule fight/refund/disqualifying case for every entry in the table, the Mastercard `4853` subtype detector (including the "no subtype matched" fall-through), unmapped network and unmapped code both correctly returning `None`, and `test_every_rule_table_entry_is_reachable` — a structural test that walks `RULES` itself to confirm no entry is dead code no test exercises.

## Where to look in the code

- **`decision_rules.py`** — everything described in this document.
- **`evidence_tags.py`** — the `EvidenceTag` closed vocabulary and `EVIDENCE_TAG_LABELS`, kept in its own module specifically so `decision_rules.py` and `chargeback_agent.py` don't need to import each other in a circle.
- **`chargeback_agent.py`** — search for `decision_rules.` to find all three live-chat call sites (`_extract_evidence_node`, `_decide_node`, `_reflect_node`).
- **`chargeback_analysis.py`** — the shared background-automation call site, and the evidence-free quirk from §6.
- **`test_decision_rules.py`** — the full test suite, one good example test per pattern described above.
- **`README.md`** — this table's place in the overall architecture (Design principles' "Rule-based over LLM-based" section, and the Module reference entry for `decision_rules.py`).
