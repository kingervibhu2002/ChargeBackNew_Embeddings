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
