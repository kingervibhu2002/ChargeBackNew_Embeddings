---
title: "Visa 13.6 — Credit Not Processed"
section: "04_Visa"
category: "Visa Reason Codes"
document_type: "Reference"
keywords: ["Visa 13.6", "credit not processed", "refund not issued", "agreed refund chargeback", "refund chargeback", "credit not posted", "refund delay chargeback"]
difficulty: "Beginner"
---

# Visa 13.6 — Credit Not Processed

Visa reason code 13.6 is the most preventable chargeback code in the Visa system. It is filed when a merchant agreed to issue a refund to a cardholder but never processed it — or processed it so late that the cardholder had already filed a dispute. There is almost no scenario where a 13.6 chargeback represents a legitimate defense. If you agreed to a refund and did not issue it promptly, the chargeback is valid. The right response is to fix the process that allowed this to happen, not to fight the dispute.

## What This Chargeback Means

A 13.6 chargeback is the cardholder or issuer stating: "This merchant agreed to give me a refund. I have waited for it. It has not appeared. I am taking it back through my bank."

This chargeback code arises in these situations:

**Agreed Refund Never Processed:** A customer service agent, sales representative, or manager verbally agreed to a refund — by phone, email, chat, or in person — but the actual credit transaction was never submitted through the payment system.

**Refund Processed but to Wrong Account:** The refund was issued, but was applied to a different card or account than the one that was charged, so it never appeared on the cardholder's statement.

**Refund Processed Too Late:** The cardholder agreed to wait a specific number of days. The refund was issued, but after the cardholder lost patience and filed the chargeback before the credit posted.

**Refund for Partial Amount Only:** The merchant issued a partial refund where a full refund was agreed upon, and the cardholder disputes the remainder.

**Return Accepted But Refund Not Issued:** The merchant received the returned goods but did not process the corresponding refund within a reasonable time.

## This Chargeback Is Almost Always a Merchant Loss

A 13.6 chargeback is the payment system doing its job correctly: when a merchant agrees to a refund and fails to deliver it, the cardholder has recourse. Attempting to fight a 13.6 chargeback where a refund was genuinely agreed to and not processed is a waste of resources and will fail at representment.

The only legitimate defenses to a 13.6 are:

1. **The refund was already processed and posted to the cardholder's account before the chargeback was filed** — provide the refund transaction ID and timestamp
2. **No refund was agreed to** — the cardholder is falsely claiming a refund agreement that never occurred, and you can demonstrate (with email records, customer service logs, or recorded calls) that no refund was promised

## Evidence for the Only Viable Defense: Refund Was Already Processed

If a refund was processed and posted before the chargeback was filed, the chargeback should not have been allowed under Visa rules. Cardholders are required to wait 15 calendar days after a credit posts to their account before filing a chargeback for credit not processed.

**Evidence to submit:**
- Refund transaction ID from your payment gateway
- Gateway or processor confirmation showing the credit was submitted and settled
- Timestamp of the refund transaction showing it was processed and posted before the chargeback was filed
- The refund amount matching the disputed amount

Submit this evidence with a rebuttal letter noting that a credit was processed on [date] — before the chargeback was filed — and that the cardholder did not wait the required 15 calendar days before initiating the dispute. If the evidence is clear, this is grounds for reversing the chargeback via compliance as well.

## Timing of Refunds: How Long Is Too Long?

Cardholders must wait 15 calendar days after a credit posts before filing a 13.6 chargeback. However, in practice, cardholders become impatient when refunds take longer than 5–7 business days to appear on their statement. The safest practice is:

- Process refunds the same day they are agreed to
- Refund to the exact payment method used for the original transaction
- Send an email confirmation to the cardholder immediately upon processing the refund, including the expected posting timeframe
- Monitor for refund posting issues (sometimes gateway or acquirer processing delays prevent the credit from actually clearing) and follow up proactively

## Why the Refund Must Go to the Original Card

A common merchant error is issuing a store credit, a gift card, or a payment to a different account when a card credit is what the cardholder expects. Unless the cardholder has explicitly agreed in writing to a non-cash alternative to their card refund, the refund must go back to the card used in the original transaction. A store credit does not satisfy the cardholder's right to a card credit and does not protect you from a 13.6 chargeback.

## Issuer Timeline

Before filing a 13.6 chargeback, issuers are supposed to confirm that 15 calendar days have passed since the expected credit date. The 15-day window is designed to allow for standard payment processing time between the merchant processing the refund and the credit appearing on the cardholder's statement.

If you process a refund on Day 0, it typically posts within 3–5 business days. The 15-day buffer gives significant leeway. However, if your refund process is delayed beyond 10 business days for any reason, cardholders may contact their issuer before the credit posts, and some issuers will file the chargeback before the 15 days have elapsed if they see no pending credit in the system.

## Best Practice: Process Refunds Immediately

The single most effective prevention for 13.6 chargebacks is to process agreed-upon refunds the same day you agree to them — ideally within hours. A refund processing SLA of "same business day" for customer service-approved refunds essentially eliminates 13.6 as a chargeback exposure.

**Operational checklist for refund compliance:**

1. Customer contacts support requesting a refund
2. Agent evaluates and approves the refund
3. Agent triggers the refund in the payment system **before closing the support ticket** (not as a follow-up task)
4. Confirmation email sent to customer with refund transaction ID and expected posting timeframe
5. Support ticket notes updated with refund transaction ID for audit trail
6. QA review of any open support tickets flagged for refund where no refund transaction ID exists within 24 hours

---

## Frequently Asked Questions

**Q: Can I win a 13.6 chargeback if the customer agreed to a store credit instead of a card refund?**
A: Only if you have documented evidence that the cardholder explicitly agreed in writing to accept a store credit in lieu of a card refund. A cardholder who verbally agreed to a store credit but later changed their mind and filed a 13.6 is in a gray area — if you have a written agreement (email, chat transcript) showing they accepted the store credit, you have a defense. Without written evidence of their acceptance, the card refund expectation controls.

**Q: The customer returned the item but never received their refund because our return processing team lost the package internally. Should I fight this?**
A: No. This is an internal operational failure — the customer returned the item and is entitled to a refund. Accept the chargeback, process the refund if not already done, and investigate your return processing workflow. Fighting a chargeback caused by your own internal error wastes representment resources and will fail.

**Q: A customer filed a 13.6 chargeback one day after I processed the refund. The refund hadn't posted yet. Can I win?**
A: Yes, if your refund was processed before the chargeback was filed and the cardholder filed before the 15-day Visa waiting period elapsed. Submit your refund transaction timestamp as evidence, note the filing date of the chargeback, and note that the cardholder did not observe the required 15-day waiting period. This is grounds to reverse the chargeback. Even if the refund had not yet posted to the cardholder's account, the processing timestamp proves the credit was initiated and in progress.

**Q: We use a subscription billing platform. A customer cancelled and our billing platform issued a refund, but it was to the wrong card because the customer had updated their payment method. Is this a 13.6?**
A: This depends on where the refund went. If the refund was returned to the original card used for the transaction (the old card), the cardholder may need to contact that card's issuer to retrieve those funds, especially if the card is closed. If the refund disappeared because the old card account is closed, you may need to work with your acquirer to resolve the routing issue. From a chargeback perspective, processing a refund to the original payment method is technically correct — the issue becomes one of card account lifecycle.

**Q: How long do refunds take to post under Visa rules?**
A: Visa does not mandate a specific posting time for credits, but standard processing means a credit submitted by the merchant typically settles within 1–3 business days and posts to the cardholder's account within 3–5 business days of the merchant initiating the credit. From end to end, cardholders should expect to see credits within 5–7 business days in most cases. Communicating this timeframe clearly to the cardholder at the time of refund agreement prevents impatient 13.6 disputes.
