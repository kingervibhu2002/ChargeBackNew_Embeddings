---
title: "Subscription and Free Trial Fraud"
section: "08_Fraud"
category: "Fraud Encyclopedia"
document_type: "Fraud Reference"
keywords: ["subscription fraud", "free trial fraud", "recurring billing", "trial abuse", "credential sharing", "Visa 13.2", "Mastercard 4853", "3DS subscription"]
difficulty: "Intermediate"
---

# Subscription and Free Trial Fraud

## What Is Subscription and Free Trial Fraud?

Subscription fraud encompasses a range of abusive behaviors targeting merchants who offer recurring billing models, free trials, or subscription-based access to products or services. The fraud exploits the structure of subscription commerce — low initial barriers, delayed billing, and automated renewals — to obtain goods or services without valid payment.

This is a high-priority fraud category for SaaS companies, streaming platforms, digital media services, fitness apps, meal kit providers, and any business offering a free or discounted trial period.

## Types of Subscription and Free Trial Fraud

### Using Stolen Cards for Free Trials

The most straightforward form: a fraudster uses a stolen credit card to sign up for a trial that requires a payment method on file. The trial period provides legitimate access to the service. Before the trial converts to a paid subscription, the fraudster cancels — but has already extracted full value from the trial period (downloaded content, scraped data, or used premium features for competitive intelligence).

The chargeback arrives later when the legitimate cardholder notices even the $0.01 verification charge or a small trial fee.

### Repeat Free Trial Abuse

Legitimate customers — not fraudsters — repeatedly exploit free trials by creating new accounts with different email addresses. This is not illegal in most jurisdictions but is a form of policy abuse. The merchant provides full service value to the same person repeatedly while receiving no revenue.

Patterns to detect:
- Same device fingerprint across multiple "new" accounts.
- Same billing address or payment card across different email accounts.
- Same IP address associated with multiple trial sign-ups.
- Name and address variations that resolve to the same individual (John Smith vs. J. Smith vs. John A. Smith, same billing ZIP).

### Credential Sharing

A paying subscriber shares login credentials with multiple non-paying users. This reduces legitimate subscription revenue without generating chargebacks directly. However, it can lead to chargebacks if the primary account holder disputes charges they consider "unfair" (paying for service others are using without their consent) or if the account is later taken over.

Netflix's 2023 crackdown on credential sharing demonstrated the scale: the practice was depressing subscriber counts by tens of millions globally.

### Chargebacks After Trial Converts

The most common subscription chargeback scenario: a cardholder signs up for a free or low-cost trial, forgets to cancel, and the trial converts to a full-priced subscription. The charge appears on their statement — sometimes weeks or months after sign-up — and they dispute it as unauthorized because they do not recognize it or forgot about the trial.

This is friendly fraud in most cases. The cardholder agreed to the terms, failed to cancel, and received the service during the subscription period. However, issuers frequently side with cardholders on these disputes because:
- Terms and conditions are often difficult to find or understand.
- The billing descriptor may not match the trial brand name.
- The amount differs significantly from the trial price.

Visa codes for this scenario: **13.2** (Cancelled Recurring Transaction). Mastercard: **4853** (Cardholder Dispute — Recurring).

## How to Prevent Subscription Fraud

### Require Card Verification at Signup

A $0.00 authorization (card verification) or a small refundable hold confirms that the payment card is valid and associated with a real account. This alone eliminates most stolen-card trial fraud, as many stolen card numbers will decline at authorization.

Some merchants use a $1.00 authorization hold that is immediately released. This has the added benefit of establishing a prior transaction record with the same card for Visa CE3.0 compelling evidence purposes.

### Delay Fulfillment on New High-Risk Accounts

For digital goods or high-value services, impose a short delay (2–24 hours) before fulfilling trial benefits on flagged new accounts. During this window, run additional fraud scoring. Fraudsters seeking immediate access (to scrape, resell credentials, etc.) often cannot wait.

### 3DS for Subscription Initial Transaction

Under Visa and Mastercard rules, authenticating the initial subscription transaction with 3D Secure provides liability protection for subsequent recurring charges linked to that initial authenticated transaction. If the cardholder later disputes a recurring charge as unauthorized, you can reference the original 3DS authentication to demonstrate the cardholder enrolled knowingly.

This is a critically underused protection. 3DS2 frictionless flow means the authentication step is often invisible to the customer while still providing the liability shift.

**How to implement:**
- Mark the initial subscription transaction with the appropriate 3DS authentication data (ECI 05 for full auth, ECI 06 for attempted).
- Store the authentication value (CAVV/AAV) with the subscription record.
- When subsequent recurring charges are disputed, include the original 3DS authentication record in your evidence.

### Clear Billing Descriptors

Your billing descriptor must match the brand name the customer recognizes. If your trial is called "StreamFlix Free Trial" but your billing entity is "Digital Media Holdings LLC," cardholders will dispute the charge. Use a consistent descriptor that includes a recognizable brand name and a customer service URL or phone number.

### Email Notification Before Trial Conversion

Send a clear email 3–7 days before a free trial converts to a paid subscription. Include:
- The exact amount that will be charged.
- The billing date.
- A clear cancellation link.
- Customer service contact information.

This is now legally required in many U.S. states (California's Automatic Renewal Law, for example). More importantly, it dramatically reduces the "I didn't know I was being charged" disputes that make up the majority of subscription chargebacks.

### Cancellation Accessibility

A cardholder who can easily cancel will not dispute. Make cancellation available 24/7 via your website without requiring a phone call or chat. A cancellation process that takes more than three clicks is a chargeback generator.

## Evidence for Subscription Chargebacks

When a subscription chargeback arrives, your evidence package should tell the story of the customer's willing enrollment and ongoing service use.

**Enrollment records:**
- Timestamp and IP address of trial signup.
- Checkbox confirmation of terms of service and cancellation policy (with timestamp).
- Email address used for signup.
- Card verification result at enrollment.

**Communication records:**
- Order confirmation email sent (include email header metadata).
- Trial conversion reminder email sent (with timestamp and delivery confirmation).
- Any other service emails opened by the cardholder.

**Usage logs:**
- Login records showing cardholder accessed the service during the subscription period.
- Feature usage events (content streamed, documents accessed, app activity).
- For SaaS: API call logs, data storage records, feature activation.

**Terms and conditions:**
- Screenshot or PDF of the terms accepted, with the cancellation policy highlighted.
- If using a checkbox, evidence that it was checked (not pre-checked) before account creation completed.

**Recurring billing authorization:**
- Documentation that recurring billing was disclosed at signup and accepted.
- For Visa disputes under 13.2 (Cancelled Recurring Transaction), you must show either the transaction was not cancelled before processing or that the amount and billing date matched what was disclosed at signup.

## Visa 13.2 and Mastercard 4853

**Visa 13.2 — Cancelled Recurring Transaction:** Cardholder claims they cancelled the subscription before the disputed charge. Your defense: evidence that no valid cancellation was received before the billing date, or that the cancellation was received after billing had already processed.

**Mastercard 4853 — Cardholder Dispute:** Covers recurring charges the cardholder did not recognize or did not expect. Your defense: documentation of the recurring billing agreement at signup, notification emails, and service usage logs.

In both cases, merchants who can show the cardholder received service during the period being disputed — through login and usage logs — have a materially stronger case than those relying solely on billing agreement documentation.

## Summary

Subscription fraud is a composite problem: stolen card trials, repeat account abuse, and post-conversion friendly fraud all generate chargebacks under similar codes. The most effective merchant strategy combines technical prevention (card verification, 3DS on initial transaction, device fingerprinting for repeat trials) with process controls (clear terms disclosure, pre-conversion email notification, accessible cancellation) and evidence infrastructure (usage logs, enrollment records, communication archives). Merchants who build this infrastructure see substantially lower subscription dispute rates and higher win rates on disputes they do fight.
