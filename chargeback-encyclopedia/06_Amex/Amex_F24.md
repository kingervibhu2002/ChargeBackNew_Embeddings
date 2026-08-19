---
title: "Amex Dispute Code F24 — No Card Member Authorization (CNP Fraud)"
description: "Complete merchant guide to American Express dispute code F24: the most common Amex fraud code for online transactions, SafeKey authentication, evidence requirements, and how to build a winning defense."
category: Amex
reason_code: "F24"
chargeback_type: "No Card Member Authorization — Card Not Present Fraud"
win_rate: Medium (with strong evidence); High (with SafeKey)
last_updated: 2026-06-29
tags: [amex, F24, CNP-fraud, no-authorization, safekey, AVS, CVV, online-fraud, chargeback-defense]
---

# Amex F24 — No Card Member Authorization

## What This Dispute Code Means

Amex dispute code F24 is the most common fraud-related chargeback code for merchants who accept American Express online. It is filed when a cardholder states they did not authorize a card-not-present (CNP) transaction — typically an e-commerce purchase. The cardholder's claim may be genuine (their card data was stolen and used fraudulently) or it may be friendly fraud (they made the purchase and are disputing it).

The distinction between genuine fraud and friendly fraud matters less than it might seem when building your defense — your evidence strategy is identical in both cases. What changes is the probability of success: against genuine fraud, strong authentication evidence shifts liability back to Amex; against friendly fraud, the same evidence proves the cardholder placed the order.

F24 sits at the top of most online merchants' chargeback code frequency lists because e-commerce card-not-present fraud is a major, ongoing issue. Amex's bar for compelling evidence is higher than Visa or Mastercard — Amex has a premium brand standard to maintain, and that standard extends to dispute resolution.

---

## The SafeKey Advantage: Liability Shift for CNP

American Express SafeKey is Amex's implementation of 3-D Secure (3DS) authentication. When a cardholder completes SafeKey authentication, they verify their identity through a mechanism controlled by Amex (not just the merchant) — typically a one-time passcode sent to their phone or email.

**A successful SafeKey authentication produces an AEVV (American Express Verification Value)** — a cryptographic token submitted with the authorization. If Amex-authenticated fraud occurs on a SafeKey-verified transaction, the F24 liability shifts to Amex as the issuer. The merchant is protected.

This is the most direct and reliable F24 defense available. SafeKey integration is strongly recommended for all merchants with material Amex CNP volume.

SafeKey also supports **frictionless authentication** via 3DS2 — for low-risk transactions, the cardholder identity check happens in the background without any visible prompt. This reduces cart abandonment while maintaining the liability shift benefit.

---

## Evidence Hierarchy for F24 (Without SafeKey)

When SafeKey was not used, merchants must build their defense from transaction data. Amex evaluates this evidence holistically, but certain elements carry significantly more weight:

### Tier 1: Strongest Evidence

**Prior purchase history from the same cardholder/device**
If the same cardholder has placed 2, 3, or more previous orders using the same card with no prior disputes, this pattern is highly consistent with an authorized customer. Amex issuers find repeat-customer history compelling — a fraudster rarely uses a stolen card for multiple purchases over months without triggering earlier disputes.

Include: dates, amounts, and products of prior orders. If prior orders were delivered successfully to the same address, include delivery confirmations.

**Delivery to the cardholder's billing address**
A shipping address that matches the billing address on the card (confirmed via AVS) is strong evidence of an authorized transaction. Criminals typically ship stolen-card purchases to drop addresses, not the cardholder's home.

**Successful AVS and CVV match**
- **AVS (Address Verification Service)**: The billing street address and zip code provided at checkout matched the address on the card account. Full match (both street and zip) is ideal.
- **CVV2 match**: The 3-digit security code printed on the card's signature panel was correctly entered. CVV is not stored by merchants after authorization — a correct CVV indicates the physical card (or its data) was present at the time of purchase.

### Tier 2: Supporting Evidence

**IP address and geolocation consistency**
The IP address used to place the order should be geolocated and compared to the cardholder's billing address. A US billing address and an order placed from a US-based IP is consistent. An order from an overseas IP on a US-issued card is a yellow flag that may work against your defense if unexplained.

If the IP is consistent with prior orders from the same account, note this in your rebuttal.

**Device fingerprint**
If your checkout platform captures device ID or browser fingerprint, and this matches a device used in prior successful orders from the same cardholder, this is useful corroborating evidence. Same device = same customer.

**Account login record**
If the order was placed through a registered account (not guest checkout), show that the cardholder's credentials were used to log in at the time of purchase. Include the login timestamp and IP address.

**Order confirmation email delivery**
Show that an order confirmation was sent to the email address on the account and was not bounced. If your email platform tracks opens (pixel tracking), log confirmation of email opening — a cardholder who opened the order confirmation email received it.

**Customer service interactions post-order**
Any contact from the cardholder after the order — asking about delivery status, requesting a change, etc. — proves they knew about the order. Include email transcripts, chat logs, or call records.

---

## Amex's Higher Bar for Compelling Evidence

Amex evaluates evidence with a stricter lens than Visa or Mastercard. A rebuttal that would succeed on Visa may not succeed on Amex. Specific considerations:

- **Single-factor evidence is rarely sufficient.** AVS match alone, or CVV alone, typically does not overcome an F24 with Amex. You need multiple corroborating data points.
- **Guest checkout orders are harder to defend.** Without an account login record, you lose the ability to cite login history. Guest checkout removes a layer of authentication evidence.
- **International IP addresses with domestic billing addresses are a liability.** If you cannot explain the geographic mismatch, do not include IP data that works against you.
- **Amex tends to give cardholders the benefit of the doubt on first disputes.** Repeat disputers from the same cardholder (if you have multiple orders) are treated differently — note if this is the first dispute from an otherwise consistent customer.

---

## Structuring Your F24 Rebuttal

An effective F24 rebuttal for Amex follows this structure:

1. **Opening statement**: Identify the transaction and state clearly that it was authorized by the cardholder based on the evidence below.
2. **Authentication evidence**: Lead with your strongest data — SafeKey AEVV, or the combination of AVS/CVV match + delivery to billing address.
3. **Identity evidence**: Prior purchase history, device match, account login.
4. **Delivery confirmation**: If applicable, proof the goods arrived at the cardholder's address.
5. **Summary request**: Ask Amex to reverse the dispute based on the compiled evidence.

Keep the letter to two pages maximum. Attach labeled exhibits. Amex reviewers process high volumes — clarity and conciseness win.

---

## Frequently Asked Questions

**Q: How is F24 different from F29 (Card Not Present)?**
A: Both codes involve CNP fraud disputes. F24 specifically cites "No Card Member Authorization" as the cardholder's claim. F29 is a broader CNP fraud classification. In practice, your evidence strategy and response are nearly identical for both. Some Amex issuers file F24 or F29 based on their internal routing rather than any meaningful substantive difference in the cardholder's claim.

**Q: If I have a SafeKey AEVV, do I still need to submit other evidence?**
A: The AEVV alone is typically sufficient to obtain a liability shift. However, submitting it within a brief rebuttal explaining the authentication result is best practice — Amex reviewers appreciate context. Include the AEVV value, the authentication method, and the date of authentication.

**Q: The billing and shipping addresses matched but the order was a gift. Can I still win?**
A: Yes, if you can document that the order was shipped to the billing address (same address for billing and shipping) or that both parties were in the same household. Gift orders shipped to the billing address are stronger than those shipped elsewhere. If shipped to a different address, include any gift messaging or notes from the order that suggest it was an intentional gift.

**Q: We process a lot of Amex and our F24 rate is rising. What should we do?**
A: Implement SafeKey immediately if not already integrated — this is the single most impactful change. Additionally, review your order data for patterns in F24 disputes (common shipping addresses, IP ranges, email domains, product types) and implement fraud screening rules targeting those patterns. SafeKey frictionless authentication handles the legitimate-customer volume without adding friction.

**Q: A cardholder disputes via F24 but later contacts our support asking where their order is. What do we do?**
A: This is strong evidence of friendly fraud — the cardholder is simultaneously disputing the transaction and inquiring about delivery, which proves they knew about the order. Preserve this support record and include it prominently in your rebuttal. This type of evidence is highly effective with Amex issuers.
