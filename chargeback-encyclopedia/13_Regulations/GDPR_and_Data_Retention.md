---
title: "GDPR and Data Retention for Chargeback Evidence"
category: Regulations
doc_type: regulation
audience: merchants
last_updated: 2026-06-01
tags: [GDPR, data retention, chargeback, PII, privacy, right to erasure, evidence]
---

# GDPR and Data Retention for Chargeback Evidence

## The Core Tension: Privacy vs. Evidence Retention

The General Data Protection Regulation (GDPR) — which applies to any merchant processing personal data of EU/UK residents regardless of where the merchant is located — creates a fundamental tension for chargeback management. GDPR requires merchants to minimize data collection, limit retention to what is necessary, and honor cardholder requests to erase their personal data. Chargeback defense, by contrast, requires merchants to retain detailed transaction records, delivery logs, IP addresses, device data, and customer communications — sometimes for 18+ months — to fight disputes effectively.

Navigating this tension requires understanding which legal bases justify retaining dispute-relevant personal data, what must be redacted in submissions, and how to respond when a cardholder requests erasure of data that may be needed for an open dispute.

---

## How Long to Keep Transaction Data

### Recommended Retention Periods

| Data Type | Recommended Retention | Legal Basis |
|---|---|---|
| Transaction records (amount, date, auth code) | 7 years | Legal obligation (accounting, tax) |
| Delivery confirmation (carrier records) | 18–24 months | Legitimate interest (dispute defense) |
| IP address / device fingerprint | 18 months | Legitimate interest (dispute defense) |
| Customer email communications | 24 months | Legitimate interest (dispute defense) |
| Customer service chat/phone logs | 24 months | Legitimate interest (dispute defense) |
| CRM account records (for subscription billing) | Duration of contract + 24 months | Contract performance + legitimate interest |
| Signed contracts / terms acceptance | 7 years | Legal obligation / contract performance |
| Authorization records (incl. AVS/CVV response) | 18 months | Legitimate interest (dispute defense) |

### Why 7 Years for Core Transaction Records

Seven years aligns with the document retention requirements of most financial regulations globally:
- US IRS: 7 years for financial records
- EU VAT Directive: typically 10 years for accounting records (varies by member state)
- UK Companies Act 2006: 6 years for company records
- PCI DSS: no specific retention period mandated, but recommends audit log retention of 12 months minimum

For chargeback purposes, the practical risk window is 18–24 months (dispute filing windows plus arbitration timelines). Retaining core transaction data for 7 years provides a compliance buffer for tax and accounting purposes that also covers all realistic dispute scenarios.

### Why 18 Months for Dispute Evidence

The cardholder's maximum filing window (120 days from transaction or expected delivery date) plus the representment and pre-arbitration periods can extend to approximately 12 months in extreme cases. Adding a 6-month buffer for edge cases and legal actions produces an 18-month evidence retention recommendation. Some legal counsel recommends 24 months for merchants in high-chargeback industries.

---

## GDPR Legal Bases for Chargeback Data Retention

Under GDPR, every processing activity — including retaining personal data for dispute purposes — requires a lawful basis. The relevant bases for chargeback-related retention are:

### Legal Obligation (Article 6(1)(c))
Merchants are legally required to maintain financial records under tax law, company law, and anti-money laundering regulations. Core transaction records (amount, date, card type, currency, authorization code) qualify as financial records subject to legal retention obligations. This is the strongest basis for retaining transaction data — the GDPR right to erasure does not apply when processing is necessary for compliance with a legal obligation.

### Legitimate Interests (Article 6(1)(f))
Retaining data to defend against chargebacks and legal claims is a legitimate interest of the merchant. The GDPR requires a balancing test: the merchant's legitimate interest in retaining data must not be overridden by the cardholder's privacy rights. For dispute evidence:
- Transaction-specific delivery logs, IP addresses, and device data used solely to defend specific disputes satisfy the balancing test.
- Broad behavioral tracking or marketing use of dispute-related data would fail the test.

Document your legitimate interest assessment in your privacy impact assessment (DPIA) or privacy notice to satisfy GDPR accountability requirements.

### Contract Performance (Article 6(1)(b))
For ongoing subscription relationships, retaining account data is necessary to perform the contract (billing, service delivery, account access). Contract performance justifies retaining account records for the duration of the subscription and for a reasonable post-termination period.

---

## The Right to Erasure vs. Open Disputes

Under GDPR Article 17, individuals have the right to request deletion of their personal data. This right is not absolute — it does not apply when processing is necessary for compliance with a legal obligation or for the establishment, exercise, or defense of legal claims.

### Chargeback as a Legal Claim

A filed chargeback constitutes a legal claim — it is a formal dispute with financial consequences adjudicated by the card network. This means the merchant may lawfully retain personal data relevant to an open chargeback dispute for as long as the dispute (and any appeals) remain active, even if the cardholder submits a GDPR erasure request.

### Responding to Erasure Requests During Active Disputes

When a cardholder (or anyone on their behalf) submits a GDPR erasure request while a chargeback is pending:

1. **Acknowledge the request** within 30 days as GDPR requires.
2. **Invoke the legal claims exemption** in your response: cite Article 17(3)(e) — "processing is necessary for the establishment, exercise or defence of legal claims."
3. **Document the open dispute** as the specific legal claim justifying the retention.
4. **Commit to delete** the dispute-relevant data once all appeal windows have closed and no legal claims remain open.
5. **Erase non-dispute personal data** that the erasure request covers and that is not needed for the open dispute (e.g., marketing profile data, browsing history).

### After the Dispute Is Closed

Once the chargeback and all appeal timelines have concluded, the legal claims exemption no longer applies. If a retention period based on another legal basis (legal obligation for accounting records) also applies, that data can be retained under that basis. Data that was retained solely for dispute defense — and for which no other retention basis applies — must be deleted within a reasonable timeframe after the dispute closes.

---

## Personal Data in Chargeback Submissions

When submitting evidence to your acquirer (who forwards to the issuing bank), you are sharing personal data with third parties. This must be managed in compliance with GDPR data minimization principles.

### What to Include

Evidence submissions to the card network dispute system fall under the legal claims exemption and are permissible data transfers. Include:
- Transaction details (date, amount, authorization code)
- Card number (last four digits only — never full PAN)
- Shipping address as needed to prove delivery
- IP address relevant to the specific transaction
- Email address (cardholder's account email, needed to identify the account)
- Delivery records, usage logs, and service records tied to the specific transaction

### What to Redact

- Full card number (PAN) — never included; last four digits only
- Social Security Number or government ID numbers — never relevant to dispute evidence
- Banking credentials or account login passwords
- Medical or health information
- Unrelated transaction history or personal data (e.g., other customers' data that appears in a database export)
- Internal notes unrelated to the dispute (employee comments, unrelated CRM fields)

### Data Transfer to Non-EU Recipients

Submitting chargeback evidence to a US-based acquirer or to a card network headquartered in the US constitutes a cross-border data transfer under GDPR. Ensure that your acquirer agreement includes appropriate safeguards: Standard Contractual Clauses (SCCs), adequacy decisions, or other GDPR-compliant transfer mechanisms.

---

## Privacy Notice Obligations

Your GDPR privacy notice must inform cardholders about:
- What transaction data you collect and retain
- How long you retain it and why (including the chargeback defense basis)
- Whether you share data with payment processors, acquirers, and card networks
- The cardholder's rights and how to exercise them (including erasure requests and the limitations that apply)

A privacy notice that clearly explains dispute-related retention provides the documentation required by GDPR's transparency principle and supports the legitimate interest assessment.

---

## Practical Data Governance Checklist for Merchants

- [ ] Transaction records retained for 7 years under legal obligation basis
- [ ] Delivery and IP logs retained for 18–24 months under legitimate interest basis
- [ ] Retention periods documented in your data retention policy
- [ ] Legitimate interest assessment completed and documented for dispute-related processing
- [ ] Privacy notice updated to describe chargeback-related data use and retention
- [ ] Erasure request process includes check for open disputes (legal claims exemption)
- [ ] Chargeback evidence submissions use last-four card digits only (no full PAN)
- [ ] Acquirer agreement includes GDPR-compliant data transfer mechanism (SCCs)
- [ ] Post-dispute deletion process implemented for data with no remaining retention basis
