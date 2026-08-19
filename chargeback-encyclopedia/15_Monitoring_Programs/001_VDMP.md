---
title: "Visa Dispute Monitoring Program (VDMP)"
category: Monitoring Programs
doc_type: program-overview
program: VDMP
network: Visa
audience: merchants
last_updated: 2026-06-01
tags: [VDMP, Visa, monitoring, chargeback ratio, fines, dispute, threshold]
---

# Visa Dispute Monitoring Program (VDMP)

## What Is VDMP?

The Visa Dispute Monitoring Program (VDMP) is Visa's mechanism for identifying and managing merchants whose dispute (chargeback) ratios exceed acceptable thresholds. VDMP exists to protect the integrity of the Visa payment network — excessive dispute ratios indicate that a merchant's business practices, fraud controls, or product quality create systemic risk for cardholders, issuers, and the network.

When a merchant is placed in VDMP, they face monthly program reviews, mandatory remediation plans, escalating fines, and the risk of losing their ability to process Visa transactions if they fail to exit the program within defined timeframes.

---

## VDMP Thresholds

VDMP operates on three tiers, determined by a merchant's dispute ratio and absolute monthly dispute count:

| Tier | Dispute Ratio | Monthly Dispute Count | Status |
|---|---|---|---|
| Early Warning | ≥ 0.65% | ≥ 75 disputes | Monitored — no fines yet |
| Standard | ≥ 0.9% | ≥ 100 disputes | Monitored — fines begin |
| Excessive | ≥ 1.8% | ≥ 1,000 disputes | High-risk — elevated fines |

**How Visa calculates the ratio:** Number of disputes in a given month ÷ number of Visa transactions in the same month × 100. Visa uses a calendar-month rolling window.

**The count threshold matters:** A merchant processing 50,000 transactions per month at a 0.9% dispute rate has 450 disputes — placing them in Standard tier. A merchant processing only 500 transactions per month at a 0.9% rate has only 4.5 disputes per month — they do not meet the 100-dispute count threshold and are not entered into VDMP even at the same ratio.

---

## How Merchants Enter VDMP

Visa monitors all merchants' dispute ratios monthly at the MID (Merchant ID) level. When a merchant's ratio first crosses a threshold:

1. Visa notifies the acquiring bank.
2. The acquirer notifies the merchant.
3. Visa begins the formal program month count.

The notification typically arrives via the acquirer within 30 days of the end of the month in which the threshold was first crossed.

---

## VDMP Fine Schedule

Fines begin when a merchant enters the Standard tier and escalate based on the length of time in the program:

| Month in Program | Fine Amount | Structure |
|---|---|---|
| Month 1–4 (Standard) | $50 per dispute | Per excess dispute above threshold |
| Month 5–6 (Standard) | $50 per dispute | Per excess dispute + issuer reimbursement fees |
| Month 1–6 (Excessive) | $50 per dispute | Per excess dispute |
| Month 7–12 | $50 per dispute + $25,000/month | Escalated enforcement |
| Month 13+ | $50 per dispute + $25,000/month | Review for disqualification |

**"Excess dispute" calculation:** If your dispute count is 250 this month and the Standard threshold at your transaction volume is 100, your excess disputes are 150 — the fine is 150 × $50 = $7,500 for that month.

In practice, fines compound quickly for merchants who do not remediate promptly. A merchant with 500 monthly chargebacks at $50/excess dispute above the 100-threshold level pays $20,000/month in fines alone, before any other program fees.

---

## 6-Month Review Period and Exit Criteria

Merchants are given an initial 6-month period (for Standard tier) to remediate:

- **Month 1–3:** Remediation expected. Acquirer submits merchant remediation plan to Visa.
- **Month 4–6:** Progress assessed. Merchant must demonstrate declining dispute counts.
- **Month 6:** If the merchant has exited the threshold (ratio below 0.9%, or dispute count below 100), they exit VDMP.

**Exit condition:** A merchant exits VDMP when their dispute ratio falls below the threshold for **three consecutive months.** Staying just below the threshold for two months, then bouncing above it, resets the exit timeline.

---

## Consequences of Failing to Exit VDMP

If a merchant remains in VDMP beyond the Standard program's remediation window:

- **Month 7+:** Fines escalate. Visa may add an additional $25,000 per month enforcement fine.
- **Month 12+:** Visa reviews the merchant for disqualification — potential termination of Visa processing privileges.
- **MATCH list placement:** Account termination due to VDMP failure qualifies as a MATCH list placement reason (Code 1: Excessive Chargebacks). The merchant would be placed on MATCH for 5 years.
- **Increased acquirer reserve:** Acquirers typically respond to VDMP placement by increasing rolling reserves to cover potential liability.

---

## Merchant Obligations Upon VDMP Entry

When notified of VDMP placement, merchants should immediately:

1. **Request the dispute data:** Obtain a breakdown of disputes by reason code, issuer, and product type from your acquirer. Understanding what is driving the ratio is the prerequisite for remediation.

2. **Prepare a remediation plan:** Submit a written plan to your acquirer detailing: root cause analysis, specific actions being taken (fraud tool deployment, 3DS implementation, product changes, customer service improvements), and projected timeline for improvement.

3. **Implement immediate controls:** Any fraud controls that can be implemented quickly (3DS2 activation, velocity rules, fraud scoring) should be enabled immediately — not scheduled for the next quarter.

4. **Monitor weekly, not monthly:** During active VDMP remediation, monitor chargeback counts and ratio weekly. Monthly monitoring is too slow to detect whether measures are working.

5. **Work with a chargeback management vendor:** Professional chargeback management services (Chargebacks911, Midigator, Kount) have experience with VDMP remediation and can assist with representment processes that reduce the effective ratio impact.

---

## How Representments Affect VDMP

Winning representments does not reduce the VDMP ratio. The VDMP ratio is calculated based on gross chargebacks received, not net chargebacks after representment wins. This is a critical distinction: fighting and winning chargebacks is valuable for recovering funds, but it does not help exit VDMP.

**What actually reduces the VDMP ratio:**
- Preventing new chargebacks from being filed (via 3DS, Verifi/Ethoca alerts, customer service improvement)
- Growing transaction volume (same chargeback count at higher denominator = lower ratio)
- Refunding high-risk orders before they become chargebacks (via pre-chargeback alerts)

---

## Common Causes of VDMP Entry

| Root Cause | Remediation |
|---|---|
| High CNP fraud — no 3DS | Implement 3DS2 immediately |
| Friendly fraud — subscription charges | Add reminder emails, easy cancel button, CDRN/Ethoca alerts |
| Unrecognized descriptor | Update billing descriptor to brand name |
| Poor customer service — escalation to bank | Improve response SLA, offer proactive refunds |
| Return fraud and "not as described" disputes | Update product descriptions, require return before refund |
| High-risk product category | Consider MCC reassessment; consult acquirer |

---

## VDMP vs. VFMP: Key Differences

| Feature | VDMP | VFMP |
|---|---|---|
| What is measured | Dispute count ratio (all disputes) | Fraud dollar volume / ratio |
| Primary threshold | 0.9% dispute ratio | 0.65% fraud ratio + $75K fraud volume |
| Fine structure | Per-excess-dispute | Tiered by fraud dollar volume |
| Remediation focus | Reduce total chargeback count | Reduce fraud chargebacks specifically |
| Simultaneous enrollment | Possible | Yes — merchants can be in both |

A merchant can be enrolled in both VDMP and VFMP simultaneously. In this case, fines from both programs accumulate.
