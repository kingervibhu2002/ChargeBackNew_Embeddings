---
title: "Amex Dispute Code C02 — Credit Not Processed"
description: "Complete merchant guide to American Express dispute code C02: why agreed refunds must be processed immediately, the evidence needed to win, and why this dispute is almost always a merchant loss."
category: Amex
reason_code: "C02"
chargeback_type: "Credit Not Processed"
win_rate: Very Low (if refund truly not processed)
last_updated: 2026-06-29
tags: [amex, C02, credit-not-processed, refund, chargeback-defense, refund-timeline]
---

# Amex C02 — Credit Not Processed

## What This Dispute Code Means

American Express dispute code C02 is filed when a cardholder believes they are owed a refund that has not appeared on their account. This arises when a merchant agrees — explicitly or implicitly — to issue a credit and then either fails to process it, processes it late, or processes an incorrect amount.

C02 is the Amex equivalent of Mastercard's reason code 4860 and Visa's reason code 13.7. Across all three networks, credit-not-processed disputes share the same fundamental characteristic: they are almost entirely the result of merchant-side process failures, not cardholder abuse. Unlike fraud chargebacks where merchants can be victims of criminal activity, C02 disputes happen because the merchant did not do what they said they would do.

Amex's stance on C02 is stricter than Visa or Mastercard, consistent with its premium brand positioning and higher standards for merchant performance. Cardholders who are owed refunds from Amex purchases tend to follow up quickly, and Amex tends to act on their behalf with urgency.

---

## The 15-Day Cardholder Wait Period

Before filing a C02 dispute, cardholders must wait **at least 15 days** after requesting a refund. This waiting period gives merchants time to process credits, which typically clear in 5–10 business days on the cardholder's account.

However, this waiting period is cold comfort for merchants who genuinely did not process the refund. The window simply delays the inevitable — if no credit appears, the cardholder files at Day 15 or later, and the dispute is valid.

The operational implication is clear: **process every agreed refund the same day it is agreed to.** Do not batch refund requests, do not require secondary approvals for routine returns, and do not let tickets sit in customer service queues.

---

## Amex's Strict Stance on Credit Disputes

American Express holds merchants to a high standard on refund processing. Key aspects of Amex's approach:

**Amex investigates rapidly.** Because Amex is both the issuer and the network, C02 disputes do not require issuer-acquirer communication rounds. Amex can verify directly — and immediately — whether a credit transaction appears on the cardholder's account. There is no ambiguity, no waiting for the issuer to confirm.

**The merchant response window is 20 days.** Shorter than Visa (30 days) or Mastercard (45 days). Merchants who do not monitor Amex disputes in real time may miss the window entirely.

**Alternative refund forms require explicit cardholder consent.** If you offered store credit instead of a card refund, you must have written proof that the cardholder agreed to this alternative. Imposing store credit unilaterally — even if it is a common practice — does not satisfy Amex's C02 requirements.

---

## The Evidence Set That Wins C02

If the refund was genuinely processed, these are the documents that reverse an Amex C02 dispute:

| Evidence | Why It Matters |
|---|---|
| Refund transaction ID | The unique reference from your payment processor confirming the credit was issued |
| Refund amount and date | Confirms the full agreed amount was credited on a specific date |
| Payment gateway record | Settlement report or transaction log showing the credit status as "settled" |
| Refund confirmation email | Email sent to cardholder confirming the credit was issued |
| Original transaction reference | Links the refund to the disputed purchase |
| Store credit agreement (if applicable) | Written cardholder acceptance of alternative refund form |

The refund transaction ID is the single most decisive piece of evidence. Amex can cross-reference this ID against the cardholder's account to confirm the credit. Without it, you cannot prove the refund was processed regardless of what your internal records say.

---

## When You Cannot Win C02

If any of the following is true, accept the chargeback and fix the underlying process:

- **The refund was never processed.** There is no evidence to submit. Accept the C02, process the refund immediately to stop additional chargebacks, and audit why the refund was not processed.
- **The refund was processed for the wrong amount.** A partial refund when a full refund was promised creates a valid C02 for the difference. Process the remaining amount immediately.
- **The refund was issued as store credit without consent.** The C02 will succeed. Process a card refund immediately or provide proof of written consent to the alternative.
- **The refund is "pending" but not settled.** A pending credit has not reached the cardholder's account. Submit evidence of the initiation, but also escalate with your payment processor to accelerate settlement. The dispute may still stand until the credit clears.

---

## Proactive Prevention of C02 Disputes

**Same-day refund processing.** Every refund request — regardless of the channel it comes through (email, chat, phone, in-person) — should trigger an immediate refund transaction. Do not hold refunds for "review" unless you are investigating potential fraud.

**Automated refund confirmation emails.** Your payment platform should automatically send a confirmation email with the refund amount, transaction reference, and expected credit timeline (typically 5–10 business days). This email serves two purposes: it sets cardholder expectations so they do not file at Day 5, and it serves as evidence in any eventual dispute.

**Refund status visibility.** Give customers a way to check refund status — either through your website, app, or a dedicated support email. Customers who can self-serve their refund status are less likely to escalate to their bank.

**Daily refund queue audits.** If your operation uses any form of refund approval workflow, audit the queue daily. No refund request should sit unprocessed for more than 24–48 hours.

**Train support teams on refund authorization.** Empower customer service agents to process refunds up to a reasonable threshold (e.g., $500) without manager approval. Approval bottlenecks are a primary cause of delayed refunds that turn into C02 chargebacks.

---

## Handling C02 When Discovered Late

If you receive a C02 dispute and realize the refund was never processed, do not spend time building a rebuttal. The more productive path:

1. Process the refund immediately and note the refund transaction ID
2. Contact your acquirer and provide the refund transaction ID — in many cases, the issuing bank will withdraw the dispute when they see the credit pending
3. Document the timeline for your own records (when the refund was requested, when it was processed, the delay cause)
4. Fix the internal process that caused the delay

For small-dollar disputes where the refund has now been processed, the chargeback fee is the cost of the process failure. Accept it, fix the process, and move on.

---

## Frequently Asked Questions

**Q: I processed a refund but the cardholder says they still don't see it. What should I tell my acquirer?**
A: Submit your refund transaction ID and the settlement date of the credit. Advise that the refund has been processed and ask your acquirer to communicate this to Amex. Credit posting timelines vary by issuing bank — some credits appear in 2–3 business days, others up to 10 business days. The dispute should be resolved in your favor once Amex confirms the credit in the cardholder's account.

**Q: Is there a scenario where I can win a C02 if I haven't processed the refund but the cardholder's claim is inaccurate?**
A: Yes — if the cardholder claims you agreed to a refund but you have evidence no such agreement was made. If your terms of service explicitly state refunds are not available for a specific product category, and the customer agreed to those terms at checkout, you may have grounds to contest the underlying refund request. However, this requires clear, documented policy evidence — a vague "all sales are final" note buried in a long ToS is insufficient.

**Q: We issued a refund to the wrong card number by mistake. Is that my problem?**
A: Yes. A refund sent to the wrong account is not a refund to the cardholder. Process a new refund to the correct card immediately. The C02 dispute is valid until the cardholder receives the credit on their account.

**Q: The customer filed a C02 before the 15-day waiting period. Can I fight it on procedural grounds?**
A: You can note the premature filing in your rebuttal, but Amex may not dismiss the dispute solely on this basis — especially if the refund was not processed. A stronger approach is to immediately process the refund and provide the transaction ID regardless. The procedural argument is rarely sufficient on its own if no credit was issued.

**Q: Does a C02 count against my chargeback ratio?**
A: Yes. All chargebacks — including C02 — count against your dispute rate. This is another reason why same-day refund processing is worth investing in: preventing a single C02 saves the dispute fee and the ratio impact.
