---
title: "Acquiring Bank: Role, Merchant Contracts, and Chargeback Handling"
section: "01_Payment_Ecosystem"
category: "Payment Ecosystem"
document_type: "Reference"
keywords: ["acquiring bank", "acquirer", "merchant processing contract", "reserve account", "chargeback notification", "acquirer liability", "merchant account termination", "processing agreement", "acquirer chargeback", "merchant reserves"]
difficulty: "Beginner"
---

# Acquiring Bank: Role, Merchant Contracts, and Chargeback Handling

The acquiring bank — commonly called the "acquirer" — is the financial institution that establishes and maintains the merchant's bank account relationship and enables the merchant to accept card payments. In the chargeback ecosystem, the acquirer sits between the merchant and the card network, serving as the merchant's financial backer and the intermediary through which all dispute communications flow.

## What Is an Acquiring Bank?

The acquiring bank "acquires" payment transactions on behalf of merchants. When you accept a card payment, your acquirer collects the transaction data, submits it for clearing, and ultimately deposits the funds into your merchant account. Examples of acquiring banks include:

- **Dedicated acquirers**: Worldpay (FIS), Fiserv/First Data, Global Payments, Elavon, Heartland
- **Bank-owned acquiring operations**: Wells Fargo Merchant Services, Bank of America Merchant Services (Chase Paymentech)
- **PSP-acquirers**: Stripe, Square, and PayPal operate as payment service providers that include acquiring functions

In the four-party model, the acquirer and issuer are separate entities. Your acquirer has no relationship with your customer's bank until a transaction — or a dispute — connects them.

## The Merchant Processing Contract

When you establish a merchant account, you sign a **merchant processing agreement** with your acquirer. This contract governs the relationship and includes:

### Key Contract Terms

- **Discount rate**: The percentage fee the acquirer charges on each transaction (blended rate or interchange-plus pricing).
- **Chargeback threshold**: The maximum chargeback ratio you're permitted to maintain, typically mirroring network thresholds (1% for Visa, though acquirers may set lower internal limits).
- **Reserve requirements**: Whether the acquirer holds a percentage of your volume in reserve and under what conditions.
- **Funding timeline**: How quickly settled funds are deposited to your bank account (T+1, T+2, weekly, etc.).
- **Termination conditions**: Grounds for account closure, including excessive chargebacks, fraud, or regulatory violations.
- **Chargeback fee**: The per-chargeback fee assessed regardless of outcome, typically $15–$50 for standard accounts.

Merchants should read processing agreements carefully before signing. Some agreements include clauses that grant the acquirer broad discretion to withhold funds or terminate accounts on short notice.

## Reserve Accounts

One of the acquirer's primary risk management tools is the **reserve account** — a portion of merchant funds held as collateral against potential chargeback losses.

### Types of Reserves

**Rolling Reserve**: A fixed percentage (typically 5–15%) of every transaction processed is held for a defined period (90–180 days). As older reserves age out, they are released, creating a continuous "rolling" pool. Rolling reserves are most common for high-risk merchants.

**Capped Reserve**: Funds are withheld until the reserve reaches a set dollar amount, after which no further withholding occurs. Less common than rolling reserves.

**Upfront Reserve**: A lump-sum amount held at account opening, typically based on projected monthly volume and chargeback exposure.

### When Reserves Are Triggered
Even standard-risk merchants can have reserves imposed after:
- Chargeback ratio exceeds thresholds
- Account volume spikes significantly beyond projections
- Fraud indicators emerge
- The acquirer anticipates chargeback exposure (e.g., the merchant processes many advance-purchase transactions)

Reserves are particularly painful for merchants because they represent real cash being withheld. If your account is terminated while reserves are held, the acquirer may hold those funds for the duration of the reserve period (up to 6 months) to cover potential post-termination chargebacks.

## How Acquirers Handle Chargebacks

When an issuer files a chargeback through the card network, the flow reaches the acquirer first:

### Step 1: Acquirer Receives Chargeback
The card network transmits the chargeback to the acquiring bank. The acquirer receives the transaction detail, reason code, and the amount being reversed.

### Step 2: Acquirer Debits Merchant Account
The acquirer immediately debits the merchant's account for the chargeback amount plus the chargeback fee. This happens before the merchant is even notified and before any investigation.

### Step 3: Merchant Notification
The acquirer sends the merchant a chargeback notification, typically via:
- Email or portal notification
- Physical mail (less common today)
- Integrated dispute management platform

The notification includes: transaction details, chargeback amount, reason code, and the response deadline.

### Step 4: Merchant Response Window
The acquirer forwards the merchant's representment evidence to the card network within the applicable deadline. The merchant must submit their response to the acquirer before this deadline — acquirers set internal deadlines that are earlier than the network deadline to allow processing time.

### Step 5: Outcome Relay
The acquirer communicates the dispute outcome back to the merchant and either re-credits the account (if the merchant won) or confirms the permanent loss.

## Acquirer Liability

The acquiring bank has direct financial exposure in the chargeback ecosystem:

- **Merchant Default**: If a merchant cannot pay a chargeback (insufficient funds in merchant account and no reserves), the **acquirer bears the loss**. This is why acquirers impose reserves and closely monitor chargeback ratios.
- **Regulatory Violations**: If the acquirer fails to follow card network dispute processing rules (wrong timelines, improper submissions), the acquirer can lose disputes on procedural grounds.
- **High-Risk Merchant Sponsorship**: Acquirers that knowingly sponsor high-risk merchants take on elevated liability. Card networks can fine acquirers for their portfolio's chargeback performance.

### What Happens When a Merchant Can't Pay

If a merchant's account has insufficient funds to cover a chargeback:

1. The acquirer debits whatever is available in the merchant account.
2. The acquirer draws from the reserve account.
3. If reserves are exhausted, the acquirer pursues the merchant for the remaining amount through collections.
4. If the merchant is unreachable or insolvent, the acquirer absorbs the loss.
5. The acquirer terminates the merchant account and may add the merchant to the MATCH list.

This is why acquirers take chargeback monitoring seriously — a merchant with a 5% chargeback ratio and high volume represents a significant contingent liability for the acquirer.

## Acquirer Monitoring Programs

Both Visa and Mastercard hold acquirers responsible for their merchants' chargeback performance through acquirer monitoring programs. Acquirers with merchant portfolios showing elevated chargeback or fraud rates face:

- Mandatory remediation plans
- Network fines
- Loss of network participation rights

This regulatory pressure is what motivates acquirers to impose chargeback thresholds lower than the network's published limits, to terminate high-ratio merchants proactively, and to require evidence retention from merchants.

---

## FAQs

**Q: Can my acquirer take money out of my account without notice for a chargeback?**
Yes. Your merchant processing agreement grants the acquirer the right to debit your account for chargeback amounts and fees as soon as the chargeback is received from the card network. This is standard industry practice and is typically disclosed in the contract you signed during onboarding.

**Q: What is the difference between my acquirer and my payment processor?**
Sometimes they are the same entity. Some acquirers perform their own processing; others outsource the technical processing function to independent payment processors (like Tsys, Worldline, or i2c). In either case, your contractual relationship is with the acquirer, and the acquirer is responsible for chargeback management regardless of which entity processes the transaction technically.

**Q: If I switch acquirers, does my chargeback history follow me?**
Your historical chargeback data is visible to card networks and may be disclosed to new acquirers during their underwriting review. If you are on the MATCH list (placed there by a previous acquirer), this will significantly impair your ability to obtain a new merchant account with any standard acquirer.

**Q: Can I negotiate my chargeback fee with my acquirer?**
Chargeback fees are negotiable, particularly for merchants with high processing volume. High-volume merchants with low chargeback rates have more leverage. PSPs like Stripe typically have fixed chargeback fees that are not negotiable on an individual merchant basis.

**Q: What should I do if my acquirer terminates my account due to chargebacks?**
First, request written documentation of the termination reason and the status of any reserve funds. Ensure any outstanding representments are still being processed. If you believe the termination was in error, you can file a complaint with your state banking regulator or the Consumer Financial Protection Bureau (CFPB). To obtain a new merchant account, you will need to address the underlying chargeback issue — typically by demonstrating a remediation plan to a new acquirer.
