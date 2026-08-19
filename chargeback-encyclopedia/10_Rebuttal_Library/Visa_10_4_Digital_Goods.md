---
title: "Rebuttal Template — Visa Reason Code 10.4 (Digital Goods)"
category: Rebuttal Library
doc_type: template
reason_code: Visa 10.4
dispute_type: Card Absent – Other Fraud
channel: Digital Goods, Software, Gaming, Streaming
audience: merchants
last_updated: 2026-06-01
tags: [Visa, 10.4, fraud, digital goods, rebuttal, template, download, 3DS]
---

# Rebuttal Template: Visa Reason Code 10.4 — Card Absent Environment / Other Fraud (Digital Goods)

## About This Reason Code in the Digital Context

Visa Reason Code 10.4 covers unauthorized card-not-present transactions. Digital goods merchants face a specific challenge: there is no physical delivery to prove. Instead, the defense relies on logs proving the product was digitally delivered and consumed — download records, activation events, login sessions, streaming usage, and IP/device data tying all activity back to the cardholder's device or account. The absence of a tracking number does not mean absence of delivery proof.

Digital goods covered by this template include: software licenses, game purchases, in-game items, streaming subscriptions, e-books, music downloads, digital gift cards, and online course access.

---

## Pre-Submission Checklist

- [ ] Authorization code and AVS/CVV response codes
- [ ] Download log (timestamp, IP address, file or license delivered)
- [ ] Activation or license key redemption record
- [ ] 3-D Secure (3DS) authentication result (if 3DS was used)
- [ ] Account creation record (email, IP, timestamp)
- [ ] Login history showing account access after purchase
- [ ] Feature or content usage data post-purchase
- [ ] IP geolocation records

---

## Rebuttal Letter Template

---

**[MERCHANT NAME]**
[Merchant Address]
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

[MERCHANT NAME] respectfully disputes Chargeback Case [CASE NUMBER] filed under Visa Reason Code 10.4. The transaction of [AMOUNT] processed on [TRANSACTION DATE] involved the digital delivery of [PRODUCT NAME]. The product was successfully delivered to the account associated with this card and was accessed by the account holder following purchase. We submit the following evidence.

---

### Section 1: Transaction Summary

| Field | Value |
|---|---|
| Transaction Date | [DATE] |
| Transaction Time (UTC) | [TIME] |
| Transaction Amount | [AMOUNT] |
| Authorization Code | [AUTH CODE] |
| Card Number (Last 4) | [XXXX] |
| AVS Response | [CODE — Description] |
| CVV Response | M — Match |
| Order / Transaction ID | [ID] |
| Account Email | [ACCOUNT EMAIL] |
| Product | [PRODUCT NAME — e.g., "GameTitle Pro License", "StreamCo Monthly Plan"] |

---

### Section 2: 3-D Secure Authentication Result

[INCLUDE THIS SECTION IF 3DS WAS USED. IF 3DS WAS NOT USED, DELETE THIS SECTION.]

This transaction was authenticated via 3-D Secure [version 1.0 / 2.x] prior to authorization. 3-D Secure requires the cardholder to authenticate directly with their issuing bank using a one-time password, biometric verification, or push approval. A successful 3DS authentication result transfers liability from the merchant to the issuing bank under Visa's rules.

| Field | Value |
|---|---|
| 3DS Version | [1.0 / 2.1 / 2.2] |
| Authentication Result | [Y — Fully Authenticated] |
| ECI Indicator | [05 — Full authentication] |
| Transaction ID (XID/dsTransID) | [ID] |
| Authentication Timestamp | [TIMESTAMP] |

**Under Visa's rules, a fully authenticated 3DS transaction (ECI 05) shifts liability to the issuing bank. This chargeback should be declined on that basis alone.**

Please refer to **Exhibit 1**: 3DS Authentication Record.

---

### Section 3: Digital Delivery Confirmation

Unlike physical goods, digital products are delivered via a secure download link, license key, or in-platform access. Our system logs every delivery event.

**Delivery Event Log:**

| Field | Value |
|---|---|
| Delivery Method | [Download Link / License Key / Platform Access / Stream Unlock] |
| Delivery Timestamp | [TIMESTAMP — within minutes of purchase] |
| Delivery Email Sent To | [EMAIL ADDRESS] |
| Email Status | Delivered and Opened |
| Download/Access IP Address | [IP ADDRESS] |
| File or License Delivered | [PRODUCT FILE NAME / LICENSE KEY PREFIX] |
| Download Completion | [Yes — bytes transferred: X MB] |

The product [PRODUCT NAME] was delivered to the email address [EMAIL] at [TIME] on [DATE]. The download was initiated and completed from IP address [IP ADDRESS], which geolocates to [CITY, STATE, COUNTRY], consistent with the cardholder's billing address.

Please refer to **Exhibit 2**: Digital Delivery Log (exported from [PLATFORM]).
Please refer to **Exhibit 3**: Delivery Confirmation Email.

---

### Section 4: Account Creation and Post-Purchase Usage

An account was created (or an existing account was used) to complete this purchase. The following account activity demonstrates that the product was accessed and used after the transaction date:

**Account Record:**

| Field | Value |
|---|---|
| Account Email | [EMAIL] |
| Account Created | [DATE] |
| Registration IP | [IP ADDRESS] |
| Purchase Date | [DATE] |
| First Login After Purchase | [DATE AND TIME] |
| Login IP | [IP ADDRESS] |
| Total Sessions (Post-Purchase) | [NUMBER] |
| Content/Features Accessed | [E.g., "Level 1–7 completed", "3 hours of streaming", "5 documents processed"] |
| Last Activity Date | [DATE] |

This account was accessed [NUMBER] times between [DATE] and [DATE]. This usage pattern is inconsistent with a fraudulent or unauthorized transaction, as the product was actively used by the account holder over an extended period.

Please refer to **Exhibit 4**: Account Activity Report.
Please refer to **Exhibit 5**: Session/Usage Log.

---

### Section 5: IP and Device Consistency

The IP addresses captured at account creation, purchase, and subsequent logins are consistent with one another and geolocate to the same region as the cardholder's billing address:

| Event | IP Address | Geolocation | Timestamp |
|---|---|---|---|
| Account Creation | [IP] | [City, Country] | [TIMESTAMP] |
| Purchase | [IP] | [City, Country] | [TIMESTAMP] |
| First Post-Purchase Login | [IP] | [City, Country] | [TIMESTAMP] |
| Most Recent Login | [IP] | [City, Country] | [TIMESTAMP] |

No anonymizing proxies, VPNs, or Tor exit nodes were detected during any of these sessions.

Please refer to **Exhibit 6**: IP Geolocation and Device Report.

---

### Section 6: Why Digital Delivery Is Complete

Digital goods are considered fully delivered when:
1. The product (file, license, or access key) is transmitted to the account associated with the purchasing card;
2. The account's delivery email is successfully received; and
3. The product is accessed using the delivered credentials.

All three conditions are satisfied in this case. The cardholder cannot claim non-delivery when our logs confirm download completion and post-delivery account activity from the same geographic region as the cardholder's billing address.

---

### Section 7: Closing

[MERCHANT NAME] has demonstrated through server logs, delivery records, authentication data, and post-purchase usage that the transaction was authorized, the digital product was delivered, and the product was used. We respectfully request reversal of Chargeback Case [CASE NUMBER] and restoration of [AMOUNT] to our merchant account.

Sincerely,

[YOUR NAME]
[YOUR TITLE]
[MERCHANT NAME]
[EMAIL] | [PHONE]

---

## Evidence Index

| Exhibit | Document | Purpose |
|---|---|---|
| Exhibit 1 | 3DS Authentication Record | Proves liability shift (if 3DS used) |
| Exhibit 2 | Digital Delivery Log | Proves product was transmitted |
| Exhibit 3 | Delivery Confirmation Email | Proves email delivery to cardholder |
| Exhibit 4 | Account Activity Report | Proves product was accessed post-purchase |
| Exhibit 5 | Session/Usage Log | Details features and content used |
| Exhibit 6 | IP Geolocation Report | Ties all activity to cardholder location |

---

## Merchant Notes

- If the cardholder shares an IP address with the purchase session, this is the strongest evidence available for digital goods. Highlight it prominently.
- If 3DS ECI 05 is present, lead with it. Liability is technically shifted and the issuer should decline the dispute at that point.
- For gaming platforms: include in-game purchase history, items equipped or redeemed, and multiplayer session logs as supplemental usage evidence.
- For streaming: include playback history (titles, timestamps, duration) pulled from your media server.
- Do not submit raw database exports without explaining what they show. Convert logs to a readable table and label each column clearly.
