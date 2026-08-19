---
title: "Proof of Delivery"
section: "09_Evidence"
category: "Evidence Library"
document_type: "Evidence Reference"
keywords: ["proof of delivery", "carrier tracking", "signature confirmation", "POD", "delivery evidence", "FedEx", "UPS", "USPS", "DHL", "digital goods delivery", "chargeback non-receipt"]
difficulty: "Beginner"
---

# Proof of Delivery

## Why Delivery Proof Is Central Evidence

For physical goods disputes filed under non-receipt codes (Visa 13.1, Mastercard 4855), proof of delivery is your primary — and often decisive — evidence. Without it, a merchant almost cannot win a non-receipt dispute regardless of how strong other evidence is. With it, a merchant can rebut a non-receipt claim directly and specifically.

Proof of delivery is also relevant in friendly fraud disputes where you want to establish that the cardholder received the goods they now claim were unauthorized. Combined with usage logs and prior purchase history, delivery confirmation completes the narrative: the cardholder ordered, received, and used the product.

This document covers all major forms of delivery proof for physical goods and digital goods, how to obtain official documentation from carriers, when signature confirmation is required, and how to handle international delivery evidence challenges.

## Types of Physical Goods Delivery Evidence

### Carrier Tracking

Every shipment via a major carrier (USPS, FedEx, UPS, DHL, and regional carriers) generates a tracking number that records the package journey from pickup to delivery. Basic carrier tracking is the minimum acceptable delivery evidence for most disputes.

**What tracking shows:**
- Acceptance date and location.
- Transit events (sort facility scans, carrier hub arrivals).
- Delivery date and time.
- Delivery location description ("Front Door," "Mailbox," "Signature Required").
- Delivery confirmation scan.

**Obtaining and presenting tracking:**
- Pull the full tracking detail page from the carrier's tracking portal.
- Take a screenshot or PDF of the complete tracking history, not just the final status.
- Include the tracking number, shipment date, and delivery date visually.
- Ensure the delivery address shown in the carrier record matches the cardholder's billing or shipping address.
- Highlight the delivery confirmation event.

Basic tracking ("Delivered" status) is sufficient for lower-value disputes. For high-value disputes, carriers' additional services provide stronger evidence.

### Signature Confirmation

Signature confirmation (FedEx: Signature Required, UPS: Signature Required, USPS: Signature Confirmation) requires the recipient to sign for the package at the time of delivery. The carrier records the signature and makes it available to the shipper.

**Obtaining signed Proof of Delivery (POD):**

- **FedEx:** Log into FedEx Reporting, navigate to "Proof of Delivery," enter the tracking number, and download the official POD letter. This includes the recipient's name (as signed), delivery date, and delivery address. FedEx POD letters are formally acceptable as legal documentation of delivery.
- **UPS:** Log into UPS Quantum View or UPS My Choice for Business. Download the Proof of Delivery document with signature image.
- **USPS:** Request a "Delivery Confirmation Signature" copy through the USPS Postal Inspector or business portal. USPS Adult Signature Required and Signature Confirmation services generate accessible signature records.
- **DHL:** Use the DHL Business Customer Portal to access Proof of Delivery documents with recipient signatures.

A signed POD document is significantly stronger than basic delivery tracking. It proves not only that the package arrived at an address, but that a human being signed for it — making the "I never received it" claim much less credible.

### GPS Confirmation and Photo-at-Door

Many carriers (FedEx, UPS, and their delivery personnel) now capture GPS coordinates and/or photographs at the time of delivery:

- **GPS confirmation:** The carrier's handheld device records GPS coordinates at the time of the delivery scan. This proves the carrier was at the delivery address, not just that a scan occurred at a remote facility.
- **Photo-at-door:** Increasingly standard practice. The carrier photographs the package at the delivery point (front door, reception desk, mailbox area). This image is time-stamped and GPS-stamped.
- **UPS Photo Delivery:** Available for select service levels; provides a photo of the delivered package at the delivery location.
- **Amazon Delivery Services:** Amazon's delivery network routinely captures delivery photos linked to specific orders.

Photo-at-door evidence is extremely compelling in non-receipt disputes because it is difficult to argue the package was not delivered when a time-stamped photograph shows it sitting at the delivery address.

## When Signature Confirmation Is Required

Network rules and best practices create thresholds above which signature confirmation is advisable:

- **Visa rules:** For disputes under 13.1 (Non-Receipt), merchants can compel the cardholder to provide a sworn statement of non-receipt for high-value items. Signature confirmation strengthens the merchant's position regardless.
- **Best practice threshold:** Most chargeback consultants recommend signature confirmation for orders above $200–$500. Your specific threshold should be based on your average chargeback rate and product category.
- **Cardholder request:** Some cardholders request signature confirmation at checkout. Honor these requests and document them.
- **High-risk addresses:** Any shipment to a freight forwarder, package reshipping service, or address flagged by your fraud system should include signature confirmation.

## Limitations of Delivery Proof

**Delivered to mailbox, not cardholder:** "Delivered to Mailbox" or "Left at Front Door" tracking is weaker than signed POD for high-value disputes. A cardholder can credibly argue the package was left unattended and stolen.

**Multi-unit buildings:** Delivery to a building lobby or mailroom rather than the specific unit is common in apartments and condominiums. This creates room for the argument that the cardholder never received the package from the building's internal delivery point.

**Triangulation fraud:** In triangulation fraud, the package was delivered to a valid address — but the legitimate cardholder was not the recipient (see 08_Fraud/005_Triangulation_Fraud.md). Delivery to the fraudster's designated recipient does not disprove the cardholder's claim.

**USPS vs. private couriers:** USPS tracking is generally less detailed than private courier tracking for higher-value shipments. For high-value goods, consider UPS or FedEx over USPS for the enhanced delivery documentation.

## International Delivery Evidence

International shipments present additional evidence challenges:

- **Customs clearance records:** For international shipments, customs clearance documentation confirms the package cleared customs at the destination country. This is supplementary delivery evidence even if final-mile tracking is less detailed.
- **Local carrier tracking:** Many international shipments transfer to local postal carriers for final-mile delivery. Obtain tracking from both the outbound carrier and the local carrier.
- **Commercial invoice:** Required for international shipments; documents what was shipped and its value. Include in evidence as proof of what was sent.
- **Country-specific carrier documentation:** DHL International, FedEx International, and UPS Worldwide provide POD documentation for many international destinations. Obtain and include these.

For high-value international shipments, consider requiring signature confirmation or requiring the customer to pick up from a carrier location, which provides the carrier's record of in-person pickup.

## Digital Goods Delivery Evidence

For digital goods (software, media, account access, downloads), there is no physical carrier tracking. Delivery evidence must be reconstructed from platform logs:

### Download Logs
- Record the IP address and timestamp of each download event.
- Record the user agent (browser/OS) of the downloading device.
- For unique download links: log when the link was first accessed, how many times, and from what IP.
- For streaming delivery: log the start time, duration, content accessed, and IP of each streaming session.

### Activation Records
- Record when a software license key was activated, on what machine (hardware fingerprint), from what IP, and at what timestamp.
- For SaaS: record account creation, initial login, and first feature use.
- For gaming: record character creation, first login, or first game session.

### Email Delivery Evidence
- Your order confirmation email, sent to the cardholder's email address, with a download link or access instructions, constitutes a form of delivery notice.
- Include the email send timestamp, recipient address, and (if available) email open and click events.

### Service Completion (Services Merchants)
For service businesses (consulting, custom work, website development):
- Signed work completion certificate.
- Client-approved deliverable submission record.
- Email from client acknowledging receipt or requesting revision (proves delivery and engagement).
- Time-tracking records showing service hours worked.

## Building Your Delivery Evidence Package

For a non-receipt dispute, your delivery evidence package should include:

1. **Order fulfillment record:** Shipping date, carrier, tracking number, and shipped-to address.
2. **Full tracking history:** All carrier scan events from pickup to delivery.
3. **Delivery confirmation:** The final delivery event, including delivery type (to door, mailbox, signature).
4. **Signed POD** (for high-value orders or signature-required shipments): Official carrier document.
5. **Photo-at-door** (if available): Carrier delivery photograph.
6. **Shipping address match:** Confirmation that the delivery address matches the cardholder's billing or approved shipping address.

Present these in a single exhibit, annotated with labels pointing to the delivery address match and delivery confirmation event.

## Summary

Proof of delivery is the cornerstone evidence for non-receipt chargebacks and an important supporting element for friendly fraud rebuttals. The hierarchy — from basic tracking to signed POD to GPS/photo confirmation — allows you to match evidence strength to dispute value. For high-value orders, invest in signature confirmation at shipping time; it is far cheaper than losing a $500+ dispute for lack of evidence. For digital goods, delivery proof must come from platform logs — download events, activation records, login timestamps — that must be built into your system architecture from the start.
