---
title: "Amex Dispute Code F29 — Card Not Present"
description: "Complete merchant guide to American Express dispute code F29: CNP fraud dispute classification, distinction from F24, evidence requirements, and how SafeKey authentication protects merchants."
category: Amex
reason_code: "F29"
chargeback_type: "Card Not Present — CNP Fraud"
win_rate: Medium (with strong evidence); High (with SafeKey)
last_updated: 2026-06-29
tags: [amex, F29, CNP, card-not-present, fraud, safekey, chargeback-defense, online-fraud]
---

# Amex F29 — Card Not Present

## What This Dispute Code Means

Amex dispute code F29 — Card Not Present — is a CNP fraud classification used when a cardholder disputes a transaction that was processed without the physical card being present. Like F24 (No Card Member Authorization), F29 reflects a cardholder's assertion that they did not initiate or authorize the transaction. The code is most commonly applied to e-commerce transactions, telephone orders (MOTO), and recurring billing charges.

The practical difference between F24 and F29 within Amex's system is subtle and largely administrative — Amex issuers may route the same type of dispute under either code depending on internal protocols. Merchants should not assume the two codes require fundamentally different defenses. The evidence set, the response strategy, and the key liability-shifting mechanism (Amex SafeKey) are the same for both.

What is important is that F29 is a fraud code — not a "goods not received" or "credit not processed" dispute. The cardholder is asserting that the transaction itself was unauthorized, not that something went wrong with order fulfillment.

---

## Why F29 Occurs

F29 disputes arise from two primary sources:

**Genuine CNP fraud**: A criminal obtains the cardholder's account data through phishing, data breaches, credential stuffing, or social engineering and uses it to make unauthorized online purchases. The cardholder reviews their statement, sees unfamiliar charges, and files a dispute.

**Friendly fraud**: The cardholder made the purchase intentionally, received the goods or services, and then disputes the charge — claiming it was unauthorized. This is more common than most merchants expect, particularly for high-ticket items, digital goods that cannot be physically returned, and subscription products.

In both cases, your response strategy is identical — the goal is to demonstrate that the transaction was authorized and that the goods or services were delivered.

---

## Amex SafeKey: The Key Defense

SafeKey is Amex's 3-D Secure (3DS) implementation for CNP transactions. A successful SafeKey authentication is the most powerful defense against F29 because it creates a cryptographic proof that Amex itself verified the cardholder's identity at time of purchase. When this verification occurs:

- Amex bears the fraud liability if the transaction is later disputed as unauthorized
- The F29 dispute cannot succeed against the merchant — the liability has already been shifted to the issuer

For merchants with meaningful Amex CNP volume, SafeKey integration is the highest-ROI fraud prevention investment available. Modern 3DS2-based SafeKey implementations offer frictionless authentication for most low-risk transactions — cardholders see no friction, but the liability protection is still in place.

**SafeKey evidence to submit with an F29 rebuttal:**
- AEVV (American Express Verification Value) — the authentication token generated at checkout
- Authentication method and timestamp
- Confirmation that the AEVV was included in the authorization request

---

## Evidence Requirements Without SafeKey

When SafeKey was not used, merchants must construct a compelling evidentiary case from transaction-level data. Amex applies a high standard — a single data point is rarely enough. The following evidence elements should be combined:

### Address Verification Service (AVS)
AVS compares the billing address entered at checkout against the address on file with the card issuer. A full AVS match (street address and zip code both match) is strong evidence that the person who placed the order had access to the cardholder's billing information — consistent with the cardholder themselves placing the order.

Document: AVS result code, the billing address matched, and the timestamp of the authorization.

### CVV2 Result
CVV2 is the 3-digit code on the back of the physical card (or 4-digit on the front of some Amex cards). Merchants are not permitted to store CVV2 after authorization. A correct CVV2 entry means the person placing the order had physical possession of the card or its data at time of checkout.

Document: CVV2 match confirmation from your payment gateway or acquirer.

### IP Address and Device Data
- IP address geolocation consistent with the cardholder's billing address
- Device fingerprint matching prior orders from the same account
- Browser/user-agent data consistent with prior sessions

These elements establish that the order was placed from a device and location consistent with the cardholder's known behavior.

### Prior Purchase History
If the cardholder has placed multiple previous orders using the same card without prior disputes, this pattern contradicts the claim that the transaction was unauthorized. Present: dates, amounts, and products of all prior orders within the last 12–24 months.

### Delivery Evidence
If physical goods were shipped:
- Carrier tracking number showing delivery to the cardholder's billing address
- Signed proof of delivery where available
- Delivery confirmation email sent to the cardholder's address

Delivery to the cardholder's own billing address is a significant counter to fraud claims — criminals typically ship to alternative addresses.

### Account Activity
If the order was placed through a registered account:
- Login timestamp and IP address matching the order time
- Account email address consistency (same email for account registration and order confirmation)
- Any post-order activity from the account (reviews, return requests, follow-up orders)

---

## Structuring the F29 Response

**Rebuttal letter structure:**

1. Transaction identification (date, amount, order number, cardholder name on account)
2. Authentication evidence (SafeKey AEVV if available, or statement that 3DS was not available)
3. Address and identity evidence (AVS result, CVV result, IP/device data)
4. Behavioral evidence (prior purchase history, account activity)
5. Delivery confirmation (if applicable)
6. Request for reversal

Amex reviewers appreciate a structured, factual rebuttal. Avoid emotional or defensive language. The goal is to present a coherent picture that makes it highly plausible the cardholder authorized the transaction.

---

## F29 Prevention Strategies

Beyond SafeKey, additional controls reduce F29 exposure:

**Require CVV2 for all Amex transactions.** Do not process orders where CVV2 fails to match. The incremental revenue lost from declined orders is far less than the cost of fraud chargebacks.

**Screen high-risk order patterns.** Orders with mismatched billing/shipping addresses, international shipping on domestically issued cards, multiple high-value items, and rush delivery to freight forwarders are disproportionately fraudulent. Implement velocity rules and manual review for orders matching these patterns.

**Use email and phone verification for high-value orders.** For orders above a threshold (e.g., $300 or $500), contact the customer through the email or phone number on the account to confirm the order. This step filters out fraudsters and provides corroborating evidence for legitimate orders.

**Enable 3DS2/SafeKey for all CNP Amex transactions.** Many payment platforms now include SafeKey/3DS2 as a configurable option. Enable it and monitor authentication rates to ensure frictionless authentication is working for your customer base.

---

## Frequently Asked Questions

**Q: Is F29 harder to win than F24?**
A: In practice, no. The dispute mechanics and evidence requirements are nearly identical. The code designation is an internal Amex classification. Focus on the quality of your evidence rather than the specific code.

**Q: A recurring subscription charge was disputed as F29. How do I respond?**
A: Include the original sign-up date and confirmation, the recurring billing authorization your terms of service describe, prior billing history showing earlier charges that were not disputed, and the billing notification sent before this charge. If the cardholder signed up with their own credentials and email, their claim of non-authorization is significantly weakened.

**Q: The disputed Amex transaction is for a digital product — there is no delivery address. How do I prove delivery?**
A: For digital goods, "delivery" evidence includes: server-side download logs (IP, timestamp, session ID), product activation records (license key redemption), account access logs showing the digital product was accessed, and the confirmation email with the download link sent to the cardholder's address. Strong server-side logging is essential for digital merchants.

**Q: Our fraud filters flagged this order but we processed it anyway. Does that hurt our defense?**
A: Not necessarily in the dispute itself — Amex does not see your internal fraud score. However, if your own systems flagged the order as suspicious and you processed it, that is a risk management problem worth addressing. Going forward, use fraud flags as actionable decision points: review orders your systems flag before authorizing them.

**Q: How long do I have to respond to an F29 dispute?**
A: Amex gives merchants **20 days** from the date of the dispute notification. This is shorter than Visa (30 days) and Mastercard (45 days). Set up immediate alert routing for Amex disputes to ensure you do not miss this window.
