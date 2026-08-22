---
title: "NPCI U005 — Fraudulent Transaction"
section: "07_RuPay"
category: "RuPay / NPCI Reason Codes"
network: "RuPay / NPCI"
reason_code: "U005"
document_type: "Reason Code Reference"
keywords: ["NPCI", "UPI", "fraud", "U005", "social engineering", "vishing", "QR code fraud", "fake merchant"]
difficulty: "Intermediate"
---

# NPCI U005 — Fraudulent Transaction

## Overview

U005 is NPCI's broad fraud classification code, applied when a UPI transaction is disputed as fraudulent but does not fit the narrower U001 definition (where the customer had no involvement whatsoever). Under U005, the customer may have initiated the payment but was deceived into doing so by a third party — through social engineering, impersonation, or fake merchant setups.

This distinction matters: U001 is pure unauthorized access (someone else used the customer's UPI PIN), while U005 covers cases where the customer actively participated but was manipulated. Both result in a chargeback, but the liability determination differs.

## Common Scenarios

**Social engineering / vishing**: Fraudsters call customers impersonating bank officials, NPCI representatives, or customer service agents. They convince the customer to approve a UPI collect request or make a payment to "verify" their account or receive a prize. Once approved, the money is gone.

**Fake merchant QR codes**: Physical QR codes at shops, parking meters, or market stalls are replaced with fraudster-controlled codes. Customer scans and pays thinking they are paying the legitimate merchant. The real merchant never receives the money.

**Marketplace impersonation**: On platforms like OLX or Facebook Marketplace, fraudsters pose as sellers. Customer pays via UPI for goods that never arrive. The "merchant" VPA belongs to the fraudster, not a real business.

**Fake refund / reversal scam**: Customer is told they are receiving a refund and asked to approve a UPI collect request — which is actually a debit. Customer approves thinking it is a credit.

**Screen sharing fraud**: Fraudster convinces customer to install a remote access app (TeamViewer, AnyDesk) under the guise of helping with a UPI issue, then initiates payments while watching the screen.

## Merchant Liability

For **legitimate merchants** (registered businesses with proper VPA), liability under U005 is generally low. NPCI's investigation focuses on the beneficiary VPA — if the receiving account belongs to a genuine, KYC-compliant merchant, and goods or services were actually delivered, the merchant is typically not held liable.

Liability falls on the **merchant when**:
- The merchant's QR code or VPA was advertised incorrectly and caused customer confusion
- Merchant staff participated in the fraud
- Merchant has a pattern of U005 disputes suggesting a scheme

Liability falls on the **bank / fraudster when**:
- A third party impersonated a legitimate merchant
- The customer was deceived by a fraudster using a spoofed or fake VPA

## Required Evidence (for legitimate merchants)

- NPCI transaction reference (UTR number) confirming funds were received into the correct merchant VPA
- Order fulfillment records (invoice, delivery confirmation, service completion)
- Merchant registration documents (GST registration, NPCI merchant onboarding records)
- Customer communication records (any interaction with the actual customer before the disputed transaction)
- Proof that the VPA belongs to the registered merchant entity

## What NPCI Investigates

NPCI's fraud investigation under U005 typically examines:
1. **Beneficiary VPA ownership** — Is the receiving VPA KYC-compliant and linked to a real business?
2. **Transaction pattern** — Is this VPA associated with multiple fraud complaints?
3. **Device and IP at transaction** — Was the collect request sent from a suspicious device or location?
4. **UPI app interaction** — Did the customer approve a collect request (pull) or initiate a push payment? (Collect request fraud is more likely to succeed for fraudsters)

## Winning Strategy for Legitimate Merchants

1. **Provide complete order records** showing goods or services were delivered to the customer who matches the VPA/phone number
2. **Show VPA legitimacy** — merchant is properly registered, KYC-compliant, no prior fraud flags
3. **Demonstrate no contact with the complainant** — if the customer was deceived by a fraudster, the real merchant had no interaction with the complainant customer at all
4. **Respond promptly** — within the 30-day NPCI window; late responses are treated as acceptance

## Common Mistakes

- Ignoring U005 disputes because "it wasn't our fraud" — even legitimate merchants must respond formally
- Failing to provide order/delivery evidence — NPCI needs to confirm goods were delivered to establish the real merchant is not the fraudster
- Not reporting if your VPA or QR code was spoofed — you are also a victim and should file a complaint with NPCI and your acquiring bank

## Timeline

| Milestone | Timeframe |
|-----------|-----------|
| Customer reports to bank | Within 3 days for zero-liability protection |
| Bank files with NPCI | Within 7 days of customer complaint |
| Merchant response window | 30 days from NPCI notification |
| Bank resolution mandate | 30 days from complaint filing |
| Escalation to RBI Ombudsman | If unresolved after 30 days |

<!-- NEEDS VERIFICATION: every figure in this table needs checking against real NPCI documentation — the "3 days for zero-liability protection" framing in particular reads as an analogy to card-network zero-liability provisions rather than a confirmed NPCI-specific rule, and should not be treated as established fact without a source check -->

## FAQs

**Q: If a fraudster used a fake QR code impersonating my business, am I liable?**
No — you are a victim too. Report immediately to your acquiring bank and NPCI. The fraudster's VPA (which is different from yours) is the target of the investigation.

**Q: What if the customer claims they paid me but I have no record of receiving funds?**
If your bank account shows no credit for the UTR provided, the payment likely went to a fraudster's VPA. Request the NPCI transaction settlement record to identify the actual beneficiary.

**Q: How is U005 different from U001?**
U001 means the transaction was entirely unauthorized — the customer did not interact with it at all (someone else used their credentials). U005 means the customer initiated or approved the transaction but was deceived into doing so. Both are fraud, but the investigation path differs.

**Q: Can a repeat pattern of U005 disputes get my merchant account flagged?**
Yes. Multiple U005 disputes against the same VPA will trigger NPCI and acquiring bank scrutiny, even if each individual dispute is resolved. Maintain clean dispute records and ensure your QR codes and VPAs are not being spoofed.

## Key Takeaways

- U005 is fraud involving deception — the customer participated but was manipulated
- Legitimate merchants are rarely liable if they can prove delivery and VPA legitimacy
- NPCI investigates the beneficiary VPA, not just the customer complaint
- Respond within 30 days with order and delivery evidence
- If your VPA is being impersonated, report it immediately — you are also a fraud victim
