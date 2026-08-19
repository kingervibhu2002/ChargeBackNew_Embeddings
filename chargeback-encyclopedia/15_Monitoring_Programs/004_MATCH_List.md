---
title: "MATCH List — Member Alert to Control High-Risk Merchants"
category: Monitoring Programs
doc_type: program-overview
program: MATCH List
network: Mastercard (maintained); accessed by all networks
audience: merchants
last_updated: 2026-06-01
tags: [MATCH list, high-risk, merchant account termination, blacklist, payment processing]
---

# MATCH List: Member Alert to Control High-Risk Merchants

## What Is the MATCH List?

The MATCH List (Member Alert to Control High-Risk Merchants) — formerly known as the Terminated Merchant File (TMF) — is a database maintained by Mastercard and accessed by acquiring banks and payment service providers globally. When an acquirer terminates a merchant's account for qualifying reasons, the acquirer is required under Mastercard's rules to report the merchant to the MATCH list. This report includes the merchant's legal name, doing-business-as (DBA) name, business address, Tax Identification Number (TIN), and the reason code for termination.

Every major acquiring bank queries the MATCH list as part of their merchant underwriting process. A merchant on the MATCH list will be declined for a new merchant account at virtually every mainstream acquirer, effectively ending their ability to accept card payments through normal channels.

---

## Why the MATCH List Exists

The MATCH list serves as the payment industry's shared warning system. Without it, a merchant terminated by one acquirer for fraud or excessive chargebacks could immediately apply to a different acquirer and resume the same problematic behavior. The MATCH list creates network-wide accountability by making merchants' termination histories visible to any acquirer they subsequently approach.

---

## 9 MATCH List Placement Reasons

Mastercard defines the following reason codes for MATCH list placement:

### Reason Code 1: Excessive Chargebacks
The merchant's chargeback ratio or count exceeded the acquirer's threshold or card network monitoring program levels (Mastercard ECP, Visa VDMP) and the account was terminated as a result. This is the most common placement reason for legitimate businesses that failed to manage their chargeback ratios.

### Reason Code 2: Excessive Fraud
The merchant facilitated or was the target of fraud at levels exceeding the acquirer's or network's acceptable thresholds. Includes accounts terminated due to VFMP or Mastercard Fraud Excessive Program enrollment failure.

### Reason Code 3: Breach of Merchant Agreement / Rule Violation
The merchant violated the terms of their merchant processing agreement or card network operating rules. Examples include processing for other merchants under their MID (factoring), processing for prohibited product categories, or misrepresenting the business type at sign-up.

### Reason Code 4: Fraud Conviction
A principal owner or controlling officer of the merchant was convicted of fraud, forgery, extortion, or related crimes in connection with the business.

### Reason Code 5: Bankrupt / Insolvent
The merchant declared bankruptcy or became insolvent while having unresolved chargeback liabilities that the acquirer could not recover.

### Reason Code 6: Collusion with Fraud
The merchant colluded with fraudsters — for example, knowingly processing fraudulent transactions submitted by a third party, or participating in bust-out fraud schemes.

### Reason Code 7: Counterfeit / Fraudulent Instruments
The merchant submitted fraudulent, counterfeit, or altered transaction documents.

### Reason Code 8: Identity Theft
The merchant's identity (business name, address, or principals) was used by fraudsters to open a merchant account without the legitimate business owner's knowledge. Inclusion under this code is a protective action, not a punitive one.

### Reason Code 9: PCI DSS Non-Compliance with Data Breach
The merchant experienced a data breach resulting from PCI DSS non-compliance, exposing cardholder data.

---

## How Long MATCH Listings Last

MATCH list placements remain active for **5 years** from the date of placement. The specific listing remains associated with the merchant's legal name, DBA, business address, and TIN. After 5 years, the entry expires and is removed from the active MATCH database.

During the 5-year listing period, every acquirer that queries MATCH during underwriting will see the record and the reason code.

---

## How to Check If You Are on the MATCH List

Only acquirers can query the MATCH list directly — merchants do not have self-service access. However:

- If you apply for a merchant account and are declined without explanation, ask the acquirer specifically whether a MATCH list record exists for your business.
- Your former acquirer (the one that terminated your account) may be willing to confirm the placement and reason code upon request.
- Some MATCH list management services and attorneys specializing in payment processing can query the list on your behalf through licensed acquirer relationships.
- Mastercard also offers a formal MATCH inquiry process through their customer engagement team for merchants who believe they have been placed in error.

---

## Impact on Merchant Account Acquisition

A MATCH listing with Reason Code 1 (Excessive Chargebacks) or Reason Code 2 (Excessive Fraud) is visible to every mainstream acquirer during underwriting. The practical impact:

- **Mainstream acquirers** (Chase, Worldpay, Fiserv, Adyen, Stripe, Square): All will decline a MATCH-listed merchant. These companies have automated MATCH query systems that return an automatic decline.

- **High-risk acquirers:** Some specialized high-risk acquirers (primarily offshore or in less-regulated jurisdictions) may be willing to process for MATCH-listed merchants at significantly higher rates, larger reserves (25–50% rolling reserve), and with restrictive processing caps. This is a last resort for merchants who have a legitimate business but were listed for manageable past problems.

- **Alternative payment methods:** While MATCH-listed merchants cannot easily accept Visa/Mastercard through normal channels, they may be able to use ACH bank transfers, cryptocurrency, or cash on delivery during the listing period for their core business.

---

## How to Get Removed from the MATCH List

Removal before the 5-year expiration is **extremely rare and extremely difficult.** The process:

1. **Contact the placing acquirer.** Only the acquirer that placed you on MATCH can initiate removal. Mastercard itself cannot unilaterally remove a valid placement.

2. **Grounds for removal (very limited):**
   - The placement was made in error (factual mistake — wrong business name, wrong TIN).
   - The chargeback chargebacks underlying the placement have been subsequently resolved (rare — most chargebacks cannot be "resolved" after the fact).
   - A court order overturning the basis for placement.
   - Identity theft placement (Code 8) — may be removed more readily once the genuine business owner establishes they were a victim.

3. **Process:** Submit a written removal request to the placing acquirer with supporting documentation. The acquirer reviews and, if they agree, contacts Mastercard to remove the record. This process can take 60–180 days even when the removal is appropriate.

4. **Legal assistance:** If you believe you were improperly placed on MATCH, an attorney specializing in payment processing disputes may be able to negotiate removal with the placing acquirer or assist with a legal challenge.

---

## How to Avoid MATCH List Placement

Prevention is far more effective than removal:

- **Maintain chargeback ratio below thresholds:** Stay below 0.9% (Visa) and 1.0% (Mastercard) at all times.
- **Respond to monitoring program notifications immediately:** An ECP or VDMP notice is a warning, not an automatic MATCH placement. Rapid remediation prevents escalation to termination.
- **Do not violate processing agreements:** Do not factor, do not process for unauthorized products, and do not misrepresent your business type to your acquirer.
- **Maintain PCI compliance:** A breach caused by non-compliance triggers Reason Code 9 placement.
- **Communicate proactively with your acquirer:** If you are experiencing a chargeback spike, contact your acquirer before they contact you. A merchant who proactively presents a remediation plan is treated differently than one who ignores monitoring program notices.

---

## MATCH List — Quick Reference Card

| Element | Detail |
|---|---|
| Maintained by | Mastercard |
| Accessible by | All acquirers (required to query during underwriting) |
| Placement duration | 5 years from placement date |
| Most common reason | Code 1: Excessive Chargebacks |
| Removal possibility | Extremely rare; requires placing acquirer's agreement |
| Self-service query | Not available to merchants directly |
| Best prevention | Keep chargeback ratio below monitoring thresholds |
| Legal remedy | Attorney specializing in payment disputes (for wrongful placement) |
