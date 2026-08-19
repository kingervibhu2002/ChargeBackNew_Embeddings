---
title: "Email and Communication Evidence"
section: "09_Evidence"
category: "Evidence Library"
document_type: "Evidence Reference"
keywords: ["email evidence", "order confirmation", "shipping notification", "email metadata", "email open tracking", "CRM evidence", "cancellation policy", "communication history"]
difficulty: "Beginner"
---

# Email and Communication Evidence

## What Is Email Evidence?

Email and communication evidence encompasses all electronic communications between your merchant systems and the cardholder before, during, and after a transaction. This includes automated system emails (order confirmations, shipping notifications, subscription reminders), customer service interactions (email support tickets, chat transcripts), and CRM records of all contact with the customer account.

Email evidence serves multiple functions in chargeback defense:
- It proves the cardholder received notifications about the transaction.
- It demonstrates the cardholder engaged with your communications (proving awareness).
- It documents the terms and policies the cardholder agreed to.
- It shows any complaint the cardholder raised — and whether the merchant attempted to resolve it.
- It can demonstrate bad faith in a friendly fraud context (complaint filed after chargeback, not before).

## Order Confirmation Emails

The order confirmation email is sent immediately after a successful transaction and is the most fundamental email evidence for any chargeback response.

**What an effective order confirmation email provides as evidence:**

- **Timestamp:** The exact date and time the order was confirmed, proving the transaction was processed.
- **Delivery address:** The shipping address the cardholder specified, which should match what is in your order records.
- **Order details:** What was purchased, at what price, and the order reference number.
- **Billing descriptor notice:** If your company name differs from the transaction descriptor, include both in the confirmation so the cardholder recognizes the charge on their statement.
- **Customer acknowledgment:** Many merchants include a "Did you make this purchase?" security notice in order confirmations. If the cardholder received and did not respond to this notice, it supports the inference they recognized the transaction.

**Presenting order confirmation as evidence:**
Include a screenshot or PDF of the order confirmation email with the recipient's email address, send timestamp, and key order details visible. If your email service provider tracks opens (see below), note whether the email was opened and when.

## Shipping Notification Emails

For physical goods, the shipping notification email is sent when the order ships and includes carrier tracking information. This email is important evidence in non-receipt disputes because it demonstrates:

1. The merchant shipped the goods as promised.
2. The cardholder was notified of the shipment and given tracking information to monitor delivery.
3. If the cardholder clicked the tracking link in the email, they were actively monitoring their package (undermining a non-receipt claim).

**Content to preserve:**
- Send timestamp.
- Recipient email address.
- Tracking number included in the email.
- Carrier name.
- Estimated delivery date (if included).
- Whether the tracking link was clicked (and when, from what IP).

## Customer Service Email Threads

Customer service email threads are among the most contextually rich evidence in chargeback defense. They reveal:

**What the cardholder actually complained about:** If the cardholder's email complaint says "the product arrived damaged" but their chargeback code is "did not receive," there is a clear inconsistency that works in the merchant's favor.

**Whether the merchant attempted resolution:** Issuers look favorably on merchants who tried to resolve issues before the cardholder disputed. A documented offer to replace damaged goods, issue a partial refund, or extend a subscription demonstrates good faith.

**Timeline of complaint vs. chargeback:** If the cardholder filed the chargeback before ever contacting the merchant for resolution, this is a strong friendly fraud indicator. Conversely, if the merchant received multiple complaints and failed to respond, this undermines the merchant's position.

**How to present customer service threads:**
Export the full email thread as a PDF, including timestamps for each message, sender and recipient addresses, and the full text of each message. If the thread is long, highlight the most relevant exchanges in your rebuttal letter and include the full thread as the exhibit.

## Using Email Metadata (Headers) to Prove Delivery

Email headers contain technical delivery metadata that can be used to prove an email reached the cardholder's inbox:

**Key header fields:**
- `From:` — The sender address (your company's email system).
- `To:` — The recipient address (cardholder's email).
- `Date:` — The send timestamp, including timezone.
- `Message-ID:` — A unique identifier for the email.
- `Received:` — A chain of servers the email passed through, with timestamps. This proves the email was transmitted to the recipient's mail server.
- `DKIM-Signature:` — Proves the email was genuinely sent from your domain and not forged.
- `Delivered-To:` — Confirms acceptance by the recipient's mail server.

If the cardholder claims they "never received" an order confirmation, email headers showing the message was accepted by their mail server (`@gmail.com`, `@yahoo.com`, `@outlook.com`, etc.) undermine this claim. The message reached their inbox — whether they chose to read it is a separate matter.

**How to obtain headers:**
Most email service providers (Mailchimp, SendGrid, Postmark, AWS SES, Klaviyo) provide delivery logs including SMTP response codes confirming acceptance by the recipient's mail server. Export this log for the specific email send event associated with the disputed transaction.

## Email Open and Click Tracking

Many email service providers track whether recipients open emails and click links within them. This tracking works by embedding a unique 1×1 pixel image (open tracking) and redirect links (click tracking) in emails.

**When email open tracking is available:**
- Email service providers that track opens: Mailchimp, Klaviyo, Postmark, SendGrid, Mailgun, HubSpot, Intercom, and most marketing email platforms.
- Confirm that your platform logs open events with timestamps and (where available) approximate geolocation of the opening device.

**Evidentiary value:**
"The order confirmation email for Order #48291 was sent to customer@email.com on March 15, 2024 at 14:31 UTC. Email delivery logs confirm the message was accepted by Gmail's mail servers at 14:31:04 UTC. The email was opened on March 15, 2024 at 16:45 UTC from an IP address geolocating to Chicago, Illinois — consistent with the cardholder's billing address."

This sequence — transaction processed, confirmation email delivered, email opened from cardholder's location — is a powerful narrative that directly counters "I never received any notice of this transaction."

**Limitation:** Apple's Mail Privacy Protection (MPP), introduced in iOS 15, pre-fetches email images (including tracking pixels) using Apple's proxy servers, making open-tracking unreliable for Apple Mail users. Open tracking events from Apple Mail proxy IPs are not indicative of actual human opens. Factor this limitation into your evidence presentation — if the open event IP is from an Apple/iCloud proxy range, note the limitation and do not rely solely on this evidence.

## Cancellation Policy Sent at Sign-Up

For subscription merchants, including the cancellation policy in your evidence package proves the cardholder was informed of recurring billing terms at the time they enrolled.

**Evidence to include:**
- Screenshot of the sign-up page showing the cancellation policy or link to cancellation terms.
- Copy of the terms accepted during sign-up (pulled from your system at the time the cardholder enrolled, not the current terms).
- Confirmation that the enrollment email included a link to cancellation instructions.
- Pre-conversion reminder email sent before trial converted to paid subscription.

This documentation directly addresses Visa 13.2 (Cancelled Recurring Transaction) and Mastercard 4853 (Cardholder Dispute — Recurring) disputes where the cardholder claims they did not know the subscription would continue billing.

## CRM Communication History

Your Customer Relationship Management (CRM) system may contain the complete history of every interaction with the customer account — not just email, but phone call notes, chat transcripts, and logged actions.

**Valuable CRM evidence:**
- Timeline of all contacts with the account (sorted by date).
- Notes from customer service representatives summarizing call content.
- Log of any refund or replacement offered (and accepted or declined).
- Documentation that the cardholder requested support but the issue was resolved.
- Documentation that a cancellation was processed (or that no cancellation was received).

When exporting CRM records for dispute evidence, include the account history timeline in chronological order and highlight the interactions most relevant to the specific dispute claim.

## Complaint Received After Chargeback Filed

One of the clearest friendly fraud indicators is receiving a customer complaint about a transaction after the chargeback has already been filed. This sequence — chargeback filed, then complaint sent — demonstrates the cardholder went to the bank first rather than to the merchant, which is inconsistent with a genuine dispute.

If your CRM records show:
1. Chargeback notification received on [Date A].
2. Cardholder's first contact with your support team on [Date B, which is after Date A].

This strongly suggests the cardholder did not attempt to resolve the issue through the merchant first — a pattern consistent with deliberate chargeback abuse rather than a legitimate complaint.

Include both the chargeback notification timestamp and the first customer contact timestamp in your evidence package when this pattern exists.

## Summary

Email and communication evidence provides a documented timeline of the cardholder's awareness of and engagement with the transaction. Order confirmation emails prove transaction notification, shipping emails prove fulfillment, customer service threads reveal the true nature of the complaint, and email metadata proves delivery to the cardholder's inbox. When combined with email open and click tracking, this evidence demonstrates not just that communications were sent, but that the cardholder received and engaged with them. Maintain complete CRM records for all customer accounts, archive email delivery logs, and use communication evidence as the documentary backbone of your chargeback rebuttal alongside technical records (device fingerprint, IP, usage logs).
