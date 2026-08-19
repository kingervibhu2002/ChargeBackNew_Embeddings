---
title: "Visa Claims Resolution (VCR) — Complete Framework Overview"
section: "04_Visa"
category: "Visa Reason Codes"
network: "Visa"
reason_code: "N/A"
document_type: "Overview"
keywords: ["VCR", "Visa Claims Resolution", "dispute process", "allocation", "collaboration", "chargeback workflow", "Visa overview"]
difficulty: "Beginner"
---

# Visa Claims Resolution (VCR) — Complete Framework Overview

## What Is Visa Claims Resolution?

Visa Claims Resolution (VCR) is the standardized dispute framework that Visa introduced in April 2018 to replace the older, more fragmented chargeback process. VCR fundamentally changed how disputes are initiated, adjudicated, and resolved between cardholders, issuers, merchants, and acquirers.

Before VCR, the Visa dispute process involved multiple back-and-forth cycles — chargebacks, representments, pre-arbitration, and arbitration — that could drag on for months and cost all parties significant time and money. VCR was designed to compress that timeline, reduce the number of invalid chargebacks, and place liability assignment logic directly into the processing infrastructure rather than leaving it entirely up to manual review.

The core innovation of VCR is its two-workflow model: **Allocation** and **Collaboration**. Every Visa dispute is routed into one of these two workflows based on the reason code and the nature of the dispute.

---

## The Two VCR Workflows

### Allocation Workflow

The Allocation workflow applies primarily to fraud and authorization disputes — situations where Visa's own processing data (authorization records, authentication logs, chip data) can definitively determine which party bears liability without requiring back-and-forth documentation exchange.

Under Allocation, Visa or the issuer assigns liability automatically based on processing rules. If a merchant processed an EMV chip transaction correctly, the issuer bears liability for counterfeit fraud. If the merchant failed to use a chip terminal, liability shifts to the merchant. The system makes this determination algorithmically.

**Reason codes in the Allocation workflow include:**
- 10.1 — EMV Liability Shift Counterfeit Fraud
- 10.2 — EMV Liability Shift Non-Counterfeit Fraud
- 11.1 — Card Recovery Bulletin
- 11.2 — Declined Authorization
- 11.3 — No Authorization

In the Allocation workflow, merchants typically have a narrow window to dispute by providing compelling counter-evidence that overrides the automated liability assignment. Simply claiming the transaction was valid is not sufficient — you must produce evidence that directly contradicts the basis for the chargeback.

### Collaboration Workflow

The Collaboration workflow applies to consumer disputes and processing error disputes — situations where documentation and communication between parties is necessary to resolve the claim.

Under Collaboration, merchants have the opportunity to submit a rebuttal with supporting evidence. The issuer reviews this evidence and decides whether to accept the merchant's position or escalate. This workflow resembles the traditional chargeback-representment cycle but with tighter timelines.

**Reason codes in the Collaboration workflow include:**
- 12.x — Processing Errors
- 13.x — Consumer Disputes (Not Received, Cancelled, Not as Described, etc.)

The Collaboration workflow gives merchants the best opportunity to recover revenue, but it requires organized, accurate, and complete documentation submitted within strict deadlines.

---

## The VCR Dispute Process: Step by Step

### Step 1: Cardholder Dispute Filed
A cardholder contacts their issuing bank to dispute a charge. The issuer reviews the claim, determines if it qualifies under a Visa reason code, and initiates a dispute through the Visa system.

### Step 2: Pre-Dispute Notification (Where Applicable)
For some dispute types, VCR includes an optional pre-dispute phase where the issuer can reach out to the acquirer before formally filing. This allows disputes to be resolved before they become chargebacks on a merchant's record.

### Step 3: Dispute Filed Against Merchant
The issuer formally files the dispute. Funds are debited from the merchant's account. The acquirer receives the dispute and notifies the merchant.

### Step 4: Merchant Response
The merchant reviews the dispute and has two choices:
- **Accept the chargeback** (do nothing, or formally accept) — the debit stands.
- **Fight the chargeback** — submit a representment with a rebuttal letter and supporting evidence within the deadline.

### Step 5: Issuer Review
The issuer reviews the merchant's representment. If they find the evidence compelling, they accept the merchant's position and funds are returned. If they reject the representment, the dispute escalates.

### Step 6: Pre-Arbitration
If the merchant's representment is rejected, either party may escalate to pre-arbitration. At this stage, Visa's dispute rules govern which party wins. The losing party typically bears additional fees.

### Step 7: Arbitration
If pre-arbitration fails to resolve the dispute, it moves to Visa arbitration. Visa makes a binding ruling. Arbitration fees ($500 or more) are assessed against the losing party, making this stage costly for merchants with weak cases.

---

## Key VCR Timelines

| Stage | Timeframe |
|---|---|
| Issuer initiates dispute | Within 120 days of transaction date (or 120 days from expected delivery date) |
| Merchant representment deadline | 30 days from chargeback notification |
| Pre-arbitration filing | 30 days from representment |
| Arbitration filing | 10 days from pre-arbitration response |

**Critical note:** Missing the 30-day representment deadline is an automatic loss. There are no extensions. Build internal workflows that catch disputes the day they arrive.

---

## How VCR Differs from Mastercard's Dispute Process

Visa and Mastercard both operate dispute frameworks, but there are meaningful structural differences merchants should understand:

| Dimension | Visa VCR | Mastercard MDRS |
|---|---|---|
| Framework name | Visa Claims Resolution (VCR) | Mastercard Dispute Resolution System (MDRS) |
| Launched | April 2018 | October 2018 |
| Workflow model | Two workflows: Allocation & Collaboration | Single workflow with reason-code-driven logic |
| Automated liability assignment | Yes — Allocation workflow assigns liability algorithmically | Less automated; more documentation-driven |
| Compelling Evidence standard | Visa CE3.0 for 10.4 fraud disputes | Mastercard's own compelling evidence rules |
| Reason code structure | 10.x, 11.x, 12.x, 13.x | 4-digit codes (4853, 4863, etc.) |
| Arbitration fees | $500 (merchant) / $500 (issuer) | $250–$500 depending on amount |
| Pre-arbitration step | Yes | Yes (called "Second Presentment" in some contexts) |

The most significant practical difference is Visa's Allocation workflow — it removes the merchant's ability to fight certain fraud chargebacks unless they can demonstrate specific processing compliance (e.g., chip-and-PIN was used). Mastercard relies more on documentation in most categories.

---

## Visa Compelling Evidence 3.0 (CE3.0)

Introduced in April 2023, Visa CE3.0 is a major update that gives merchants a powerful tool specifically against 10.4 (Card-Absent Fraud) chargebacks when the underlying claim is likely friendly fraud.

Under CE3.0, if a merchant can show that the same cardholder (matched by device fingerprint, IP address, or account details) completed at least **two prior undisputed transactions** with the merchant in the previous 120–365 days, the liability shifts back to the issuer. This is designed to combat repeat friendly fraud by cardholders who dispute legitimate purchases.

CE3.0 requires merchants to maintain detailed transaction logs — device ID, IP address, login email, physical delivery address — to build the matching evidence profile.

---

## Visa Fraud and Dispute Monitoring Programs

Visa operates monitoring programs that penalize merchants with excessive chargeback or fraud rates:

- **Visa Fraud Monitoring Program (VFMP):** Triggers when a merchant's fraud-to-sales ratio exceeds thresholds (typically 0.9% in volume). Merchants in VFMP cannot fight certain fraud chargebacks and face escalating fines.
- **Visa Dispute Monitoring Program (VDMP):** Triggers when overall chargeback rate exceeds 0.9% (Early Warning) or 1.8% (Standard) thresholds. Fines and eventual MATCH listing can result.

Merchants who find themselves in these programs must work with their acquirer to implement fraud controls and reduce dispute rates before fines become unsustainable.

---

## Merchant Takeaways

1. **Know your workflow.** Fraud codes (10.x) often mean Allocation — your defense options are limited. Consumer dispute codes (13.x) mean Collaboration — documentation wins.
2. **Never miss the 30-day deadline.** Build an internal alert system that flags every chargeback the day it arrives.
3. **CE3.0 is a weapon against friendly fraud.** Invest in the data infrastructure to collect device fingerprints, IP addresses, and login records so you can leverage CE3.0 when cardholders repeatedly dispute legitimate purchases.
4. **Monitor your ratios.** Check your fraud and dispute ratios monthly. Entering VFMP or VDMP is far more damaging than losing individual chargebacks.
5. **Accept unwinnable chargebacks gracefully.** Fighting a chargeback you cannot win wastes representment fees and can increase your dispute rate if the representment fails and escalates.
