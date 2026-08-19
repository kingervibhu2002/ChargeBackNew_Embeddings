---
title: "Merchant: Account, Liability, and Chargeback Exposure"
section: "01_Payment_Ecosystem"
category: "Payment Ecosystem"
document_type: "Reference"
keywords: ["merchant account", "MID", "merchant ID", "merchant category code", "MCC", "KYC", "merchant onboarding", "chargeback liability", "high-risk merchant", "risk tier", "merchant agreement", "MATCH list", "TMF list"]
difficulty: "Beginner"
---

# Merchant: Account, Liability, and Chargeback Exposure

Merchants are the businesses that accept card payments in exchange for goods or services. In the chargeback ecosystem, merchants occupy a uniquely exposed position: they have fulfilled their end of the transaction, but they bear primary financial liability when disputes occur. Understanding your rights, obligations, and risk exposure as a merchant is the first step toward managing chargebacks effectively.

## What Is a Merchant Account?

A **merchant account** is a specialized type of bank account that allows a business to accept credit and debit card payments. Unlike a standard business checking account, a merchant account is governed by a processing agreement between the merchant and an acquiring bank (or payment service provider). This agreement defines:

- Permitted business types and transaction categories
- Processing volume limits and average transaction size expectations
- Reserve requirements
- Chargeback thresholds and consequences
- Termination conditions

Merchant accounts are not universally available. Businesses must apply, undergo underwriting review, and be approved before they can accept card payments.

## Merchant ID (MID)

Every merchant account is assigned a **Merchant Identification Number (MID)** — a unique numeric identifier used to route transactions, track chargeback ratios, and identify the merchant on the card network's systems.

Key facts about MIDs:

- Every location or business entity may have a separate MID.
- Your MID is visible on every transaction record and chargeback notification.
- If your MID becomes associated with excessive chargebacks, fraud, or violations, it may be terminated and placed on restricted lists.
- Merchants operating under a PSP/aggregator (like Stripe or Square) do not have their own MID — they share the aggregator's master MID, which changes their chargeback reporting and monitoring exposure.

## Merchant Category Code (MCC)

The **Merchant Category Code (MCC)** is a four-digit code assigned during merchant onboarding that classifies the type of business a merchant operates. MCCs are defined by card networks and used across the payment ecosystem for:

- **Interchange rate determination**: Different MCCs carry different interchange rates.
- **Risk assessment**: Some MCCs are considered higher risk by card networks (e.g., online gaming, nutraceuticals, travel, adult content).
- **Chargeback monitoring program thresholds**: Certain MCCs have lower chargeback tolerance thresholds.
- **Consumer protections**: Some MCCs trigger enhanced cardholder protections (e.g., airlines and advance purchase rules).

Merchants cannot self-select their MCC. It is assigned by the acquirer based on business type. If you believe your MCC is incorrect, you can request a review — but misclassification to avoid higher-risk codes violates network rules and can result in termination.

## Merchant Onboarding and KYC

Before accepting card payments, merchants must complete an **onboarding** process that includes:

### Know Your Customer (KYC) Requirements
Acquirers and PSPs are required under financial regulations (Bank Secrecy Act, AML regulations, card network rules) to verify the identity of merchants before onboarding. KYC typically includes:

- Business registration documents (articles of incorporation, business license)
- Government-issued ID for beneficial owners (typically anyone owning >25% of the business)
- Bank account verification
- Tax identification number (EIN or SSN)
- Business website review
- Processing history (if switching from another processor)

### Underwriting
The acquirer evaluates the merchant's risk profile based on: business type, processing volume projections, average ticket size, historical chargeback rates, credit history, and industry risk profile. High-risk businesses may face additional scrutiny, higher fees, or reserve requirements.

## Chargeback Liability

**Merchants bear primary financial liability for chargebacks.** When a chargeback is filed:

1. The issuer reverses the transaction amount from the acquirer.
2. The acquirer debits the merchant's account for the chargeback amount plus a chargeback fee.
3. The merchant is notified and given an opportunity to dispute (representment).
4. If the merchant wins representment, funds are returned. If the merchant loses or does not respond, the funds are permanently lost.

Merchants also lose the chargeback fee regardless of outcome. Additionally, original processing fees are not refunded when a chargeback occurs.

## Risk Tiers for Merchants

Acquirers and card networks classify merchants into risk tiers based on their industry, transaction profile, and chargeback history:

### Standard Risk
Most brick-and-mortar retailers, restaurants, and established businesses. Standard interchange rates, no reserve requirement (typically), and standard chargeback monitoring thresholds.

### Medium Risk
Businesses with moderate chargeback exposure: e-commerce (without subscription), software, digital goods. May require enhanced fraud controls and 3DS implementation.

### High Risk
Industries with historically elevated chargeback rates. Examples:
- Online gambling and gaming
- Adult content
- Nutraceuticals and dietary supplements
- Travel and timeshare
- Cryptocurrency exchanges
- Firearms and ammunition
- Online dating
- Debt collection and credit repair

High-risk merchants face: higher processing fees, mandatory rolling reserve (5-10% of monthly volume held for 90-180 days), stricter chargeback thresholds, more frequent account reviews, and fewer acquirer options.

## The Merchant Agreement and Obligations

When you sign a merchant processing agreement, you agree to comply with:

- **Card network operating regulations** (Visa Core Rules, Mastercard Rules) — these are lengthy documents but binding.
- **PCI-DSS** (Payment Card Industry Data Security Standard) — requirements for how you store, process, and transmit cardholder data.
- **Prohibited transaction types** — you cannot accept cards for transactions your MCC and merchant agreement don't permit.
- **Chargeback thresholds** — you must maintain your chargeback ratio below network and acquirer thresholds.
- **Refund and cancellation policy disclosure** — your policies must be clearly disclosed at the point of sale.
- **Evidence retention** — you must retain transaction records for a minimum period (typically 18 months) to respond to disputes.

Violating these obligations can result in account termination, fines, or placement on the MATCH list.

## The MATCH List (Member Alert to Control High-Risk Merchants)

The **MATCH list** (formerly called the TMF — Terminated Merchant File) is a database maintained by Mastercard and used by all major card networks. Merchants are added to the MATCH list when:

- Their merchant account is terminated for excessive chargebacks (typically >1% chargeback ratio sustained).
- Fraud is discovered.
- PCI-DSS non-compliance is cited.
- Violation of merchant agreement terms occurs.

Being on the MATCH list makes it extremely difficult to obtain a new merchant account. Listings remain for up to **5 years**. Merchants placed on MATCH must resolve the underlying issue with the original acquirer to request removal.

---

## FAQs

**Q: Can I have multiple merchant accounts to spread my chargeback ratio?**
Opening multiple merchant accounts with different acquirers to obscure a high chargeback ratio is a violation of network rules. Card networks share chargeback and fraud data across acquirers. Attempting to obscure chargeback rates through account splitting can result in MATCH listing.

**Q: What MCC should a new e-commerce business use?**
Your acquirer assigns the MCC based on your primary business activity. You should not attempt to obtain a lower-risk MCC to avoid scrutiny. If your business genuinely spans multiple categories, discuss the correct classification with your acquirer during onboarding.

**Q: Do I lose processing fees when a chargeback occurs?**
Yes. The original interchange and processing fees you paid on the transaction are not refunded when a chargeback occurs. You lose the transaction amount, the chargeback fee, and the original processing cost.

**Q: What is a rolling reserve, and when does it apply?**
A rolling reserve is a percentage of each transaction (typically 5-10%) held by the acquirer for a defined period (90-180 days) as a buffer against chargeback losses. Reserves are common for high-risk merchants and new businesses. Funds are released on a rolling basis once the hold period expires.

**Q: If a cardholder files a chargeback against me in error, who do I contact?**
Contact your acquirer or PSP's dispute management team immediately. They will provide the chargeback documentation and the window within which you can submit a representment (typically 20-45 days depending on the network and reason code). Do not contact the cardholder's bank directly — all communication must go through your acquirer.
