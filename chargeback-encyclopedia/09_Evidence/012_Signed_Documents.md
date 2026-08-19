---
title: "Signed Agreements and Contracts"
section: "09_Evidence"
category: "Evidence Library"
document_type: "Evidence Reference"
keywords: ["signed documents", "terms and conditions", "electronic signature", "DocuSign", "cancellation policy", "subscription consent", "hotel registration", "rental agreement", "digital consent"]
difficulty: "Intermediate"
---

# Signed Agreements and Contracts

## Why Signed Documents Are Critical Evidence

A signed agreement is documentary proof that a cardholder knowingly accepted specific terms and conditions at a defined point in time. In chargeback defense, signed documents answer the issuer's fundamental question: "Did the cardholder understand what they were agreeing to?"

For disputes involving cancelled services, subscription billing, service quality, hotel cancellation charges, or rental agreements — where the cardholder claims they did not agree to the terms — a signed agreement is often the single most important piece of evidence in your package. It moves the dispute from "merchant says vs. cardholder says" to "here is what the cardholder signed."

Signed documents are also critical for preventing disputes in the first place. Clear written agreements — including cancellation and refund policies — reduce the frequency of disputes based on "I didn't know" arguments.

## Types of Signed Agreements in Merchant Contexts

### Terms and Conditions Agreements

Online terms of service accepted during account creation or checkout are binding agreements when properly presented and captured. The legal enforceability varies by jurisdiction, but for chargeback defense purposes, issuers accept T&C acceptance records as evidence of cardholder knowledge and agreement.

**What must be captured:**
- The exact text of the terms accepted (snapshot of the T&C version at time of acceptance).
- Timestamp of acceptance (date, time, timezone — must match your server logs).
- IP address from which acceptance was made.
- How acceptance was indicated (checkbox, button click, scrolled-to bottom).
- The cardholder's account identifier (email, user ID) associated with the acceptance.

**Best practice — version control:** If your terms change over time, maintain version history with effective dates. When submitting evidence, always provide the version of the terms the cardholder accepted — not your current terms, which may have been updated since the cardholder enrolled.

### Cancellation Policy Acknowledgment

For subscription services, hotels, rental agreements, and service contracts, a specific cancellation policy acknowledgment (separate from or highlighted within the general T&C) is the most relevant document for cancellation-related disputes.

The cancellation policy must state clearly:
- How much notice is required to cancel (e.g., 24 hours before check-in, 30 days before renewal).
- What the penalty is for late cancellation (e.g., first night's room charge, full subscription period).
- How to cancel (specific instructions, contact method, cancellation link).

**Dispute relevance:** A cardholder disputing a hotel cancellation charge under "merchant did not disclose cancellation policy" is directly refuted by a signed registration card (or checkout acceptance) acknowledging the cancellation policy they agreed to at booking.

### Rental Agreements

Car rental, equipment rental, event space rental, and short-term accommodation rental agreements define the terms of the rental — including damage liability, insurance requirements, fuel policies, and late return fees.

When a cardholder disputes additional charges (damage fees, late return, fuel surcharge), the signed rental agreement is the primary defense. It documents exactly what the cardholder agreed to be responsible for.

**For car rental specifically:**
- Pre-rental inspection record (vehicle condition at pickup, signed by cardholder).
- Post-rental inspection record (vehicle condition at return, signed by the rental agent).
- Fuel level at pickup vs. return.
- Rental agreement page showing the cardholder initialed or signed the damage and fuel policy.

### Hotel Registration Cards

Hotel check-in registration cards are signed agreements that record:
- Cardholder name and signature.
- Check-in date and expected check-out date.
- Room rate per night.
- Cancellation policy.
- Authorization for incidental charges.
- Policy on additional charges (parking, room service, minibar).

When a cardholder disputes hotel charges — particularly incidental charges or cancellation penalties — the signed registration card is the starting evidence. It proves the cardholder was physically present, saw the charges, and agreed to the terms.

For disputes involving disputed room rates or unexpected charges, compare the signed registration card rate to the billed amount and explain any authorized rate differences.

### Subscription Consent Checkboxes (With Timestamp and IP)

E-commerce subscription sign-ups increasingly use explicit consent checkboxes rather than buried terms:

**Strong consent implementation:**
- A checkbox that is NOT pre-checked (the cardholder must actively check it).
- Text adjacent to the checkbox that clearly states the subscription terms: "By checking this box, you agree to a monthly subscription of $29.99/month, billed on the same date each month. Cancel anytime by visiting [URL]."
- Server-side recording of when the checkbox was checked (timestamp), from what IP address, and in what browser session.

**Evidentiary value:** For subscription disputes (Visa 13.2, Mastercard 4853), a server-side log showing the consent checkbox was checked — with timestamp, IP, and account association — directly addresses the claim that the cardholder did not agree to recurring billing.

In your dispute rebuttal: "The cardholder checked the subscription consent checkbox at [timestamp] from IP address [X], indicating explicit agreement to monthly recurring billing of $29.99/month, as shown in Exhibit C (consent log record) and Exhibit D (screenshot of sign-up page with consent language)."

### Invoice with Customer Signature

For B2B transactions or high-value consumer transactions, a signed invoice is the strongest form of written authorization. The cardholder's signature on an invoice acknowledging the transaction amount and goods/services is difficult to dispute.

**For B2B merchants:** Signed purchase orders, statements of work, and invoices with physical or electronic signatures are your primary authorization evidence. Even for credit card payments, a signed invoice confirms the cardholder's organization agreed to the purchase.

### Signed Delivery Receipts

A delivery receipt signed by the cardholder at the time of delivery is a form of signed document proving both delivery and acknowledgment of receipt. This is distinct from carrier tracking POD (which shows a carrier scan or an anonymous signature) because it involves the cardholder's own signature confirming receipt of the specific goods.

For high-value goods delivered in person (furniture, large appliances, custom orders with personal delivery), requiring a signed delivery receipt form is valuable dispute protection.

## Electronic Signatures: DocuSign, AdobeSign, and Similar Services

Electronic signatures (e-signatures) generated through DocuSign, AdobeSign, PandaDoc, HelloSign, or similar platforms are legally binding under the U.S. ESIGN Act (2000), UETA, and equivalent international laws (EU eIDAS Regulation).

**What e-signature platforms provide as evidence:**
- **Audit trail:** A complete, tamper-evident log of every action taken on the document — who opened it, when, from what IP, when they signed, and the exact signature applied.
- **Certificate of completion:** A document generated by the platform certifying all signatories completed their signing. This is a third-party verification, not just a merchant assertion.
- **Signed document archive:** The signed PDF with embedded signature data, the timestamp of signing, and the signer's email address associated with the signature.

**DocuSign Certificate of Completion specifically:** DocuSign provides a "Certificate of Completion" document as an appendix to every signed agreement. This certificate includes:
- Document title.
- Envelope ID (unique document identifier).
- Signatory name, email, and timestamp.
- IP address at time of signing.
- Security level of authentication used (email authentication, ID verification, etc.).

This certificate is third-party certified and extremely credible with issuers because DocuSign is a recognized, reputable platform. Include both the signed document and the Certificate of Completion as a single exhibit.

## When Digital Consent Is Accepted by Issuers

Issuers review electronic consent evidence by asking:
1. Was the consent mechanism clear and unambiguous?
2. Was the consent record generated at the time of the cardholder's action (contemporaneous)?
3. Is there a reliable record linking the cardholder to the consent action?

**Accepted formats:**
- DocuSign/AdobeSign Certificate of Completion (strong — third-party certified).
- Server-side consent log with timestamp, IP, account ID, and T&C version (accepted — provides context).
- Screenshot of consent checkbox page with a corresponding log record (accepted when both elements are present).

**Not accepted or weak:**
- Screenshot of a consent page without a corresponding server-side log proving the cardholder actually checked the box.
- Oral representation that the cardholder agreed to terms (without documentation).
- A link to current T&C without proof that the cardholder saw or accepted the specific version.

## Presenting Signed Documents as Chargeback Evidence

**Physical documents (hotel cards, rental agreements):** Scan at 300 DPI minimum. Include the entire document — do not crop out any section. Highlight the signature, the cardholder's name, and the specific policy language (cancellation terms, rate agreed upon) that is relevant to the dispute.

**Electronic records:** Include both the document itself and the consent/signature record. For DocuSign: include the signed PDF and the Certificate of Completion. For server-side consent: include a screenshot of the sign-up page and the relevant consent log record (formatted as in 008_Login_and_Usage_Logs.md guidance).

**In your rebuttal letter:** Reference the signed document exhibit and quote the specific provision: "As shown in Exhibit D, the cardholder signed the hotel registration card on [date] acknowledging the 48-hour cancellation policy. The cancellation was received [X hours] after check-in, outside the cancellation window. The disputed charge represents the cancellation fee disclosed in the signed agreement."

## Summary

Signed agreements — whether physical hotel registration cards, electronic subscription consent records, or DocuSign-certified contracts — provide documentary proof that the cardholder knowingly agreed to the terms now in dispute. For any chargeback involving cancellation fees, service quality, subscription billing, or recurring charges, locating and presenting the signed agreement is the first priority. Electronic consent documentation (checkbox records, e-signature certificates) is accepted by issuers when it is clearly timestamped, linked to the cardholder's account, and accompanied by the specific consent language shown to the cardholder. Strong signed document evidence, combined with the technical and communication evidence described in the rest of this library, builds a complete and compelling chargeback rebuttal.
