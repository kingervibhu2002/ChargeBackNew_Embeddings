---
title: "Mastercard Excessive Chargeback Program (ECP)"
category: Monitoring Programs
doc_type: program-overview
program: Mastercard ECP
network: Mastercard
audience: merchants
last_updated: 2026-06-01
tags: [Mastercard, ECP, excessive chargeback, CMM, ECM, fines, monitoring, MATCH list]
---

# Mastercard Excessive Chargeback Program (ECP)

## What Is the Mastercard ECP?

The Mastercard Excessive Chargeback Program (ECP) is Mastercard's monitoring and enforcement framework for merchants with elevated chargeback ratios. Similar in purpose to Visa's VDMP, the ECP identifies merchants whose dispute levels exceed Mastercard's acceptable thresholds and imposes mandatory remediation requirements, monthly fines, and ultimately the risk of termination and MATCH list placement for merchants who fail to exit.

The ECP operates at two severity levels — Chargeback Monitored Merchant (CMM) and Excessive Chargeback Merchant (ECM) — with different thresholds and fine structures for each.

---

## ECP Threshold Tiers

Mastercard uses a combined ratio + count approach, similar to Visa's VDMP:

### CMM — Chargeback Monitored Merchant

| Metric | Threshold |
|---|---|
| Monthly chargeback count | ≥ 100 chargebacks |
| Chargeback-to-transaction ratio | > 1.0% |

Both conditions must be met simultaneously to enter CMM status.

### ECM — Excessive Chargeback Merchant

| Metric | Threshold |
|---|---|
| Monthly chargeback count | ≥ 300 chargebacks |
| Chargeback-to-transaction ratio | > 1.5% |

A merchant automatically moves to ECM status when they exceed the higher thresholds — they do not need to pass through CMM first, though merchants at CMM who do not remediate may escalate to ECM.

---

## How Mastercard Calculates the Ratio

Mastercard's ratio calculation: (number of Mastercard chargebacks received in a given month) ÷ (number of Mastercard transactions in the prior calendar month) × 100.

Note the denominator: Mastercard uses the **prior month's transaction count**, not the current month's. This means a sudden drop in sales volume in the current month can cause the ratio to spike even if chargeback counts remain stable.

---

## ECP Fine Schedule

Mastercard's fine structure under ECP is more complex than Visa's VDMP and escalates based on the tier and the duration in the program:

### CMM Fine Schedule

| Month in Program | Fine Amount |
|---|---|
| Month 1 | $1,000 |
| Month 2 | $2,000 |
| Month 3 | $5,000 |
| Month 4 | $25,000 |
| Month 5 | $50,000 |
| Month 6+ | $100,000/month |

### ECM Fine Schedule

| Month in Program | Fine Amount |
|---|---|
| Month 1 | $25,000 |
| Month 2 | $50,000 |
| Month 3 | $100,000 |
| Month 4+ | $100,000/month + issuer filing fee reimbursement |

In addition to monthly fines, Mastercard may assess an **Issuer Recovery Assessment** — a per-chargeback fee charged to the merchant's acquirer and passed to the merchant — once a merchant has been in the program beyond Month 4. This assessment reimburses issuing banks for the operational cost of processing disputes with the merchant.

---

## Concurrent Fine Exposure

A merchant enrolled in both CMM (or ECM) and Mastercard's Fraud Excessive Program (a separate monitoring track for fraud) faces fines from both programs simultaneously. At Month 6+ of ECM status with concurrent fraud program fines, total monthly fine exposure can reach $200,000 or more — making rapid remediation an urgent financial priority.

---

## MATCH List Risk from ECP

When Mastercard terminates a merchant account due to ECP failure, the acquirer is required to place the merchant on the MATCH list under **Reason Code 1: Excessive Chargebacks.** 

MATCH list placement means:
- A 5-year block on obtaining a new merchant account with any major acquirer
- Effectively the end of the ability to accept card payments through normal channels
- Required disclosure to any acquirer during the placement period
- Potential impact on business sale/valuation due to payment processing inability

The threat of MATCH list placement is one of the primary reasons merchants must treat ECP enrollment as a crisis-level event requiring immediate executive attention.

---

## ECP Remediation Plan Requirements

When a merchant is enrolled in the ECP, Mastercard requires the acquiring bank to submit a merchant remediation plan. The plan must include:

1. **Root cause analysis:** What is driving the elevated chargeback count and ratio? (Fraud? Fulfillment failures? Subscription practices? Product quality?)

2. **Specific action items with timelines:** Not vague commitments ("we will improve fraud controls") but specific actions ("We will implement 3DS2 for all CNP transactions by [DATE]").

3. **Monthly progress milestones:** Expected chargeback counts and ratios for each month of the remediation period.

4. **Measurable success criteria:** How will the merchant and acquirer know that remediation is complete?

The remediation plan must be submitted within 30 days of ECP enrollment notification. Failure to submit or failure to meet milestones accelerates the fine escalation.

---

## How to Exit ECP

### CMM Exit

A merchant exits CMM status when their chargeback ratio falls below 1.0% **and** their monthly chargeback count falls below 100 for **three consecutive months.**

### ECM Exit

A merchant exits ECM status when their chargeback ratio falls below 1.0% **and** their monthly chargeback count falls below 300 for **three consecutive months.** 

Note: ECM exit reduces the merchant to monitoring, but they remain in CMM status until they also exit the CMM thresholds.

---

## Differences Between Mastercard ECP and Visa VDMP

| Feature | Mastercard ECP | Visa VDMP |
|---|---|---|
| Tier names | CMM / ECM | Early Warning / Standard / Excessive |
| Ratio threshold (standard tier) | > 1.0% (CMM) | ≥ 0.9% (Standard) |
| Count threshold (standard tier) | ≥ 100 (CMM) | ≥ 100 |
| Maximum monthly fine | $100,000/month (ECM Month 4+) | $25,000/month (Month 7+) + per-dispute |
| Denominator for ratio | Prior month's transactions | Same month's transactions |
| Exit requirement | 3 consecutive compliant months | 3 consecutive compliant months |
| MATCH placement risk | Yes (on termination) | Yes (on termination) |

Mastercard's fines escalate more aggressively than Visa's in the early months (CMM Month 4 = $25,000; ECM Month 1 = $25,000), making early intervention even more critical.

---

## High-Priority Actions Upon ECP Notification

1. **Do not panic — immediately assess:** Pull a complete breakdown of your Mastercard chargebacks by reason code, product, issuer, and month. This data is available through your acquirer.

2. **Identify the root cause:** Is this a fraud problem (MC 4837 concentrated)? A fulfillment problem (MC 4855)? A subscription problem (MC 4853)? Different root causes require different remediation strategies.

3. **Calculate the fine trajectory:** Project your current monthly chargeback count against the fine schedule. Understand what Month 3, Month 4, and Month 6 look like financially if remediation is not achieved. This motivates the investment in remediation.

4. **Engage professional help if needed:** Chargeback management platforms with Mastercard ECP experience (Chargebacks911, Kount, Ethoca) can accelerate remediation. The cost is typically far lower than continuing fine exposure.

5. **Consider temporary business process changes:** If certain products, channels, or marketing practices are driving disproportionate chargebacks, consider temporarily suspending them during remediation to protect the core business's processing ability.

---

## Monthly ECP Tracking Template

| Month | MC Chargebacks | MC Transactions | Chargeback Ratio | Program Tier | Monthly Fine | Cumulative Fines |
|---|---|---|---|---|---|---|
| [Month 1] | [COUNT] | [COUNT] | [X%] | [CMM/ECM] | [$X] | [$X] |
| [Month 2] | [COUNT] | [COUNT] | [X%] | [CMM/ECM] | [$X] | [$X] |
| [Month 3] | [COUNT] | [COUNT] | [X%] | [CMM/ECM] | [$X] | [$X] |
| [Month 4] | [COUNT] | [COUNT] | [X%] | [CMM/ECM] | [$X] | [$X] |
| [Month 5] | [COUNT] | [COUNT] | [X%] | [CMM/ECM] | [$X] | [$X] |
| [Month 6] | [COUNT] | [COUNT] | [X%] | [CMM/ECM] | [$X] | [$X] |

Track the trend weekly during active remediation — monthly data arrives too late for real-time course correction.
