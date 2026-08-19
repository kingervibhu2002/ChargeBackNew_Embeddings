---
title: "Evidence Strategy Overview"
section: "09_Evidence"
category: "Evidence Library"
document_type: "Evidence Reference"
keywords: ["evidence strategy", "chargeback rebuttal", "burden of proof", "evidence hierarchy", "exhibit organization", "submission timeline", "issuer review"]
difficulty: "Beginner"
---

# Evidence Strategy Overview

## Why Evidence Strategy Matters

Winning a chargeback dispute is not about having the most documents — it is about presenting the right documents, organized clearly, in a format that an issuer's dispute analyst can evaluate in 3–5 minutes. Dispute analysts review hundreds of cases per day. They are not investigators; they are reviewers. If your evidence does not immediately make your case obvious, you lose.

This document establishes the foundational principles of chargeback evidence strategy. The individual evidence types are covered in depth in subsequent documents (002 through 012). This overview focuses on the meta-skills: what issuers are looking for, how to organize your response, and the common mistakes that cause well-documented merchants to lose disputes they should win.

## The Burden of Proof

In chargeback disputes, the initial burden of proof falls on the merchant. When a cardholder files a dispute, the issuer provisionally credits the cardholder and requires the merchant to prove their case. This is the opposite of how most legal systems work — you are guilty until proven innocent.

The standard of proof is not "beyond reasonable doubt" — it is "preponderance of evidence." You must show that it is more likely than not that:
- The transaction was authorized (for authorization disputes).
- The goods or services were delivered as described (for non-receipt or quality disputes).
- The cardholder had a prior relationship with the merchant (for friendly fraud disputes).
- The merchant followed all required procedures (for processing error disputes).

You do not need certainty. You need a coherent, documented story that makes the cardholder's claim implausible.

## Evidence Hierarchy: Strongest to Weakest

Not all evidence is equal. Issuers weigh evidence based on its relevance, objectivity, and verifiability.

### Tier 1: Objective Technical Records (Strongest)
- 3D Secure authentication result with ECI code and CAVV value.
- AVS and CVV response codes from the authorization record.
- Carrier tracking with signed proof of delivery.
- Device fingerprint matching prior authenticated customer sessions.
- Login and usage logs from platform systems.
- IP address geolocation matching cardholder's billing address region.

These are machine-generated records that the cardholder cannot credibly dispute. They are also difficult to fabricate, which gives issuers confidence in their accuracy.

### Tier 2: Documented Communications
- Order confirmation email with timestamps and metadata.
- Shipping notification email with tracking link.
- Customer service interaction records (email tickets, chat logs).
- CRM notes with timestamps.
- Terms of service acceptance records.

These are semi-objective — they exist in your systems — but they are records you created and could theoretically alter. Issuers generally accept them but weigh them alongside Tier 1 evidence.

### Tier 3: Merchant Declarations and Policies
- Rebuttal letter narrative.
- Screenshots of return/cancellation policy.
- Screenshots of terms and conditions.
- Product description evidence (for "not as described" disputes).

This is the weakest evidence category because it is entirely merchant-generated. A rebuttal letter alone, without supporting documentation, almost never wins.

### Tier 4: Third-Party Support (Context)
- Cardholder's prior purchase history (showing established relationship).
- Prior disputes record (or absence thereof).
- Fraud intelligence data (device consortiums, fraud flags).

Third-party data is strong when available but is supplementary — it strengthens Tier 1 or 2 evidence rather than standing alone.

## What Issuers Look For

An issuer's dispute analyst is asking a simple question: "Did this merchant do what they should have done, and is the cardholder's claim credible?" Specifically:

**For authorization disputes (fraud codes):**
- Did the merchant verify the cardholder at transaction time?
- Is there evidence the cardholder (not a fraudster) initiated the transaction?
- Does the transaction fit the cardholder's purchase history?

**For non-receipt disputes:**
- Did the merchant ship the goods?
- Can the merchant prove delivery to the cardholder's address?
- Was the shipping address the cardholder's billing address?

**For "not as described" disputes:**
- Does the evidence show the goods matched the description?
- Did the merchant attempt to resolve the issue before the cardholder disputed?

**For cancelled recurring disputes:**
- Was the cardholder informed about recurring billing at signup?
- Was the cardholder's cancellation request honored within the required timeframe?

## Evidence Submission Timelines

Deadlines are absolute. A perfect evidence package submitted one day late is treated as no response — the chargeback stands.

| Network | Merchant Response Window |
|---|---|
| Visa | 30 days from chargeback notification |
| Mastercard | 45 days from chargeback notification |
| American Express | 20 days from chargeback notification |
| Discover | 30 days from chargeback notification |

Your actual working time is shorter than these windows suggest:
- Your acquiring bank may impose an earlier internal deadline (5–10 days before the network deadline).
- Evidence must be uploaded and accepted by your acquirer's system, not just drafted.
- Holiday and weekend timing can compress the effective window.

Set internal deadlines at 15 days for most chargebacks. Never let a dispute go unresponded — even a weak response is better than no response in most cases.

## How to Organize and Label Exhibits

Treat your evidence package like a legal brief, not an email attachment dump. Issuers respond better to organized evidence with clear labeling.

**Recommended structure:**
1. Rebuttal letter (1–2 pages maximum) that tells the narrative story and references each exhibit.
2. Exhibit A: Transaction record (authorization data, order details).
3. Exhibit B: Primary evidence (delivery proof, usage logs, authentication record — varies by dispute type).
4. Exhibit C: Supporting evidence (communication records, customer history, policy screenshots).
5. Exhibit D: Additional supporting documents if needed.

**Labeling standards:**
- Include the exhibit label in the filename: "ExhibitA_AuthorizationRecord.pdf"
- If submitting multiple pages as one exhibit, merge them into a single PDF.
- Highlight or annotate key information within exhibits (circle the delivery confirmation, highlight the login timestamp).

**Page count:** Most issuers have page limits (10–20 pages is typical). Prioritize ruthlessly. Five well-chosen, clearly annotated pages beat 30 pages of raw system exports.

## Quality vs. Quantity

The most common mistake in chargeback evidence submission is confusing volume with strength. Merchants who attach everything — every email, every system log page, every policy document — often lose to merchants who submit three targeted exhibits that directly address the dispute code.

Apply this test to each piece of evidence before including it: "Does this directly address the cardholder's specific claim?" If not, omit it.

A 200-page packet of server logs is not compelling evidence if the dispute analyst cannot find the three relevant log lines within it. Extract, annotate, and present — do not dump.

## Common Mistakes That Cause Merchants to Lose

**Wrong evidence for the dispute code:** Submitting delivery tracking for a "not as described" dispute. Submitting cancellation policy for a "non-receipt" dispute. Match your evidence to the specific dispute reason.

**Missing the key document:** A compelling rebuttal letter with no actual proof. Delivery tracking without the signed POD for a high-value dispute. Usage logs for a different date than the disputed transaction.

**Unreadable evidence:** Blurry screenshots, truncated PDFs, system exports in raw database format. Annotate and make your key evidence visually obvious.

**Rebuttal letter without exhibits:** A narrative without supporting documentation is a merchant statement — it has no evidential value on its own.

**Late submission:** The most common loss reason for merchants with valid defenses. Build internal deadline tracking and alert systems.

**Not matching dispute code requirements:** Visa and Mastercard have specific documentary requirements per dispute code. Submit exactly what the code requires, then add supporting evidence.

## Digital vs. Physical Evidence

**Digital evidence** (logs, screenshots, email records) must be presented in a readable format. Raw database exports are not acceptable. Convert to PDF or annotated screenshots. Include clear timestamps, and if timestamps are in server time (UTC), note the conversion to local time or transaction time zone.

**Physical evidence** (signed delivery receipts, handwritten notes, physical contracts) must be scanned clearly. Use a minimum 300 DPI scan. Ensure the entire document is captured, including signatures and dates.

## Summary

Chargeback evidence strategy is a discipline, not a document collection exercise. The winning approach: understand the specific dispute code and its requirements, build your evidence package around Tier 1 objective records first, organize and label clearly for a time-pressured reviewer, submit well before the deadline, and include only evidence that directly advances your case. Every subsequent document in this library provides detailed guidance on specific evidence types. This overview provides the framework within which all of them should be applied.
