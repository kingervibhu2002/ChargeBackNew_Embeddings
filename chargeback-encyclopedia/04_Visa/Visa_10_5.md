---
title: "Visa 10.5 — Visa Fraud Monitoring Program (VFMP)"
section: "04_Visa"
category: "Visa Reason Codes"
network: "Visa"
reason_code: "10.5"
document_type: "Reason Code Reference"
keywords: ["VFMP", "Visa Fraud Monitoring Program", "10.5", "fraud monitoring", "thresholds", "fines", "MATCH"]
difficulty: "Advanced"
---

# Visa 10.5 — Visa Fraud Monitoring Program (VFMP)

## Definition

Visa reason code 10.5 is unique in the Visa framework because it is not a traditional chargeback code that merchants can defend against with evidence. Instead, it applies when a merchant has been enrolled in Visa's **Fraud Monitoring Program (VFMP)** due to excessive fraud rates. Chargebacks filed under 10.5 are issued specifically against merchants in VFMP and represent Visa-level enforcement action — not individual cardholder disputes.

When a merchant receives a 10.5 chargeback, it means Visa has determined that this merchant's fraud rate is high enough to warrant program-level oversight. The 10.5 code signals that Visa (through the issuer) is filing fraud chargebacks under the monitoring program rules, separate from ordinary individual cardholder disputes.

Understanding VFMP is critical for any merchant operating at scale, particularly in high-fraud verticals such as digital goods, travel, nutraceuticals, gambling, and subscription services.

---

## What Is the Visa Fraud Monitoring Program (VFMP)?

VFMP is Visa's mechanism for identifying and penalizing merchants whose fraud-to-sales ratios exceed defined thresholds. It is distinct from the Visa Dispute Monitoring Program (VDMP), which tracks chargeback rates broadly. VFMP specifically tracks fraud — transactions that issuers report as unauthorized after the fact.

Visa monitors all merchants' fraud metrics on a rolling monthly basis. When a merchant breaches VFMP thresholds, Visa notifies the merchant's acquirer, who must then notify the merchant. The merchant is formally enrolled in VFMP and given a remediation period to reduce fraud rates.

### VFMP Thresholds

VFMP thresholds are defined by two metrics measured over a rolling month:

| Program Level | Fraud-to-Sales Volume Ratio | Monthly Fraud Volume (USD) |
|---|---|---|
| Early Warning | 0.65% | $50,000 |
| Standard | 0.90% | $75,000 |
| High-Risk | 1.80% | $250,000 |

A merchant must breach both the ratio threshold AND the volume threshold in the same month to be placed in VFMP. This dual-threshold system prevents tiny merchants with a few fraudulent transactions from being penalized disproportionately.

Once in VFMP, the merchant has a **remediation period** (typically three months) to reduce their metrics before fines begin.

---

## The VFMP Timeline

### Month 0: Breach Detected
Visa detects that the merchant has breached VFMP thresholds in a calendar month.

### Month 1–3: Notification Period
Visa notifies the acquirer. The acquirer notifies the merchant. No fines are imposed yet, but the merchant must immediately implement fraud reduction measures.

### Month 4+: Fine Period
If thresholds are still breached after the remediation period, monthly fines begin:

| Program Level | Monthly Fine |
|---|---|
| Standard (Month 4–6) | $25,000/month |
| Standard (Month 7–9) | $50,000/month |
| Standard (Month 10+) | $75,000/month |
| High-Risk | Higher fine schedules apply |

These fines are assessed against the acquirer, who passes them to the merchant. Prolonged VFMP enrollment can result in hundreds of thousands of dollars in fines and ultimately termination of the merchant's processing agreement.

---

## Why Merchants Cannot Fight 10.5 Chargebacks Directly

Unlike 13.x consumer dispute chargebacks where a merchant can submit evidence and potentially win, **10.5 chargebacks under VFMP cannot be fought on a transaction-by-transaction basis**. The dispute is not between the merchant and an individual cardholder — it is a program-level enforcement action.

When you receive a 10.5 chargeback, Visa's position is: your fraud rate is too high, your processing carries systemic risk, and these fraud transactions are being reversed as part of program enforcement. The individual transaction details are largely irrelevant at this stage — the problem is your aggregate fraud rate, not one specific transaction.

This is why VFMP remediation is a strategic business problem, not a documentation problem. You cannot paper your way out of VFMP.

---

## Common Reasons Merchants Enter VFMP

### High-Risk Business Models
Certain business types attract disproportionate fraud: digital goods that can be resold, subscription services with easy sign-up and cancel cycles, travel merchants, nutraceuticals, and adult content are all statistically overrepresented in VFMP.

### Inadequate Fraud Screening
Merchants who do not run real-time fraud scoring on transactions, don't implement 3DS, and don't use velocity checks will naturally accumulate more fraudulent orders.

### Data Breach
A merchant whose systems are compromised may find stolen card data being used against them — or worse, the breached data being used elsewhere, generating chargebacks that track back to the original merchant's fraud ratio.

### Rapid Growth Without Fraud Controls
A fast-growing merchant that scaled volumes without scaling fraud prevention often crosses VFMP thresholds suddenly as fraudsters discover the weak defenses.

### CNP Transactions Without 3DS
Online merchants who don't implement 3D Secure expose themselves to the full weight of CNP fraud, which directly feeds VFMP metrics.

---

## How to Exit VFMP

Exiting VFMP requires reducing your fraud metrics below the threshold for three consecutive months. This demands systematic, not incremental, fraud reduction:

### 1. Implement 3D Secure Immediately
3DS is the single most impactful intervention. Authenticated 3DS transactions do not count as merchant fraud — liability shifts to the issuer. Even a partial implementation across high-risk transaction segments can materially reduce your VFMP-qualifying fraud rate.

### 2. Deploy Real-Time Fraud Scoring
Use a fraud scoring service (Sift, Kount, Signifyd, or similar) to evaluate every transaction at checkout. Score-based declinations prevent fraudulent transactions from completing — transactions that never complete cannot generate chargebacks.

### 3. Implement Velocity Controls
Block or flag cards, emails, IP addresses, or devices that attempt multiple purchases within short windows. Fraudsters running stolen card data in bulk are stopped by velocity limits.

### 4. Tighten AVS and CVV Rules
Require AVS match and CVV for all CNP transactions. Consider declining transactions where AVS fails or CVV is incorrect.

### 5. Review and Improve Refund Policies
Proactive refunds for suspicious transactions reduce chargebacks. If your fraud scoring flags a transaction as risky after the fact, issuing a proactive refund before the cardholder disputes prevents the chargeback from counting against your VFMP metrics.

### 6. Work With Your Acquirer
Your acquirer's risk team has VFMP reporting tools and may be able to help identify which transaction segments are generating the most fraud. Some acquirers have dedicated merchant risk support teams for VFMP remediation.

### 7. Segment High-Risk Products
If a specific product line or customer segment generates disproportionate fraud, consider restricting or removing those offerings until fraud controls are in place.

---

## VFMP and the MATCH List

Prolonged VFMP enrollment, repeated breaches, or failure to pay VFMP fines can lead to consequences beyond the program itself:

- **Processing agreement termination:** Acquirers have contractual rights to terminate merchants who remain in VFMP for extended periods without improvement.
- **MATCH listing:** If a merchant's account is terminated due to fraud-related reasons, the acquirer may place the merchant on the Mastercard MATCH list (also called the TMF — Terminated Merchant File). MATCH listing makes it extremely difficult to obtain a new processing account with any card network for five years.

VFMP is a warning system. Taking it seriously and remediating quickly is far less damaging than ignoring it until termination.

---

## Merchant Liability

Under 10.5, the merchant bears liability for all fraud chargebacks processed under the VFMP program. These chargebacks are in addition to the monthly fines — the combination of lost revenue from chargebacks and escalating fines makes VFMP one of the most financially damaging situations a merchant can face.

---

## Required Evidence

There is no "evidence submission" that fights individual 10.5 chargebacks in the traditional sense. The appropriate response is:

1. Acknowledge the program enrollment with your acquirer.
2. Develop and document a fraud remediation plan.
3. Implement fraud controls and track metrics monthly.
4. Report progress to your acquirer, who reports to Visa.
5. Demonstrate sustained metric improvement over three consecutive months to exit the program.

---

## Timeline for VFMP Remediation

| Phase | Duration | Action Required |
|---|---|---|
| Breach detection | Month 0 | Visa identifies threshold breach |
| Notification | Month 1 | Acquirer and merchant notified |
| Remediation period | Months 1–3 | Implement fraud controls; no fines yet |
| Fine period | Month 4+ | Fines begin if still in breach |
| Exit eligibility | After 3 consecutive months below threshold | Program exit possible |

---

## Frequently Asked Questions

**Q: Can I dispute individual 10.5 chargebacks like I would a 13.1 dispute?**
A: No. 10.5 chargebacks are program-level enforcement actions. You cannot fight them transaction by transaction with cardholder dispute evidence. The only resolution is reducing your overall fraud rate below VFMP thresholds.

**Q: My acquirer says I'm in VFMP but I didn't know my fraud rate was that high. How do I monitor it?**
A: Ask your acquirer for monthly fraud reporting. Many acquirers provide a merchant portal showing your fraud-to-sales ratio. You can also calculate it yourself from your authorization records and chargeback reports. Monitor monthly — don't wait for VFMP notification.

**Q: Will implementing 3DS immediately get me out of VFMP?**
A: It won't immediately exit the program, but it will quickly reduce the fraud rate that feeds VFMP metrics. You need three consecutive months below threshold. If 3DS is implemented correctly and your fraud rate drops accordingly, you could exit within three to four months.

**Q: What if the fraud is driven by a data breach we experienced?**
A: Report the breach to your acquirer and to Visa immediately. Document that the fraud source is a specific breach event. While this doesn't automatically exempt you from VFMP, demonstrating the cause and implementing remediation (reissuing affected cards, patching vulnerabilities) can sometimes result in more flexible treatment. Every situation is different — work directly with your acquirer's risk team.

**Q: What's the difference between VFMP and VDMP?**
A: VFMP tracks fraud-to-sales ratios (unauthorized transaction rates). VDMP tracks overall chargeback rates across all reason codes. A merchant can be in one program without being in the other, or in both simultaneously. Both carry fines and MATCH listing risk if not remediated.

---

## Sample Rebuttal Points (Remediation Plan Communication)

For communication with your acquirer regarding VFMP enrollment (not a chargeback rebuttal, but a remediation plan):

- "We acknowledge enrollment in VFMP effective [date]. We have identified the primary drivers of our elevated fraud rate as [CNP transactions without 3DS / specific product category / geographic concentration of fraud orders]."
- "Effective [date], we have implemented 3D Secure authentication across 100% of eligible e-commerce transactions. Preliminary data shows a [X]% reduction in fraud-flagged transactions in the first week."
- "We have engaged [fraud scoring vendor] to implement real-time transaction risk scoring. Transactions scoring above [threshold] are declined automatically. This is expected to reduce fraud volume by an estimated [X]% based on historical data."
- "We are providing a 90-day remediation tracking report to our acquirer on a bi-weekly basis. Our target is to reach below the 0.90% fraud ratio threshold within 60 days and maintain that level for the required three-month exit period."
