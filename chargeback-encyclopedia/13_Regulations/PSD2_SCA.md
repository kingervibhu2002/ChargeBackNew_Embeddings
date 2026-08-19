---
title: "PSD2 and Strong Customer Authentication (SCA) — EU/UK Merchant Guide"
category: Regulations
doc_type: regulation
audience: merchants
last_updated: 2026-06-01
tags: [PSD2, SCA, 3DS2, EU, UK, authentication, liability shift, exemptions]
---

# PSD2 and Strong Customer Authentication: EU/UK Merchant Guide

## What Is PSD2?

The Revised Payment Services Directive (PSD2) is a European Union directive that governs electronic payment services across the EU and European Economic Area (EEA). A central component of PSD2 is the requirement for Strong Customer Authentication (SCA) on electronic payments — a mandate that fundamentally changed how online merchants must authenticate cardholders for EU and UK-issued cards.

PSD2 SCA requirements came into full force across the EU in January 2021 and in the UK (post-Brexit) in March 2022, regulated by the Financial Conduct Authority (FCA) rather than EU bodies. The practical effect for merchants: any online transaction involving an EU- or UK-issued card must be authenticated using SCA unless an exemption applies.

---

## SCA Requirements: Two of Three Factors

SCA requires authentication using at least two of three independent factor categories:

| Factor Category | Examples |
|---|---|
| Knowledge (something the cardholder knows) | Password, PIN, security question answer |
| Possession (something the cardholder has) | Mobile phone, hardware token, SIM card |
| Inherence (something the cardholder is) | Fingerprint, face recognition, iris scan, voice pattern |

The two factors used must come from different categories — a password plus a security question does not satisfy SCA because both are knowledge factors. A password (knowledge) plus an OTP sent to the cardholder's phone (possession) does satisfy SCA.

---

## 3DS2 as the Primary SCA Method

3-D Secure version 2 (3DS2) is the card industry's standardized SCA solution for online card payments. 3DS2 implements SCA by requiring the cardholder to authenticate with their issuing bank during checkout:

- **Frictionless flow:** The issuer's Access Control Server (ACS) assesses the transaction risk in the background using device fingerprint, behavioral data, and transaction history. If the ACS is confident the genuine cardholder is making the purchase, it approves silently with no customer action required.
- **Challenge flow:** For higher-risk transactions or where the ACS needs additional confirmation, the cardholder is presented with a challenge — typically an OTP sent to their registered phone number, a push notification in their banking app, or a biometric prompt.

A successful 3DS2 full-authentication result produces ECI 05 (Visa) or ECI 02 (Mastercard), confirming SCA compliance and triggering liability shift.

### How to Implement 3DS2

3DS2 is implemented through your payment gateway or payment service provider. All major European payment gateways support 3DS2:

- **Stripe:** Enables 3DS2 automatically for EU/UK transactions when configured. Uses Stripe Radar for risk assessment.
- **Adyen:** Native 3DS2 with built-in frictionless optimization and exemption handling.
- **Braintree:** 3DS2 implemented through Braintree's 3DS SDK.
- **Checkout.com:** Full 3DS2 support with exemption engine.

Merchants must ensure their checkout integration passes the required 3DS2 data fields (device fingerprint, browser information, transaction metadata) to achieve high frictionless pass rates and avoid unnecessary customer challenges.

---

## SCA Exemptions

Not every transaction must undergo full SCA. PSD2 defines several exemptions that issuers can grant, allowing transactions to proceed without a customer-facing authentication challenge:

### Low-Value Exemption
Transactions under €30 (or £25 in the UK) may be exempt from SCA. However, the exemption accumulates: after 5 consecutive exempt transactions, or when the total of exempt transactions since the last SCA-authenticated transaction reaches €100 (£100 UK), the next transaction must be fully SCA-authenticated regardless of value.

### Transaction Risk Analysis (TRA) Exemption
Payment service providers with low fraud rates (below 0.13% for transactions under €100; lower thresholds for higher amounts) may apply a risk-based exemption. This is primarily available to the issuer's PSP, not the merchant directly, though merchants can request this exemption via 3DS2 by including an exemption flag.

### Trusted Beneficiary (Whitelisting) Exemption
Cardholders can instruct their issuing bank to whitelist specific merchants. Subsequent transactions at whitelisted merchants do not require SCA challenge. Merchants who build strong customer relationships and encourage whitelisting benefit from reduced friction for returning customers.

### Recurring Transaction Exemption
The first payment in a recurring series requires SCA. Subsequent recurring charges for the same amount (fixed-amount subscription) do not require SCA at each recurrence — they are classified as "Merchant-Initiated Transactions" (MITs). Variable recurring amounts require fresh SCA at each charge.

### Secure Corporate Payment Exemption
Business-to-business payments made through secure corporate payment processes (lodge cards, virtual cards) may be exempt if the payer is a legal entity rather than a natural person.

### Mail Order / Telephone Order (MOTO) Exemption
Transactions initiated by the merchant on behalf of the cardholder (where the cardholder is not present in the session, such as phone orders) are out of scope for SCA as the cardholder is not digitally interacting with the checkout.

---

## Liability Shift Under SCA

SCA compliance directly affects liability in chargeback disputes:

**If SCA was applied and the transaction was fully authenticated (ECI 05/02):** The liability for any subsequent fraud chargeback shifts from the merchant to the issuing bank. The issuer is responsible for the fraud loss — the merchant wins the dispute automatically.

**If the merchant applied for an exemption and the issuer approved it (frictionless flow with exemption flag):** The issuer bears the fraud liability, as they accepted the risk by granting the exemption.

**If the merchant bypassed SCA without a valid exemption:** The merchant retains full fraud liability and cannot use the liability shift defense.

**If the issuer soft-declined the exemption request (asking for SCA challenge instead):** The merchant must step up to a 3DS challenge. Forcing the transaction through without compliance results in hard decline or fraud liability retention.

---

## Impact on UK Merchants (Post-Brexit)

Following the UK's departure from the EU, SCA requirements in the UK are governed by the FCA under its implementation of PSD2 principles (the Payment Services Regulations 2017). UK SCA requirements are substantively identical to EU SCA requirements. Cross-border transactions between UK merchants and EU cardholders — or UK cardholders and EU merchants — remain subject to SCA on the issuer side, even though regulatory authority is split.

---

## Common Merchant SCA Mistakes

- **Not passing 3DS2 browser data:** The 3DS2 protocol requires specific browser and device data fields. Missing fields cause the ACS to default to a full challenge, increasing friction unnecessarily.
- **Hardcoding exemption flags:** Requesting an exemption on every transaction, regardless of risk, will result in many exemption declines and frustrated customers.
- **Not handling soft declines:** When an issuer soft-declines an exemption request (SCA required), the merchant must retry the transaction with a 3DS challenge. Merchants who treat soft declines as hard declines lose orders unnecessarily.
- **Ignoring MOTO classification:** Telephone orders should be flagged as MOTO in the transaction metadata to exempt them from SCA properly rather than attempting 3DS on a non-digital transaction.

---

## SCA and Subscription Billing

For subscription merchants billing EU/UK cardholders:

- **First charge:** Must be SCA-authenticated, either through full 3DS2 challenge or a scope-in trial authorization.
- **Subsequent charges (same amount, same merchant):** Classified as Merchant-Initiated Transactions (MITs) — exempt from SCA, but must reference the initial SCA-authenticated transaction via the network transaction ID.
- **Variable amount subscriptions:** Each charge at a different amount may require fresh SCA — confirm with your payment gateway whether MIT exemption applies for variable amounts in your jurisdiction.

---

## Quick Reference: SCA Compliance Checklist

- [ ] 3DS2 implemented for all EU/UK customer transactions
- [ ] 3DS2 browser data fields (accept headers, screen size, color depth) passed correctly
- [ ] Frictionless exemption flags configured appropriately by transaction risk tier
- [ ] Soft decline handling implemented (retry with challenge on exemption refusal)
- [ ] MIT framework implemented for recurring subscription charges
- [ ] MOTO flag set for telephone-order transactions
- [ ] First recurring authorization stored with network transaction ID for future MIT references
