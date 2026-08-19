---
title: "Synthetic Identity Fraud"
section: "08_Fraud"
category: "Fraud Encyclopedia"
document_type: "Fraud Reference"
keywords: ["synthetic identity", "fabricated identity", "bust-out fraud", "thin file", "credit building", "identity fraud", "account takeover"]
difficulty: "Advanced"
---

# Synthetic Identity Fraud

## What Is Synthetic Identity Fraud?

Synthetic identity fraud is the creation of a fictitious persona using a combination of real and fabricated information. Unlike traditional identity theft — where a fraudster steals and uses an existing person's complete identity — synthetic fraud constructs a new "person" who does not actually exist.

The most common pattern in the United States involves a real Social Security Number (often belonging to a child, elderly person, or recent immigrant with no credit history) combined with a fabricated name, date of birth, and address. Because the SSN is real, it passes basic verification checks. Because the name does not match any real person, the victim has no way to discover the fraud until significant damage has been done.

Synthetic identity fraud is estimated to account for 80–85% of all identity fraud losses in the United States according to McKinsey & Company, with losses exceeding $20 billion annually in the U.S. alone. It is the fastest-growing financial crime category globally.

## How Fraudsters Build a Synthetic Identity

The construction of a usable synthetic identity is a patient, multi-stage process.

### Phase 1: SSN Acquisition
Real SSNs are purchased on dark web marketplaces, obtained through data breaches, or selected using pattern knowledge of SSN issuance ranges. Child SSNs are particularly valuable because children typically have no credit file — meaning the synthetic identity can be built without conflicting with any existing credit history.

### Phase 2: Credit File Creation
The fraudster applies for credit using the synthetic identity. The first applications will fail or return a "thin file" or "no file" result. However, the application itself may create a credit file entry (an inquiry). The fraudster may also be added as an authorized user on a legitimate cardholder's account, which "seeds" the synthetic identity's credit file with positive payment history.

### Phase 3: Credit Building ("Nurturing")
Over months or years, the fraudster cultivates the synthetic identity: secured cards, small retail credit lines, timely payments. The synthetic identity's credit score improves steadily. This phase can take 6–24 months. During this period, the identity looks indistinguishable from a thin-file legitimate consumer.

### Phase 4: Bust-Out
Once credit limits across multiple accounts are substantial, the fraudster maxes out all available credit simultaneously — purchases, cash advances, balance transfers — then disappears. No payments are made. All accounts charge off. This is called a "bust-out."

## Why Synthetic Identity Fraud Is Hard to Detect

Traditional fraud detection relies on matching presented identity to known identity. Synthetic fraud defeats this:

- **No real victim to report fraud:** The SSN owner (often a child) is unaware their number is being used. There is no fraud complaint until the bust-out phase, often years later.
- **Positive credit behavior:** The fraudster builds a genuine payment history. Underwriting models score this as low risk.
- **Clean device and IP:** Synthetic fraudsters often operate from clean environments. No prior fraud flags on the device.
- **Consistent application behavior:** Applications may look identical to legitimate thin-file consumers.

The identity is real in every verifiable sense. The person is not.

## Warning Signals for Merchants

While synthetic fraud is primarily a credit extension problem, merchants see it as:

**New account + high-value immediate purchase:** A newly created account with no history placing a large order is a red flag, especially for high-resale-value goods (electronics, jewelry, gift cards).

**Thin or mismatched identity signals:**
- SSN date of issuance does not match the stated age of the individual.
- Phone number registered recently (new number associated with new identity).
- Email address created recently with no social footprint.
- Address exists but has no history of occupancy associated with the stated name.

**Velocity signals:**
- Multiple accounts created with similar information variations (synthetic fraudsters often manage portfolios of fake identities).
- Multiple purchases shipped to the same address under different names.

**Device and behavioral signals:**
- Device associated with multiple identities (detected via device fingerprinting).
- Unusual purchasing pattern — no browsing history, direct add-to-cart, checkout in under 2 minutes.

## Merchant Impact

Merchants face synthetic fraud primarily in:

- **Buy Now Pay Later (BNPL) and installment products** where the fraudster is extended merchant-level credit.
- **High-value CNP orders** for resaleable goods.
- **Account creation and onboarding** where the synthetic identity is used to obtain signup bonuses, promotional credits, or subsidized first orders.

The merchant's exposure occurs at the bust-out phase or when the underlying card account is eventually closed and all transactions charged back. By then, goods have long since been shipped. Delivery confirmation is useless because the fraudster controlled the delivery address.

## The No-Win Problem for Merchants

This is the defining characteristic of synthetic fraud from a merchant's perspective: **the identity presented is internally consistent and passes all standard checks.** AVS may match. CVV may match. 3DS may authenticate. IP may geolocate correctly. The fraudster has invested months ensuring everything checks out.

When the chargeback arrives, the merchant cannot prove the customer was not who they claimed to be — because the fraudster constructed an identity designed to withstand exactly that scrutiny. Standard compelling evidence (delivery proof, usage logs) may exist but does not address the root question: was this a real person?

## Link to Account Takeover

Synthetic identities are sometimes layered with account takeover tactics. A fraudster may:
1. Create a synthetic identity with a legitimate email address obtained through phishing.
2. Use the synthetic identity to create accounts, bypassing new-account fraud controls.
3. Combine purchased card data from breaches with the synthetic identity for purchases.

This blurring of fraud types complicates detection: signals that would flag account takeover (new device login) may not appear because the account was never "taken over" — it was synthetic from inception.

## Prevention Strategies

**Identity verification at onboarding:** For high-risk products (credit extensions, high-value first orders), require government ID verification (KYC). Services like Socure, Alloy, and LexisNexis RiskView cross-reference SSNs, names, and dates of birth against authoritative databases to detect synthetic patterns.

**Behavioral biometrics at account creation:** Keystroke dynamics, mouse movement patterns, and form-fill speed can distinguish human new-user behavior from automated synthetic identity creation.

**Velocity controls on new accounts:** Impose purchase limits, delayed shipping, or manual review for accounts under 30 days old, especially for high-value or high-resale-value goods.

**Device consortium data:** Fraud intelligence platforms that aggregate device signals across many merchants can flag devices associated with multiple synthetic identities.

**Email and phone intelligence:** Verify that email and phone number have reasonable age and association history. Newly created Gmail accounts associated with a "10-year customer" are suspicious.

## Summary

Synthetic identity fraud represents the most sophisticated end of the identity fraud spectrum. Merchants selling high-value goods or extending credit face material exposure, particularly at the bust-out moment. Because the fraud is often undetectable with standard controls, the most effective merchant strategies focus on new-account friction, identity verification services, and device consortium data rather than transactional evidence collection after the fact.
