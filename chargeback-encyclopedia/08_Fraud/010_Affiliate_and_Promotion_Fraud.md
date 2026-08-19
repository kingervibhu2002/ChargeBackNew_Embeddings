---
title: "Affiliate and Promotion Fraud"
section: "08_Fraud"
category: "Fraud Encyclopedia"
document_type: "Fraud Reference"
keywords: ["affiliate fraud", "promotion fraud", "coupon abuse", "promo stacking", "referral fraud", "click fraud", "discount exploitation", "policy abuse"]
difficulty: "Intermediate"
---

# Affiliate and Promotion Fraud

## What Is Affiliate and Promotion Fraud?

Affiliate and promotion fraud is a category of merchant abuse that exploits marketing programs, discount mechanisms, referral systems, and promotional offers to extract free or below-cost goods and services, generate illegitimate commissions, or obtain refunds on discounted purchases. Unlike pure payment fraud (using stolen cards), promotion fraud often uses the fraudster's own legitimate payment method — the exploitation is in the discount or commission structure, not the payment.

This fraud type is particularly costly because it is often invisible in standard fraud detection systems. Transactions complete cleanly, payment authorizes, and no chargeback is immediately filed. The cost appears as inflated commission payouts, eroded margins, or delayed fraud chargebacks after the promotional benefit has been extracted.

## Types of Promotion and Affiliate Fraud

### Coupon Abuse and Code Exploitation

**Bulk coupon code hoarding:** Fraudsters obtain legitimate coupon codes through customer email campaigns, browser extension leaks, public code-sharing sites (RetailMeNot, Honey), or social media exposure. They then use each code multiple times across different accounts, or distribute codes to networks of buyers.

**Coupon code brute-forcing:** Coupon codes with predictable patterns (SAVE10, PROMO2024, JUNE20) are systematically guessed and tested. Similar to card testing, bots cycle through variations until valid codes are identified, then exploit them at scale.

**Code interception:** If discount codes are transmitted or stored insecurely (in URL parameters, client-side JavaScript, or unencrypted API responses), they can be intercepted and reused.

**Single-use code resale:** A fraudster legitimately obtains a single-use code, photographs or copies it before using, and sells it on discount code marketplaces. The code may be sold to multiple buyers, each of whom tries to redeem it.

### Promo Stacking

Promo stacking occurs when a customer applies multiple discounts simultaneously in ways the merchant did not intend:
- Stacking a percentage discount code with a dollar-off code.
- Combining a promotional credit with a referral bonus.
- Applying a first-order discount to an account that has ordered before (via a new account).
- Using a category discount with a bundle discount for items that qualify for both.

Some stacking is a policy design flaw — the merchant's discount logic allows it when it should not. Other stacking requires intentional manipulation of checkout parameters. Either way, the merchant sells goods at below-cost margins.

### Referral Fraud

Referral programs ("give $10, get $10") are exploited when the referrer and the referred customer are the same person (or coordinating):

**Self-referral:** A customer creates a new account, refers themselves, earns the referral credit, and uses it against the same person's purchases. May be repeated with multiple fake accounts.

**Referral ring:** Multiple accounts controlled by a coordinated group refer each other in a ring, each earning referral credits that are then redeemed for real purchases. The merchant pays commissions for transactions that do not represent genuine new customer acquisition.

**Fake account referral farms:** A fraudster creates dozens of fake accounts, refers them all from a primary account, and earns referral credits against the threshold with no genuine new customers. If each fake account must make a qualifying purchase, the fraudster may make minimum purchases (charged to stolen cards or sacrificial legitimate cards) to trigger the referral credit.

### Affiliate Click and Conversion Fraud

Affiliate marketing programs pay commission (typically 5–20% of sale value) to affiliates for referring customers who purchase. Affiliate fraud involves manufacturing fake referral traffic or conversions:

**Click fraud:** Automated bots or paid click farms generate fake clicks on affiliate links, inflating click counts and sometimes triggering commission payments based on click volume rather than conversions.

**Conversion fraud:** The affiliate controls both the referral source and the buyer. They self-purchase (or recruit straw buyers), generating commission-qualifying transactions. They may use stolen payment cards for the purchase, collect the commission payout, and then the cardholder disputes the purchase. The merchant pays the commission and absorbs the chargeback loss.

**Cookie stuffing:** The affiliate drops affiliate tracking cookies on users' browsers without their knowledge or consent. When those users later visit the merchant and purchase through normal browsing, the affiliate receives commission credit for a referral they did not generate.

**Forced clicks:** Malvertising or browser hijacking that automatically clicks affiliate links in the background without user intent, generating artificial commission-qualifying traffic.

### Free Goods Exploitation Then Dispute

A sophisticated combination: a fraudster exploits a promotion to obtain goods at steep discount (or free), receives the goods, and then disputes the transaction. This results in a double loss — the promotional cost plus the chargeback.

Example: A merchant offers a "buy one get one free" promotion. A fraudster purchases a BOGO order, receives both items, disputes the entire purchase as unauthorized, and retains both items with a full refund.

## Detection Strategies

**Account velocity monitoring:** Track account creation rates, referral activities, and new-account purchase behavior in aggregate. Spikes in new account creation, particularly followed by immediate referral code generation, indicate referral fraud.

**Device fingerprint across accounts:** A single device fingerprint appearing across dozens of "different" accounts is a clear signal of self-referral or fake account farming. Fraud platforms that maintain device fingerprint history can flag this automatically.

**Email domain and pattern analysis:** Referral fraud accounts often use patterned email addresses (user001@domain.com, user002@domain.com) or disposable email providers. Flag accounts with similar email patterns or non-standard email domains.

**IP address clustering:** Multiple accounts created from the same IP address or IP range suggest a single operator. Residential proxy detection helps identify fraudsters attempting to distribute account creation across IP addresses.

**Referral network graph analysis:** Map referral relationships as a network graph. Legitimate referral programs produce tree structures (one referrer, multiple independent referrees). Fraud produces ring structures or single operators with hundreds of self-referrals.

**Affiliate conversion quality:** Monitor affiliate-referred customers for: chargeback rates above baseline, return rates above baseline, and customer lifetime value below baseline. Low-quality affiliate traffic that converts but immediately reverses is a fraud signal.

**Promo stacking logic testing:** Regularly test your own discount logic across combinations of active promotions. Identify and close unintended stacking opportunities before fraudsters discover them.

## Policy Controls

**Unique, single-use codes:** Generate unique per-customer coupon codes that cannot be shared. Use server-side validation with a "used" flag rather than client-side code validation.

**Code format randomization:** Use sufficiently random code formats (not sequential or predictable) to prevent brute-force guessing. A random alphanumeric 12-character code has 3.2 trillion possible values and cannot be practically brute-forced.

**Minimum referral quality requirements:** Require that referred accounts make a minimum purchase value, use a payment method not shared with the referring account, and have a shipping address not associated with the referring account.

**Time-delayed commission payouts:** Pay affiliate commissions only after the return window has closed. This eliminates the incentive to make purchases with stolen cards (which will be charged back) to earn immediate commission.

**Affiliate network vetting:** Require affiliates to provide business documentation, sign anti-fraud agreements, and undergo periodic traffic quality audits. Remove affiliates with consistently high chargeback rates on referred orders.

## Merchant Evidence for Promotion Fraud Chargebacks

When a promotion fraud transaction escalates to a chargeback:
- Document all promotional discounts applied to the order (showing the customer actively applied them).
- Show account creation history, referral activities, and prior order history.
- If the same device fingerprint appears across multiple accounts, include this in the rebuttal as evidence of coordinated abuse.
- For digital goods, include usage logs showing the product was accessed and used.

The core argument: the cardholder (or a coordinated party) exploited your promotional system, received full value from the transaction, and the chargeback is a secondary exploitation of the dispute mechanism.

## Summary

Affiliate and promotion fraud exploits the marketing infrastructure merchants build to attract genuine customers. The fraud is often low-visibility until it reaches significant scale. Detection requires monitoring program analytics (referral graphs, account clustering, device fingerprints) rather than standard transaction-level fraud detection. Prevention requires technical controls (unique codes, server-side validation, commission delay) and policy design that eliminates unintended stacking opportunities. When it escalates to chargebacks, it overlaps with friendly fraud dynamics — the cardholder extracted value and is now using the dispute system for a double recovery.
