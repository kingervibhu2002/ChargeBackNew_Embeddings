"""
chargeback_analysis.py — Shared "what should happen to this chargeback"
logic, used by both auto_decision_poller.py (acts on it for merchants who
opted into auto-decision) and suggestion_poller.py (advises merchants who
didn't, without touching their case). Single source of truth so the two
pollers can never silently diverge on what a given case's recommendation is.
"""

from typing import NamedTuple, Optional

import decision_rules
from cbs import (
    count_credits,
    find_refund_for_utr,
    get_debit_attempt_status,
    has_pending_suspense,
    reconcile_utr,
)
from merchant_db import deadline_bucket

# All chargebacks in this schema are NPCI/UPI disputes — see
# auto_decision_poller.py's matching comment for why this is a constant
# rather than a column read.
_NETWORK = "RuPay"


class Analysis(NamedTuple):
    action: Optional[str]   # "fight" | "refund" | None (no confident recommendation)
    reason: str
    source: str              # "cbs" | "ledger" | "network" | "rules" | ""
                              # ("" only when action is None from decision_rules —
                              # every ledger/network-derived branch, including the
                              # action=None ones, sets a real source string)
    deadline_expired: bool = False  # True when response_deadline is already in the
                              # past. Reported live: a case's recommendation said
                              # "fight, submit evidence" with the deadline mentioned
                              # only as decorative prose elsewhere — never actually
                              # checked as part of the recommendation itself, so
                              # nothing changed about the advice once the response
                              # window had already closed. Computed once here so it
                              # travels with the recommendation everywhere Analysis
                              # goes, rather than being recomputed (or forgotten)
                              # ad hoc at each call site. Default False, not
                              # Optional — every call site below sets it explicitly;
                              # the default only covers a future call site that
                              # forgets to, which should degrade to "not flagged"
                              # rather than crash.

    # Additive fields (a company review's follow-up to the 5-way assessment
    # work) — `reason` alone was being asked to answer several DIFFERENT
    # merchant questions at once ("what evidence do I have," "what's
    # missing," "does my ledger prove X") by being cited verbatim as the
    # answer to all three, which read as near-identical, repetitive prose
    # regardless of which was actually asked (chargeback_agent.py's
    # _answer_case_fact() reused `reason` for exactly this reason before
    # this change). These are OPTIONAL, deliberately not a parallel state
    # model — every EXISTING call site (auto_decision_poller.py,
    # suggestion_poller.py, chargeback_agent.py's case-intro/prose builders)
    # keeps reading `reason` exactly as before; only U002's ledger/network
    # branches below populate the new fields, since that's the one place
    # this project actually has enough distinct sub-facts to make them
    # meaningfully different from `reason` itself. Every other branch (the
    # CBS-refund override, the decision_rules fallback) leaves them at "" —
    # callers should fall back to `reason` whenever a specific field is
    # empty, never assume it's always populated.
    evidence_summary: str = ""       # What's currently on file (merchant +
                              # network-side facts, as far as they're known)
                              # — answers "what evidence do I have?"
    evidence_gap: str = ""    # What's still missing/unverified — answers
                              # "what evidence is missing?" Empty string
                              # deliberately means "nothing missing," not
                              # "not computed" — every U002 branch below
                              # sets this explicitly, even to "".
    ledger_proof: str = ""    # What the merchant's ledger SPECIFICALLY does
                              # or doesn't establish on its own — answers
                              # "does my ledger prove X?" A narrower claim
                              # than evidence_summary: this is scoped to the
                              # ledger record alone, not the combined case.


def analyze_chargeback(row, db_path: str) -> Analysis:
    """
    Determine the recommended action for one chargeback row (anything
    dict-like with 'utr' and 'reason_code' keys — a sqlite3.Row works).

    1. CBS duplicate-refund check runs FIRST and takes priority over the
       reason-code rule table — a prior refund on this exact transaction
       makes the dispute moot/duplicate regardless of what its reason code
       claims, so it always means "fight" (dispute it, citing the refund).
    2. For U002 (duplicate transaction) specifically: the bank's own
       ledger can directly confirm or refute the claim, rather than
       falling through to decision_rules.py's evidence-free "refund"
       default. That default exists because this project has no
       evidence-capture path outside a live chat session — every call
       here would otherwise be evidence-free, and per decide()'s logic,
       no evidence means no realistic chance of winning, so EVERY U002
       case would resolve to "refund" purely because there's nothing to
       ask the merchant for — even when the ledger clearly shows only one
       credit landed and the customer's duplicate-charge claim doesn't
       hold. The ledger is real, bank-side evidence a background poller
       can act on with no merchant involved, same justification as the
       CBS refund check above. count_credits() is reversal-aware (see
       cbs.py's _net_posted_credits()) — a credit that was reversed and
       correctly reposted nets to one effective credit, not two, so this
       can't misread that sequence as a duplicate.
    2b. When ledger_entries alone shows exactly one clean credit (the
        "fight" case above), that's checked a second, INDEPENDENT way
        before being trusted: does the bank's own ledger actually agree
        with what the payment network separately reported as settled
        (cbs.reconcile_utr())? A ledger that's internally tidy can still
        disagree with an independent source — and that disagreement is
        itself real signal a same-source-only check could never surface,
        not the absence of evidence "refund" already means elsewhere in
        this function. A reconciliation mismatch here downgrades a would-
        be "fight" to "cannot confidently decide" instead.
    2c. Even a reconciled single credit only proves what reached the
        MERCHANT — it says nothing about how many times the CUSTOMER's
        account was actually debited upstream, at the NPCI switch. Reported
        live: a merchant asked "what if an intermediate party charged the
        customer?" after being told the duplicate claim was "not supported
        by the bank's own records," and that record was, in fact, silent on
        exactly that question — a real, unproven inferential leap from
        "merchant ledger clean" to "customer wasn't double-charged." Checked
        here via cbs.get_debit_attempt_status(), a genuinely independent
        (simulated) network-side transaction log: no record at all yet
        downgrades "fight" to "cannot confidently decide" (same shape as
        2b's reconciliation-mismatch case, for the same reason — absence of
        a check is not the same as a passed one); a second attempt that
        succeeded and was never reversed — invisible to the merchant's own
        ledger — flips the recommendation to "refund" entirely, since the
        network itself confirms the customer's claim even though it never
        reached this merchant's books.
    3. Otherwise, decision_rules.decide() with no evidence present, same
       as before: known reason codes resolve to "refund", unmapped codes
       return no recommendation (action=None) rather than guessing.
    """
    deadline_expired = deadline_bucket(row["response_deadline"]) == "overdue"

    cbs_refund = find_refund_for_utr(row["utr"], db_path=db_path)
    if cbs_refund:
        return Analysis(
            action="fight",
            reason=(
                f"CBS record shows this transaction was already refunded on "
                f"{cbs_refund['posting_date']} (ref: {cbs_refund['reference_id']}, "
                f"amount: {cbs_refund['amount']}) — the dispute appears moot/duplicate. "
                f"Disputing it should prevent a second payout for the same transaction."
            ),
            source="cbs",
            deadline_expired=deadline_expired,
        )

    if row["reason_code"] == "U002":
        credits = count_credits(row["utr"], db_path=db_path)
        if credits >= 2:
            recon = reconcile_utr(row["utr"], db_path=db_path)
            return Analysis(
                action="refund",
                reason=(
                    f"Ledger shows {credits} separate credits posted for this transaction "
                    f"(₹{recon['ledger_credit_total']:,.2f} total credited, against a network-"
                    f"reported settlement of ₹{recon['settlement_amount']:,.2f}) — the customer's "
                    f"duplicate-charge claim is confirmed by the bank's own posting records, not "
                    f"merely unrebutted. The duplicate amount should be refunded."
                ),
                source="ledger",
                deadline_expired=deadline_expired,
                evidence_summary=(
                    f"The merchant ledger shows {credits} separate credits totaling "
                    f"₹{recon['ledger_credit_total']:,.2f}, against a network-reported "
                    f"settlement of ₹{recon['settlement_amount']:,.2f}."
                ),
                evidence_gap="",
                ledger_proof=(
                    f"Yes — the ledger itself shows {credits} separate credits, directly "
                    f"confirming the duplicate-charge claim rather than refuting it."
                ),
            )
        if has_pending_suspense(row["utr"], db_path=db_path):
            return Analysis(
                action=None,
                reason=(
                    "A ledger entry for this transaction is still pending/unresolved — "
                    "cannot confidently recommend fight or refund until it settles."
                ),
                source="ledger",
                deadline_expired=deadline_expired,
                evidence_summary="A ledger entry for this transaction is still pending/unresolved.",
                evidence_gap="The pending ledger entry needs to settle before a recommendation can be made.",
                ledger_proof=(
                    "Not yet — the entry hasn't settled, so the ledger can't establish "
                    "anything conclusively yet."
                ),
            )
        if credits in (0, 1):
            # credits == 0 (no credit ever posted for this UTR at all) used to
            # fall straight through to decision_rules.decide()'s evidence-free
            # default below, which resolves EVERY such U002 case to "refund"
            # purely because there's nothing to ask the merchant for — even
            # when the network side hasn't been checked at all yet. That's a
            # real, live gap: a genuinely fresh chargeback (ledger not even
            # posted yet) got a confident-sounding "refund" recommendation
            # instead of "we haven't reconciled this yet." Folded into the
            # same reconciliation path credits==1 already used, rather than a
            # separate branch, so both counts get the same network-side
            # scrutiny — only the wording of what the ledger itself shows
            # differs between the two.
            ledger_desc = "no posted credit" if credits == 0 else "one posted credit"
            recon = reconcile_utr(row["utr"], db_path=db_path)
            if recon["status"] == "mismatch":
                return Analysis(
                    action=None,
                    reason=(
                        f"Ledger shows {ledger_desc} (₹{recon['ledger_credit_total']:,.2f}), "
                        f"but it does not reconcile with the network-reported settlement "
                        f"(₹{recon['settlement_amount']:,.2f}) for this transaction — cannot "
                        f"confidently recommend fight or refund until this discrepancy is "
                        f"investigated."
                    ),
                    source="ledger",
                    deadline_expired=deadline_expired,
                    evidence_summary=f"Ledger shows {ledger_desc} (₹{recon['ledger_credit_total']:,.2f}).",
                    evidence_gap=(
                        f"The ledger does not reconcile with the network-reported "
                        f"settlement (₹{recon['settlement_amount']:,.2f}) — this "
                        f"discrepancy needs investigation before a recommendation can "
                        f"be made."
                    ),
                    ledger_proof=(
                        "No — the ledger doesn't even reconcile with the network's own "
                        "settlement record, so it can't be trusted as proof on its own yet."
                    ),
                )
            # A reconciled (or, for credits==0, simply absent) ledger only
            # proves what reached the MERCHANT — it can't by itself rule out
            # a duplicate debit upstream that was reversed (or, worse, one
            # that succeeded but never reached this merchant's ledger at
            # all). get_debit_attempt_status() checks the network's own,
            # independent transaction log for exactly that — see this
            # function's 2c docstring entry.
            debit = get_debit_attempt_status(row["utr"], db_path=db_path)
            if debit["status"] == "no_data":
                return Analysis(
                    action=None,
                    reason=(
                        f"Merchant ledger shows {ledger_desc} — but that only confirms "
                        "what reached the merchant, not how many times the customer's "
                        "account was actually debited upstream. No NPCI/PSP transaction-"
                        "status reconciliation is on file for this UTR yet, so a duplicate "
                        "debit at an intermediary layer can't be ruled out. Recommend "
                        "checking with the acquiring PSP/NPCI before responding."
                    ),
                    source="network",
                    deadline_expired=deadline_expired,
                    evidence_summary=f"The merchant ledger shows {ledger_desc}.",
                    evidence_gap=(
                        "Customer-side debit/transaction status, transaction attempts, "
                        "and PSP/NPCI reconciliation are not yet on file for this UTR."
                    ),
                    ledger_proof=(
                        "No — it confirms what reached the merchant, not how many times "
                        "the customer's account was actually debited upstream."
                    ),
                )
            if debit["status"] == "duplicate_unreversed":
                return Analysis(
                    action="refund",
                    reason=(
                        f"Merchant ledger shows {ledger_desc}, but NPCI/PSP "
                        f"transaction records show {debit['attempt_count']} separate debit "
                        f"attempts against the customer with no reversal recorded — the "
                        f"customer's duplicate-charge claim is confirmed at the network "
                        f"level even though it was never reflected in the merchant's own "
                        f"ledger. Recommend refunding the customer and separately "
                        f"reconciling the missing settlement with the acquiring bank."
                    ),
                    source="network",
                    deadline_expired=deadline_expired,
                    evidence_summary=(
                        f"Merchant ledger shows {ledger_desc}, and NPCI/PSP transaction "
                        f"records show {debit['attempt_count']} separate debit attempts "
                        f"against the customer with no reversal recorded."
                    ),
                    evidence_gap="",
                    ledger_proof=(
                        "No — if anything, the network's own records confirm the "
                        "opposite: a genuine duplicate debit occurred upstream, even "
                        "though it was never reflected in the merchant's ledger."
                    ),
                )
            if debit["status"] == "duplicate_reversed":
                return Analysis(
                    action="fight",
                    reason=(
                        f"Merchant ledger shows {ledger_desc}, and NPCI/PSP transaction "
                        "records confirm a second debit attempt was made but reversed by "
                        "the network before settlement — the customer was not net-charged "
                        "twice, even though a duplicate attempt did occur upstream."
                    ),
                    source="network",
                    deadline_expired=deadline_expired,
                    evidence_summary=(
                        f"Merchant ledger shows {ledger_desc}, and NPCI/PSP transaction "
                        f"records confirm a second debit attempt was made but reversed "
                        f"by the network before settlement."
                    ),
                    evidence_gap="",
                    ledger_proof=(
                        "Yes — the network's own records confirm the customer was not "
                        "net-charged twice, even though a duplicate attempt did occur "
                        "upstream."
                    ),
                )
            return Analysis(
                action="fight",
                reason=(
                    f"Merchant ledger shows {ledger_desc}, and NPCI/PSP transaction "
                    "records confirm only one debit attempt was made against the customer "
                    "with no reversal — the duplicate-charge claim is not supported by "
                    "either the merchant's ledger or the network's own transaction record."
                ),
                source="network",
                deadline_expired=deadline_expired,
                evidence_summary=(
                    f"Merchant ledger shows {ledger_desc}, and NPCI/PSP transaction "
                    "records confirm only one debit attempt was made against the "
                    "customer with no reversal."
                ),
                evidence_gap="",
                ledger_proof=(
                    "Not by itself — but combined with the NPCI/PSP transaction "
                    "records (which confirm only one debit attempt, no reversal), "
                    "there's no evidence of a second charge."
                ),
            )

    result = decision_rules.decide(
        card_network=_NETWORK,
        reason_code=row["reason_code"],
        evidence_present=[],
        evidence_missing=[],
    )
    if result is None:
        return Analysis(action=None, reason="", source="", deadline_expired=deadline_expired)

    decision, reason = result
    return Analysis(action=decision, reason=reason, source="rules", deadline_expired=deadline_expired)
