---
title: "NPCI UPI Dispute Code U002 — Duplicate Transaction"
description: "Complete merchant guide to NPCI UPI dispute code U002: double debits from UPI system retries, reconciliation evidence, merchant's obligation to refund, and how to prove only one credit was received."
category: RuPay / NPCI
reason_code: "U002"
chargeback_type: "Duplicate Transaction — Same Amount Debited Twice"
win_rate: Low for merchant (if duplicate credit is confirmed); High (if only one credit received)
last_updated: 2026-06-29
tags: [NPCI, UPI, U002, duplicate-transaction, double-debit, system-retry, reconciliation, refund, India]
---

# NPCI U002 — Duplicate Transaction

## What This Dispute Code Means

NPCI UPI dispute code U002 covers situations where a customer's bank account is debited more than once for the same UPI transaction — a double or duplicate debit. The customer pays once (intentionally), but their account is charged twice for the same amount, either because of a system retry, a network timeout that caused the payment to be processed twice, or a bank system failure that duplicated the settlement instruction.

This dispute is fundamentally different from a merchant error. In most U002 scenarios, both the customer and the merchant are victims of a technical failure in the payment infrastructure — the customer loses double the intended amount from their bank account, and the merchant may or may not have received two credits depending on where the duplication occurred.

---

## How Duplicate UPI Debits Happen

Understanding the technical root cause is essential for building a response.

### System Retry Loops

When a UPI payment request times out — the network response is delayed beyond the app's timeout threshold — the UPI app or bank system may automatically retry the payment. If the original request actually succeeded (the money was debited) but the confirmation was delayed, the retry creates a second debit. The customer's account shows two identical transactions at nearly the same time.

### PSP (Payment Service Provider) Layer Failures

UPI transactions flow through multiple layers: the customer's UPI app, the customer's PSP, NPCI's central infrastructure, the merchant's PSP, and the merchant's acquiring bank. A failure in the communication handoff between any two layers can cause a transaction to be processed at one layer but not confirmed at the next — triggering a retry that doubles the debit.

### Bank Core Banking System (CBS) Issues

Occasionally, a bank's core banking system processes a debit instruction twice due to internal duplication in the queue management system. This is rare but does happen, particularly during high-traffic periods (festival seasons, month-end, auspicious payment dates in India when UPI volumes spike dramatically).

### Merchant-Side Retry Configuration

Some merchants configure their payment gateway to retry failed UPI payment attempts automatically. If the retry is sent before the first attempt's confirmation is received, two separate payment requests can reach the customer's bank — resulting in two debits. This is a merchant-configurable failure and represents a case where the merchant bears responsibility.

---

## What the Merchant Typically Receives

The key question in a U002 dispute: how many credits did the merchant actually receive?

**Scenario A: Merchant received one credit (most common)**
The technical failure occurred between the customer's bank and NPCI, or within the bank's internal systems. The customer was debited twice, but only one credit reached the merchant's settlement account. NPCI's settlement records will show one transaction.

**Scenario B: Merchant received two credits (less common)**
The duplication propagated all the way through the payment chain. The merchant's bank account shows two credits for the same amount at nearly the same timestamp. The merchant effectively received double payment.

---

## Merchant Obligations by Scenario

### If the Merchant Received Only One Credit

As general policy, a duplicate debit that never produced a duplicate merchant credit is the customer's bank/PSP's obligation to investigate and auto-reverse, not something the merchant owes a refund for. This describes the typical policy position and a typical merchant defense — it is NOT, on its own, proof that a specific customer's account was debited only once. "Merchant received one credit" establishes what reached the merchant; it does not by itself establish the customer's debit history, which still needs to be reconciled against the customer's bank/PSP/NPCI records before a specific case can be considered settled.

**Merchant's action:**
- Provide transaction records confirming one credit was received (bank statement excerpt, payment gateway settlement report)
- Provide the NPCI transaction reference (UTR) for the single confirmed transaction
- Cooperate with the acquiring bank if they request documentation

### If the Merchant Received Two Credits

The merchant received payment twice and must refund the duplicate. Under NPCI rules, merchants are obligated to refund duplicate payments promptly.

**Merchant's action:**
- Initiate a UPI refund for the duplicate credit amount
- Provide the refund UTR to the acquiring bank as evidence
- Document the refund in your order management system

Retaining a duplicate UPI credit without issuing a refund is a violation of NPCI's merchant obligations and will result in a forced reversal plus potential penalties. <!-- NEEDS VERIFICATION: confirm the specific "forced reversal plus potential penalties" consequence against real NPCI merchant-obligation documentation -->

---

## Evidence for U002 Disputes

**To demonstrate only one credit was received:**

| Evidence | What It Shows |
|---|---|
| Payment gateway settlement report | Shows only one credit for this transaction in the settlement period |
| Bank statement for merchant account | Shows a single credit for the transaction amount on the relevant date |
| NPCI transaction reference (UTR) | A single UTR = a single NPCI-processed transaction |
| Payment gateway transaction log | Shows one successful authorization and one settlement |

**To demonstrate refund of duplicate credit:**

| Evidence | What It Shows |
|---|---|
| Refund UTR | Proof the duplicate amount was returned to the customer |
| Refund confirmation from payment gateway | Refund was processed and settled |
| Customer communication confirming refund | Good practice; not strictly required |

---

## T+1 Auto-Reversal Relevance

For U002 disputes where the duplicate debit did not result in a duplicate credit to the merchant (Scenario A), NPCI's auto-reversal mandate applies. The customer's bank should automatically detect the duplicate debit through their reconciliation systems and initiate a reversal within T+1 (the next business day). If the auto-reversal mechanism works correctly, the customer never needs to file a formal U002 dispute — they simply see the reversal appear on their account.

When auto-reversal fails, the customer files a formal complaint with their bank, triggering the NPCI dispute process. The bank then has 30 days to investigate and resolve. <!-- NEEDS VERIFICATION: same 30-day mandate flagged in 000_RuPay_NPCI_Overview.md -->

---

## Prevention for Merchants

**Configure retry logic carefully.** If your payment gateway is configured to retry UPI payment requests automatically, ensure retries are sent only after a definitive failure response from NPCI — not after a timeout where the first attempt may have succeeded. Work with your PSP to review retry configurations.

**Implement idempotency keys.** Modern payment gateways support idempotency keys — unique identifiers for each payment request that prevent duplicate processing even if the same request is submitted multiple times. Ensure idempotency keys are implemented for all UPI payment initiations.

**Monitor for duplicate UTRs.** A simple daily reconciliation check — flagging cases where two transactions share the same amount, VPA, and date within a short window — catches duplicate credits before they accumulate. Automate this check.

**Reconcile credits against orders daily.** Compare each credit in your bank statement against your order management system. A credit with no corresponding order is either a duplicate or an unmatched transaction that needs investigation.

---

## Frequently Asked Questions

**Q: The customer's bank says they were debited twice, but we only show one credit. Who is responsible for the refund?**
A: As a general policy matter, the customer's bank is responsible for reversing a duplicate debit that never produced a duplicate merchant credit — you would not owe a refund in that scenario. Provide your settlement records to your acquiring bank to document that only one credit arrived; your acquirer submits this to NPCI as merchant-side evidence. This settlement record on its own does not confirm how many times the customer's account was actually debited — that still depends on the customer-side/NPCI reconciliation your acquirer and the customer's bank carry out, not on your settlement report alone.

**Q: Can we keep both credits if the customer is not complaining?**
A: No. Retaining a duplicate credit is a violation of NPCI merchant rules. If your reconciliation identifies a duplicate credit, you must initiate a refund for the excess amount. Proactively contact the customer and issue the refund. This protects you from a future U002 dispute with accrued interest or penalties.

**Q: A customer filed U002 claiming duplicate charge, but our records show two separate orders were placed, each with a separate payment. How do we handle this?**
A: This is not a U002 — it is a legitimate two-order scenario. Provide your order management records showing two distinct orders were placed with different order IDs, along with the corresponding payment records showing each UTR matches a distinct order. The customer may have made a second purchase accidentally, but that is not a duplicate transaction.

**Q: Our payment gateway says there was a "retry" and two UTRs were generated. Did we get two payments?**
A: Check your bank settlement statement directly. Two UTRs may have been generated but only one may have settled to your account. Reconcile your gateway report against your bank statement — the bank statement is authoritative. If both UTRs appear in your bank credits, you received two payments and must refund one.

**Q: Is there a time limit for a customer to file a U002 complaint?**
A: Customers must typically file transaction complaints within 30–90 days (depending on the bank's complaint policy). <!-- NEEDS VERIFICATION: this 30-90 day range is wider and less specific than the 30-day figure used elsewhere in this encyclopedia's RuPay docs — confirm against real bank/NPCI complaint-window policy rather than assuming consistency --> However, NPCI's broader dispute window and the Banking Ombudsman's jurisdiction extend protection for longer periods. For this reason, maintain transaction records for at least 18–24 months.
