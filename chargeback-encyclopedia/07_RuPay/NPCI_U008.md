---
title: "NPCI U008 — Goods or Services Not Delivered"
section: "07_RuPay"
category: "RuPay / NPCI Reason Codes"
network: "RuPay / NPCI"
reason_code: "U008"
document_type: "Reason Code Reference"
keywords: ["NPCI", "UPI", "not delivered", "U008", "non-delivery", "goods", "services", "tracking"]
difficulty: "Intermediate"
---

# NPCI U008 — Goods or Services Not Delivered

## Overview

U008 is raised when a customer paid via UPI but the merchant did not deliver the purchased goods or services. Unlike U003 (system failure where merchant also didn't receive payment) or U006 (technical failure), U008 is a merchant fulfillment failure — the merchant received the payment but did not deliver.

This is the code where merchant liability is highest. NPCI expects merchants to either prove delivery or issue a refund. There is no technical defense — if the goods or services were genuinely not delivered, the merchant must refund.

## Common Scenarios

**Physical goods not shipped**: Customer paid for a product online. Merchant received payment but never dispatched the order.

**Order lost in transit**: Merchant shipped the order but it was lost by the courier. From NPCI's perspective, the customer did not receive the goods regardless of courier fault.

**Digital goods not delivered**: Customer paid for a software key, digital voucher, or downloadable content but received nothing — no email, no download link, no activation code.

**Service not rendered**: Customer paid for a service (cleaning, repair, consultation) that the merchant never provided.

**Partial delivery dispute**: Customer ordered 5 items, received 3. The undelivered portion triggers a U008.

**Delayed delivery beyond promised date**: Merchant promised 3-day delivery; 30 days later, goods haven't arrived. Customer files U008.

## Merchant Liability

Under U008, **the merchant is the primary liable party** if delivery cannot be proven. NPCI's position is straightforward: payment was made, goods/services should have been provided.

**Merchant wins when:**
- Delivery is confirmed with courier tracking showing delivery to correct address and/or signature
- Digital goods were delivered with timestamp, email record, IP at download, and activation logs
- Service was rendered with completion certificate, signed work order, or attendance/session records
- Customer accepted partial delivery and the remaining dispute amount is proportional

**Merchant loses when:**
- No tracking record exists
- Courier tracking shows delivery failed or returned to sender
- No digital delivery logs for digital goods
- Customer has written evidence from the merchant acknowledging non-delivery

## Required Evidence

### Physical Goods
- Courier tracking number with delivery confirmation (FedEx, Delhivery, Blue Dart, India Post, etc.)
- Signed POD (Proof of Delivery) if signature was required
- Dispatch/shipment confirmation (warehouse dispatch record, courier receipt)
- Customer's delivery address matching the order address

### Digital Goods
- Email delivery timestamp and recipient confirmation (email server logs)
- Download logs: timestamp, IP address, file name, file size
- Activation code generation and redemption record
- Account creation/access timestamp after purchase

### Services
- Signed work completion certificate
- Service report / job card
- Photo documentation (for physical services — repair, cleaning)
- Client sign-off or attendance confirmation
- Invoice marked as "Service Completed" with date

## Timeline

| Milestone | Timeframe |
|-----------|-----------|
| Customer files U008 with bank | Within 30 days of payment date |
| NPCI notifies merchant's bank | Within 7 days of customer complaint |
| Merchant response window | 30 days from notification |
| Bank resolution mandate | 30 days from complaint date |
| Refund if delivery unproven | Within 5-7 working days of resolution |
| RBI Ombudsman escalation | If unresolved after 30 days |

## Winning Strategy

1. **Provide complete delivery documentation** matched to the UTR/transaction: tracking number, customer address, delivery timestamp
2. **Correlate with order records**: show the UTR matches a specific order that was fulfilled — item ordered, quantity, shipping date
3. **For digital goods**: provide server-side logs, not just a screenshot — NPCI and banks accept logs, not just email copies
4. **If delivery failed due to courier**: still provide the shipping record; consider offering re-delivery or refund to close the dispute amicably
5. **Respond within 30 days**: late response = automatic loss; no extensions typically granted

## Common Mistakes

- **Relying solely on "we dispatched it"**: Dispatch records don't prove delivery. Get tracking with delivery confirmation.
- **No logging for digital goods**: Merchants who don't log downloads or activations have no defense for digital U008 disputes
- **Not capturing customer address verification at checkout**: Delivery to a wrong address is still non-delivery for dispute purposes
- **Waiting too long to respond**: 30 days passes quickly, especially for small merchants without dedicated dispute workflows

## Difference from U003

| Aspect | U003 | U008 |
|--------|------|------|
| Payment received by merchant? | No (system failure) | Yes |
| Customer debited? | Yes | Yes |
| Merchant fault? | No (technical failure) | Yes (non-fulfillment) |
| Resolution | Auto-reversal by bank | Merchant refund or delivery proof |

## FAQs

**Q: The courier lost my package — do I still lose the U008 dispute?**
From NPCI's perspective, if the customer didn't receive the goods, U008 is valid regardless of who lost the package. You may have a claim against the courier, but you need to refund the customer and pursue the courier separately. Consider shipping insurance for high-value orders.

**Q: Can I just submit the dispatch email as proof?**
Dispatch/shipment confirmation is helpful but not sufficient by itself. You need courier tracking with a confirmed delivery event. If your courier can't provide that, it weakens your defense.

**Q: The customer claims non-delivery but I have tracking showing delivered — what do I do?**
Submit the tracking page showing delivery to the customer's address and date. If the dispute continues, NPCI will contact the issuing bank to verify the customer's claim against the tracking data.

**Q: A customer filed U008 for a service I rendered. How do I prove service delivery?**
A signed completion certificate or job card is the strongest evidence. For time-based services (tutoring, consulting), session attendance records, meeting logs, or work output documents work well. Get a customer sign-off whenever possible.

## Key Takeaways

- U008 is a clear merchant-liability code: payment received, goods/services not delivered
- Winning requires definitive delivery proof matched to the specific UTR/order
- Physical goods: use tracked shipping with delivery confirmation for all UPI orders
- Digital goods: log every delivery event server-side (timestamp, IP, file, activation)
- Services: always obtain a signed completion record
- Respond within 30 days — no exceptions
