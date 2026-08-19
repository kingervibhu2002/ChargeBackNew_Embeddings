---
title: "Rebuttal Template — Mastercard Reason Code 4837 (CNP Fraud)"
category: Rebuttal Library
doc_type: template
reason_code: Mastercard 4837
dispute_type: No Cardholder Authorization — CNP
channel: E-Commerce, Card Not Present
audience: merchants
last_updated: 2026-06-01
tags: [Mastercard, 4837, CNP, fraud, unauthorized, rebuttal, template]
---

# Rebuttal Template: Mastercard Reason Code 4837 — No Cardholder Authorization (CNP)

## About This Reason Code

Mastercard Reason Code 4837 is the primary fraud dispute code for card-not-present transactions under Mastercard's dispute resolution framework. It is used when a cardholder claims they did not authorize a transaction made without their physical card being present. This is functionally equivalent to Visa's 10.4 for the CNP channel.

Under Mastercard's rules, the merchant bears the burden of proving that the transaction was authorized by the genuine cardholder, particularly through authentication data (AVS, CVC2, Mastercard Identity Check/3DS) and behavioral evidence. Mastercard's Second Presentment requires the merchant to provide compelling documentation rebutting the cardholder's claim.

---

## Mastercard-Specific Terminology

- **Second Presentment:** Mastercard's term for the merchant's rebuttal/representment
- **CVC2:** Mastercard's card verification code (equivalent to Visa's CVV2)
- **Mastercard Identity Check:** Mastercard's 3-D Secure program (EMVCo 3DS2)
- **Pre-Arbitration:** Mastercard's stage following Second Presentment if the issuer rejects the representment
- **Arbitration:** Final card network adjudication

---

## Pre-Submission Checklist

- [ ] Transaction authorization record from acquirer (with CVC2 and AVS results)
- [ ] Mastercard Identity Check authentication result (if 3DS was used)
- [ ] Device fingerprint and IP address at checkout
- [ ] Carrier delivery confirmation (if physical goods)
- [ ] Digital delivery logs (if digital goods)
- [ ] Prior transaction history with the same cardholder
- [ ] Order details and cardholder-confirmed billing/shipping address

---

## Rebuttal Letter Template (Mastercard Second Presentment)

---

**[MERCHANT NAME]**
[Merchant Address]
[Merchant Email]
Merchant ID: [MID]
Acquirer: [ACQUIRER NAME]

Date: [DATE]

Re: Mastercard Second Presentment — Case No. [CASE NUMBER]
Reason Code: 4837 — No Cardholder Authorization
Transaction Date: [TRANSACTION DATE]
Transaction Amount: [AMOUNT] [CURRENCY]
Cardholder Name: [CARDHOLDER NAME]
Card Number (Last 4): [XXXX]
ARN: [ACQUIRER REFERENCE NUMBER]

---

**To the Chargeback Review Team,**

[MERCHANT NAME] submits this Second Presentment in response to Mastercard Chargeback Case [CASE NUMBER] filed under Reason Code 4837. The cardholder asserts they did not authorize the transaction of [AMOUNT] on [DATE]. [MERCHANT NAME] disputes this claim and submits the following evidence demonstrating that the transaction was initiated by an authorized individual in possession of the cardholder's payment credentials and that the goods/services were delivered as ordered.

---

### Section 1: Transaction Details

| Field | Value |
|---|---|
| Transaction Date | [DATE] |
| Transaction Time (UTC) | [TIME] |
| Transaction Amount | [AMOUNT] [CURRENCY] |
| Authorization Code | [AUTH CODE] |
| Acquirer Reference Number (ARN) | [ARN] |
| Card Number (Last 4) | [XXXX] |
| Mastercard BIN | [BIN — first 6 digits] |
| Merchant Category Code (MCC) | [MCC] |
| Order / Transaction ID | [ID] |

---

### Section 2: CVC2 and AVS Authentication

At the time of the transaction, [MERCHANT NAME]'s payment gateway transmitted the following authentication parameters to the issuing bank via the Mastercard network:

**CVC2 (Card Verification Code 2):**

| Field | Value |
|---|---|
| CVC2 Submitted | Yes |
| CVC2 Response | **M — Match** |

The CVC2 is printed on the back of the physical Mastercard and is not encoded on the magnetic stripe or stored by merchants. A CVC2 match confirms that the person who entered payment data had access to the physical card.

**Address Verification Service (AVS):**

| Field | Value |
|---|---|
| Billing Address Submitted | [ADDRESS] |
| ZIP Code Submitted | [ZIP] |
| AVS Response Code | [CODE] |
| AVS Result | [e.g., "Full match — street address and ZIP"] |

Please refer to **Exhibit 1**: Authorization Record from Payment Gateway (showing CVC2 = M, AVS Response).

---

### Section 3: Mastercard Identity Check (3-D Secure)

[INCLUDE IF 3DS WAS USED. DELETE IF NOT APPLICABLE.]

This transaction was authenticated via Mastercard Identity Check (EMVCo 3DS version [2.1 / 2.2]) prior to authorization. Mastercard Identity Check requires the cardholder to complete an authentication challenge with their issuing bank.

| Field | Value |
|---|---|
| 3DS Version | [2.1 / 2.2] |
| Authentication Result | **Y — Verified** |
| ECI Value | **02 — Full Authentication** |
| dsTransID | [TRANSACTION ID] |
| ACS URL | [ACS DOMAIN] |
| Authentication Timestamp | [TIMESTAMP] |

**Per Mastercard's dispute rules, a fully authenticated 3DS transaction (ECI 02) results in liability shifting to the issuing bank. This Second Presentment should be accepted on this basis.**

Please refer to **Exhibit 2**: Mastercard Identity Check Authentication Record.

---

### Section 4: IP and Device Evidence

Our platform's fraud detection system captured the following data at the time of checkout:

| Field | Value |
|---|---|
| Checkout IP Address | [IP ADDRESS] |
| IP Geolocation | [CITY, STATE, COUNTRY] |
| IP Type | [Residential / Commercial — Not Proxy/VPN] |
| Device Type | [Desktop / Mobile / Tablet] |
| Operating System | [OS] |
| Browser | [BROWSER VERSION] |
| Device Fingerprint ID | [ID] |
| Fraud Score | [SCORE — e.g., "Low risk: 12/100"] |

The geolocation of the checkout IP is [LOCATION], which corresponds to the cardholder's billing address region. No proxy, VPN, or anonymizing service was detected.

Please refer to **Exhibit 3**: IP and Device Intelligence Report.

---

### Section 5: Delivery Evidence

[PHYSICAL GOODS — USE THIS SECTION. REPLACE WITH DIGITAL DELIVERY LOG IF DIGITAL GOODS.]

The ordered merchandise was shipped and delivered to the address confirmed by the cardholder:

| Field | Value |
|---|---|
| Carrier | [CARRIER NAME] |
| Tracking Number | [TRACKING NUMBER] |
| Ship Date | [DATE] |
| Delivery Date | [DATE] |
| Delivery Time | [TIME] |
| Delivery Address | [FULL ADDRESS] |
| Delivery Status | **Delivered** |
| Signature | [Obtained / Not Required] |

Please refer to **Exhibit 4**: Carrier Tracking Record.
Please refer to **Exhibit 5**: Signed Proof of Delivery (if obtained).

---

### Section 6: Prior Transaction History

The account or card has been used for prior transactions with [MERCHANT NAME] without dispute, demonstrating an established relationship with the genuine cardholder:

| Transaction Date | Amount | Authorization Code | Dispute Filed |
|---|---|---|---|
| [DATE] | [AMOUNT] | [AUTH CODE] | No |
| [DATE] | [AMOUNT] | [AUTH CODE] | No |
| [DATE] | [AMOUNT] | [AUTH CODE] | No |

Please refer to **Exhibit 6**: Transaction History Report.

---

### Section 7: Closing

[MERCHANT NAME] has submitted evidence demonstrating CVC2 match, [3DS authentication / AVS full match], IP geolocation consistent with the cardholder's address, delivery confirmation, and prior undisputed transaction history. The transaction of [AMOUNT] was completed by an authorized individual with possession of the cardholder's card details and was fulfilled as ordered.

We respectfully request that Mastercard Chargeback Case [CASE NUMBER] be reversed under Second Presentment and the amount of [AMOUNT] [CURRENCY] be restored to our account.

Sincerely,

[YOUR NAME]
[YOUR TITLE]
[MERCHANT NAME]
[EMAIL] | [PHONE]

---

## Evidence Index

| Exhibit | Document | Purpose |
|---|---|---|
| Exhibit 1 | Authorization Record | Proves CVC2 Match and AVS response |
| Exhibit 2 | Identity Check Record | Proves 3DS liability shift (if applicable) |
| Exhibit 3 | IP / Device Report | Ties checkout to cardholder's geography |
| Exhibit 4 | Carrier Tracking | Proves delivery to confirmed address |
| Exhibit 5 | Signed POD | Proves physical acceptance |
| Exhibit 6 | Transaction History | Shows established cardholder relationship |

---

## Mastercard-Specific Notes

- Reference the ARN (Acquirer Reference Number) in your submission header — Mastercard's dispute system uses the ARN as the primary transaction identifier.
- Mastercard's ECI 02 (full 3DS) is equivalent to Visa's ECI 05 — both represent full authentication and liability shift. If you have this, lead with it.
- Mastercard's Second Presentment must typically be filed within 45 days of the chargeback date. Confirm the exact deadline with your acquirer, as some have internal cutoffs of 30 days.
- Under Mastercard's rules, submitting a Second Presentment that is rejected leads to pre-arbitration. The merchant can accept pre-arbitration or escalate to arbitration (costly: $250-$500 filing fee). Only escalate if the chargeback amount justifies the fee and the evidence is very strong.
