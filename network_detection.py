"""
network_detection.py — Shared "which payment network is this query about"
logic, used by both chargeback_agent.py's _answer_question_node (Dispute
Assistant tab) and api_server.py's /search endpoint (Q&A tab).

Originally lived inline in _answer_question_node only, so /search — a
deliberately LLM-free, raw-similarity endpoint — had no way to recognize
that a query about "Google Pay" or "PhonePe" is really about UPI/NPCI. Real
users name the app they used, not the payment rail it runs on, so a query
naming zero technical terms ("Visa", "UPI", "NPCI") but a common consumer
app matched no network keyword at all and fell through to plain semantic
search — verified to never surface the NPCI-specific overview doc in its
top 10 results for exactly this kind of question.

Factored out here as the single source of truth so the two call sites can't
silently diverge on what counts as a network reference.
"""

# Title keywords shared by every UPI/NPCI-flavored query.
UPI_LABELS = ["NPCI", "U001", "U002", "U003", "U004",
              "U005", "U006", "U007", "U008", "U009", "U010"]

# Query keyword → document title keywords to match via filter_by_title().
NETWORK_TITLE_KEYS = {
    "amex":             ["Amex", "American Express"],
    "american express": ["Amex", "American Express"],
    "visa":             ["Visa"],
    "mastercard":       ["Mastercard"],
    "rupay":            ["RuPay", "NPCI"],
    "ru pay":           ["RuPay", "NPCI"],
    "upi":              UPI_LABELS,
    "npci":             ["NPCI"],
    # Real users say the app name, not the rail it runs on.
    "phonepe":          UPI_LABELS,
    "google pay":       UPI_LABELS,
    "gpay":             UPI_LABELS,
    "paytm":            UPI_LABELS,
    "bhim":             UPI_LABELS,
    "amazon pay":       UPI_LABELS,
    "whatsapp pay":     UPI_LABELS,
}

# Keys whose detection means "this is a UPI/NPCI transaction" specifically —
# used to decide when Visa/Mastercard-style framing (issuing/acquiring bank)
# would be actively wrong rather than just imprecise. "rupay"/"ru pay"
# deliberately excluded: RuPay is a card network with its own issuing/
# acquiring model, distinct from UPI's remitter/beneficiary model, even
# though both are NPCI products.
UPI_CONTEXT_KEYS = {
    "upi", "npci", "phonepe", "google pay", "gpay",
    "paytm", "bhim", "amazon pay", "whatsapp pay",
}


def detect_network_title_keys(*texts: str) -> tuple:
    """
    Scan one or more texts (query, plus optionally prior conversation
    context) for network/app keywords.

    Args:
        *texts: any number of strings to scan (e.g. query, additional_context).

    Returns:
        tuple: (title_keys, detected_keywords)
          title_keys        — de-duplicated document-title keywords to pass
                               to VectorStore.filter_by_title().
          detected_keywords — the raw matched keywords themselves (e.g.
                               ["phonepe"]), for callers that need to check
                               membership in UPI_CONTEXT_KEYS or count
                               distinct networks (e.g. compare_intent).
    """
    combined = " ".join(t.lower() for t in texts if t)
    title_keys: list = []
    detected: list = []
    for kw, labels in NETWORK_TITLE_KEYS.items():
        if kw in combined:
            detected.append(kw)
            for label in labels:
                if label not in title_keys:
                    title_keys.append(label)
    return title_keys, detected


def is_upi_context(detected_keywords) -> bool:
    """True if any detected keyword indicates a UPI/NPCI (not RuPay-card) context."""
    return bool(UPI_CONTEXT_KEYS & set(detected_keywords))


# Query keyword -> chunk-collection knowledge_domain folder. Same keyword set
# as NETWORK_TITLE_KEYS, mapped to folder names instead of title substrings —
# used to narrow/boost chunk retrieval toward the right network's docs.
# Added after the chunking migration showed chunk-level ranking alone isn't
# always enough: even with chunking, a generic FAQ chunk phrased "What
# happens if I don't respond..." can outscore a topically-correct but more
# narrative NPCI-specific chunk on question-form similarity alone, regardless
# of topical relevance — confirmed empirically (RuPay Overview's best chunk
# rose from a 0.554 whole-document score to 0.67 once chunked, but generic
# FAQ chunks still scored ~0.80 on question-phrasing overlap for the exact
# query that motivated this whole migration).
NETWORK_KNOWLEDGE_DOMAINS = {
    "amex":             "06_Amex",
    "american express": "06_Amex",
    "visa":             "04_Visa",
    "mastercard":       "05_Mastercard",
    "rupay":            "07_RuPay",
    "ru pay":           "07_RuPay",
    "upi":              "07_RuPay",
    "npci":             "07_RuPay",
    "phonepe":          "07_RuPay",
    "google pay":       "07_RuPay",
    "gpay":             "07_RuPay",
    "paytm":            "07_RuPay",
    "bhim":             "07_RuPay",
    "amazon pay":       "07_RuPay",
    "whatsapp pay":     "07_RuPay",
}


def detect_knowledge_domain(*texts: str):
    """
    Scan text(s) for a network/app keyword and return the corresponding
    chunk-collection knowledge_domain, or None if none detected.

    Args:
        *texts: any number of strings to scan (e.g. query, additional_context).

    Returns:
        str or None: e.g. "07_RuPay", or None if no network/app keyword found.
    """
    combined = " ".join(t.lower() for t in texts if t)
    for kw, domain in NETWORK_KNOWLEDGE_DOMAINS.items():
        if kw in combined:
            return domain
    return None


# Minimum domain-candidate pool size to fetch before selecting — needs to be
# wide, not narrow. Confirmed by measurement: for a general "what happens if
# I get a chargeback" query, the RuPay Overview doc's best chunk ranked 9th
# of 10 domain candidates, behind several narrow single-scenario pages
# ("Technical Root Causes of Multi-Debit Events", "Wrong Amount Transferred
# — Resolution Process", etc.) whose denser, more concrete vocabulary
# outscored the Overview's more general phrasing on raw similarity alone. A
# top_k=3 fetch (the original width) would never even see the Overview
# chunk to prefer it.
DOMAIN_CANDIDATE_POOL_SIZE = 15


def select_domain_chunk(domain_hits: list, reason_code: str = ""):
    """
    Pick which domain-filtered chunk (if any) a network-named query's
    results should be built around, given an already-fetched candidate pool
    (see DOMAIN_CANDIDATE_POOL_SIZE for why that pool must be wide).

    Two preferences, mutually exclusive, both fixing the same underlying
    problem: within one narrow domain, raw embedding similarity doesn't
    reliably track "is this actually the right document," because nearly
    every code's page reuses near-identical section headings ("Required
    Evidence", "Evidence the Merchant Should Maintain") and generic
    vocabulary, so whichever page phrases it slightly more like the query
    wins on score regardless of whether it's the page actually named.

    - reason_code given (e.g. "U001"): prefer a chunk whose own reason_code
      matches it — confirmed necessary: for "What evidence is needed for a
      RuPay U001 chargeback?", U001's own "Evidence the Merchant Should
      Maintain" chunk (0.768) lost to FOUR other codes' "Required Evidence"
      chunks (0.79-0.81) despite U001 being the exact code named.
    - reason_code not given (general query): prefer a chunk from the
      domain's Overview document instead — see the module-level comment on
      DOMAIN_CANDIDATE_POOL_SIZE for the equivalent measurement on that case.

    Args:
        domain_hits: Chunks already fetched via
                     VectorStore.search_chunks(..., knowledge_domain=...),
                     ranked by score descending.
        reason_code: The specific reason code named in the query (e.g.
                     classifier.extract_network_and_code(query)[1], skipping
                     the "Unknown" case), or "" for a general query.

    Returns:
        (tier, chunk): tier is "strong" (score >= 0.65 — caller should
        promote this to lead the results), "weak" (0.60 <= score < 0.65 —
        caller should guarantee it a slot but not the lead), or (None, None)
        if nothing in the pool clears even the weak floor.
    """
    if reason_code:
        preferred = [r for r in domain_hits if r.get("reason_code") == reason_code]
    else:
        preferred = [r for r in domain_hits if "overview" in r["document_title"].lower()]

    if preferred and preferred[0]["score"] >= 0.60:
        best = preferred[0]
        return ("strong" if best["score"] >= 0.65 else "weak"), best

    strong = [r for r in domain_hits if r["score"] >= 0.65]
    if strong:
        return "strong", strong[0]
    weak = [r for r in domain_hits if 0.60 <= r["score"] < 0.65]
    if weak:
        return "weak", weak[0]
    return None, None
