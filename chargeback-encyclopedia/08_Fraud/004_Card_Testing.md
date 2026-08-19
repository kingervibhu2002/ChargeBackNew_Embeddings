---
title: "Card Testing / Carding"
section: "08_Fraud"
category: "Fraud Encyclopedia"
document_type: "Fraud Reference"
keywords: ["card testing", "carding", "BIN attack", "velocity fraud", "CAPTCHA", "VFMP", "micro-transaction", "card validation"]
difficulty: "Intermediate"
---

# Card Testing / Carding

## What Is Card Testing?

Card testing — also known as carding — is a fraud technique in which criminals use automated tools to validate stolen payment card data against real merchant checkout endpoints. The goal is not the purchase itself; the goal is to determine which card numbers are active and usable before deploying them for larger fraudulent purchases elsewhere.

Fraudsters obtain large batches of card numbers from data breaches, dark web marketplaces, and skimming operations. A batch of 100,000 stolen card numbers may include many that are expired, cancelled, or blocked. Card testing identifies the "live" cards quickly and efficiently, so the fraudster can sell the validated subset at a premium or use them directly.

From the merchant's perspective, a card testing attack looks like a sudden surge of very small transactions — often $0.00 authorization-only requests, $0.01 charges, $1.00 purchases, or low-value items like a single postcard or a minimum-value gift card. Hundreds or thousands of these transactions may hit within a few hours.

## BIN Attacks: A Related Threat

A BIN (Bank Identification Number) attack is a specific form of card testing where the fraudster knows the first six (or eight) digits of a card number and systematically generates and tests the remaining digits. Because credit card numbers follow predictable Luhn algorithm patterns, a fraudster with a BIN can generate all mathematically valid numbers within that range and test them in bulk.

A successful BIN attack against a vulnerable merchant can generate:
- Thousands of authorization attempts in a short window.
- Significant processor fees for each authorization (even declined ones often carry a small fee).
- A spike in decline rates that triggers issuer-level account reviews.
- Chargeback wave when the validated cards are used for fraud downstream (the testing merchant may not receive these chargebacks, but the downstream merchant will).

Card issuers are sensitive to BIN attacks because they see the same card numbers being tested across multiple merchants simultaneously.

## Impact on Merchants

Card testing is uniquely damaging because the merchant is used as a tool — their checkout is the testing infrastructure — and then suffers consequences:

### Direct Financial Impact
- **Transaction fees:** Processors charge per-authorization fees, often $0.05–$0.30 each. Ten thousand test transactions cost $500–$3,000 in fees alone.
- **Chargeback fees:** Test transactions that result in actual charges generate chargebacks when legitimate cardholders notice unauthorized micro-charges.
- **Refund processing costs:** If the merchant identifies the attack and refunds micro-charges proactively, there are refund processing costs.

### Visa Fraud Monitoring Program (VFMP) Risk
Visa's fraud monitoring program (VFMP) evaluates merchants by chargeback count and ratio. A card testing attack that generates hundreds of chargebacks from micro-transactions can push a merchant over the VFMP threshold:
- **Standard VFMP:** 75+ chargebacks in a month AND chargeback ratio over 0.65%.
- **High-Risk VFMP:** 1,000+ chargebacks in a month AND chargeback ratio over 2.00%.

Merchants placed in VFMP face monthly fines and eventual processor termination. A single card testing attack can trigger a monitoring program placement that takes 6–12 months to exit.

Mastercard's equivalent is the Excessive Chargeback Program (ECP). Both programs penalize merchants for fraud they did not cause but failed to prevent.

### Reputational and Operational Impact
- Processing account suspension by payment processor.
- Placement on card network terminated merchant lists (MATCH list / TMF).
- Legitimate customer decline rates may increase if the issuer blocks your MID due to fraud signals.
- Customer service volume spike from legitimate cardholders calling about unauthorized micro-charges.

## How to Detect a Card Testing Attack

**Velocity anomalies:** A sudden spike in transaction volume — especially of small-value transactions — is the clearest signal. Set real-time alerts for unusual transaction velocity relative to your historical baseline.

**High decline rates:** Card testing batches include many invalid cards. A spike in decline rate (especially if your normal decline rate is under 10% and suddenly jumps above 30–40%) strongly suggests testing activity.

**Same BIN across many transactions:** If dozens of failed authorizations all start with the same 6–8 digit BIN prefix, it is almost certainly a BIN attack.

**Unusual checkout behavior:** Card testers use bots that skip normal browsing behavior — no page views before checkout, extremely fast form completion (under 3 seconds), no mouse movement variation, no cart abandonment.

**Single-use email addresses:** Card testers often generate throwaway email addresses using patterns (test1@mail.com, test2@mail.com) or use disposable email domains (mailinator.com, guerrillamail.com).

**Geographic concentration:** Many card testing bots route through the same proxy or data center IP ranges. A cluster of transactions from the same IP block or from data center rather than residential IPs is suspicious.

## Chargeback Codes Triggered

Card testing that results in actual charges generates chargebacks under:
- **Visa 10.4:** Other Fraud — Card Absent Environment
- **Mastercard 4837:** No Cardholder Authorization
- **Mastercard 4863:** Cardholder Does Not Recognize

These are standard card-not-present fraud codes. The volume rather than individual transaction characteristics is what distinguishes card testing chargebacks from ordinary fraud chargebacks.

## Prevention Strategies

### CAPTCHA and Bot Detection
Deploy CAPTCHA (reCAPTCHA v3 preferred — it is invisible to legitimate users) on your checkout and login pages. Bot detection solutions like Cloudflare Bot Management, Imperva, or DataDome analyze request patterns to block automated checkout tools without adding friction for real customers.

### Velocity Rules
Implement per-IP and per-device velocity limits:
- Maximum X transactions per IP address per hour.
- Maximum X failed payment attempts per session before blocking.
- Flag accounts that create accounts and immediately attempt purchases.

Velocity limits must be tuned carefully — too aggressive and you block legitimate customers during peak periods.

### Card Fingerprinting
Tokenize and fingerprint card numbers (hashed, not stored) to detect the same card being used across multiple sessions or accounts. A card number appearing in 15 different orders in one hour is a testing signal.

### Fraud Scoring
Real-time fraud scoring (Kount, Signifyd, Forter) incorporates hundreds of signals at checkout and assigns a risk score. Card testers have distinct behavioral signatures that fraud models detect well. Configure automatic rejection above a risk score threshold.

### Minimum Transaction Value
If your business model allows, set a minimum transaction value. Card testers prefer $0.01 or $1.00 tests — a $5.00 minimum eliminates the cheapest testing vectors.

### 3DS on High-Risk Sessions
Trigger 3DS authentication challenges when fraud scoring indicates elevated risk. Card testing bots cannot complete cardholder challenges, which effectively filters them out while adding friction for legitimate customers only in high-risk scenarios.

### Monitor Authorization Decline Rates in Real Time
Set automated alerts for decline rate spikes and configure thresholds that trigger manual review or temporary velocity restriction. Catching an attack in hour one is far less damaging than discovering it the next morning.

## Responding to an Active Card Testing Attack

If you detect an active card testing attack:
1. Block or rate-limit the offending IP ranges immediately.
2. Enable stricter CAPTCHA or manual review on all new checkout attempts temporarily.
3. Alert your payment processor — they may have additional controls or intelligence.
4. Notify the card network fraud teams if you can identify the BIN range being attacked.
5. Document the attack timeline and attack characteristics for any future chargeback rebuttal.

## Summary

Card testing attacks are automated, high-velocity, and disproportionately damaging because the merchant suffers fees, chargebacks, and monitoring program risk for fraud they did not benefit from. Prevention requires technical controls at the checkout layer (CAPTCHA, velocity limits, bot detection, fraud scoring) rather than evidence collection after the fact. A merchant without these controls is a target of choice for carding operations, which actively seek out unprotected checkouts.
