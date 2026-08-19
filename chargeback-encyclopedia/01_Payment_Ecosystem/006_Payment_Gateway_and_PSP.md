---
title: "Payment Gateway, PSP, and Aggregator: Differences and Chargeback Implications"
section: "01_Payment_Ecosystem"
category: "Payment Ecosystem"
document_type: "Reference"
keywords: ["payment gateway", "PSP", "payment service provider", "payment aggregator", "Stripe", "Square", "PayPal", "shared merchant account", "aggregator chargeback", "merchant account vs aggregator", "gateway vs PSP", "sub-merchant"]
difficulty: "Beginner"
---

# Payment Gateway, PSP, and Aggregator: Differences and Chargeback Implications

Three terms are frequently used interchangeably in commerce but describe distinct entities with different functions and different chargeback implications: payment gateway, payment service provider (PSP), and payment aggregator. Understanding these differences is essential because your relationship with the entity processing your payments determines exactly how chargebacks are handled, reported, and resolved.

## Payment Gateway: The Technical Conduit

A **payment gateway** is technology infrastructure — not a financial entity — that securely captures, encrypts, and transmits payment data from a merchant's checkout (online or point-of-sale) to the payment processor.

### What a Gateway Does
- Encrypts card data using SSL/TLS at the point of collection
- Tokenizes sensitive card numbers to reduce PCI scope
- Routes authorization requests to the appropriate payment processor
- Returns authorization responses to the merchant's system
- Handles 3D Secure (3DS) authentication redirects

### What a Gateway Does Not Do
- Hold or move money
- Process chargebacks (the acquirer does that)
- Issue or manage merchant accounts

### Examples of Pure Gateways
- **Authorize.Net** (owned by Visa): A gateway that connects to various acquirers but is not itself an acquirer.
- **NMI (Network Merchants Inc.)**: White-labeled gateway used by ISO/MSP channels.
- **Braintree Gateway** (in its standalone form): The underlying gateway infrastructure that PayPal acquired.

When you use a pure gateway, you still need a separate merchant account with an acquirer. Chargebacks are handled by the acquirer; the gateway just transmits the data.

## Payment Service Provider (PSP): Bundled Solution

A **payment service provider (PSP)** bundles gateway, processing, and (often) acquiring functions into a single integrated solution. The merchant signs one agreement with the PSP and receives one monthly statement, one API, and one point of contact.

### Full-Stack PSP Model
In the full-stack PSP model:
- The PSP operates its own gateway technology.
- The PSP partners with one or more acquiring banks for settlement.
- The PSP manages chargeback processing on the merchant's behalf.
- The merchant has a dedicated MID.

### PSP Chargeback Handling
PSPs that provide individual MIDs to merchants handle chargebacks within the standard network dispute process:
- Merchants receive chargeback notifications through the PSP's portal.
- Representments are submitted through the PSP.
- Chargeback ratios are tracked against the individual merchant's MID.

## Payment Aggregator: The Shared MID Model

A **payment aggregator** (also called a merchant aggregator or payment facilitator/PayFac) operates fundamentally differently from a traditional PSP or gateway. Instead of providing each merchant with a dedicated MID, the aggregator maintains a **master merchant account** with an acquiring bank and onboards businesses as **sub-merchants** under that master account.

### How Aggregation Works
1. The aggregator applies for and obtains a master merchant account from an acquiring bank.
2. Businesses (sub-merchants) sign up with the aggregator — often in minutes, with minimal underwriting.
3. All sub-merchant transactions process under the aggregator's master MID.
4. The aggregator handles settlement to each sub-merchant's bank account.

### Major Aggregators
- **Stripe**: Operates as a PayFac; individual businesses are sub-merchants under Stripe's master account. Stripe has its own chargeback policies layered on top of network rules.
- **Square**: PayFac model; primarily targets SMBs and brick-and-mortar. Square's chargeback handling is internal.
- **PayPal**: Operates primarily as an aggregator for standard merchant accounts; PayPal disputes are governed by PayPal's User Agreement, which parallels but differs from Visa/Mastercard chargeback rules.
- **Shopify Payments**: PayFac model powered by Stripe. Chargebacks are managed through Shopify's dashboard.

## Critical Differences in Chargeback Handling

The aggregator vs. direct acquirer distinction has significant chargeback implications:

### Chargeback Ratio Tracking
- **Direct acquirer/dedicated MID**: Your chargeback ratio is tracked at your MID level. If your ratio exceeds thresholds, you are individually flagged by the card network's monitoring programs.
- **Aggregator/PayFac**: Your transactions contribute to the aggregator's master MID ratio. Individual sub-merchants are not directly tracked by card networks. The aggregator conducts its own internal chargeback monitoring.

This means a small merchant on Stripe with a 5% chargeback ratio may not immediately trigger Visa's monitoring programs — but they will trigger Stripe's internal policies, which can result in account suspension or termination faster than a network program would act.

### Dispute Resolution Process
- **Direct acquirer**: Disputes go through the formal card network process (chargeback → representment → pre-arb → arbitration).
- **Aggregator**: The aggregator adds an internal layer. Stripe, for example, provides its own dispute management portal, has its own internal resolution rules, and may make decisions based on internal policies in addition to network rules.

### Evidence Submission
- **Direct acquirer**: Evidence submitted to the acquirer enters the formal network dispute chain and reaches the issuer.
- **Aggregator**: Evidence submitted through the aggregator's portal is reviewed and packaged by the aggregator before submission to the network. Quality of advocacy varies by aggregator.

### Chargeback Fees
- **Direct acquirer**: Negotiable; typically $15–$50 per chargeback.
- **Stripe**: $15 per dispute (refunded if merchant wins). Non-negotiable.
- **Square**: $0 for merchants on Square; Square absorbs chargebacks internally below certain thresholds (though they may hold seller funds).
- **PayPal**: Separate "Dispute Resolution" process; $20 chargeback fee for card-funded transactions; PayPal's own Buyer/Seller Protection rules apply.

### Risks of the Aggregator Model
- **Account termination without appeal**: Aggregators can terminate sub-merchant accounts under their own terms, often with less process than a formal acquirer relationship. Termination by Stripe does not place you on the MATCH list (Stripe's termination), but it can make obtaining a new aggregator account difficult.
- **Fund holds**: Aggregators commonly place fund holds on sub-merchant accounts when chargeback or fraud indicators appear. Funds may be held for 90–120+ days.
- **Limited representment support**: Some aggregators provide limited support for chargeback representment; merchants must sometimes navigate disputes with minimal guidance.
- **Shared MID risk**: If another sub-merchant on the aggregator's master MID engages in massive fraud, the resulting acquirer scrutiny can affect all sub-merchants.

## When to Use Each Model

| Factor | Aggregator (Stripe/Square) | Dedicated Merchant Account |
|--------|---------------------------|---------------------------|
| Setup speed | Minutes to hours | Days to weeks |
| Underwriting | Minimal | Full KYC/underwriting |
| Processing fees | Typically higher | Negotiable, often lower at volume |
| Chargeback control | Limited | Full formal dispute process |
| Account stability | Lower (risk of holds/termination) | Higher |
| Best for | Startups, low volume, low chargeback risk | Established merchants, high volume, or high chargeback risk |

---

## FAQs

**Q: I use Stripe. Does that mean I don't have a real merchant account?**
Correct — you operate as a sub-merchant under Stripe's master merchant account. You do not have a dedicated MID with an acquiring bank. This simplifies setup but means you are subject to Stripe's internal policies and risk management decisions in addition to card network rules.

**Q: Can I switch from an aggregator to a direct acquirer if I have chargebacks?**
Yes, but your chargeback history matters. A new acquirer will assess your historical chargeback rate, your business type, and your volume. If your rate is under control and you can explain your business model, direct acquirer relationships are obtainable. Some high-risk acquirers specialize in onboarding merchants who have had aggregator accounts terminated.

**Q: Do Stripe/PayPal disputes follow the same rules as Visa/Mastercard chargebacks?**
For card-funded transactions, disputes ultimately must follow card network rules, but the aggregator adds its own internal dispute process on top. PayPal disputes through PayPal's internal Buyer/Seller Protection system are governed by PayPal's User Agreement and may not follow network rules at all. Bank-funded PayPal transactions (ACH) are governed by Regulation E and NACHA rules, not card network chargeback rules.

**Q: What does "payment facilitator" mean, and is it different from an aggregator?**
"Payment facilitator" (PayFac) and "aggregator" are often used interchangeably. In formal card network terminology, a "payment facilitator" is a registered entity that has been approved by the card network to board sub-merchants under its master merchant account. Stripe, Square, and PayPal are registered payment facilitators with Visa and Mastercard.

**Q: If my aggregator holds my funds due to chargebacks, what can I do?**
Review your aggregator's terms of service regarding fund holds — most allow holds of 90–180 days for chargeback risk exposure. You can request an explanation of the specific hold trigger, provide documentation demonstrating your legitimate business operations, and in some cases negotiate partial release. If the hold is indefinite and unjustified, consult with a payment industry attorney. Regulatory complaints to the CFPB may also be appropriate if the aggregator is not following its disclosed policies.
