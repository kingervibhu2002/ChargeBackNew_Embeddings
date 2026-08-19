"""
test_qa_stress.py — 100-query stress test of the Q&A tab's real routing logic.

Mirrors chat.html's handleQA() exactly: a query matching listIntent goes to
the LangGraph /dispute agent (answer_question_node), everything else goes to
the plain LLM-free /search path. Runs in-process (direct mode, like
eval_retrieval.py) to avoid api_server.py's Qdrant lock and RateLimiter —
this needs api_server.py stopped.

Usage:
    python test_qa_stress.py --out qa_stress_results.json
"""

import argparse
import json
import re
import sys
import time

# Exact regex from chat.html's handleQA() — must stay byte-identical to what
# the real frontend runs, or this test measures a different routing decision
# than what users actually hit.
_LIST_INTENT_RE = re.compile(
    r"\b(list|all|every|enumerate|what are|show all|types of|kinds of|codes|categories|compare|difference|covered|coverage)\b",
    re.IGNORECASE,
)

QUERIES = [
    # 1. Brand names vs. technical terms
    (1, "brand_vs_technical", "What happens if I get a chargeback for a Google Pay transaction?"),
    (2, "brand_vs_technical", "My customer paid via Paytm and is now disputing — what's the process?"),
    (3, "brand_vs_technical", "Someone used BHIM to pay and now claims fraud — who's involved?"),
    (4, "brand_vs_technical", "Is a WhatsApp Pay dispute handled differently from a normal UPI one?"),
    (5, "brand_vs_technical", "Customer says Amazon Pay deducted twice — what reason code applies?"),
    (6, "brand_vs_technical", "I use Razorpay as my payment gateway — does that change anything?"),
    (7, "brand_vs_technical", "My settlement is through HDFC — are they the acquiring bank here?"),
    (8, "brand_vs_technical", "Customer's bank is SBI — what's SBI's role in this dispute?"),
    (9, "brand_vs_technical", "Is a CRED transaction handled the same as UPI?"),
    (10, "brand_vs_technical", "What if the customer paid with their RuPay-linked UPI ID?"),

    # 2. Ambiguous quantifiers / arithmetic
    (11, "quantifier_arithmetic", "What are the top 3 minus 1 fraud-related reason codes?"),
    (12, "quantifier_arithmetic", "List the first 5 of the 10 UPI codes."),
    (13, "quantifier_arithmetic", "Give me half of the Visa reason codes."),
    (14, "quantifier_arithmetic", "What's the second most common reason code after fraud?"),
    (15, "quantifier_arithmetic", "Show me codes 2 through 6 for Mastercard."),
    (16, "quantifier_arithmetic", "What are all the codes except the fraud ones?"),
    (17, "quantifier_arithmetic", "List every code that isn't about delivery."),
    (18, "quantifier_arithmetic", "Give me the last 3 Amex codes."),
    (19, "quantifier_arithmetic", "How many total codes are there minus the ones needing no evidence?"),
    (20, "quantifier_arithmetic", "What's the middle one of the Visa fraud codes?"),

    # 3. Substring / word-boundary collisions
    (21, "substring_collision", "Explain the difference between UPI transactions in general."),
    (22, "substring_collision", 'What does "unpaid" mean in a chargeback context?'),
    (23, "substring_collision", 'Is "amexpert" a real evidence requirement term?'),
    (24, "substring_collision", "What is a rupaycard exactly?"),
    (25, "substring_collision", "Explain visanet's role (not asking about the network \"Visa\")."),
    (26, "substring_collision", 'What\'s a "masterclass" dispute strategy?'),
    (27, "substring_collision", "What is UPIN used for?"),
    (28, "substring_collision", 'Explain "cvvresult" fields.'),
    (29, "substring_collision", 'What does "arbitrationstage" mean?'),
    (30, "substring_collision", 'Is "npciupi" one word or two systems?'),

    # 4. Multi-intent compound questions
    (31, "multi_intent", "Which codes are at pre-arbitration and what evidence do they need?"),
    (32, "multi_intent", "List all Visa codes and tell me which stage each is typically escalated to."),
    (33, "multi_intent", "Compare Visa and Mastercard's arbitration timelines, and list their fraud codes too."),
    (34, "multi_intent", "Are all Amex codes covered, and which ones are at the arbitration stage?"),
    (35, "multi_intent", "What's the difference between chargeback and pre-arbitration, and list codes for each?"),
    (36, "multi_intent", "Give me every RuPay code and explain the lifecycle stage concept."),
    (37, "multi_intent", "Is my list of Mastercard codes complete, and what's missing from arbitration coverage?"),
    (38, "multi_intent", "Compare all four networks' arbitration processes in one table."),
    (39, "multi_intent", "List codes needing delivery evidence, sorted by lifecycle stage."),
    (40, "multi_intent", "What are all fraud codes across networks, grouped by which stage they escalate at?"),

    # 5. Follow-up / anaphoric context (tested cold, no prior turn — see notes in report)
    (41, "anaphoric", "Are all of those covered?"),
    (42, "anaphoric", "What about the other one?"),
    (43, "anaphoric", "Is that the complete list?"),
    (44, "anaphoric", "Same question but for Mastercard."),
    (45, "anaphoric", "And what about evidence for that one?"),
    (46, "anaphoric", "Did I miss anything?"),
    (47, "anaphoric", "What's the difference between those two?"),
    (48, "anaphoric", "Show me the rest."),
    (49, "anaphoric", "Same thing but for RuPay."),
    (50, "anaphoric", "Is there more to it?"),

    # 6. Hinglish / mixed-language
    (51, "hinglish", "Chargeback kya hota hai aur usme kaun kaun involved hote hain?"),
    (52, "hinglish", "Visa aur Mastercard mein kya fark hai?"),
    (53, "hinglish", "Mujhe saare fraud codes ki list chahiye."),
    (54, "hinglish", "Arbitration stage ka matlab kya hai?"),
    (55, "hinglish", "Evidence submit karne ka process kya hai?"),
    (56, "hinglish", "Kaunse codes mein delivery proof chahiye hota hai?"),
    (57, "hinglish", "Pre-arbitration aur arbitration mein kya difference hai?"),
    (58, "hinglish", "Mera dispute kitne din mein resolve hoga?"),
    (59, "hinglish", "Kya sabhi RuPay codes yahan cover hain?"),
    (60, "hinglish", "Refund aur chargeback mein kya fark hai samjhao."),

    # 7. Codes that look like other things
    (61, "fake_codes", "What does reason code 4 mean?"),
    (62, "fake_codes", 'Is there a reason code called "13"?'),
    (63, "fake_codes", "What's code U8 about?"),
    (64, "fake_codes", "Explain reason 4837 versus amount ₹4837."),
    (65, "fake_codes", "What's the code for a $10.4 transaction?"),
    (66, "fake_codes", "Is F2 a real Amex code?"),
    (67, "fake_codes", "What does code 001 mean?"),
    (68, "fake_codes", "Explain C8 evidence requirements."),
    (69, "fake_codes", "What's U010 vs U10?"),
    (70, "fake_codes", "Is 12.6 the same as 12.6.1?"),

    # 8. Unanswerable / schema-adjacent concepts
    (71, "unanswerable", "What's my chargeback ratio right now?"),
    (72, "unanswerable", "Am I in the Visa Fraud Monitoring Program?"),
    (73, "unanswerable", "What's the average resolution time for my disputes?"),
    (74, "unanswerable", "Which of my transactions used 3-D Secure?"),
    (75, "unanswerable", "Was this a fallback (chip-fail) transaction?"),
    (76, "unanswerable", "What's my current MATCH list status?"),
    (77, "unanswerable", "Did this transaction have AVS match?"),
    (78, "unanswerable", "What's my acquirer's name?"),
    (79, "unanswerable", "Is this merchant PCI-DSS compliant?"),
    (80, "unanswerable", "What's the interchange fee on this transaction?"),

    # 9. Cross-network / negation phrasing
    (81, "negation", "Which codes require NO evidence at all?"),
    (82, "negation", "What's NOT covered by the Visa liability shift?"),
    (83, "negation", "Which networks don't have an arbitration stage?"),
    (84, "negation", "What codes exist in Mastercard but not Visa?"),
    (85, "negation", "Which evidence type is never required for fraud codes?"),
    (86, "negation", "What's the one thing RuPay does differently from every other network?"),
    (87, "negation", "Which codes can't be fought regardless of evidence?"),
    (88, "negation", "What doesn't count as delivery proof?"),
    (89, "negation", "Which network has the fewest reason codes?"),
    (90, "negation", "What's excluded from the EMV liability shift?"),

    # 10. Meta / self-referential
    (91, "meta", "How does this suggestion feature actually work?"),
    (92, "meta", "What data do you have access to about me?"),
    (93, "meta", "Are you using an LLM or just a database?"),
    (94, "meta", "How accurate are your recommendations?"),
    (95, "meta", "What happens to my data after I ask a question?"),
    (96, "meta", "Can you see other merchants' data?"),
    (97, "meta", "What's your confidence score on this answer?"),
    (98, "meta", "Is this advice legally binding?"),
    (99, "meta", "How is my answer being generated right now?"),
    (100, "meta", "What can't you help me with?"),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="qa_stress_results.json")
    parser.add_argument("--qdrant-path", default="./qdrant_data")
    args = parser.parse_args()

    from fastembed import TextEmbedding
    from vector_store import VectorStore
    from api_server import search_documents
    from chargeback_agent import build_dispute_agent

    print("Loading embedding model and connecting to Qdrant (server must be stopped)...")
    model = TextEmbedding("BAAI/bge-small-en-v1.5")
    store = VectorStore(persist_path=args.qdrant_path)
    print(f"Connected — {len(store)} documents.")

    def embed(text):
        return next(model.embed([text])).tolist()

    print("Building dispute agent (compiles LangGraph, needs GROQ_API_KEY)...")
    agent = build_dispute_agent(store=store, embed_fn=embed)
    print(f"Ready. Running {len(QUERIES)} queries.\n")

    results = []
    for qid, category, query in QUERIES:
        is_list_intent = bool(_LIST_INTENT_RE.search(query))
        t0 = time.time()
        row = {"id": qid, "category": category, "query": query, "route": "dispute" if is_list_intent else "search"}

        try:
            if is_list_intent:
                out = agent.run(query, additional_context="")
                row.update({
                    "is_valid_query": out.get("is_valid_query"),
                    "needs_more_info": out.get("needs_more_info"),
                    "decision": out.get("decision", ""),
                    "reason_code": out.get("reason_code", ""),
                    "confidence_score": out.get("confidence_score"),
                    "is_grounded": out.get("is_grounded"),
                    "groundedness_issues": out.get("groundedness_issues", ""),
                    "final_answer_preview": (out.get("final_answer") or "")[:400],
                })
            else:
                top_k = 4
                docs = search_documents(store, embed, query, top_k=top_k)
                row.update({
                    "n_results": len(docs),
                    "results": [{"title": d["title"], "score": d["score"]} for d in docs],
                })
        except Exception as e:
            row["error"] = f"{type(e).__name__}: {e}"

        row["latency_s"] = round(time.time() - t0, 2)
        results.append(row)

        tag = row["route"][0].upper()
        summary = row.get("error") or (
            f"valid={row.get('is_valid_query')} needs_info={row.get('needs_more_info')} conf={row.get('confidence_score')}"
            if is_list_intent else
            f"n={row.get('n_results')} top={row['results'][0]['title'][:40] if row.get('results') else None}"
        )
        print(f"  [{tag}] {qid:>3} ({category}): {summary}  ({row['latency_s']}s)")
        sys.stdout.flush()

    with open(args.out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nWrote {len(results)} results to {args.out}")


if __name__ == "__main__":
    main()
