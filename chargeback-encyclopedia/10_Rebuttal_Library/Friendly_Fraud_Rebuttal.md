---
title: "Rebuttal Template — Suspected Friendly Fraud"
category: Rebuttal Library
doc_type: template
reason_code: Multiple (Visa 10.4, 13.1, 13.2; MC 4837, 4853)
dispute_type: Friendly Fraud — First-Party Misuse
channel: E-Commerce, Digital Goods, Subscription, Retail
audience: merchants
last_updated: 2026-06-01
tags: [friendly fraud, first-party fraud, chargeback abuse, rebuttal, template, Visa CE3.0]
---

# Rebuttal Template: Suspected Friendly Fraud

## About Friendly Fraud

Friendly fraud — also called first-party misuse — occurs when a legitimate cardholder makes a purchase, receives the goods or services, and then disputes the charge with their bank claiming they did not authorize it or did not receive it. Unlike criminal fraud where a stolen card is used, the genuine account holder is deliberately abusing the chargeback process to avoid paying for something they kept and used.

Friendly fraud is the fastest-growing category of chargeback loss for merchants, accounting for an estimated 60–80% of all disputes in some industries. The challenge for merchants is that friendly fraud disputes look identical to genuine fraud disputes in the card network's initial review. The defense strategy is to prove, through a pattern of behavioral evidence, that the cardholder is the person who made and benefited from the transaction.

This template applies when you suspect friendly fraud across Visa codes 10.4, 13.1, 13.2, and Mastercard codes 4837 and 4853.

---

## Indicators That a Dispute May Be Friendly Fraud

- The cardholder has purchased from you multiple times without prior disputes
- The shipping address matches the billing address
- The IP at checkout is consistent with the cardholder's home region
- The product was delivered and no return was initiated
- The product was used, streamed, logged in to, or activated after delivery
- The cardholder contacted customer support about the product (proving awareness)
- The dispute is filed long after delivery (90+ days suggests regret, not fraud)
- The cardholder has filed multiple chargebacks across different merchants

---

## Pre-Submission Checklist

- [ ] Prior purchase history for this cardholder (dates, amounts, no disputes)
- [ ] Delivery confirmation (carrier tracking or digital delivery logs)
- [ ] Post-delivery product usage logs (login, activation, streaming, API use)
- [ ] Device and IP consistency data (same device across prior purchases and this one)
- [ ] Customer service contact after delivery (proves cardholder knew about the order)
- [ ] Compelling Evidence 3.0 (CE3.0) qualifying transactions (Visa: two prior undisputed transactions from same cardholder)
- [ ] Any communication where the cardholder references the product they now claim they never received

---

## Rebuttal Letter Template

---

**[MERCHANT NAME]**
[Merchant Address]
[Merchant Email]
Merchant ID: [MID]

Date: [DATE]

Re: Chargeback Dispute — Case No. [CASE NUMBER]
Reason Code: [REASON CODE — e.g., Visa 10.4 / MC 4837]
Transaction Date: [TRANSACTION DATE]
Transaction Amount: [AMOUNT]
Cardholder Name: [CARDHOLDER NAME]
Card Number (Last 4): [XXXX]

---

**To the Chargeback Review Team,**

[MERCHANT NAME] disputes Chargeback Case [CASE NUMBER]. While the cardholder has filed under [REASON CODE] claiming [STATED CLAIM — e.g., "transaction was not authorized"], the cumulative evidence below demonstrates that the genuine cardholder initiated and completed this transaction, received the goods/services ordered, and used or consumed the product following delivery. We respectfully submit this as a case of first-party dispute abuse.

---

### Section 1: Transaction Summary

| Field | Value |
|---|---|
| Transaction Date | [DATE] |
| Transaction Amount | [AMOUNT] |
| Authorization Code | [AUTH CODE] |
| Card Number (Last 4) | [XXXX] |
| AVS Response | [CODE] |
| CVV Response | [M — Match] |
| Order Number | [NUMBER] |
| Product | [PRODUCT NAME] |
| Account Email | [EMAIL] |

---

### Section 2: Prior Purchase History — Established Cardholder Relationship

The card ending in [XXXX] has been used for [NUMBER] prior transactions with [MERCHANT NAME] over [TIME PERIOD] without any dispute:

| Transaction Date | Amount | Product | Authorization Code | Disputed? |
|---|---|---|---|---|
| [DATE] | [AMOUNT] | [PRODUCT] | [CODE] | No |
| [DATE] | [AMOUNT] | [PRODUCT] | [CODE] | No |
| [DATE] | [AMOUNT] | [PRODUCT] | [CODE] | No |
| [DATE — Disputed] | [AMOUNT] | [PRODUCT] | [CODE] | **Yes** |

The cardholder has spent a total of [AMOUNT] at [MERCHANT NAME] prior to this dispute. A pattern of repeated, undisputed purchases with the same card strongly suggests the cardholder is familiar with and has accepted prior charges from our merchant. The disputed transaction does not differ in any meaningful way from these prior accepted purchases.

**Under Visa's Compelling Evidence 3.0 framework, two or more prior undisputed transactions from the same cardholder on the same card constitute compelling evidence that the cardholder authorized the disputed transaction. Exhibit 1 presents [NUMBER] qualifying prior transactions.**

Please refer to **Exhibit 1**: Prior Transaction History (CE3.0 qualifying transactions highlighted).

---

### Section 3: Delivery to Confirmed Address

The product ordered in the disputed transaction was delivered to the same address associated with all prior undisputed orders:

| Field | Value |
|---|---|
| Shipping Address (This Order) | [ADDRESS] |
| Shipping Address (Prior Orders) | [SAME ADDRESS — confirms consistency] |
| Carrier | [CARRIER] |
| Tracking Number | [NUMBER] |
| Delivery Date | [DATE] |
| Delivery Status | **Delivered** |

The cardholder has received prior shipments at this same address without dispute. A claim that this specific delivery was not received is inconsistent with the pattern of all previous deliveries.

Please refer to **Exhibit 2**: Carrier Delivery Confirmation.
Please refer to **Exhibit 3**: Prior Order Shipping Records (showing same delivery address used for all orders).

---

### Section 4: Post-Delivery Product Usage Evidence

Following delivery of [PRODUCT NAME], the product was accessed, activated, or used by the account or device associated with the cardholder:

| Event | Date | IP Address | Details |
|---|---|---|---|
| [Login / Download / Activation] | [DATE — after delivery] | [IP] | [DESCRIPTION] |
| [Usage Event] | [DATE] | [IP] | [DESCRIPTION] |
| [Most Recent Usage] | [DATE] | [IP] | [DESCRIPTION] |

The IP addresses for post-delivery usage are consistent with those used in prior undisputed transactions. The device fingerprint recorded during the disputed transaction matches the device used in prior purchases.

A genuine fraud victim does not use the fraudulently delivered product. Active product usage after delivery contradicts the claim of unauthorized transaction or non-receipt.

Please refer to **Exhibit 4**: Post-Delivery Usage Log.
Please refer to **Exhibit 5**: Device Fingerprint Consistency Report (matching prior orders).

---

### Section 5: Customer Service Contact After Delivery (If Applicable)

[INCLUDE IF CARDHOLDER CONTACTED SUPPORT AFTER RECEIVING THE PRODUCT. DELETE IF NO CONTACT.]

On [DATE — after delivery], the cardholder contacted [MERCHANT NAME] customer service via [EMAIL / CHAT / PHONE] regarding Order [NUMBER]. The subject of the inquiry was **[SUBJECT — e.g., "Usage question about Product X" / "Requesting instructions for setup"]**.

This contact post-delivery confirms that the cardholder was aware of the order, had received the product, and was using it. A customer who never received a product would not contact the merchant with a usage question.

Please refer to **Exhibit 6**: Customer Service Contact Record (dated after delivery).

---

### Section 6: Device and IP Address Consistency

Across all transactions associated with this account, the same device and IP address cluster have been used consistently:

| Order Date | IP Address | Device | Geolocation |
|---|---|---|---|
| [PRIOR ORDER DATE] | [IP] | [DEVICE] | [LOCATION] |
| [PRIOR ORDER DATE] | [IP] | [DEVICE] | [LOCATION] |
| [DISPUTED ORDER DATE] | [IP] | [DEVICE] | [LOCATION] |

The IP address and device used for the disputed transaction are indistinguishable from those used in all prior undisputed orders. There is no evidence of an unauthorized third party using a different device or location.

Please refer to **Exhibit 7**: IP and Device Consistency Report (all orders on this account).

---

### Section 7: Compelling Evidence 3.0 Summary (Visa Only)

[INCLUDE THIS SECTION FOR VISA 10.4 DISPUTES ONLY.]

Visa's Compelling Evidence 3.0 (CE3.0) program, effective April 2023, provides merchants with a mechanism to shift liability back to the issuer in fraud disputes when the merchant can demonstrate:

1. **Two or more prior undisputed transactions** from the same cardholder on the same card within 120–365 days of the disputed transaction.
2. The prior transactions share at least **two matching data elements** with the disputed transaction (e.g., same device fingerprint + same IP address, or same shipping address + same device fingerprint).

[MERCHANT NAME] meets both CE3.0 criteria:

- **Prior qualifying transactions:** [NUMBER] undisputed transactions from card XXXX between [DATE] and [DATE] (within the 365-day lookback period)
- **Matching data elements:** [SPECIFY — e.g., "Same device fingerprint (Device ID: XXXXX) and same shipping address (123 Main St)"] present in the disputed transaction and both qualifying prior transactions

Please refer to **Exhibit 8**: CE3.0 Matching Elements Report.

---

### Section 8: Closing

The evidence presented demonstrates a clear pattern: the same cardholder, using the same device and IP address from the same location, purchased from [MERCHANT NAME] multiple times without dispute, received and used the product from the disputed transaction, and then filed a chargeback. There is no evidence of third-party fraud. The disputed charge of [AMOUNT] was authorized by the genuine cardholder and the goods/services were received and used.

We respectfully request that Chargeback Case [CASE NUMBER] be reversed and [AMOUNT] be restored to our account.

Sincerely,

[YOUR NAME]
[YOUR TITLE]
[MERCHANT NAME]
[EMAIL] | [PHONE]

---

## Evidence Index

| Exhibit | Document | Purpose |
|---|---|---|
| Exhibit 1 | Prior Transaction History | Proves CE3.0 pattern / established relationship |
| Exhibit 2 | Carrier Delivery Confirmation | Proves delivery to same address used historically |
| Exhibit 3 | Prior Order Shipping Records | Proves address consistency |
| Exhibit 4 | Post-Delivery Usage Log | Proves product was used after delivery |
| Exhibit 5 | Device Fingerprint Report | Proves same device across all orders |
| Exhibit 6 | Customer Service Contact Record | Proves cardholder was aware of and using the product |
| Exhibit 7 | IP/Device Consistency Report | Proves all sessions originate from same cardholder device |
| Exhibit 8 | CE3.0 Matching Elements Report | Formalizes Visa CE3.0 liability shift claim |
