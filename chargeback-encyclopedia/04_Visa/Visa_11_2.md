---
title: "Visa 11.2 — Declined Authorization"
section: "04_Visa"
category: "Visa Reason Codes"
network: "Visa"
reason_code: "11.2"
document_type: "Reason Code Reference"
keywords: ["declined authorization", "11.2", "authorization declined", "force transaction", "retry logic", "no defense"]
difficulty: "Beginner"
---

# Visa 11.2 — Declined Authorization

## Definition

Visa reason code 11.2 applies when a merchant completed a transaction after receiving a **declined authorization response** from the issuer. The merchant either deliberately forced the transaction through, processed it offline after a decline, or used a retry loop that resulted in completing a transaction that should have been rejected.

This is one of the clearest examples of a chargeback where the merchant has essentially no defense. The issuer said "no." The merchant completed the transaction anyway. The cardholder disputes the charge, and the chargeback is valid by definition — authorization was explicitly denied.

11.2 chargebacks represent a fundamental breach of the payment processing agreement. Merchants are contractually obligated to honor authorization decisions. Processing a transaction that has been declined is a violation that exposes the merchant to chargebacks, fines, and potential termination of their processing account.

---

## Why Authorization Declines Happen

Understanding why cards get declined helps merchants build systems that handle declines properly rather than attempting to work around them.

### Issuer-Side Decline Reasons
- **Insufficient funds:** The cardholder has exceeded their credit limit or their bank account has insufficient balance.
- **Suspicious activity:** The issuer's fraud detection system flagged the transaction as potentially fraudulent.
- **Card reported lost or stolen:** The card has been flagged in the issuer's system.
- **Expired card:** The card's expiration date has passed.
- **Account closed:** The cardholder's account has been closed.
- **Do not honor (Code 05):** A general decline that can cover multiple issuer-side reasons.
- **Restricted card (Code 62):** The card is restricted from certain transaction types.
- **Exceeds frequency limits:** The cardholder has exceeded their daily transaction count or amount limits.

### Technical Decline Reasons
- **Timeout:** The authorization request timed out before a response was received.
- **Invalid card number:** The card number failed a validation check.
- **Communication failure:** A network or system issue prevented proper authorization.

---

## How Declined Transactions Get Processed Anyway

### Forced Transactions
Some older POS systems allow a "force" function where a clerk can enter an authorization code manually and complete a transaction even after receiving a decline. This is almost always misuse — force transactions are intended for voice authorizations where the clerk obtained a code by phone, not for overriding electronic declines with a fabricated or reused code.

### Retry Logic Errors
E-commerce systems often include retry logic — if an authorization fails, the system automatically retries with slightly modified parameters (different amount, different card brand routing, different transaction type). In some cases, poorly designed retry logic can result in a declined transaction being resubmitted and processed under circumstances that shouldn't have been used, generating a transaction that violates authorization rules.

### System Configuration Errors
Some payment systems have configuration errors that allow offline fallback even when a decline response has been received — the system treats any non-approved response as a "connection failure" and falls back to offline mode, completing the transaction.

### Staff Overriding Declines
In retail environments, a determined customer or a poorly trained employee might attempt to complete a transaction after a decline by using a different method — swiping when the chip declined, or trying an older terminal that has less strict authorization logic. Any transaction completed after a valid decline has been received exposes the merchant to 11.2 liability.

### Incorrect Decline Interpretation
Sometimes merchants misinterpret response codes. A "referral" response (code 01 or 02) means the merchant should call for voice authorization — it is not an approval and should not be treated as one. Processing after a referral without obtaining a voice approval can result in an 11.2 chargeback if the voice authorization is never actually completed.

---

## Common Scenarios

- An e-commerce merchant's retry logic retries a declined transaction with a different amount and receives an approval — but the approval was for the wrong amount and the underlying card was decline-listed. The cardholder disputes both the original decline and the eventual charge.
- A retail clerk at a small store uses the terminal's "force" function to complete a transaction for a regular customer after receiving a decline. The customer disputes the transaction later, and the 11.2 chargeback arrives.
- A merchant's payment gateway has a misconfiguration that routes declined transactions into an offline queue. These are batch-processed overnight. The resulting transactions are declined by the issuer upon settlement.
- A hotel pre-authorizes a card for room rental, receives a decline on the final settlement attempt, but continues to process the checkout and bills the card through an alternate method that bypasses the authorization check.

---

## Merchant Liability

Liability under 11.2 is absolute. There are no circumstances under which completing a transaction after an explicit authorization decline is defensible. The authorization system exists precisely to give the issuer the ability to approve or reject transactions. Bypassing that decision eliminates the merchant's chargeback protection entirely.

If you receive an 11.2 chargeback and it is accurate — meaning you did process the transaction after a decline — accept it. Do not file a representment. Focus instead on identifying and fixing the system or process that allowed the declined transaction to complete.

---

## Required Evidence

There is essentially no evidence that will overcome a valid 11.2 chargeback. However, there are narrow scenarios where a representment makes sense:

- **Authorization was actually approved, not declined:** The chargeback was filed in error. Your authorization records show an approval code, not a decline. This would be a procedural error on the issuer's side.
- **The decline was for a different transaction:** If the decline response was for a prior authorization attempt and the final completing transaction had a valid separate approval, document this clearly.
- **System error created a false decline log:** In extraordinary cases, a system error may have logged a decline that never occurred. Processor logs can support this.

**Evidence for these narrow defenses:**
- Authorization response records showing approval codes
- Processor transaction logs with timestamps
- Payment gateway records showing the complete authorization flow

---

## Winning Strategy

For most 11.2 chargebacks, there is no winning strategy — accept the chargeback. The energy should go into:

1. **Identifying the root cause.** Was it forced manually by staff? Retry logic? A system configuration error? Find the exact mechanism that allowed the declined transaction to process.
2. **Fixing the system.** Disable force transaction capability unless properly controlled. Fix retry logic so it does not complete declined transactions. Test payment gateway configuration.
3. **Training staff.** Reinforce that a decline means "no transaction" — not "try again differently."
4. **If you believe the chargeback was filed in error** (you have a genuine approval code), pull your authorization records and file a representment with that evidence.

---

## Losing Mistakes

- **Filing a representment without an approval code.** If your authorization records show a decline, you have nothing to submit.
- **Arguing the customer "said it was fine."** The cardholder's verbal assurance at the point of sale is irrelevant to authorization compliance.
- **Claiming the system "glitched."** A system glitch that completes a declined transaction is a system error, and the loss falls to the merchant who operated that system.
- **Submitting a signed receipt.** A signed receipt doesn't override the authorization decline.

---

## Prevention

- **Strictly honor decline responses.** Train all staff: a decline code means the transaction cannot be completed. Period.
- **Disable or audit force transaction capability.** The force function should require a manager code and should only be used when a valid voice authorization code has been obtained through the proper channel.
- **Audit retry logic.** If your e-commerce system retries failed authorizations, review the retry logic carefully. Retries should only be attempted with a new authorization request, not as a workaround to a decline.
- **Test offline fallback configuration.** Ensure your payment system does not fall into offline mode after a decline — offline mode should only trigger on connectivity failures, not on issuer declines.
- **Review daily authorization reports.** Flag any batch that contains transactions without a matching approved authorization code.

---

## Timeline

| Stage | Timeframe |
|---|---|
| Transaction processed (post-decline) | Day 0 |
| Cardholder notices charge | Typically within 30–60 days |
| Dispute filed with issuer | Within 120 days of transaction |
| 11.2 chargeback received | After issuer reviews dispute |
| Merchant response deadline | 30 days from notification |

---

## Frequently Asked Questions

**Q: A customer's card declined but they insisted it was fine and asked us to try again. We tried again and it went through. Is that a problem?**
A: Potentially. If the first transaction was declined and you retried with the same card and it was approved on the second attempt, that retry may have captured different authorization parameters. If the retry resulted in a legitimate approval — different authorization code, clean response — you are likely protected. If the "approval" came from forcing the transaction or from an offline fallback after the decline, you have exposure to an 11.2 chargeback.

**Q: What is the difference between a decline and a referral?**
A: A referral (response code 01 or 02) means "call us for voice authorization" — not an approval and not a decline. You must call the authorization center, provide the card details, and obtain a voice authorization code before completing the transaction. Processing after a referral without calling for voice auth is equivalent to processing without authorization.

**Q: My payment processor is at fault — they configured the system wrong. Can I recover the chargeback loss from them?**
A: This depends on your processing agreement and the specific failure. Document the misconfiguration thoroughly, escalate to your processor in writing, and review your contract for liability provisions related to processing errors. Some processors will make merchants whole for configuration errors; others will not.

**Q: How common are 11.2 chargebacks?**
A: They are relatively uncommon in well-run operations because modern payment systems are designed to prevent declined transactions from completing. They are more common in legacy systems, heavily customized payment environments, and businesses where staff have override capabilities.

**Q: Can multiple retry attempts generate multiple 11.2 chargebacks?**
A: Each completed transaction that was preceded by a decline is a potential 11.2 chargeback. If your retry logic generates multiple declined-then-completed transactions, each one is a separate chargeback exposure. Fix the retry logic immediately.

---

## Sample Rebuttal Points

For the narrow case where you have a genuine approval record:

- "We dispute this chargeback on the basis that the transaction referenced was processed with a valid authorization approval. Attached are our processor's transaction records showing authorization code [X] was issued at [timestamp], confirming that the transaction received issuer approval — not a decline."
- "Our payment gateway records (attached) show the complete authorization flow for this transaction. The final authorization request returned approval code [X]. No decline response was received for this completing transaction. We request that the issuer review their records and confirm the authorization response for the specific authorization request that resulted in the completed transaction."
- "We acknowledge that a prior authorization attempt for this cardholder was declined. However, the completing transaction used a separate authorization request that received approval code [X], as shown in our attached authorization records. The 11.2 code appears to have been applied incorrectly to a separately authorized transaction."
