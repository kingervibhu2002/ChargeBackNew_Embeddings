---
title: "Visa 13.1 — Merchandise/Services Not Received"
section: "04_Visa"
category: "Visa Reason Codes"
document_type: "Reference"
keywords: ["Visa 13.1", "not received chargeback", "merchandise not received", "delivery dispute", "tracking number chargeback", "digital goods dispute", "services not received", "CE3.0 Visa", "non-delivery chargeback"]
difficulty: "Beginner"
---

# Visa 13.1 — Merchandise/Services Not Received

Visa reason code 13.1 is the most common consumer dispute reason code in e-commerce. When a cardholder claims they paid for something and never received it — whether a physical product, a digital download, or a service — this is the code the issuer uses. Winning 13.1 disputes requires specific, delivery-focused evidence. The strength of your delivery documentation directly determines whether you recover the revenue or absorb the loss.

## What This Chargeback Means

A 13.1 chargeback means the cardholder is telling their bank: "I paid for this item or service, but I never received it, or it arrived outside the timeframe the merchant promised, and the merchant has not issued a refund."

The cardholder's claim can arise from genuinely non-delivered goods, goods delivered to the wrong address, stolen packages, or — in many cases — friendly fraud (where the goods were received but the cardholder denies receipt to obtain both the product and a refund). Distinguishing between genuine non-delivery and friendly fraud determines your evidence strategy.

## Physical Goods: Building Your Evidence Package

### Carrier Tracking Number and Delivery Confirmation

The most important single piece of evidence for a physical goods 13.1 dispute is carrier tracking data showing delivery at the cardholder's address.

**What you need:**
- Carrier tracking number and carrier name (UPS, FedEx, USPS, DHL, etc.)
- Tracking event history showing the package progressed from origin to the cardholder's address
- Delivery confirmation event: "Delivered — [Address]" with a timestamp

Tracking that ends at a sorting facility or shows "Out for Delivery" without a final delivered scan is insufficient — it establishes that you shipped the item, not that it was delivered. You need the delivery confirmation.

### Signature Confirmation

For high-value items, signature capture at delivery is powerful evidence. If the carrier obtained a signature at the delivery address, provide:
- The signature capture image or signature name
- The delivery confirmation showing the signature was obtained

A cardholder who signed for a package and then files a 13.1 chargeback has a very difficult position — their own signature refutes the non-receipt claim.

### GPS-Stamped Photo at Door (Proof of Delivery)

Many carriers (FedEx, UPS, USPS, Amazon Logistics) now provide photo-at-door confirmation — a timestamped photograph of the package placed at the delivery address. This visual evidence placed at the specific delivery address is compelling even without a signature.

Provide the carrier's proof-of-delivery image in your representment package.

### When the Delivery Address Differs from the Billing Address

If the customer requested delivery to an address different from their billing address (a gift, a work delivery), note this explicitly in your rebuttal letter. Include the order confirmation showing the customer specified the alternate delivery address and confirmation that delivery occurred at that requested address.

Delivery to an address different from billing is not unusual and does not automatically support a non-receipt claim — the cardholder specified that address.

## Digital Goods: Building Your Evidence Package

For digital goods (software licenses, streaming access, downloadable files, activation keys, game credits), the "delivery" evidence looks different from physical goods.

### Download Logs With IP Address and Timestamp
Server logs showing the specific digital good was downloaded from the same IP address used during the checkout process, at a timestamp after the purchase, are strong evidence. Include:
- IP address at download
- Timestamp of download event
- File or product identifier downloaded
- Device type or browser fingerprint if available

### Activation or Account Access Records
If the digital product requires account creation or activation (software with a license key, streaming subscription, SaaS platform), show that the account was activated and used after the purchase:
- Account creation timestamp (matching the cardholder's email)
- Login records after the purchase date
- Feature usage metrics post-purchase

### Email Delivery Logs
Email service provider logs showing the delivery confirmation email, activation link, or digital product was successfully delivered to the cardholder's email address, including:
- Recipient email address
- Sent timestamp
- Delivery status (delivered, not bounced)
- Open event (if tracked) showing the email was opened

## Services: Building Your Evidence Package

For services (consulting, repair, subscriptions, professional services), evidence of completion is required.

### Service Completion Records
- Signed work order or service agreement
- Service completion report signed by the customer or customer representative
- Milestone sign-offs in a project management system
- Job completion photos (for physical service work such as installations, repairs)

### Communications Showing Service Was Delivered
- Email threads showing deliverables were sent and acknowledged
- Meeting or session records
- Timesheets or billing records with customer acknowledgment

## Timeframe Disputes: Promised Delivery Window

A 13.1 chargeback can also be filed when the cardholder received the item, but it arrived later than the merchant promised — and the cardholder had already disputed because the promise was not kept.

In this scenario:
- Provide your stated delivery timeframe (from the product page or order confirmation email)
- Provide the actual delivery date from carrier tracking
- If delivery was within the promised window, you win this dispute
- If delivery was outside the promised window, assess whether to fight or offer a partial resolution

## Visa CE3.0 Application for 13.1

Visa's Compelling Evidence 3.0 framework applies to 13.1 disputes. If you can demonstrate that the same cardholder (matching device ID, IP address, shipping address, or login credentials across at least two data points) made prior undisputed purchases from your business between 120 and 365 days before the disputed transaction, you can use those prior transactions as evidence of a legitimate customer relationship — strengthening your position that the current "non-receipt" claim is not credible given the history.

## When to Issue a Refund vs. Fight

### Issue a Refund When:
- You cannot produce carrier tracking showing delivery to the cardholder's address
- The item was delivered to the wrong address due to a merchant error
- The shipping address on the order was wrong and you shipped to it anyway
- Carrier tracking confirms the package was lost in transit

### Fight the Chargeback When:
- You have carrier tracking confirming delivery to the cardholder's specified address
- Signature confirmation or photo-at-door is available
- Download logs or activation records confirm digital goods were accessed
- The customer has made prior undisputed purchases (CE3.0 pattern of behavior)

---

## Frequently Asked Questions

**Q: Carrier tracking shows delivered but the customer says the package was stolen. Who wins?**
A: This is one of the gray areas in 13.1 disputes. If you have delivery confirmation at the cardholder's address, you have met the standard delivery evidence requirement. However, issuers sometimes side with the cardholder on stolen-from-doorstep claims even when delivery is confirmed, particularly without signature or photo evidence. For high-value items, require signature upon delivery — it materially increases your win rate on delivery disputes.

**Q: Can I fight a 13.1 if I never shipped because the order was out of stock?**
A: No. If you never shipped the item, the cardholder's 13.1 claim is valid and you should accept the chargeback and issue a refund. Additionally, if you knew the item was out of stock and did not notify the customer, you may face additional scrutiny. Always notify customers of out-of-stock situations immediately and issue refunds without waiting for a chargeback.

**Q: The tracking shows delivered, but to a city 200 miles from the cardholder's billing address. Can I still fight?**
A: Review the order carefully. If the cardholder specifically requested delivery to that address at checkout, you have a valid argument — submit the order confirmation showing they specified that delivery address. If you shipped to the wrong address due to an error on your part, accept the chargeback, correct the shipping error, and improve your address verification process.

**Q: My digital product requires no account creation — it is just a file download. How do I prove delivery?**
A: Server-side download logs are your primary evidence. Ensure your delivery system logs the IP address, timestamp, and user identifier for every download. If your platform does not currently log this, it is a critical gap — implement logging immediately. Without download logs, digital goods disputes are very difficult to win.

**Q: A customer filed a 13.1 chargeback before the estimated delivery window closed. Is this valid?**
A: This is a premature dispute. If your order confirmation clearly stated an estimated delivery window and the cardholder filed before that window expired, submit the order confirmation and the stated delivery timeframe as evidence. Note in your rebuttal letter that the dispute was filed before the promised delivery date, making the non-receipt claim premature. This is a strong defense.
