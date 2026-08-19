---
title: "Chargeback Glossary — S to Z"
category: Glossary
doc_type: glossary
audience: merchants
last_updated: 2026-06-01
tags: [glossary, definitions, terminology, chargeback, payments, S-Z]
---

# Chargeback Glossary: S to Z

This glossary provides definitions for key terms in chargeback, payments, and dispute management. Terms are arranged alphabetically from S to Z, plus numeric reason codes.

---

## S

**SCA (Strong Customer Authentication)**
A regulatory requirement under the EU's Revised Payment Services Directive (PSD2) mandating that electronic payments be authenticated using at least two of three independent factors: something the customer knows (password, PIN), something the customer has (phone, hardware token), and something the customer is (fingerprint, face). SCA applies to all online card transactions within the European Economic Area. Merchants serving EU/UK cardholders must implement 3-D Secure 2 (3DS2) as their primary SCA method. Non-compliant transactions may be soft-declined by the issuer. Certain low-risk exemptions exist, including transactions under €30 and payments to pre-approved trusted beneficiaries.

**Second Presentment**
Mastercard's term for the merchant's formal rebuttal of a chargeback. The merchant submits a Second Presentment through their acquirer to challenge the issuing bank's chargeback decision. The Second Presentment must include a rebuttal letter, supporting evidence exhibits, and must be submitted within the deadline (typically 45 days from the chargeback date). A successful Second Presentment results in the chargeback being reversed and funds returned to the merchant. A rejected Second Presentment may lead to pre-arbitration and, ultimately, card network arbitration.

**Settlement**
The transfer of funds from the cardholder's account to the merchant's account following authorization and clearing. Settlement typically occurs within 1–3 business days of the transaction. In batch settlement, the merchant submits all approved transactions for a period to the acquirer; the acquirer submits to the network; the network routes debits to issuing banks; and the acquirer credits the merchant's account minus interchange fees and processing costs. Settlement is the point from which chargeback filing windows begin to run.

**Soft Descriptor**
A portion of the billing descriptor that can be dynamically set per transaction to include additional contact information — typically a customer service phone number or website URL. Soft descriptors appear alongside the static merchant name (DBA descriptor) on the cardholder's statement. Including a recognizable brand name and a support phone number in the soft descriptor reduces "I don't recognize this charge" disputes, which account for a significant share of friendly fraud. Not all issuing banks display the soft descriptor field; coverage varies by issuer.

**Split Shipment**
A single order fulfilled across multiple shipments with separate carrier tracking numbers — common for large orders or mixed inventory locations. Each split shipment must be documented separately in a chargeback response, with individual tracking numbers for each package. If a cardholder disputes a "not received" claim on a split-shipment order, confirm whether all packages are shown as delivered and document each package individually in your rebuttal.

---

## T

**3-D Secure (3DS)**
An authentication protocol for card-not-present transactions that routes the cardholder through an authentication check with their issuing bank before the transaction is authorized. Version 2.x (3DS2) uses risk-based assessment that can approve low-risk transactions silently (frictionless) or require the cardholder to complete a challenge (OTP, biometric). A successful full-authentication result produces an ECI value of 05 (Visa) or 02 (Mastercard), which shifts liability for fraud chargebacks from the merchant to the issuing bank. 3DS is required for EU/UK SCA compliance under PSD2.

**Terminal (Payment Terminal)**
A physical device at the point of sale that reads payment card data via chip (EMV), magnetic stripe, or contactless (NFC/tap). Chip-read transactions on a compliant terminal generate a unique cryptographic token per transaction, making counterfeiting essentially impossible and earning the merchant EMV liability shift protection. Merchants who process chip cards via magnetic stripe swipe forfeit this protection.

**Tribunal**
The internal adjudication panel within a card network that issues the final binding ruling in arbitration cases. After both issuer and merchant submit their evidence at the arbitration stage, the network's tribunal reviews the documentation and decides in favor of one party. The losing party bears the disputed amount and the arbitration fees (which range from $250 to $500 or more per case). Tribunal decisions are final and cannot be appealed.

---

## U

**UPI (Unified Payments Interface)**
India's real-time interbank payment system, operated by NPCI (National Payments Corporation of India). UPI enables instant bank-to-bank transfers via a smartphone VPA (Virtual Payment Address). UPI disputes follow NPCI's dispute management framework rather than Visa/Mastercard chargeback rules, with RBI-mandated 30-day resolution timelines. Indian merchants must comply with RBI guidelines on two-factor authentication, dispute handling, and data localization for UPI transactions.

---

## V

**VCR (Visa Claims Resolution)**
Visa's modernized dispute resolution framework introduced in April 2018. VCR replaced the traditional multi-step chargeback process with two tracks: "Allocation" (Visa rules determine initial liability based on transaction data; no documentation required) and "Collaboration" (both parties provide documentation and attempt to reach resolution). VCR standardized timelines, capped reason codes, and introduced the compelling evidence framework. Under VCR, many simple fraud disputes in the Allocation track are resolved without merchant participation — which can be beneficial (automatic wins on 3DS-authenticated transactions) or detrimental (automatic losses if the merchant has no qualifying data).

**VDMP (Visa Dispute Monitoring Program)**
Visa's monitoring program for merchants whose chargeback ratio exceeds defined thresholds. Three tiers: Early Warning (ratio ≥ 0.65% or ≥ 75 chargebacks), Standard (ratio ≥ 0.9% or ≥ 100 chargebacks), and Excessive (ratio ≥ 1.8% or ≥ 1,000 chargebacks). Monthly fines begin at $50 per chargeback above the threshold and escalate over time. Merchants are expected to remediate within 6 months. Failure to exit within 12 months risks fines increasing to $25,000/month and potential account termination with MATCH list placement.

**Verifi**
A Visa-owned chargeback management platform providing the CDRN (Cardholder Dispute Resolution Network) pre-chargeback alert service, chargeback representment tools, and analytics for Visa merchants. The CDRN service connects merchants with enrolled issuing banks to enable pre-chargeback alerts, allowing merchants to refund disputes before a formal chargeback is filed. Verifi also powers Order Insight, a transaction data enrichment service that allows cardholders to see detailed order information within their banking app, reducing "I don't recognize this charge" disputes.

**VFMP (Visa Fraud Monitoring Program)**
Visa's monitoring program for merchants with excessive fraud-to-sales ratios. Merchants enter the Early Warning tier when monthly fraud volume exceeds $75,000 and the fraud ratio exceeds 0.65%. Merchants enter the High-Risk Merchant tier at $250,000 in monthly fraud. Both tiers carry monthly fines and remediation requirements. VFMP is separate from VDMP; a merchant can be simultaneously enrolled in both programs. VFMP focuses on fraud dollar volume; VDMP focuses on chargeback count ratio.

**Void**
The cancellation of an authorized transaction before it is submitted for settlement. A voided transaction is never settled and never moves funds, making it ineligible for chargeback. Voids can only be processed before the batch settlement cutoff for the day. After settlement, a reversal must be processed as a refund (credit transaction) rather than a void.

---

## W

**Win Rate**
The percentage of submitted chargeback representments that result in a decision favorable to the merchant. Industry-average win rates: fraud disputes (Visa 10.4, MC 4837) with strong evidence: 30–50%; non-fraud disputes (not received, not as described): 40–65%; subscription disputes: 35–55%. Win rate is calculated as: (won representments ÷ total representments submitted) × 100. Merchants who do not respond have a 0% win rate. Win rate improvement comes from better evidence collection processes and accurate alignment of evidence to the specific reason code being disputed.

---

## Z

**Zero Liability**
A card network policy that protects cardholders from being held responsible for unauthorized transactions on their card. Under Visa's Zero Liability Policy and Mastercard's equivalent, cardholders who report fraudulent transactions are not held responsible for those charges — they receive a full refund from their issuer. This policy is the mechanism that makes chargebacks mandatory for issuers: the issuer must credit the cardholder and then pursue recovery from the merchant. Zero Liability policies make it very easy for cardholders to dispute transactions, which contributes to the high volume of chargeback filings.

---

## Numeric Reason Codes Quick Reference

| Code | Network | Name | Common Defense |
|---|---|---|---|
| 10.4 | Visa | Card Absent — Other Fraud | AVS, CVV, 3DS, delivery, device/IP, CE3.0 |
| 13.1 | Visa | Merchandise Not Received | Carrier tracking, digital delivery logs |
| 13.2 | Visa | Cancelled Recurring | CRM log (no cancellation), policy disclosure |
| 13.3 | Visa | Not As Described | Product description vs. shipped, return policy |
| 4837 | Mastercard | No Cardholder Authorization | CVC2, AVS, Identity Check, delivery proof |
| 4853 | Mastercard | Cardholder Dispute | Service delivery records, completion certificate |
| 4855 | Mastercard | Goods/Services Not Provided | Check-in records, boarding pass, digital logs |
