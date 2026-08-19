---
title: "Best Practices for Retail Merchants — Chargeback Prevention and Defense"
category: Best Practices
doc_type: industry-guide
industry: Retail, E-Commerce (Physical Goods)
audience: merchants
last_updated: 2026-06-01
tags: [retail, physical goods, return fraud, point of sale, best practices, chargeback]
---

# Best Practices for Retail Merchants: Chargeback Prevention and Defense

## Unique Challenges for Retail Merchants

Physical goods retail — both brick-and-mortar and e-commerce — faces a specific set of chargeback challenges distinct from digital goods or service merchants:

- **Delivery disputes:** "I never received it" is the most common retail chargeback, requiring carrier-level proof of delivery.
- **Merchandise condition disputes:** "Not as described" or "arrived damaged" chargebacks require evidence of what was shipped.
- **Return fraud:** Customers exploit liberal return policies by keeping goods and disputing the charge, or by returning different items while keeping the original.
- **High transaction volumes:** Retail merchants processing thousands of orders per month cannot custom-review every chargeback — they need scalable evidence systems.
- **Seasonal spikes:** Holiday volumes create shipment delays and delivery exceptions that drive "not received" chargebacks 60–120 days later.

---

## Evidence to Capture at Point of Sale (In-Store)

For card-present retail transactions, the chargeback risk is lower (EMV chip provides liability shift for fraud), but disputes still occur for "not as described" and return-related claims. Capture at POS:

- **EMV chip read:** Always use the chip reader, not the magnetic stripe swipe, for chip-enabled cards. This secures the liability shift for fraud disputes.
- **Signed receipt:** For transactions above your signature threshold ($50 is common), require signature. The signed receipt is evidence in "not authorized" disputes.
- **Receipt with itemized description:** Print a receipt that includes the item name, SKU, price, and return policy. This addresses "not as described" claims where the customer cannot dispute what they signed for.
- **Photo ID for high-value purchases:** For transactions above a defined threshold (e.g., $500), require and log the presentation of photo ID. This is not a card network requirement but a merchant risk measure.
- **Return policy disclosure at POS:** Print the return policy on the receipt and have it posted at the point of sale. Verbal disclosure is insufficient — physical evidence of disclosure is necessary.

---

## Evidence to Capture for E-Commerce Orders

For online retail, build these capture events into your order processing workflow:

| Capture Event | System | Evidence Type |
|---|---|---|
| Order placement | Payment gateway / OMS | Authorization record (auth code, AVS, CVV) |
| Order placement | Fraud platform | IP address, device fingerprint, geolocation |
| Order placement | Email platform | Order confirmation email (sent record + timestamp) |
| Item picking | Warehouse system | Packing slip with SKU and quantity |
| Item packing | Warehouse | Photograph of item(s) before sealing (for high-value orders) |
| Shipment creation | Carrier / OMS | Tracking number assigned |
| Carrier pickup | Carrier API | Carrier intake confirmation |
| Delivery | Carrier webhook | Delivery timestamp, GPS coordinates, delivery photo |

---

## Carrier Selection and Service Level Policy

Carrier and service level choices directly affect your chargeback exposure:

- **High-value orders ($200+):** Require signature confirmation. The carrier signature is the gold standard for "not received" defense.
- **Mid-value orders ($50–$200):** Standard tracked service. GPS-verified delivery confirmation is sufficient in most cases.
- **Low-value orders (under $50):** Standard mail or flat-rate tracked. Chargeback economics may not justify signature cost.
- **Geographic risk:** Certain zip codes or apartment complexes have high package theft rates. Flag these for signature requirement regardless of order value.
- **Carrier selection:** Use carriers that provide delivery photos (FedEx, UPS both offer photo delivery on many residential routes). This adds significant defense value without requiring the customer to be present.

---

## Return Policy Design to Reduce Chargebacks

A clearly disclosed, accessible return policy reduces "not as described" and general dissatisfaction chargebacks by giving customers an alternative to the bank dispute:

- **Display the return policy on every product page, at checkout, and in the order confirmation email.**
- **Offer a minimum 30-day return window.** Consumers who feel they have time to return an item are less likely to immediately dispute. Restrictive policies (7-day returns) create urgency that pushes customers to the bank.
- **Make returns easy:** A pre-paid return label or a portal (returnly.com, loop returns) removes friction and gives you control of the process.
- **Document return requests:** When a customer submits a return request, the CRM record is evidence that they attempted to use your return process — and if they later file a chargeback having never contacted you, that is evidence of chargeback abuse.

---

## Return Fraud Prevention

Return fraud — keeping the original item and returning an empty box, wrong item, or used/damaged item — is distinct from chargeback fraud but often connected:

- **Photograph items before shipping:** For any item above your photo threshold, capture a date-stamped image of the packaged item showing the serial number or UPC.
- **Require original packaging for returns:** Reduces "I returned it in the original box" fraud where a different item is inserted.
- **Weight verification at return receipt:** Log the weight of returned packages. A returned "empty box" weighs less than the original.
- **Inspect returns immediately:** Document the condition of returned items with photos and log the inspection in your CRM. If the returned item does not match the original shipment, dispute the refund.
- **Serial number tracking:** For electronics, log serial numbers at shipment and verify at return. A different serial number proves a substitute was returned.

---

## High-Value Item Procedures

For retail orders above a defined high-value threshold (e.g., $500):

1. **Manual review before shipment:** Human review of order details, IP geolocation, billing/shipping address match, and card BIN type.
2. **Pre-shipment customer verification:** Call or email the customer to confirm the order before shipping expensive items. Document the confirmation.
3. **Adult signature required:** Require the recipient to be physically present to accept the package, not just any available signature.
4. **Insurance:** Purchase carrier insurance for the shipment value. In a worst-case scenario, carrier insurance provides a recovery path even if the chargeback is lost.
5. **Split shipment documentation:** If shipping multiple items across shipments, document each shipment's tracking number and delivered status individually.

---

## Chargeback Defense Reference for Common Retail Codes

| Reason Code | Common Scenario | Key Evidence |
|---|---|---|
| Visa 10.4 / MC 4837 | Online purchase disputed as fraud | Auth record (AVS Y, CVV M), carrier tracking, device/IP report |
| Visa 13.1 / MC 4855 | "I never got it" | Carrier tracking showing "Delivered," delivery photo, address confirmation |
| Visa 13.3 | "Not what I ordered" | Product listing screenshot, packing slip, fulfillment photo, return policy |
| Visa 13.2 | Subscription charge disputed | CRM no-cancel-log, policy screenshot, billing history |

---

## Seasonal and High-Volume Period Planning

During peak periods (Black Friday, Cyber Monday, holiday season), chargeback volumes spike 60–120 days later:

- **Pre-peak evidence infrastructure audit:** Confirm that all delivery webhook integrations, IP logging, and email delivery tracking are functioning before peak season.
- **Extended carrier SLA awareness:** Communicate realistic delivery estimates during peak periods. A customer expecting 3-day delivery who receives their order in 8 days is an unhappy customer who may dispute.
- **Staff the response queue in January/February:** Holiday chargebacks arrive in December–February. Ensure chargeback response capacity matches the increased volume.
- **Seasonal carrier partnerships:** Engage carriers who provide enhanced tracking and delivery confirmation for peak-period volumes.
