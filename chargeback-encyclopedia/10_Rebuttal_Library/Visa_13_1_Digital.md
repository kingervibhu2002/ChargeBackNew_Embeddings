---
title: "Rebuttal Template — Visa Reason Code 13.1 (Not Received — Digital Goods)"
category: Rebuttal Library
doc_type: template
reason_code: Visa 13.1
dispute_type: Merchandise / Services Not Received
channel: Digital Goods, Software, Downloads
audience: merchants
last_updated: 2026-06-01
tags: [Visa, 13.1, not received, digital goods, download, delivery, rebuttal, template]
---

# Rebuttal Template: Visa Reason Code 13.1 — Merchandise / Services Not Received (Digital Goods)

## About This Reason Code in the Digital Context

Visa Reason Code 13.1 for digital goods occurs when a cardholder claims they never received a digital product — a software download, a license key, an e-book, a digital media file, or access credentials to a platform. Unlike physical goods, you cannot point to a carrier delivery. Instead, your defense rests on server-generated delivery logs: the email delivery record, the download initiation and completion log, the license key redemption event, and the IP address at the time of access.

Key defense principle: **digital delivery is proven by server logs, not by the cardholder's assertion.** If your logs show a file was transmitted and the download session completed, delivery has occurred.

---

## Pre-Submission Checklist

- [ ] Email delivery record (sent to cardholder's email at what time)
- [ ] Email open record (if tracked via delivery receipt or email service provider)
- [ ] Download initiation log (timestamp, IP address, session ID)
- [ ] Download completion log (bytes transferred, completion timestamp)
- [ ] License key delivery and/or redemption record (if applicable)
- [ ] Activation confirmation (if product required activation)
- [ ] Post-delivery account login or content access record
- [ ] IP geolocation for all delivery and access events
- [ ] Authorization record

---

## Rebuttal Letter Template

---

**[MERCHANT NAME]**
[Merchant Address]
[Merchant Email]
Merchant ID: [MID]

Date: [DATE]

Re: Chargeback Dispute — Case No. [CASE NUMBER]
Reason Code: Visa 13.1 — Merchandise Not Received (Digital Goods)
Transaction Date: [TRANSACTION DATE]
Transaction Amount: [AMOUNT]
Cardholder Name: [CARDHOLDER NAME]
Card Number (Last 4): [XXXX]

---

**To the Chargeback Review Team,**

[MERCHANT NAME] respectfully disputes Chargeback Case [CASE NUMBER] filed under Visa Reason Code 13.1. The cardholder claims that digital goods were not received. Our server logs and delivery records demonstrate that [PRODUCT NAME] was transmitted electronically to the email address [CARDHOLDER EMAIL] at [DELIVERY TIME] on [DELIVERY DATE], the download was completed by a session originating from an IP address consistent with the cardholder's billing region, and the license or access credentials were subsequently used.

---

### Section 1: Transaction Summary

| Field | Value |
|---|---|
| Transaction Date | [DATE] |
| Transaction Amount | [AMOUNT] |
| Authorization Code | [AUTH CODE] |
| Card Number (Last 4) | [XXXX] |
| Order / Transaction ID | [ID] |
| Product Purchased | [PRODUCT NAME] |
| Account / Recipient Email | [EMAIL] |
| Delivery Method | [Email Link / Inline Download / License Key / Platform Access] |

---

### Section 2: Email Delivery Record

Immediately following payment confirmation, our system generated and transmitted a delivery email containing the product download link or access credentials to the cardholder's email address.

| Field | Value |
|---|---|
| Sender | [noreply@merchantdomain.com] |
| Recipient | [CARDHOLDER EMAIL] |
| Email Subject | [e.g., "Your [Product Name] is Ready to Download"] |
| Sent Timestamp | [DATE AND TIME UTC] |
| Email Provider Record | [SendGrid / Mailgun / SES — Message ID: XXXXX] |
| Delivery Status | **Delivered** |
| Open Timestamp | [DATE AND TIME] (if tracked) |
| Open IP Address | [IP ADDRESS] (if tracked) |

The email was delivered to the cardholder's inbox at [TIMESTAMP]. Our email service provider (ESP) has confirmed delivery with Message ID [MESSAGE ID].

Please refer to **Exhibit 1**: ESP Delivery Log (showing sent status, recipient, and timestamp).
Please refer to **Exhibit 2**: Delivery Confirmation Email (copy of the email sent to cardholder).

---

### Section 3: Download Log

Our platform server logs record every download event including the session IP address, the file transmitted, and whether the download was completed.

**Download Event Record:**

| Field | Value |
|---|---|
| Download Initiated | [DATE AND TIME UTC] |
| Download Completed | [DATE AND TIME UTC] |
| Session Duration | [MINUTES / SECONDS] |
| File Delivered | [FILENAME or PRODUCT IDENTIFIER] |
| File Size | [SIZE IN MB/GB] |
| Bytes Transferred | [BYTES] — Indicating completed download |
| Session IP Address | [IP ADDRESS] |
| IP Geolocation | [CITY, STATE, COUNTRY] |
| Device / User-Agent | [BROWSER AND OS] |

The download session completed fully — the byte count confirms the entire file was transferred, not a partial or failed download. The IP address geolocates to [LOCATION], which is consistent with the billing address on the card ending in [XXXX].

Please refer to **Exhibit 3**: Server Download Log (exported from [PLATFORM]).

---

### Section 4: License Key Delivery and Redemption (If Applicable)

[INCLUDE IF PRODUCT USED A LICENSE KEY SYSTEM. DELETE IF NOT APPLICABLE.]

This product was delivered as a software license key. The following records apply:

| Field | Value |
|---|---|
| License Key | [KEY PREFIX — e.g., XXXX-XXXX-XXXX-****] |
| Key Delivered (Email) | [DATE AND TIME] |
| Key Redeemed / Activated | [DATE AND TIME] |
| Activation IP | [IP ADDRESS] |
| Activation Platform | [e.g., "Merchant activation server", "Steam", "Adobe"] |
| Product Version Activated | [VERSION] |

The license key assigned to this order was redeemed on [DATE] from IP address [IP], confirming that the recipient had received the key and successfully activated the product.

Please refer to **Exhibit 4**: License Issuance and Redemption Record.

---

### Section 5: Post-Delivery Content Access

Following delivery, the account or license was used to access content, confirming that the cardholder or an authorized user received and opened the product.

| Event | Timestamp | IP Address | Action |
|---|---|---|---|
| [Login / Open / Play] | [TIMESTAMP] | [IP] | [e.g., "Opened downloaded file", "Played chapter 1"] |
| [Next Access] | [TIMESTAMP] | [IP] | [ACTION] |
| [Most Recent Access] | [TIMESTAMP] | [IP] | [ACTION] |

The account was accessed [NUMBER] times in the [TIME PERIOD] following delivery, all from IPs geolocating to [REGION]. This access pattern is inconsistent with a claim of non-delivery.

Please refer to **Exhibit 5**: Access / Activity Log.

---

### Section 6: Why Digital Delivery Is Complete

Under Visa's rules, digital goods are considered delivered when:
1. They are transmitted to the email address or platform account associated with the purchasing card;
2. The delivery confirmation is verifiable through an independent channel (ESP log, download server record); and
3. There is no technical error returned (bounce, failed transmission, download error).

None of the above exceptions apply. The delivery email was successfully received. The file was downloaded to completion. The license was redeemed. The cardholder cannot claim non-receipt when verifiable server records confirm each step of the delivery chain.

---

### Section 7: Closing

[MERCHANT NAME] has produced email delivery records, server download logs, license redemption records, and post-access logs that conclusively demonstrate [PRODUCT NAME] was delivered and accessed. The charge of [AMOUNT] represents a fully fulfilled transaction.

We respectfully request that Chargeback Case [CASE NUMBER] be reversed and [AMOUNT] be restored to our merchant account.

Sincerely,

[YOUR NAME]
[YOUR TITLE]
[MERCHANT NAME]
[EMAIL] | [PHONE]

---

## Evidence Index

| Exhibit | Document | Purpose |
|---|---|---|
| Exhibit 1 | ESP Delivery Log | Proves email was delivered to cardholder inbox |
| Exhibit 2 | Delivery Email Copy | Shows content and download link sent |
| Exhibit 3 | Server Download Log | Proves complete file transmission |
| Exhibit 4 | License Redemption Record | Proves key was used (if applicable) |
| Exhibit 5 | Post-Delivery Access Log | Proves product was opened and used after delivery |

---

## Merchant Notes

- Logs must be from server-side records, not client-side assertions. A claim that "our system shows it was delivered" without an actual log export will not be convincing. Export the raw record with timestamps and include it as an exhibit.
- For email delivery, SendGrid, Mailgun, and AWS SES all produce event logs with timestamps, recipient addresses, and delivery/open status. Export these logs and include them as exhibits.
- If your product is browser-accessed (no download), focus on the access log: when was the link clicked, what was accessed, how long was the session. This replaces the download log.
- If the cardholder claims the download link was broken or expired, review your link expiry policy. If the link had expired, consider whether re-delivery was attempted. Either way, document it.
