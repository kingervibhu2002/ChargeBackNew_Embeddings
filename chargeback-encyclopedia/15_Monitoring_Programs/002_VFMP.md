---
title: "Visa Fraud Monitoring Program (VFMP)"
category: Monitoring Programs
doc_type: program-overview
program: VFMP
network: Visa
audience: merchants
last_updated: 2026-06-01
tags: [VFMP, Visa, fraud monitoring, fraud ratio, fines, threshold, remediation]
---

# Visa Fraud Monitoring Program (VFMP)

## What Is VFMP?

The Visa Fraud Monitoring Program (VFMP) is Visa's monitoring and enforcement mechanism for merchants whose fraud-to-sales dollar ratios or absolute fraud volumes exceed defined thresholds. VFMP focuses specifically on fraud chargebacks — transactions disputed as unauthorized — rather than all dispute types as measured by VDMP (Visa Dispute Monitoring Program).

VFMP exists because high fraud volumes at a specific merchant indicate either that the merchant is processing fraudulent transactions (knowingly or unknowingly), has inadequate authentication controls, or has been specifically targeted by organized fraud rings. High fraud rates at one merchant can generate issuance-level losses that damage the overall Visa network.

---

## How VFMP Differs from VDMP

| Feature | VFMP | VDMP |
|---|---|---|
| Measures | Fraud chargebacks only (fraud reason codes) | All chargebacks (all reason codes) |
| Metric | Fraud dollar volume + fraud-to-sales ratio | Dispute count ÷ transaction count |
| Primary focus | Unauthorized transaction fraud | All dispute types |
| Thresholds | Dollar volume + ratio | Ratio + count |
| Can be simultaneous | Yes | Yes |

A merchant can be enrolled in both VFMP and VDMP at the same time — fines from both programs accumulate separately.

---

## VFMP Thresholds

VFMP operates on two tiers based on the combination of monthly fraud dollar volume and fraud-to-sales ratio:

### Early Warning / Standard Tier
| Metric | Threshold |
|---|---|
| Monthly fraud dollar volume | ≥ $75,000 |
| Fraud-to-sales ratio | ≥ 0.65% |

**Both conditions must be met** to enter this tier. A merchant with $80,000 in fraud but only a 0.40% fraud ratio does not enter VFMP. A merchant with a 0.80% fraud ratio but only $50,000 in fraud volume does not enter VFMP.

### High-Risk Merchant Tier
| Metric | Threshold |
|---|---|
| Monthly fraud dollar volume | ≥ $250,000 |
| Fraud-to-sales ratio | ≥ 0.65% |

Merchants who reach the High-Risk Merchant tier face additional fines and accelerated remediation timelines compared to the Standard tier.

---

## What Counts as "Fraud" for VFMP?

VFMP counts only chargebacks filed under Visa's fraud reason codes:
- **Visa 10.1:** EMV Chip Counterfeit (card-present counterfeit)
- **Visa 10.2:** EMV Chip and PIN (lost/stolen card-present)
- **Visa 10.3:** Other Fraud — Card Present
- **Visa 10.4:** Other Fraud — Card Absent (CNP fraud — the most common for e-commerce)
- **Visa 10.5:** Visa Fraud Monitoring Program (internal)

The vast majority of online merchant VFMP activity comes from Visa 10.4 (CNP fraud). Non-fraud codes (13.1 not received, 13.2 cancelled, 13.3 not as described) do not count toward VFMP metrics.

---

## VFMP Fine Schedule

Fines begin when a merchant enters the Standard tier:

| Program Stage | Monthly Fine Structure |
|---|---|
| Month 1–4 (Standard) | $25,000 flat monthly fine (some programs: per-transaction fees) |
| Month 5–6 (Standard) | $25,000 + issuer reimbursement assessments |
| Month 1–4 (High-Risk) | $50,000 flat monthly fine |
| Month 5–6 (High-Risk) | $50,000 + issuer reimbursement assessments |
| Month 7+ (either tier) | Escalated enforcement; disqualification review |

Note: Visa updates fine schedules periodically. Always confirm current fine amounts with your acquiring bank, as they reflect the most current Visa Operating Regulations.

---

## Relationship Between VFMP and VDMP

Since VFMP measures fraud chargebacks and VDMP measures all chargebacks:

- A merchant with high fraud chargeback volume may be in **both programs simultaneously**.
- Remediating VFMP (by reducing fraud chargebacks via 3DS, fraud scoring) simultaneously reduces VDMP metrics.
- A merchant in VDMP but not VFMP has chargeback problems beyond fraud — they also have high rates of service, delivery, or subscription disputes.

The distinction matters for remediation planning: VFMP remediation focuses on fraud controls (3DS2, AVS, velocity rules, fraud scoring). VDMP remediation requires a broader approach including customer service improvements, product quality, and subscription billing practices.

---

## How to Exit VFMP

Exit criteria require that the merchant's fraud metrics fall below both the dollar volume AND ratio thresholds for three consecutive months:

| Exit Condition | Standard Tier | High-Risk Tier |
|---|---|---|
| Monthly fraud volume | Below $75,000 | Below $75,000 |
| Fraud-to-sales ratio | Below 0.65% | Below 0.65% |
| Consecutive months required | 3 | 3 |

A merchant who achieves compliance in one month but exceeds the threshold again in the following month resets the three-month exit timeline.

---

## Remediation Strategy for VFMP

Because VFMP specifically measures fraud chargebacks, the remediation toolkit is focused on authentication and fraud prevention:

### 1. Implement 3-D Secure 2 (3DS2) — Highest Priority

A Visa 10.4 chargeback on a 3DS-authenticated transaction (ECI 05) is a liability transfer — the issuer bears the loss, not the merchant. Critically: **3DS-authenticated transactions do not count as merchant fraud in VFMP calculations.** They are attributed to the issuer's fraud metrics, not the merchant's. This makes 3DS2 implementation the single most effective VFMP remediation action.

If 3DS2 is not already fully implemented, it should be live within 30 days of receiving a VFMP notice.

### 2. Deploy or Upgrade Fraud Scoring

Transactions approved by fraud scoring tools like Kount, Signifyd, or Stripe Radar that subsequently result in fraud chargebacks indicate the model is miscalibrated. Review:
- Model performance against fraud chargeback data
- Velocity rules effectiveness
- BIN risk scoring (certain foreign BINs carry higher fraud rates)
- Device fingerprinting accuracy

### 3. Analyze Fraud Chargeback Patterns

Request fraud chargeback data broken down by:
- Issuer (which issuing banks are filing the most fraud disputes)
- BIN range (which card types are most affected)
- Product type (which products in your catalog generate the most fraud)
- Transaction time and day (fraud concentrations may indicate bot attacks during off-hours)
- Geolocation of checkout IP (fraud from specific regions may indicate organized rings)

This analysis identifies specific attack vectors that targeted controls can address.

### 4. Enroll in Verifi CDRN and Ethoca Alerts

Pre-chargeback alerts from Verifi (Visa) and Ethoca (Mastercard) allow refunding before fraud disputes become formal chargebacks. Since VFMP counts filed chargebacks, not resolved disputes, stopping disputes before they are formally filed directly reduces VFMP metrics.

### 5. Restrict High-Risk Transactions

Temporarily implementing stricter controls — declining high-risk BINs, requiring 3DS for all CNP transactions (not just EU/UK), rejecting VPN/proxy IP checkout sessions — can rapidly reduce fraud volume during active remediation. Accept the short-term decline in acceptance rate to exit the monitoring program and then calibrate more precisely.

---

## Acquirer Obligations Under VFMP

Your acquiring bank has its own obligations under VFMP:
- Must notify merchants upon VDMP/VFMP placement
- Must submit remediation plans to Visa on behalf of enrolled merchants
- May face their own fines from Visa if the acquirer fails to enforce remediation requirements
- May terminate the merchant relationship if VFMP exposure becomes too large for the acquirer's risk appetite

If your acquirer terminates your relationship due to VFMP/VDMP, the MATCH list placement adds a 5-year bar to obtaining a new merchant account.

---

## VFMP Monitoring: What to Track Weekly

During active VFMP remediation:

| Metric | Target | Current | Week-over-Week Trend |
|---|---|---|---|
| New fraud chargebacks (Visa 10.4) | Declining | [X] | [↓/→/↑] |
| 3DS authentication rate (% of transactions) | > 80% | [X%] | [↑] |
| 3DS full-auth rate (ECI 05 %) | > 60% | [X%] | [↑] |
| Fraud-to-sales ratio (weekly estimate) | < 0.65% | [X%] | [↓] |
| Fraud volume (weekly) | < $18,750 (to hit <$75K/mo) | [$X] | [↓] |
| Alert refund rate (Verifi/Ethoca) | > 70% | [X%] | [→] |
