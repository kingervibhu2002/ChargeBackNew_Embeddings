---
title: "Chargeback Alert Services — Verifi CDRN and Ethoca Alerts"
category: Monitoring Programs
doc_type: program-overview
program: Verifi CDRN, Ethoca Alerts
network: Visa (Verifi), Mastercard (Ethoca)
audience: merchants
last_updated: 2026-06-01
tags: [Verifi, CDRN, Ethoca, chargeback alerts, pre-chargeback, prevention, refund]
---

# Chargeback Alert Services: Verifi CDRN and Ethoca Alerts

## The Problem Alert Services Solve

Every formal chargeback costs a merchant: the disputed amount (temporarily or permanently), a chargeback fee ($15–$100), staff time for evidence assembly and submission, and — critically — a count against the merchant's chargeback ratio. The ratio impact persists regardless of whether the merchant ultimately wins the dispute. A merchant who fights and wins 80% of their chargebacks still counts 100% of them against their VDMP/ECP ratio.

Pre-chargeback alert services — Verifi CDRN for Visa and Ethoca Alerts for Mastercard — exist to intercept dispute signals **before** they become formal chargebacks. When a merchant refunds a dispute in response to an alert, the formal chargeback is stopped at the bank level, and the transaction never enters the merchant's chargeback count.

This is not merely a cost reduction tool — it is a ratio management mechanism that can be the difference between staying below monitoring thresholds and entering a $100,000/month fine program.

---

## How Verifi CDRN Works (Visa)

**CDRN:** Cardholder Dispute Resolution Network.

### The Alert Flow

1. A cardholder contacts their Visa-issuing bank to dispute a transaction.
2. The issuing bank (if enrolled in CDRN) transmits a dispute notification to Verifi's CDRN platform instead of immediately filing a formal chargeback.
3. CDRN matches the dispute to the merchant based on the transaction descriptor, MID, and BIN.
4. CDRN sends the merchant an alert with the transaction details within minutes to a few hours.
5. The merchant has approximately **24 hours** to decide: issue a refund (stopping the dispute) or let it proceed (becoming a formal chargeback).
6. If the merchant refunds within the window, the alert is marked "resolved." The issuing bank receives confirmation of the refund and cancels the dispute at the bank level.
7. The transaction is never filed as a formal chargeback. It does not enter the merchant's chargeback ratio.

### What Happens If You Do Not Refund

If the merchant does not refund within the alert window, the issuing bank proceeds to file a formal chargeback through normal network channels. The alert becomes a formal chargeback that counts in the ratio. The merchant can still respond with a representment, but the ratio impact is permanent.

### Decision Framework: Refund or Fight?

Not every alert should result in a refund. Evaluate each alert:

- **Refund:** When the amount is below your representment ROI threshold; when the transaction is genuinely disputed (delivery problem, fraud); when the ratio impact of the chargeback is more costly than the refund.
- **Let proceed (fight):** When you have very strong evidence (3DS ECI 05, clear delivery proof); when the amount is high and the evidence supports winning; when the customer is a known repeat abuser.

In practice, most merchants refund 60–85% of alerts and allow the rest to proceed to chargeback where they contest with evidence.

---

## How Ethoca Alerts Work (Mastercard)

Ethoca, owned by Mastercard since 2019, operates the equivalent alert service for Mastercard-issued cards (and some Visa cards through the Ethoca network, depending on issuer enrollment).

### The Alert Flow

The process is functionally identical to Verifi CDRN:

1. Cardholder disputes a Mastercard transaction with their bank.
2. Enrolled issuing bank transmits a dispute signal to Ethoca.
3. Ethoca matches the alert to the enrolled merchant and delivers the notification.
4. Merchant has approximately 24 hours to refund or let proceed.
5. Refund stops the formal chargeback; no refund allows it to proceed.

### Ethoca Eliminator

Ethoca offers "Eliminator" as an enhanced service where Ethoca sends transaction data (enriched merchant information) to the cardholder through their banking app, allowing the cardholder to confirm or dispute the charge within the app before escalating to their bank. This serves as a pre-alert resolution layer that can stop disputes before even an Ethoca alert is generated.

---

## Visa Order Insight and Mastercard Consumer Clarity

Both networks have invested in transaction transparency tools that complement alert services:

**Visa Order Insight (formerly Visa Transaction Controls/Merchant Data):** Allows merchants to enrich transaction data visible to cardholders in their banking app — including merchant logo, product description, purchase category, and customer service contact. When cardholders can see detailed transaction information in their app, they are significantly less likely to dispute "unrecognized" charges. Order Insight is implemented through Verifi and is available for Visa transactions with enrolled issuers.

**Mastercard Consumer Clarity:** Mastercard's equivalent transaction data enrichment program. Enriched data visible in the cardholder's banking app can reduce "I don't recognize this" disputes by 20–40% for enrolled merchants.

Both programs require enrollment through a chargeback management platform or directly with Verifi/Ethoca.

---

## Cost Per Alert

Alert services charge a per-alert fee that varies by:

- Whether accessed directly or through a third-party platform
- Transaction volume tier
- Geography (US domestic vs. international)

Typical ranges:

| Service | Direct Cost (estimated) | Third-Party Platform |
|---|---|---|
| Verifi CDRN | $15–$35 per alert | Bundled or $20–$40/alert |
| Ethoca Alerts | $15–$35 per alert | Bundled or $20–$40/alert |

Note: Alert fees are charged for every alert received, regardless of whether you refund. An alert you receive and ignore (letting it become a chargeback) still incurs the alert fee.

---

## ROI Calculation for Alert Services

Determining whether alert services are economically justified:

**The cost of a formal chargeback:**
- Disputed transaction amount: $X
- Chargeback fee: $Y (typically $15–$100)
- Response labor (if contesting): $Z (estimate $15–$45/hour × hours)
- Ratio impact cost: difficult to quantify, but monitoring program fines can reach $100,000/month

**The cost of resolving via alert:**
- Alert fee: $15–$35
- Refunded transaction amount: $X

**Net difference (alert vs. chargeback):**
- If you would have won the chargeback: Alert resolution costs $X + alert fee vs. chargeback recovery of $X − chargeback fee − labor = net advantage of chargeback fight
- If you would have lost the chargeback: Alert resolution costs alert fee vs. losing $X + chargeback fee = alert is cheaper by the chargeback fee + labor

**Simplest ROI formula for merchants who win ~40% of disputes:**
- Expected chargeback cost = (1 − win rate) × transaction value + chargeback fee + labor
- Alert cost = alert fee (transaction returned to cardholder whether you win or not in both scenarios with different net effects)

For average order values above $75 and chargeback fees above $25, alert services typically show positive ROI.

---

## Enrollment Process

### Direct Enrollment

Merchants can enroll directly with Verifi (verifi.com) for CDRN and directly with Ethoca (ethoca.com) for Ethoca Alerts. Direct enrollment may require a minimum monthly volume commitment.

### Third-Party Platform Enrollment

Most merchants access both services through a unified chargeback management platform that bundles alert monitoring, automated refund decisioning, and case management:

- **Chargebacks911:** Unified CDRN + Ethoca management with automated refund decisioning
- **Midigator:** Full-cycle chargeback management including alert services
- **Kount:** Fraud + chargeback management with alert integration
- **Signifyd:** Integrated with alert services for enrolled merchants
- **Riskified / Forter:** Enterprise fraud platforms with alert service integration

### What You Need to Enroll

- Merchant ID (MID) or list of MIDs
- Business descriptor(s) exactly as they appear on cardholder statements
- Acquirer contact information
- Technical integration for alert receipt (API webhook or email-based alerts)
- Refund processing integration (to issue refunds through your payment gateway within the alert window)

---

## Operational Requirements for Alert Services

To make alert services effective:

- **24/7 alert monitoring:** Alerts arrive at any time. An alert that sits unreviewed for 26 hours has expired and becomes a chargeback. Either automate the refund decision for amounts below a threshold, or ensure human review coverage during all business hours with a defined escalation path for off-hours alerts.
- **Automated refund for low-value alerts:** Configure automatic refund for alerts below a defined amount (e.g., auto-refund all alerts under $100; human review for $100+). This maximizes the ratio benefit without excessive labor.
- **Alert-to-chargeback matching:** After issuing a refund in response to an alert, monitor whether the alert was successfully resolved or whether the issuing bank still filed a formal chargeback. Mismatched resolutions occur when the issuer is not properly enrolled and the alert fires from a secondary channel.
- **Dispute the alert if the evidence is very strong:** For high-value alerts where you have 3DS ECI 05 or clear delivery proof, letting the alert proceed to chargeback and submitting a strong representment may recover more than refunding. Calculate per case.

---

## Alert Service Coverage Limitations

Alert services cover only enrolled issuing banks. Coverage rates:

- Verifi CDRN: Covers approximately 80–90% of major US Visa issuers by volume; lower coverage for smaller regional banks and international issuers.
- Ethoca: Covers approximately 80–85% of major US Mastercard issuers by volume; expanding international coverage.

Transactions issued by non-enrolled banks generate chargebacks without alert notifications. This is why alert services reduce — but do not eliminate — chargeback volume.
