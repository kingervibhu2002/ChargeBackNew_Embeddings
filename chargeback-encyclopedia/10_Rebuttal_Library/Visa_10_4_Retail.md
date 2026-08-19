---
title: "Rebuttal Template — Visa Reason Code 10.4 (Physical Retail / E-Commerce)"
category: Rebuttal Library
doc_type: template
reason_code: Visa 10.4
dispute_type: Card Absent – Other Fraud
channel: Retail, E-Commerce
audience: merchants
last_updated: 2026-06-01
tags: [Visa, 10.4, fraud, CNP, rebuttal, template, AVS, CVV]
---

# Rebuttal Template: Visa Reason Code 10.4 — Card Absent Environment / Other Fraud (Retail & E-Commerce)

## About This Reason Code

Visa Reason Code 10.4 is issued when a cardholder (or their issuing bank) claims that a card-not-present transaction was unauthorized — meaning the genuine cardholder did not authorize the charge. This is the most common fraud-related chargeback reason code. For merchants selling physical goods online or in-store with remote card processing, the key defenses are strong authorization data (AVS, CVV), delivery confirmation, and device/IP evidence tied to the genuine cardholder.

---

## Pre-Submission Checklist

Before using this template, confirm you have:

- [ ] Authorization code from the payment processor
- [ ] AVS response code (Y, Z, A, or N) and what it means
- [ ] CVV response code (M = match)
- [ ] Carrier tracking number showing delivery to the billing/shipping address
- [ ] Device fingerprint or IP address captured at checkout
- [ ] Order confirmation email sent to the cardholder's email address on file
- [ ] Any prior purchase history for the same card

---

## Rebuttal Letter Template

---

**[MERCHANT NAME]**
[Merchant Address]
[Merchant Phone]
[Merchant Email]
Merchant ID: [MID]

Date: [DATE]

Re: Chargeback Dispute — Case No. [CASE NUMBER]
Reason Code: Visa 10.4 — Card Absent Environment / Other Fraud
Transaction Date: [TRANSACTION DATE]
Transaction Amount: [AMOUNT]
Cardholder Name: [CARDHOLDER NAME]
Card Number (Last 4): [XXXX]

---

**To the Chargeback Review Team,**

[MERCHANT NAME] respectfully disputes Chargeback Case [CASE NUMBER] filed under Visa Reason Code 10.4. The transaction of [AMOUNT] processed on [TRANSACTION DATE] was fully authorized, authenticated, and fulfilled. We submit the following evidence to demonstrate that the order was placed by the legitimate cardholder and that goods were delivered as ordered.

---

### Section 1: Transaction Summary

| Field | Value |
|---|---|
| Transaction Date | [DATE] |
| Transaction Time (UTC) | [TIME] |
| Transaction Amount | [AMOUNT] |
| Authorization Code | [AUTH CODE] |
| Card Number (Last 4) | [XXXX] |
| AVS Response Code | [CODE] — [Description, e.g., "Full match: address and ZIP"] |
| CVV Response Code | M — Match |
| Order Number | [ORDER NUMBER] |
| Billing Address | [BILLING ADDRESS] |
| Shipping Address | [SHIPPING ADDRESS] |

---

### Section 2: AVS and CVV Authentication Evidence

At the time of the transaction, [MERCHANT NAME]'s payment processing system requested and received the following authentication responses from the issuing bank:

**AVS Response: [CODE]**
[Explanation: e.g., "The billing address and ZIP code provided at checkout matched the address on file with the issuing bank. This confirms the person entering the card data had access to the cardholder's billing information."]

**CVV Response: M (Match)**
The Card Verification Value entered at checkout matched the value stored by the issuing bank. The CVV is a three-digit code printed on the physical card and is not embossed or stored on the magnetic stripe. Possession of this code strongly indicates the transaction was made with the physical card or by a person with access to it.

Please refer to **Exhibit 1**: Authorization Record showing AVS and CVV response codes.

---

### Section 3: Delivery Confirmation

The order was shipped to the shipping address confirmed by the cardholder at checkout. Below is the delivery record:

| Field | Value |
|---|---|
| Carrier | [UPS / FedEx / USPS / DHL] |
| Tracking Number | [TRACKING NUMBER] |
| Ship Date | [SHIP DATE] |
| Delivery Date | [DELIVERY DATE] |
| Delivery Time | [DELIVERY TIME] |
| Delivery Address | [FULL ADDRESS] |
| Delivery Status | Delivered |
| Signature | [Obtained / Not Required per carrier service level] |

The shipping address used matches the billing address verified by AVS. The package was delivered to [DELIVERY ADDRESS] on [DATE] at [TIME].

Please refer to **Exhibit 2**: Carrier tracking record (printed from [CARRIER] website).
Please refer to **Exhibit 3**: Signed delivery confirmation (if applicable).

---

### Section 4: Device and IP Evidence

Our platform captured the following technical data at the time of checkout:

| Field | Value |
|---|---|
| IP Address at Checkout | [IP ADDRESS] |
| Geolocation | [CITY, STATE, COUNTRY] |
| Device Type | [Desktop / Mobile / Tablet] |
| Browser | [BROWSER AND VERSION] |
| Device Fingerprint | [FINGERPRINT ID] |
| Session ID | [SESSION ID] |

The IP geolocation is consistent with the cardholder's billing address of record. No VPN or proxy was detected at the time of the transaction.

Please refer to **Exhibit 4**: Device and IP report from [PLATFORM/FRAUD TOOL].

---

### Section 5: Order Confirmation and Customer Communication

An order confirmation email was sent to [CARDHOLDER EMAIL] on [DATE] at [TIME]. This email contained the order summary, shipping address, and tracking information. The email was delivered and opened (if tracked).

[If applicable:] Prior to the disputed transaction, this cardholder completed [NUMBER] successful purchases with our store without any dispute history, totaling [AMOUNT] in prior purchases.

Please refer to **Exhibit 5**: Order confirmation email.
Please refer to **Exhibit 6**: Customer purchase history (if applicable).

---

### Section 6: Closing

Based on the authorization data (AVS full match, CVV match), the carrier-confirmed delivery to the cardholder's address, and the device/IP data consistent with the cardholder's location, [MERCHANT NAME] has demonstrated that this transaction was completed by an authorized individual with access to the physical card and the cardholder's billing information.

We respectfully request that Chargeback Case [CASE NUMBER] be reversed and the amount of [AMOUNT] be restored to [MERCHANT NAME]'s account.

Sincerely,

[YOUR NAME]
[YOUR TITLE]
[MERCHANT NAME]
[EMAIL]
[PHONE]

---

## Evidence Index

| Exhibit | Document | Purpose |
|---|---|---|
| Exhibit 1 | Authorization Record | Proves AVS Y + CVV M response |
| Exhibit 2 | Carrier Tracking Printout | Proves delivery to cardholder address |
| Exhibit 3 | Signed Delivery Confirmation | Proves recipient accepted the package |
| Exhibit 4 | Device/IP Report | Ties checkout to cardholder's geographic location |
| Exhibit 5 | Order Confirmation Email | Confirms cardholder's email received order details |
| Exhibit 6 | Purchase History | Demonstrates established cardholder relationship |

---

## Merchant Notes

- If AVS returned a partial match (A or Z) rather than a full match (Y), adjust the narrative to reflect what was matched and explain any supplemental evidence you have.
- If CVV was not collected or returned N, do not reference CVV as a defense. Focus instead on delivery and device evidence.
- Under Visa CE 3.0, two prior undisputed transactions from the same cardholder can constitute "compelling evidence." Include prior transaction dates and authorization codes if available.
- Never include the full 16-digit card number in your submission — last four digits only.
