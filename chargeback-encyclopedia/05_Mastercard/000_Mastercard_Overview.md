---
title: "Mastercard Dispute Process — Overview"
section: "05_Mastercard"
category: "Mastercard Overview"
network: "Mastercard"
reason_code: "N/A"
document_type: "Network Overview"
keywords: ["Mastercard", "dispute process", "Second Presentment", "MDR", "chargeback cycle", "timelines"]
difficulty: "Beginner"
---

# Mastercard Dispute Process — Overview

Understanding how Mastercard handles disputes is foundational to building an effective chargeback management strategy. Mastercard operates with distinct rules, timelines, and terminology that differ meaningfully from Visa and other networks. This document covers everything a merchant needs to know about the Mastercard dispute lifecycle.

## How Mastercard Differs from Visa

Mastercard and Visa are both card networks, but they administer disputes under separate rule sets. Key structural differences include:

- **Mastercard as a Pure Network**: Unlike American Express, Mastercard does not issue cards directly. It licenses its brand to issuing banks. However, unlike Visa, Mastercard takes a more active role in dispute adjudication through its Mastercard Dispute Resolution (MDR) system.
- **Reason Code Structure**: Mastercard uses a four-digit numeric reason code system (e.g., 4837, 4853). Visa migrated to alphanumeric codes in 2018 with its Visa Claims Resolution (VCR) system. Mastercard has not adopted a parallel simplification, so merchants must be familiar with the original numeric codes.
- **Chargeback Cycles**: Mastercard permits a full chargeback cycle with up to three dispute phases, whereas Visa's VCR system compressed many disputes into a single arbitration step. This gives Mastercard merchants more runway but also more complexity.
- **Pre-Arbitration and Arbitration**: After a Second Presentment is rejected, either party can escalate to Pre-Arbitration and then to Mastercard Arbitration. Mastercard acts as the final adjudicator. Filing fees apply and the losing party bears costs.

## The Mastercard Dispute Lifecycle

### Phase 1: Chargeback

The dispute begins when an issuing bank files a chargeback on behalf of the cardholder. The issuer has **120 calendar days** from the transaction processing date (or the date the cardholder became aware of the issue) to initiate a chargeback, with certain reason codes having shorter windows.

The merchant's acquiring bank receives the chargeback and debits the merchant's account for the disputed amount, plus any applicable fees.

### Phase 2: Second Presentment (Rebuttal)

The merchant has **45 calendar days** from the chargeback processing date to submit a Second Presentment — Mastercard's term for what Visa calls a representment. This is the merchant's opportunity to dispute the chargeback with supporting evidence.

A valid Second Presentment must include:
- A completed Chargeback Rebuttal Letter (CRL) or equivalent acquirer form
- All documentary evidence relevant to the reason code
- Clear articulation of why the chargeback is invalid

If no Second Presentment is filed, the chargeback becomes final and the merchant absorbs the loss.

### Phase 3: Pre-Arbitration

If the issuing bank rejects the Second Presentment, it may file a Pre-Arbitration notice within **45 days**. This is essentially a second-level review. The merchant can accept the loss or escalate to formal Arbitration.

### Phase 4: Arbitration

Formal Arbitration is the final step, resolved by Mastercard's dispute resolution team. Filing fees start at **$250**, and the losing party typically bears all fees plus the disputed amount. Merchants should only escalate to Arbitration when evidence is overwhelmingly in their favor.

## Mastercard Dispute Resolution (MDR)

MDR is Mastercard's internal system for processing and adjudicating disputes. Key features include:

- **Automated Decisioning**: For certain dispute types, MDR applies automated rules. For example, if a transaction was authenticated via Mastercard Identity Check (3DS), liability automatically shifts to the issuer.
- **Compelling Evidence Standard**: Mastercard defines specific evidence requirements per reason code. Evidence that does not meet the defined standard will not be accepted.
- **Digital Dispute Filing**: Most acquirers file and respond to disputes through the Mastercard Connect platform, which integrates with MDR.

## Mastercard Chargeback Monitoring Programs

Merchants with excessive chargebacks face enrollment in Mastercard's monitoring programs:

| Program | Threshold | Consequence |
|---|---|---|
| Excessive Chargeback Program (ECP) | > 1% ratio OR > 100 chargebacks/month | Remediation plan required |
| High Excessive Chargeback Program (HECP) | > 1.5% ratio AND > 300 chargebacks/month | Fines starting at $1,000/month |
| MATCH List | Account terminated for cause | Future merchant account denial |

## Key Mastercard-Specific Features

### Mastercard Identity Check (3DS 2.0)

Mastercard's branded version of 3D Secure authentication. When a transaction is authenticated through Identity Check, liability for fraudulent chargebacks (reason codes 4837, 4863, etc.) shifts to the issuer. Merchants should strongly consider enabling this for all card-not-present transactions.

### Second Presentment with Compelling Evidence

Mastercard's rules for what constitutes valid rebuttal evidence are codified per reason code. Merchants cannot simply submit a general denial — each response must include the specific documentation required under the applicable reason code's guidelines.

### Acquirer Role

The acquiring bank is the merchant's advocate throughout the process. A good acquirer will provide dispute management tools, coach merchants on evidence requirements, and submit Second Presentments on the merchant's behalf. Merchants should understand their acquirer's dispute SLAs to avoid missing response deadlines.

## Timeline Summary

| Event | Party | Deadline |
|---|---|---|
| Chargeback filed | Issuer | 120 days from transaction/discovery |
| Second Presentment | Merchant/Acquirer | 45 days from chargeback date |
| Pre-Arbitration | Issuer | 45 days from Second Presentment |
| Arbitration filing | Either party | Per Mastercard rules |

## Frequently Asked Questions

**Q: Can a merchant fight every chargeback?**
A: Technically yes, but fighting chargebacks where the merchant is clearly liable (e.g., genuine non-delivery) wastes resources and can increase chargeback ratios. Fight disputes where compelling evidence exists.

**Q: What is the single most important thing a merchant can do to win Mastercard chargebacks?**
A: Retain complete transaction records — authorization data, delivery confirmation, customer communications, and device/IP logs for CNP transactions — for at least 18 months.

**Q: Is there a fee to file a Second Presentment?**
A: Acquirers may charge representment processing fees. Mastercard itself charges fees only at the Arbitration stage.

**Q: How does Mastercard notify merchants of chargebacks?**
A: Notification flows through the acquiring bank. Merchants typically receive alerts via their payment gateway or acquirer's dispute management portal within 1-3 business days of the chargeback being filed.

**Q: Does the same chargeback ratio formula apply globally?**
A: Mastercard applies its monitoring thresholds globally, but some regional variations exist for certain markets. Merchants operating internationally should consult their acquirer for region-specific guidance.
