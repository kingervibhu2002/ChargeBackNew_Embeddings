---
title: "Visa 11.3 — No Authorization"
section: "04_Visa"
category: "Visa Reason Codes"
network: "Visa"
reason_code: "11.3"
document_type: "Reason Code Reference"
keywords: ["no authorization", "11.3", "forced transaction", "voice authorization", "partial authorization", "unauthorized transaction"]
difficulty: "Beginner"
---

# Visa 11.3 — No Authorization

## Definition

Visa reason code 11.3 applies when a transaction was completed without ever obtaining an authorization from the issuer. Unlike 11.2 (where authorization was attempted but declined), 11.3 means no authorization request was made at all — or the authorization process was so flawed that no valid approval exists for the transaction.

Authorization is the cornerstone of card payment processing. When a cardholder presents a card, the merchant requests permission from the issuer (via the card network) to complete the transaction. The issuer approves or declines. An 11.3 chargeback means this step was skipped, bypassed, or fundamentally broken.

The requirement to obtain authorization before completing a card transaction is absolute under Visa's processing rules. Merchants agree to this requirement in their merchant processing agreement. Violations — whether accidental or deliberate — result in full chargeback liability.

---

## Scenarios That Trigger 11.3

### Forced Transactions Without Voice Authorization
Some POS systems include a "force" feature designed for use when a merchant has obtained a voice authorization code by calling the authorization center. This function allows the merchant to manually enter the authorization code and complete the transaction. It is sometimes misused — clerks enter a made-up code, a reused code from a previous transaction, or "1234" to bypass the authorization system entirely. This produces a transaction with no valid authorization, directly triggering 11.3 liability.

### Transactions Processed Above the Floor Limit Without Authorization
In environments with floor limits — thresholds below which authorization is not required — a transaction at or above the floor limit that is processed without authorization results in 11.3 exposure. Floor limits should effectively be set at $0 in modern processing environments, but legacy systems may retain non-zero limits.

### Voice Authorization Not Completed Properly
A merchant calls for a voice authorization, is told to "call back" or receives an incomplete response, and processes the transaction anyway without a confirmed approval code. No valid authorization exists.

### Batch Processing Errors
In some batch or offline processing scenarios, transactions may be submitted for settlement without having gone through a proper authorization cycle. This can happen due to system errors, misconfigured software, or manual batch compilation errors.

### Partial Authorization Not Handled
Visa requires merchants to handle partial authorization approvals — where the issuer approves a transaction for less than the full requested amount (common with prepaid cards). If a merchant ignores a partial authorization and processes the full original amount instead, the excess is unauthorized. This can trigger 11.3 for the unauthorized portion.

### Merchant-Initiated Transactions Without Proper Agreement
Merchants who process recurring or installment transactions (subscriptions, payment plans) without a valid cardholder agreement on file, or who process a new transaction outside the terms of an existing agreement, may generate 11.3 disputes for transactions that lack a valid authorization basis.

---

## Common Scenarios

- A busy retail store has a terminal malfunction. Staff use the force function to complete transactions, entering any numbers into the authorization code field. The batch is submitted without valid auth codes. Multiple 11.3 chargebacks arrive.
- An online merchant's payment system has a bug that routes certain transaction types into a "complete without auth" path. The transactions settle without ever receiving issuer approval. Cardholders dispute the charges as 11.3.
- A gym processes the first month's membership for a new member but doesn't properly set up the recurring billing authorization. The monthly charges thereafter lack a valid standing authorization agreement.
- A hotel attempts to settle for incidentals after checkout but the card has expired. Rather than requesting a new authorization, the system processes the settlement against the old expired authorization, which is no longer valid.
- A merchant accepts a prepaid card for a $100 purchase, receives a partial authorization for $60 (the remaining balance), and processes $100 anyway. The $40 difference has no authorization.

---

## Merchant Liability

Merchants bear complete liability for 11.3 chargebacks. There is no exception — if you did not obtain a valid authorization, the chargeback will stand. The only disputes worth filing are those where an authorization did exist but was incorrectly characterized as missing.

Authorization compliance is not just a chargeback risk issue — merchants with patterns of no-authorization transactions risk processing agreement termination and fines from their acquirer.

---

## Required Evidence

For the narrow case where you believe an authorization did exist, produce:

- **Authorization record with approval code:** The specific approval code, timestamp, and issuer response for the transaction in question. This must be a genuine approval response, not a force code or fabricated number.
- **Voice authorization documentation:** If the transaction was authorized by voice, the authorization log should record the date, time, authorization code, card number (last four), and name of the authorization center representative who issued the code.
- **Processor transaction records:** Complete audit trail from your payment gateway or processor showing the authorization request and the response.
- **For partial authorization disputes:** Records showing the partial authorization amount and how it was handled, demonstrating that only the authorized amount was charged.

---

## Winning Strategy

The only winning strategy for 11.3 is proving an authorization did exist. This requires:

1. **Pull your authorization records immediately.** Look for the authorization code for the disputed transaction. If a valid code exists, you have a defense.
2. **Verify the code is genuine.** A force code entered by staff must have been obtained from a legitimate voice authorization — confirm the voice auth log.
3. **For partial authorization disputes:** Confirm that you charged only the authorized amount. If you charged more, issue a partial refund for the excess before filing a representment.
4. **If no valid authorization exists:** Accept the chargeback. Do not file a representment. Fix the underlying system or process that allowed an unauthorized transaction to complete.

---

## Losing Mistakes

- **Filing a representment with no authorization code.** Without a valid approval code, you have nothing to dispute.
- **Using a force code that was not obtained through voice authorization.** A fabricated or reused force code is not a valid authorization and will not succeed as a defense.
- **Arguing the cardholder's balance was sufficient.** Whether the cardholder had sufficient funds is irrelevant — you needed to ask the issuer through proper channels.
- **Ignoring partial authorization responses.** Partial authorizations are common with prepaid cards. Train your system and staff to handle them correctly — approve only the authorized amount or decline the transaction entirely and request another payment method.

---

## Prevention

- **Never use the force function without a genuine voice authorization code.** Disable force transaction capability for untrained or unauthorized staff.
- **Obtain authorization for every transaction.** Set floor limits to $0. There is no scenario in modern card processing where skipping authorization is acceptable.
- **Set up voice authorization correctly.** Maintain a voice authorization log that records every call, the code received, and the transaction it corresponds to.
- **Handle partial authorizations properly.** Configure your system to either complete the transaction for the partial authorized amount, split payment, or decline and request a new payment method.
- **Audit recurring transaction authorizations.** For subscriptions and installment plans, ensure each billing cycle has a valid authorization basis and that cardholder agreement is documented.
- **Reconcile authorizations to settlements.** Run daily reports comparing authorized transaction IDs to settled transactions. Any settled transaction without a matching authorization is a risk.

---

## Timeline

| Stage | Timeframe |
|---|---|
| Transaction processed (without auth) | Day 0 |
| Cardholder notices unexpected charge | Within 30–90 days |
| Dispute filed with issuer | Within 120 days of transaction |
| 11.3 chargeback received | After issuer review |
| Merchant response deadline | 30 days from notification |

---

## Frequently Asked Questions

**Q: We got an approval code — why are we receiving an 11.3 chargeback?**
A: The issuer may be claiming the approval code was invalid (fabricated, reused, or obtained under improper circumstances). Pull your complete authorization records including the full authorization request and response. If the code was legitimately issued by the authorization center, document this and file a representment with the complete authorization trail.

**Q: What is a partial authorization and how should we handle it?**
A: A partial authorization is when the issuer approves a transaction for less than the requested amount. This is common with prepaid cards. Your system should notify the customer of the partial approval, offer to split the payment (charge the approved amount on this card plus another payment for the remainder), or decline to complete the transaction. Never charge more than the authorized amount — the excess is unauthorized.

**Q: A customer called our phone line and gave us their card number. Do we need authorization if they "authorized" it verbally?**
A: Yes, absolutely. The customer's verbal authorization to charge their card is separate from the card issuer's authorization to accept the charge. You must still submit an authorization request to the issuer through proper channels and receive an approval code before completing the transaction.

**Q: Our subscription billing system charges customers monthly. Do we need a new authorization every month?**
A: You need a valid cardholder agreement documenting that the customer consented to recurring charges — but you don't necessarily need to call for a new authorization approval every single month. However, each recurring billing cycle should be submitted to the issuer for approval, and the response (approval or decline) must be handled properly. Setting up recurring billing without proper agreement documentation is a common source of 11.3 and 13.2 chargebacks.

**Q: Can we submit a transaction for settlement if the authorization has expired?**
A: No. Authorization approvals are valid for a limited time — typically 7 days for most transactions, though some card types (like debit) have shorter windows and some sectors (like hospitality) have specific rules. An expired authorization means you need to request a new one before settling. Settling against an expired authorization creates 11.3 exposure.

---

## Sample Rebuttal Points

For cases where a valid authorization did exist:

- "We are disputing this chargeback because a valid authorization was obtained for this transaction. Attached are our processor's records showing authorization code [X] was issued on [date] at [time]. This authorization was obtained through [electronic authorization / voice authorization with code obtained from [bank name] authorization center]."
- "Our voice authorization log (attached) confirms that authorization code [X] was obtained by phone on [date] at [time] for the card ending in [last four digits]. The authorization code was entered into our POS system and the transaction was completed based on this valid approval."
- "For the partial authorization dispute: our records show we charged the cardholder exactly $[partial amount], which corresponds to the partial authorization approval received. We did not charge the full $[requested amount]. Attached are our authorization and settlement records showing the matching amounts."
