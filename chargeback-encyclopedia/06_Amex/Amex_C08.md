---
title: "Amex Dispute Code C08 — Goods or Services Not Received"
description: "Complete merchant guide to American Express dispute code C08: non-delivery disputes, Amex's strict tracking requirements, digital delivery evidence, and when to refund versus fight."
category: Amex
reason_code: "C08"
chargeback_type: "Goods or Services Not Received"
win_rate: Medium (physical); Medium-Low (digital, without logs)
last_updated: 2026-06-29
tags: [amex, C08, goods-not-received, non-delivery, tracking, digital-goods, services, chargeback-defense]
---

# Amex C08 — Goods or Services Not Received

## What This Dispute Code Means

American Express dispute code C08 is filed when a cardholder claims they paid for goods or services that were never delivered or rendered. This is one of the most common Amex dispute codes across e-commerce, digital goods, and service businesses. The cardholder's claim may be entirely true (the merchant failed to deliver), partially true (delivery was late or partial), or false (the goods were delivered but the cardholder is committing friendly fraud).

C08 is the Amex equivalent of Mastercard's reason code 4855 and Visa's reason code 13.1. However, Amex's evidence standards — particularly for physical goods delivery — are stricter than those of Visa or Mastercard. Where Visa or Mastercard may accept basic carrier tracking as sufficient delivery proof, Amex frequently requires more comprehensive documentation.

---

## Why Amex's Standards Are Stricter

Amex's higher evidence threshold for C08 reflects its closed-loop structure and premium brand positioning. Because Amex acts as both issuer and network, it has direct visibility into cardholder spending behavior — and Amex cardholders who file disputes expect resolution in their favor as a feature of their premium card membership. Merchants processing Amex must meet this higher standard or face disproportionate loss rates.

**What this means practically:**
- A tracking number alone is usually insufficient — Amex wants proof of delivery to the correct address
- Signed delivery confirmation is the gold standard and should be obtained for all high-value shipments
- For digital goods, server-side delivery logs are required — order confirmation emails are supporting evidence, not primary evidence
- For services, client-acknowledged completion is preferable to merchant-only completion records

---

## Evidence by Fulfillment Type

### Physical Goods — Required Evidence

| Evidence Item | Amex Standard |
|---|---|
| Carrier tracking number | Necessary but insufficient alone |
| Carrier proof of delivery (POD) | Required — official carrier document showing delivery timestamp and recipient name |
| Signature confirmation | Strongest evidence — named recipient at cardholder's address |
| Delivery to billing address | Critical — delivery to a different address without documented cardholder authorization weakens your case significantly |
| AVS match at checkout | Confirms the billing address used was the cardholder's registered address |
| Shipping label copy | Corroborates the address the package was sent to |

For high-value shipments (items above $100–200), using a carrier service that requires signature confirmation is strongly recommended. The incremental shipping cost is insignificant compared to the cost of an Amex chargeback, dispute fee, and ratio impact.

For orders shipped to a different address than the billing address (gift shipping, alternate address), include documented evidence that the cardholder provided the alternate address (order details, email correspondence), and ensure the alternate address was verified at checkout.

### Digital Goods — Required Evidence

Digital delivery is inherently harder to document, but server-side logs are authoritative if properly maintained:

- **Download logs**: IP address, timestamp, and session ID for each download event linked to the cardholder's account or order
- **Activation records**: License key generation and redemption timestamp; redemption IP address
- **Account access logs**: For SaaS or streaming products, session records showing the cardholder's account was accessed after purchase (login events, feature usage, content views)
- **Email delivery confirmation**: Show the download link or access credentials were sent to the cardholder's email address and were not bounced (your email service provider's delivery log)
- **Support interactions**: Any contact from the cardholder after purchase (even asking for technical help) proves they received and attempted to use the product

**Build server-side delivery logging before you need it.** Merchants who win digital goods C08 disputes have invested in delivery event logging. Those who cannot produce logs beyond an "order confirmed" database record lose consistently.

### Services — Required Evidence

Service merchants need to document that the work was done:

- **Signed completion form or service agreement** with a date
- **Project deliverables submitted** (file transfer records, email delivery of completed work)
- **Meeting or appointment records** (calendar confirmations, attendance logs, session notes with timestamps)
- **Client communication acknowledging performance** (email where client references the completed work, a thank-you note, or a follow-up instruction)
- **Invoices with itemized billing** tied to specific completed work sessions or milestones

For multi-session services (ongoing consulting, recurring coaching, monthly maintenance), provide records for each session performed through the dispute date. Do not submit a single summary — detail is more convincing.

---

## Timeframe and Promised Delivery Date

A sub-variant of C08 involves merchants who promised delivery by a specific date and missed that date. The cardholder may have needed the item for a specific event and it arrived too late to be useful. In this scenario:

**Merchant wins when:**
- The cardholder did not cancel the order before shipment
- The item was delivered and the cardholder accepted it
- The delay was disclosed and acknowledged by the cardholder before dispute filing

**Merchant loses when:**
- The merchant explicitly promised a delivery date in writing and missed it
- The cardholder canceled the order before shipment (and the item was shipped anyway)
- The item was for a specific occasion that the cardholder communicated (e.g., a wedding gift ordered with a specified delivery deadline)

For seasonal or event-driven businesses (florists, event suppliers, custom apparel), be conservative with promised delivery dates. Missing a stated delivery date is one of the highest-probability C08 loss scenarios.

---

## When to Refund vs. When to Fight

**Issue a proactive refund when:**
- Tracking shows the package is lost, stuck in transit, or "delayed — no scheduled delivery date"
- The item cannot be located in your warehouse or was never shipped
- You missed the promised delivery date and the cardholder has clearly communicated they no longer want the item
- The service was not performed due to your scheduling failure

**Fight the dispute when:**
- Your carrier POD confirms delivery to the correct address with a named recipient
- Your digital delivery logs show the product was downloaded and activated
- Your service records confirm the work was completed and the client acknowledged it
- The cardholder previously acknowledged receiving the goods (support inquiry, review, follow-up order)

---

## Frequently Asked Questions

**Q: The tracking shows delivered but the cardholder says they never got the package. Amex sided with them — how do I fight this?**
A: If you have a signed proof of delivery with the cardholder's name, submit it immediately in your rebuttal. If the delivery only shows "left at door" without a signature, your evidence is weaker. Also include: prior purchase history from this cardholder, AVS match data, and the full carrier POD document (not just a screenshot). If you cannot obtain a signed POD, consider whether the chargeback cost justifies accepting the loss and implementing signature-required shipping for future high-value orders.

**Q: For a software subscription, what counts as "delivery" in Amex's eyes?**
A: Account access logs showing the cardholder logged in, used features, or consumed content after the purchase date. If you can show that the cardholder's account was active after purchase — even accessing basic features — that constitutes service delivery in Amex's framework. Supplement with login IP records and any support interactions the cardholder had about using the product.

**Q: Can I fight a C08 if the cardholder received part of their order but claims nothing was delivered?**
A: Yes. Document partial delivery with carrier records for the items that were shipped, and show the value of what was delivered versus what is outstanding. If the full order was shipped in multiple packages, provide tracking for each. For the delivered portion, request a partial reversal — you should not absorb chargebacks for items that were successfully delivered.

**Q: My service was performed but the client did not sign a completion form. Do I have any defense?**
A: Yes, but it is weaker. Rely on correspondence evidence — emails referencing the completed work, follow-up instructions sent after completion, any client feedback or communication that implicitly acknowledges the service occurred. Photographs or documentation of the work performed (before/after, project files delivered) can supplement. For future engagements, implement completion sign-off as a standard part of your service close-out process.

**Q: How does Amex's C08 differ from Mastercard 4855 and Visa 13.1 in practice?**
A: The legal structure is similar but Amex applies higher scrutiny to the evidence submitted. Amex reviewers look for carrier POD documents rather than tracking screenshots, and for digital goods they expect server-side logs rather than email records. The response window is also shorter (20 days vs. 30–45 days). Merchants who have won Visa/Mastercard non-delivery disputes should not assume the same evidence package will succeed with Amex — they should supplement with additional documentation.
