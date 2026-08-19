"""
eval_retrieval.py — Golden-set retrieval evaluation for the /search endpoint.

Runs golden_queries.json against a live api_server.py instance and reports
Recall@5, Recall@10, and MRR overall and per-category, plus nDCG@10 for the
subset of queries with graded (multi-document) relevance judgments.

This is Phase 1 of the whole-doc → chunked-embedding migration: establish a
baseline on the CURRENT (whole-document) index before any chunking work
starts, so the migration's effect can be measured against real numbers
instead of assumed. Re-run this unchanged after the chunking migration and
diff the two result files.

Usage:
    python eval_retrieval.py                                  # uses http://localhost:8000
    python eval_retrieval.py --base-url http://localhost:8000
    python eval_retrieval.py --out eval_baseline_wholedoc.json
    python eval_retrieval.py --top-k 10
"""

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from urllib.parse import quote


def _search_http(base_url: str, query: str, top_k: int) -> list:
    """
    Call /search over HTTP and return titles ranked best-first.

    NOT used by default — a 40+ query eval run trips the live server's
    RateLimiter (20 requests/hour on /search), and every request past the
    cap comes back as a 429 that this treats identically to "no results,"
    silently corrupting the back half of the run. Kept only for an
    occasional true end-to-end sanity check (rate limiting and all) of a
    handful of queries, not for full golden-set runs.
    """
    import requests
    url = f"{base_url}/search?query={quote(query)}&top_k={top_k}"
    try:
        resp = requests.get(url, timeout=30)
    except requests.RequestException as e:
        print(f"  ERROR calling /search: {e}", file=sys.stderr)
        return []
    if resp.status_code != 200:
        if resp.status_code == 429:
            print(f"  WARNING: rate-limited (429) — result is NOT a genuine miss: {query[:60]}", file=sys.stderr)
        return []
    return [r["title"] for r in resp.json()]


def _make_direct_search_fn(qdrant_path: str = "./qdrant_data"):
    """
    Build a search(query, top_k) -> list[str] callable that runs entirely
    in-process against the real Qdrant data — same search_documents() logic
    api_server.py's /search route calls, no HTTP, no rate limiting.

    Requires api_server.py to NOT be running (Qdrant local-mode allows only
    one process to hold ./qdrant_data at a time) — the caller is responsible
    for stopping it first.
    """
    from fastembed import TextEmbedding
    from vector_store import VectorStore
    from api_server import search_documents

    print("Loading embedding model and connecting to Qdrant directly (server must be stopped)...")
    model = TextEmbedding("BAAI/bge-small-en-v1.5")
    store = VectorStore(persist_path=qdrant_path)
    print(f"Connected — {len(store)} documents in the store.\n")

    def embed(text: str) -> list:
        return next(model.embed([text])).tolist()

    def _search(query: str, top_k: int) -> list:
        # search_documents() now returns chunk dicts (document_title, not
        # title — the "title" key only exists after api_server.py's route
        # handler maps it for the HTTP response model). Document-level
        # scoring in this harness stays valid either way since the golden
        # set's expected_documents are titles, and multiple chunks from the
        # same document collapse to repeats of that title, not a problem for
        # rank-of-first-hit scoring.
        results = search_documents(store, embed, query, top_k=top_k)
        return [r["document_title"] for r in results]

    return _search


def _first_hit_rank(ranked_titles: list, expected: list) -> int:
    """1-based rank of the first expected title found, or 0 if none found."""
    for i, title in enumerate(ranked_titles, start=1):
        if title in expected:
            return i
    return 0


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


def run_eval(search_fn, golden_path: str, top_k: int) -> dict:
    with open(golden_path) as f:
        golden = json.load(f)

    per_query = []
    for q in golden["queries"]:
        ranked = search_fn(q["query"], top_k)
        expected = q["expected_documents"]
        relevance = q.get("relevance", {})

        rank = _first_hit_rank(ranked, expected)
        hit5 = 1 if (rank and rank <= 5) else 0
        hit10 = 1 if (rank and rank <= 10) else 0
        rr = (1.0 / rank) if rank else 0.0

        graded = len(relevance) > 1  # nDCG only meaningful for multi-doc relevance
        ndcg10 = _ndcg(ranked, relevance, 10) if graded else None

        per_query.append({
            "id": q["id"],
            "category": q["category"],
            "query": q["query"],
            "expected_documents": expected,
            "returned_top_k": ranked,
            "first_hit_rank": rank,
            "hit_at_5": bool(hit5),
            "hit_at_10": bool(hit10),
            "reciprocal_rank": rr,
            "ndcg_at_10": ndcg10,
        })

        status = "✓" if hit5 else ("~" if hit10 else "✗")
        print(f"  [{status}] {q['id']} ({q['category']}): rank={rank or 'not found'}  {q['query'][:70]}")

    n = len(per_query)
    recall_5 = sum(r["hit_at_5"] for r in per_query) / n
    recall_10 = sum(r["hit_at_10"] for r in per_query) / n
    mrr = sum(r["reciprocal_rank"] for r in per_query) / n

    graded_rows = [r for r in per_query if r["ndcg_at_10"] is not None]
    ndcg_avg = (sum(r["ndcg_at_10"] for r in graded_rows) / len(graded_rows)) if graded_rows else None

    by_category = {}
    for r in per_query:
        c = by_category.setdefault(r["category"], {"n": 0, "hit5": 0, "hit10": 0, "rr_sum": 0.0})
        c["n"] += 1
        c["hit5"] += r["hit_at_5"]
        c["hit10"] += r["hit_at_10"]
        c["rr_sum"] += r["reciprocal_rank"]
    category_summary = {
        cat: {
            "n": c["n"],
            "recall_at_5": round(c["hit5"] / c["n"], 3),
            "recall_at_10": round(c["hit10"] / c["n"], 3),
            "mrr": round(c["rr_sum"] / c["n"], 3),
        }
        for cat, c in sorted(by_category.items())
    }

    return {
        "meta": {
            "run_at": datetime.now(timezone.utc).isoformat(),
            "golden_set": golden_path,
            "n_queries": n,
            "top_k": top_k,
        },
        "summary": {
            "recall_at_5": round(recall_5, 3),
            "recall_at_10": round(recall_10, 3),
            "mrr": round(mrr, 3),
            "ndcg_at_10_graded_subset": round(ndcg_avg, 3) if ndcg_avg is not None else None,
            "n_graded_queries": len(graded_rows),
        },
        "by_category": category_summary,
        "per_query": per_query,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mode", choices=["direct", "http"], default="direct",
                         help="direct (default): in-process against Qdrant, no rate limit, "
                              "requires api_server.py to be stopped. http: real HTTP calls "
                              "against a running server, subject to its rate limiter.")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Only used with --mode http")
    parser.add_argument("--qdrant-path", default="./qdrant_data", help="Only used with --mode direct")
    parser.add_argument("--golden", default="golden_queries.json")
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--out", default=None, help="Write full results JSON to this path")
    args = parser.parse_args()

    if args.mode == "direct":
        search_fn = _make_direct_search_fn(args.qdrant_path)
        print("Running golden-set retrieval eval (direct mode, in-process) ...\n")
    else:
        search_fn = lambda q, k: _search_http(args.base_url, q, k)
        print(f"Running golden-set retrieval eval against {args.base_url} (http mode) ...\n")

    results = run_eval(search_fn, args.golden, args.top_k)

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    s = results["summary"]
    print(f"  Queries:        {results['meta']['n_queries']}")
    print(f"  Recall@5:       {s['recall_at_5']:.1%}")
    print(f"  Recall@10:      {s['recall_at_10']:.1%}")
    print(f"  MRR:            {s['mrr']:.3f}")
    if s["ndcg_at_10_graded_subset"] is not None:
        print(f"  nDCG@10 (graded, n={s['n_graded_queries']}): {s['ndcg_at_10_graded_subset']:.3f}")

    print(f"\n{'By category':<15}{'n':>4}{'Recall@5':>12}{'Recall@10':>12}{'MRR':>8}")
    for cat, c in results["by_category"].items():
        print(f"{cat:<15}{c['n']:>4}{c['recall_at_5']:>12.1%}{c['recall_at_10']:>12.1%}{c['mrr']:>8.3f}")

    if args.out:
        with open(args.out, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nFull results written to {args.out}")


if __name__ == "__main__":
    main()
