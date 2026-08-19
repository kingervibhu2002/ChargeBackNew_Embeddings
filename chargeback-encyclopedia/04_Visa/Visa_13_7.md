---
title: "Visa 13.7 — Cancelled Merchandise/Services (Non-Recurring)"
section: "04_Visa"
category: "Visa Reason Codes"
document_type: "Reference"
keywords: ["Visa 13.7", "cancelled order chargeback", "cancelled merchandise", "order cancellation dispute", "non-recurring cancellation", "Visa consumer dispute", "already shipped chargeback", "digital goods cancellation"]
difficulty: "Beginner"
---

# Visa 13.7 — Cancelled Merchandise/Services (Non-Recurring)

Visa reason code 13.7 applies when a cardholder cancels a one-time order or service — not a recurring subscription — and the merchant charges them anyway, or charges them after the cancellation was made. This is the non-recurring counterpart to 13.2 (Cancelled Recurring Transaction). Understanding the distinction is important because the evidence requirements and the edge cases — particularly around items that were already shipped — differ significantly.

## What This Chargeback Means

A 13.7 chargeback is the cardholder asserting: "I cancelled this order (or service) before it was fulfilled, but the merchant still charged me."

This applies to:

- **Single-purchase orders cancelled before shipment:** The cardholder placed an order and then cancelled it through the merchant's cancellation process, but the charge still appears on their statement.
- **Service bookings cancelled in advance:** A one-time service appointment (a hotel reservation, a contractor booking, a photography session) was cancelled within the allowed cancellation window, but the merchant still charged a cancellation fee or the full amount.
- **Digital goods orders cancelled before delivery:** A digital product order (a software purchase, a digital download) was cancelled before the download link was sent or the license was activated.
- **Pre-orders cancelled before the item ships:** The cardholder placed a pre-order for an upcoming product and cancelled it before the item shipped or was released.

## The Critical Distinction from Visa 13.2

Understanding the boundary between 13.2 and 13.7 is essential:

| Aspect | Visa 13.2 | Visa 13.7 |
|---|---|---|
| Type of billing | Recurring subscription/recurring charge | One-time purchase or service booking |
| Pattern | Ongoing billing that should have stopped | Single charge that should not have happened |
| Common examples | Netflix subscription, SaaS monthly plan, gym membership | Hotel booking, one-time course purchase, a single product order |

If the dispute involves a subscription or any form of recurring charge, 13.2 is the applicable code. If it involves a single purchase, booking, or order, 13.7 applies.

## The "Already Shipped" Complication

The most complex scenario in 13.7 disputes is when the cardholder cancelled an order, but the merchant had already shipped the item before receiving the cancellation notice. This creates a genuine conflict between the cardholder's cancellation right and the merchant's fulfillment reality.

### When the Item Was Shipped Before Cancellation
If you shipped the item before the cardholder submitted their cancellation request — and you can document this with a carrier pickup timestamp that predates the cancellation notice — the chargeback may not be valid. You fulfilled the order in good faith before the cancellation was received.

**Evidence to submit:**
- Order timestamp showing when the order was placed
- Carrier pickup/scan timestamp showing when the package was handed to the carrier (predating the cancellation request)
- The cardholder's cancellation request timestamp (email, portal log, chat)
- Your cancellation policy stating that orders already shipped cannot be cancelled (if this is your policy)

### When the Cardholder Refuses to Return the Shipped Item
If the item was shipped after a valid cancellation (or if the cardholder rejects the shipment and it is returned to you), the refund should be issued upon return. If the cardholder is keeping the item and disputing the charge, the dispute becomes more complex — the cardholder may need to return the item as a condition of the chargeback resolution.

### Your Cancellation Policy and Its Enforceability
A clearly stated, pre-purchase-disclosed cancellation policy that defines the point of no return (e.g., "Orders cannot be cancelled after they enter the packing process") is relevant evidence. If the cardholder purchased after seeing this policy and then attempts to cancel after the stated cutoff, you can cite the policy in your defense.

## Evidence You Need to Fight a 13.7

### Proof No Cancellation Request Was Received
If the cardholder claims they cancelled but no cancellation request exists in your system:
- Customer portal activity logs showing no cancellation action was taken
- CRM records showing the account/order status as active on the charge date
- Order management system records showing the order was fulfilled without any cancellation flag

### Cancellation Confirmation (or Lack Thereof)
A well-designed order management system should generate a cancellation confirmation email whenever a cancellation is successfully submitted. If the cardholder cannot produce a cancellation confirmation and your system has no record of the cancellation, this is strong evidence the cancellation was not made.

### Cancellation Policy as Displayed at Time of Purchase
Submit a screenshot or archived version of your cancellation policy as displayed on your product page or checkout:
- Order cutoff times after which cancellation is no longer possible
- Service cancellation notice requirements (e.g., "Hotel cancellations must be made 48 hours before check-in")
- Non-refundable terms for certain purchase types

### Fulfilment Records Showing Timing
For the "already shipped" defense:
- Order entered: [timestamp]
- Order packed: [timestamp]
- Carrier pickup scan: [timestamp]
- Cancellation request received: [timestamp — must be later than carrier pickup to establish the order shipped before cancellation]

## Digital Goods: Unique Considerations

For digital products (software licenses, online courses, downloadable files), cancellation after delivery is particularly fraught because:

- The product can be consumed immediately after delivery
- Once a license is activated or a file is downloaded, the product cannot be meaningfully "returned"
- Some merchants implement "no cancellation after download" policies

Your cancellation policy for digital goods should clearly state whether cancellation is available after the download link is sent or the license is activated. If a cardholder activated a license and then filed a 13.7 chargeback, provide the activation record (timestamp showing activation before the cancellation claim) as evidence the product was used.

## When to Accept the Chargeback

Accept without fighting when:
- The cardholder cancelled through your standard process and you have a record of the cancellation but charged anyway (operational error — fix it)
- The cancellation was requested before shipment and the item had not yet shipped
- The service was cancelled within your published cancellation window
- Your customer service team verbally or in writing acknowledged the cancellation

---

## Frequently Asked Questions

**Q: A customer cancelled an order but I had already packed and labeled it. Is that too late to cancel?**
A: Packed and labeled but not yet handed to the carrier is typically not sufficient to defeat a cancellation. The meaningful point of no return is usually when the carrier takes physical possession of the package (reflected by the first carrier scan). An item packed in your warehouse can still be intercepted. If you can show the carrier scan timestamp predates the cancellation, you have a defense. If not, honor the cancellation and reroute or return the package.

**Q: My cancellation policy says no cancellations after 24 hours of purchase. The customer cancelled at hour 26. Can I enforce this?**
A: Reasonable cancellation cutoffs that were clearly disclosed before purchase are enforceable with issuers in representment. Submit the policy as it appeared at purchase alongside evidence that the cancellation was submitted outside the 24-hour window. Note that extremely short cancellation windows (under 24 hours) are scrutinized by card networks — Visa may not support a cancellation window that does not give customers a reasonable opportunity to change their mind.

**Q: A customer filed a 13.7 on a hotel booking. I charged a non-refundable deposit. Is that protected?**
A: Non-refundable bookings are defensible if the non-refundable terms were clearly disclosed before the cardholder completed the booking. Submit the booking confirmation and terms showing the non-refundable nature of the deposit. Note: non-refundable bookings cancelled due to documented extraordinary circumstances (medical emergencies, government travel restrictions) are sometimes reversed by issuers regardless of the merchant's policy — this is an area where acquirer guidance is valuable.

**Q: The customer bought a digital course, watched half the modules, and then filed a 13.7 saying they "cancelled" before completing it. What do I do?**
A: Submit your course access logs showing the cardholder accessed and consumed a substantial portion of the course content. Significant usage of a digital product before a cancellation claim significantly undermines the cancellation argument — the product was delivered and used. Also submit any "no refund after access" policy that was disclosed at enrollment.

**Q: What if the cardholder claims they cancelled via a phone call but I have no phone record of their call?**
A: If you have phone call logs showing no inbound call from the cardholder's registered phone number around the stated cancellation date, that is relevant evidence. Note it in your rebuttal. Also check if the cardholder could have called from a different number — search call logs broadly if the customer relationship is ambiguous. Without any corroboration of their claim and with no record in your system, the negative proof (absence of cancellation record) supports your position.
