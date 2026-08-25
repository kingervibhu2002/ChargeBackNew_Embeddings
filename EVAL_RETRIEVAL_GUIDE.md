# `eval_retrieval.py`, Explained

`eval_retrieval.py` answers a question none of this project's other tests ask: **not "does retrieval work at all," but "how good is it, precisely, and did a change make it better or worse?"** This document explains the information-retrieval metrics it computes, how the harness is built, and — using this project's own real before/after numbers from the whole-document → chunked-embedding migration it was built to measure — what those metrics actually looked like in practice, including a genuine surprise in the results.

No prior information-retrieval background assumed.

---

## Table of contents

1. [Why this exists, separately from the other tests](#why-this-exists-separately-from-the-other-tests)
2. [The golden query set](#the-golden-query-set)
3. [The metrics, one at a time](#the-metrics-one-at-a-time)
4. [Two ways to search: `direct` vs `http` mode](#two-ways-to-search-direct-vs-http-mode)
5. [How one query gets scored](#how-one-query-gets-scored)
6. [How scores get aggregated](#how-scores-get-aggregated)
7. [A real worked example: the chunking migration's actual numbers](#a-real-worked-example-the-chunking-migrations-actual-numbers)
8. [Running it](#running-it)
9. [Where to look in the code](#where-to-look-in-the-code)

---

## Why this exists, separately from the other tests

`test_classifier.py`/`test_decision_rules.py` assert exact outcomes for exact inputs — good for "did I break something," useless for "is the ranking any good." `test_search.py` is a smoke test — does retrieval return *anything* sane for a handful of queries, without crashing. Neither can answer the question that actually matters when you change how documents are embedded, chunked, or ranked: **for a fixed, representative set of real questions, did retrieval quality go up or down, and by how much?**

That's what `eval_retrieval.py` is for. It was built for a specific, concrete moment: this project's migration from embedding whole documents to embedding heading-based chunks (`chunking.py`). Before touching the indexing pipeline, the author ran this harness against the *current* (whole-document) index and saved the result (`eval_baseline_wholedoc.json`). After the migration, the exact same harness against the exact same 44 queries produced a second file (`eval_chunked.json`). The difference between those two files is the migration's actual, measured effect — not a guess, not "it feels better," a number. [§7](#a-real-worked-example-the-chunking-migrations-actual-numbers) walks through what those two real files actually show.

## The golden query set

`golden_queries.json` is 44 hand-written queries against the real `chargeback-encyclopedia/` corpus (159 documents at the time the set was created), each with a known-correct answer:

```json
{
  "id": "q01",
  "category": "exact_code",
  "query": "What is U001?",
  "expected_documents": [
    "NPCI UPI Dispute Code U001 — Transaction Not Done by Customer (Fraud)"
  ],
  "relevance": {
    "NPCI UPI Dispute Code U001 — Transaction Not Done by Customer (Fraud)": 3
  }
}
```

- **`expected_documents`** — the document title(s) that count as a correct hit for this query. Most queries have exactly one.
- **`relevance`** — a graded relevance score per document, not just a yes/no. The scale (documented in the file's own `_meta`): **3** = the primary/best answer, **2** = a clearly relevant secondary source, **1** = tangentially relevant. A query is only **graded** (nDCG-eligible — see [§3](#the-metrics-one-at-a-time)) when `relevance` has *more than one* entry — a query with a single expected document is evaluated with Recall@K and MRR only, since nDCG needs more than one relevant document to say anything about *ranking among relevant results*.
- **`category`** — one of 14 tags (`exact_code`, `semantic`, `ambiguous`, `multi_section`, `rebuttal`, `cross_domain`, `concept`, `lifecycle`, `fraud`, `evidence`, `faq`, `regulation`, `monitoring`, `best_practices`), letting the harness report accuracy broken down by *what kind* of question is being asked, not just one blended number. This matters because a single overall score can hide a real problem — see the `exact_code` and `cross_domain` categories in [§7](#a-real-worked-example-the-chunking-migrations-actual-numbers), where the aggregate metrics looked like unambiguous improvement while one specific category's ranking quietly got worse.

A real **graded** (multi-document relevance) example, where the correct answer is genuinely ambiguous between two real reason codes:

```json
{
  "id": "q08",
  "category": "ambiguous",
  "query": "The cardholder claims they never made this purchase",
  "expected_documents": [
    "Mastercard 4837 — No Cardholder Authorization",
    "Mastercard Chargeback Reason Code 4863 — Cardholder Does Not Recognize"
  ],
  "relevance": {
    "Mastercard 4837 — No Cardholder Authorization": 2,
    "Mastercard Chargeback Reason Code 4863 — Cardholder Does Not Recognize": 2
  }
}
```
Both documents are equally plausible answers to this exact phrasing — the query itself doesn't disambiguate which Mastercard fraud code applies. Rewarding retrieval for surfacing *either* (or both) is exactly what a graded, multi-document relevance judgment is for, and exactly what a single `expected_documents` list checked as pass/fail couldn't express.

## The metrics, one at a time

Three numbers, each answering a different question about the same ranked list of results:

### Recall@K — "was the right answer anywhere in the top K?"

The simplest metric: for each query, look at the top `K` results (this harness always computes both `K=5` and `K=10`). Score `1` if *any* expected document appears in that top-`K` list, `0` if not. Average across all queries. A binary hit/miss per query — Recall@5 = 0.864 means 86.4% of queries had a correct answer somewhere in their top 5 results.

Recall says nothing about *where* in the top K the answer landed — position 1 and position 5 score identically. That's what MRR is for.

### MRR (Mean Reciprocal Rank) — "how far down did I have to look?"

For each query, find the rank of the **first** correct hit (1st place, 2nd place, etc.), take its reciprocal (`1/rank`), and average across all queries:

```python
def _first_hit_rank(ranked_titles: list, expected: list) -> int:
    """1-based rank of the first expected title found, or 0 if none found."""
    for i, title in enumerate(ranked_titles, start=1):
        if title in expected:
            return i
    return 0
```
```python
rr = (1.0 / rank) if rank else 0.0
```

A correct answer in 1st place scores `1.0`. In 2nd place, `0.5`. In 5th place, `0.2`. Never found at all, `0.0`. MRR rewards being *close to the top*, not just present somewhere — a system that always ranks the right answer 2nd scores much better on MRR than one that ranks it 9th, even though both would score identically on Recall@10 (both are "found").

MRR only looks at the position of the *first* hit — it's blind to everything after that. If a query has two equally good answers and the system finds one at rank 1 and completely misses the other, MRR still scores a perfect `1.0`. That blindness to *multiple* relevant results is exactly the gap nDCG closes.

### nDCG@10 (Normalized Discounted Cumulative Gain) — "did I rank the BEST answers highest, among several good ones?"

The only metric of the three that uses the graded `relevance` scores (3/2/1) rather than a plain yes/no, and the only one computed exclusively over the graded-query subset (5 of the 44 queries — see [§2](#the-golden-query-set) for why single-answer queries are excluded).

```python
def _dcg(ranked_titles: list, relevance: dict, k: int) -> float:
    dcg = 0.0
    for i, title in enumerate(ranked_titles[:k], start=1):
        rel = relevance.get(title, 0)
        if rel:
            dcg += rel / math.log2(i + 1)
    return dcg

def _ndcg(ranked_titles: list, relevance: dict, k: int) -> float:
    dcg = _dcg(ranked_titles, relevance, k)
    ideal_order = sorted(relevance.values(), reverse=True)[:k]
    idcg = sum(rel / math.log2(i + 1) for i, rel in enumerate(ideal_order, start=1))
    return (dcg / idcg) if idcg > 0 else 0.0
```

Two ideas stacked together:

- **DCG (Discounted Cumulative Gain)** sums up each result's relevance score, but *discounts* it by how far down the list it appears — dividing by `log2(rank + 1)`. A relevance-3 document at rank 1 contributes `3 / log2(2) = 3.0`; the same document at rank 5 contributes only `3 / log2(6) ≈ 1.16`. Being relevant matters less the further down you have to scroll to find it.
- **Normalization** — raw DCG isn't comparable across queries with different numbers of relevant documents, so it's divided by **IDCG**, the DCG of the *best possible* ordering (all the relevant documents, sorted by relevance score, placed at the very top). The result is always between 0 and 1: `1.0` means this query's results were ranked exactly as well as they possibly could have been; lower scores mean better documents existed but weren't ranked as high as they should have been.

Why this matters *specifically* for a knowledge base where several documents can be almost-equally relevant (like the `q08` example above, or two documents on adjacent lifecycle stages): nDCG is the only one of these three metrics that can tell the difference between "found one good answer and missed a second, equally good one" and "found both good answers, in the right order." Recall@K and MRR both go blind the moment there's more than one right answer per query — nDCG is what's actually looking at ranking *quality* rather than just ranking *presence*.

## Two ways to search: `direct` vs `http` mode

```python
def _make_direct_search_fn(qdrant_path: str = "./qdrant_data"):
    """
    Build a search(query, top_k) -> list[str] callable that runs entirely
    in-process against the real Qdrant data — same search_documents() logic
    api_server.py's /search route calls, no HTTP, no rate limiting.
    """
```

**`direct` mode (the default)** loads the embedding model and connects to Qdrant *in the eval script's own process*, calling the exact same `search_documents()` function `api_server.py`'s `/search` route calls — same ranking logic, zero HTTP overhead, and critically, **no rate limiting**. It requires `api_server.py` to be stopped first, since Qdrant's local file-mode storage only allows one process to hold `./qdrant_data` at a time (the same constraint documented throughout this project — see `README.md`'s Running section).

**`http` mode** makes real HTTP calls against a live server's `/search` endpoint — genuinely end-to-end, including whatever the running server's actual deployed code does. But `guardrails.py`'s `RateLimiter` caps `/search` at 20 requests/hour, and a 44-query golden-set run blows straight through that. The harness's own comment is blunt about the consequence: every request past the cap comes back `429`, and `_search_http()` treats that identically to "no results found" — silently corrupting the second half of every run into a wall of false misses, not a real quality measurement. `http` mode is kept only for an occasional true end-to-end sanity check of a handful of queries, never for a full golden-set run — a real example of a safety guardrail (rate limiting, entirely correct and necessary for the live app) actively getting in the way of a different, legitimate use case (bulk evaluation), solved here by giving evaluation its own bypass path rather than weakening the guardrail itself.

## How one query gets scored

`run_eval()`'s per-query loop, one query at a time:

```python
ranked = search_fn(q["query"], top_k)
expected = q["expected_documents"]
relevance = q.get("relevance", {})

rank = _first_hit_rank(ranked, expected)
hit5 = 1 if (rank and rank <= 5) else 0
hit10 = 1 if (rank and rank <= 10) else 0
rr = (1.0 / rank) if rank else 0.0

graded = len(relevance) > 1
ndcg10 = _ndcg(ranked, relevance, 10) if graded else None
```

Every query gets a full record — not just a score, but the *evidence* for that score (`returned_top_k`, the actual ranked titles that came back) — so a human reviewing a regression can see exactly what the system returned instead of just the number it produced. The console output during a run reflects the same idea at a glance:

```
  [✓] q01 (exact_code): rank=1  What is U001?
  [~] q08 (ambiguous): rank=7  The cardholder claims they never made this purchase
  [✗] q23 (cross_domain): rank=not found  ...
```
`✓` = found in the top 5, `~` = found, but only within top 10 (ranks 6–10), `✗` = not found at all within `top_k`.

## How scores get aggregated

Two levels of rollup from the same per-query records:

- **Overall summary** — Recall@5, Recall@10, and MRR averaged across all 44 queries; nDCG@10 averaged across only the graded subset (5 queries).
- **By category** — the same three metrics (Recall@5, Recall@10, MRR — nDCG isn't broken out by category, since only 5 of the 44 queries have graded relevance at all, too few to slice further) computed separately for each of the 14 categories.

The category breakdown exists because a single blended number can hide exactly the kind of regression that matters most. [§7](#a-real-worked-example-the-chunking-migrations-actual-numbers) below shows this happening for real, not hypothetically.

## A real worked example: the chunking migration's actual numbers

This project's `eval_baseline_wholedoc.json` (whole-document embeddings, run first) and `eval_chunked.json` (heading-based chunk embeddings, run after migrating) are real output from real runs of this harness — not illustrative fabrications. Here's what actually changed:

| Metric | Whole-doc (before) | Chunked (after) | Change |
|---|---|---|---|
| Recall@5 | 0.864 | 0.932 | **+0.068** |
| Recall@10 | 0.932 | 0.977 | **+0.045** |
| MRR | 0.764 | 0.748 | **−0.016** |
| nDCG@10 (graded, n=5) | 0.184 | 0.562 | **+0.378** |

The headline result is unambiguous: chunking made retrieval noticeably better on almost every axis, especially nDCG — a **3× improvement** on the graded queries, meaning the chunked index isn't just finding relevant documents more often, it's ranking *multiple* relevant documents in a much better order when there's more than one right answer. That's exactly the effect chunking was expected to have: a whole document's embedding is a blurry average of everything in it, while a heading-based chunk's embedding is a sharp, specific signal for the one topic that chunk actually covers.

**But MRR went down.** A small drop (0.764 → 0.748), and it's real, not noise — worth understanding rather than glossing over, because it's a genuine lesson about these metrics, not a bug in the harness. Two things can both be true at once: more queries found a correct answer *somewhere* in the top 10 (Recall@10 went up), while the position of the *very first* hit occasionally got slightly worse for queries that were already succeeding — a single relevant chunk can rank a little lower than the single relevant whole-document sometimes did, even as chunking's real strength (surfacing multiple good chunks, and separating a specific chunk's narrow topic from a whole document's broader blend of topics) drove recall and nDCG up. The by-category breakdown makes this concrete: **`exact_code`'s MRR dropped from 0.658 to 0.526**, and **`cross_domain`'s MRR dropped from 0.5 to 0.35**, even though both categories' Recall@5/@10 held steady or improved. A single overall MRR number moving down by 0.016 doesn't tell you *where* — the category breakdown does.

The practical lesson this real result demonstrates: **no single metric tells the whole story, and a harness that only reports one number would have hidden a real, specific regression** (exact-code lookups occasionally ranking their answer slightly lower) behind a real, larger improvement (better recall and much better handling of ambiguous, multi-answer queries). Whether that tradeoff was worth taking is a judgment call a human should make with all four numbers — plus the category breakdown, plus the actual `returned_top_k` for the queries that regressed — in front of them, not something a single pass/fail threshold could have decided correctly on its own.

## Running it

```bash
# Default: in-process, no server running, no rate limit — the normal way to run this
python api_server.py &  # ... then stop it before running the eval, or just don't start it
python eval_retrieval.py

# Save full results (including every per-query record) for later comparison
python eval_retrieval.py --out eval_my_change.json

# A quick, real end-to-end HTTP sanity check against a live server (not for full runs — see §4)
python eval_retrieval.py --mode http --base-url http://localhost:8000

# Evaluate only top-5 instead of top-10
python eval_retrieval.py --top-k 5
```

To measure whether a retrieval-affecting change (chunking strategy, embedding model, reranking logic, domain-boost weighting) helped or hurt: run this once *before* the change with `--out before.json`, make the change, run it again with `--out after.json`, and diff the `summary` and `by_category` blocks the same way this document just walked through `eval_baseline_wholedoc.json` vs. `eval_chunked.json`.

## Where to look in the code

- **`eval_retrieval.py`** — everything described in this document.
- **`golden_queries.json`** — the 44-query golden set, including the `_meta` block documenting the relevance scale and when/why it was created.
- **`eval_baseline_wholedoc.json`** / **`eval_chunked.json`** — real saved output from two actual runs, the before/after pair walked through in §7.
- **`api_server.py`**'s `search_documents()` — the actual ranking logic both `direct` mode and the live `/search` route call; read it alongside this document to see what's actually being measured.
- **`chunking.py`** — the heading-based document-splitting logic whose effect this harness was built to measure.
- **`guardrails.py`**'s `RateLimiter` — the 20-requests/hour `/search` cap that makes `http` mode unsuitable for full golden-set runs (§4).
- **`test_search.py`** — the separate, simpler end-to-end retrieval *smoke test* (does it return anything sane, not "how good is it") — worth contrasting with this file's very different purpose.
- **`README.md`**'s Testing section and Module reference — this file's place in the overall project, one level up from this document's retrieval-evaluation-specific focus.
