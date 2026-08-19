---
title: "RBI Guidelines for Indian Merchants — Chargeback and Payment Compliance"
category: Regulations
doc_type: regulation
audience: merchants
last_updated: 2026-06-01
tags: [RBI, India, UPI, chargeback, 2FA, data localization, NPCI, dispute resolution]
---

# RBI Guidelines for Indian Merchants: Chargeback and Payment Compliance

## Overview of RBI's Role in Payments

The Reserve Bank of India (RBI) is the central bank and primary payment system regulator for India. RBI sets the rules for card payment security, digital payment authentication, dispute resolution timelines, customer protection obligations, and data localization requirements for all payment service providers and merchants operating within India.

Indian merchants accepting card payments (domestic and international) or UPI payments operate under an overlapping framework of RBI regulations, NPCI (National Payments Corporation of India) operational guidelines for UPI and RuPay, and PCI DSS requirements for card data security.

---

## RBI Mandate for Two-Factor Authentication (2FA)

The RBI mandated additional factor of authentication (AFA) — commonly referred to as second-factor authentication or 2FA — for all domestic online card transactions. This requirement, originally issued in 2009 and updated multiple times, requires that every card-not-present transaction using an Indian-issued card be authenticated using an additional factor beyond the card details alone.

### How 2FA Works in India

The most widely deployed 2FA solution in India is One-Time Password (OTP) authentication via SMS or bank mobile app. When a customer enters card details for an online purchase, the bank sends an OTP to the customer's registered mobile number, which must be entered to complete the transaction. This is India's functional equivalent of 3-D Secure authentication.

### RBI AFA and Chargeback Implications

- Transactions authenticated with AFA (successful OTP) shift the fraud liability to the issuing bank — the merchant is protected from fraud chargebacks on AFA-authenticated transactions, similar to the 3DS liability shift internationally.
- Transactions processed without AFA on Indian-issued cards may be declined by the issuer (especially for domestic transactions).
- For international cards processed in India, international authentication standards (3DS2) apply.

### Merchant Obligations

- Merchants must use a payment gateway that implements RBI-compliant AFA for all domestic card transactions.
- AFA bypass or workarounds (e.g., processing through foreign gateways to avoid AFA) are prohibited by RBI and can result in regulatory action against the merchant's payment service provider.

---

## UPI Dispute Rules

UPI (Unified Payments Interface) is India's real-time interbank payment system, operated by NPCI and governed by RBI oversight. UPI handles billions of transactions monthly and is now the dominant payment method in India for online and mobile commerce. Merchants accepting UPI (via QR code, payment links, or embedded UPI SDKs) must understand the UPI dispute framework.

### UPI Dispute Categories

1. **Transaction not received by merchant but debited from customer:** Funds deducted from the payer but not credited to the merchant. Resolution: automatic reconciliation or T+1 reversal.
2. **Duplicate payment:** Customer charged twice for the same transaction. Resolution: duplicate detected by NPCI and automatically reversed.
3. **Incorrect credit:** Funds credited to wrong VPA (Virtual Payment Address). Resolution: disputed through UPI dispute system; may require court order for recovery.
4. **Customer claims non-delivery:** Customer received no goods/service but payment was debited. Resolution: handled through the customer's PSP (PhonePe, GPay, Paytm, bank apps) using NPCI's dispute management system.

### UPI Dispute Management System (UDIR)

NPCI's Unified Dispute and Issue Resolution (UDIR) framework defines the handling of UPI disputes:
- Customers must raise disputes within the UPI app within **30 days** of the transaction.
- The payer's PSP forwards the dispute to the payee's PSP.
- The payee's PSP (the merchant's UPI payment provider) has a defined timeframe to respond (typically 5–7 business days).
- If unresolved, NPCI's dispute resolution body adjudicates.

### Merchant Action for UPI Disputes

Merchants receiving UPI dispute notices from their payment service provider must:
1. Verify the transaction in their order management system.
2. If the goods/service were delivered, provide proof of delivery to the PSP.
3. If the goods/service were not delivered, initiate a refund promptly.
4. Document all disputes and responses for regulatory record-keeping.

---

## RBI's 30-Day Dispute Resolution Mandate

RBI's customer protection framework mandates that payment system participants resolve digital payment disputes within **30 calendar days** of the dispute being raised. This applies to:

- Online card transactions (credit and debit)
- UPI transactions
- Netbanking transactions
- Prepaid payment instrument (PPI/wallet) transactions

For merchants, this means their payment service provider or acquiring bank must have a response turnaround that allows them to meet the 30-day mandate. Merchants who delay providing evidence or dispute responses to their PSP/acquirer risk being defaulted against simply because the PSP cannot meet the RBI deadline.

### Customer Protection Circular

RBI's 2017 Customer Protection Circular (RBI/2017-18/15) establishes zero-liability for customers on electronic transactions that result from third-party breaches (not the customer's fault). Specifically:
- If the fraud results from a merchant data breach: full liability on the merchant/bank
- If the fraud results from a system vulnerability not related to the customer: liability on the bank
- If the customer shared OTP/credentials due to negligence: limited liability based on reported timeframe

For merchants, a data breach that enables UPI fraud or card fraud activates significant liability under this circular.

---

## Data Localization Requirements

### RBI Storage of Payment Data (2018 Circular)

RBI's 2018 circular mandated that all payment data related to transactions conducted in India must be stored **exclusively in India** (data localization). This applies to:

- Full end-to-end transaction data for payments originating in India
- Processing data, including authorization, clearing, and settlement records
- Customer payment credentials

Payment networks (Visa, Mastercard) were required to maintain local mirrors of India transaction data in Indian data centers. International payment gateways serving Indian merchants must have certified compliant data storage arrangements.

### GDPR vs. RBI on Cross-Border Data Transfer

Indian merchants who also serve EU customers operate under dual regulatory frameworks:
- **RBI requires** that India-origin payment data stays in India.
- **GDPR requires** appropriate safeguards for EU personal data transferred outside the EU.
- These frameworks can conflict for multi-national merchants — consult legal counsel to design compliant cross-border data handling procedures.

---

## NPCI and RuPay Chargeback Rules

RuPay is NPCI's domestic card network (India's answer to Visa and Mastercard). RuPay-issued cards carry their own dispute rules aligned with NPCI's framework:

- RuPay chargebacks are managed through NPCI's dispute system rather than Visa/Mastercard networks.
- Merchants accepting RuPay cards through acquiring banks receive dispute notices via their acquirer in a similar format to Visa/Mastercard chargebacks.
- RuPay dispute timelines are governed by NPCI operating guidelines, which are updated periodically.
- Response windows for RuPay chargebacks are typically 30 days.

---

## Merchant Compliance Obligations Summary

| Requirement | Obligation | Authority |
|---|---|---|
| AFA / 2FA for domestic card CNP | Mandatory via payment gateway | RBI |
| UPI dispute response within PSP deadline | Mandatory | NPCI/RBI |
| 30-day dispute resolution participation | Mandatory | RBI |
| Transaction data localization (India-origin) | Mandatory for payment system participants | RBI |
| PCI DSS for card data storage | Mandatory via acquirer contract | PCI SSC |
| NPCI operating guidelines for RuPay | Mandatory | NPCI |

---

## Key Practical Steps for Indian Merchants

1. **Use an RBI-compliant payment gateway** that implements AFA (OTP) for all domestic card transactions. Verify your gateway's RBI compliance status annually.
2. **Respond to dispute notices promptly.** Given the 30-day RBI mandate, your PSP's internal deadline for your response may be as short as 7 business days.
3. **Maintain delivery and service records** for a minimum of 12 months for dispute evidence purposes.
4. **Implement UPI transaction reconciliation** — match every UPI credit in your bank account to an order in your system daily to detect failed or duplicate transactions before customers dispute them.
5. **Verify your data localization arrangements** with your payment gateway if you process transactions in India. Your gateway must certify its compliance with RBI's 2018 storage circular.
