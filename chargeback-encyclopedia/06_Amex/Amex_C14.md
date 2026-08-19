---
title: "Amex C14 — Paid by Other Means"
section: "06_Amex"
category: "Amex Reason Codes"
network: "American Express"
reason_code: "C14"
document_type: "Reason Code Reference"
keywords: ["paid by other means", "dual payment", "double charge", "cash and card", "bank transfer", "C14", "Amex chargeback", "duplicate payment", "POS reconciliation"]
difficulty: "Intermediate"
---

## Overview

Amex reason code C14 — "Paid by Other Means" — is filed when a cardholder claims they paid for the same transaction using a completely different payment instrument in addition to being charged on their American Express card. The defining characteristic of C14 is that two separate payment methods were used for what was intended to be a single transaction: for example, a hotel guest pays their bill in cash at the front desk, and the hotel's system also processes an Amex charge for the same stay. The cardholder ends up paying twice — once via each method — and disputes the card charge because they already settled the bill another way.

This code is specifically about cross-method duplication. The cardholder is not claiming the merchant never delivered a product or that the charge was fraudulent — they are asserting that the underlying transaction was already paid through a non-card channel. Common alternate payment methods include cash, bank wire, NEFT, RTGS, check, a different credit or debit card, a digital wallet transfer like PayPal or Google Pay, or a corporate invoice settlement. The dispute may arise immediately after the transaction or weeks later when the cardholder reconciles their bank statements and notices two payments leaving their accounts for the same purchase.

C14 is distinct from Amex duplicate processing code 4834 (equivalent to Visa 12.6), which covers the same card being charged twice for the same transaction. C14 requires a different payment method to be involved. The evidence requirements differ accordingly: for C14, a merchant must demonstrate that only one payment was received for the transaction, and that the Amex card charge was the legitimate and sole payment collected.

---

## Common Scenarios

**Front desk cash settlement with card on file.** A hotel guest provides an Amex card at check-in as a guarantee. At checkout, they pay the full bill in cash. The front desk agent marks the cash payment as received, but the Property Management System (PMS) auto-settles the card on file overnight. The guest receives both a cash receipt and an Amex charge for the same stay — a textbook C14.

**Corporate wire transfer plus card charge.** A B2B customer wires payment for a large equipment or services order via bank transfer. The merchant's accounts receivable team posts the wire, but the sales system also processes the Amex card on file as a backup collection method. Both payments clear, and the cardholder's finance team flags the Amex charge as a double payment.

**Online prepayment then in-person charge.** A restaurant, spa, or venue accepts prepayment through an online booking portal, and the front-of-house staff charge the customer's Amex card again at the point of service, unaware that payment was already collected online. This is especially common with OTA integrations where the online payment is not visible to in-person staff.

**Gift card full payment with card also charged.** A retail POS is configured to accept partial payment by gift card and partial by credit card. A system glitch processes the full amount against the Amex card even though the customer already tendered the full amount via store gift card. The Amex charge should have been zero, but the system charges the entire balance.

**Invoice paid by check then card processed.** A service provider issues an invoice; the client mails a check. Before the check clears, a staff member manually keys in the Amex card number provided earlier as a billing backup. Both the check and the Amex charge settle, resulting in a net double payment for a single invoice.

---

## Merchant Liability

**Merchant is liable when:**
- Internal records confirm that the Amex card was settled AND a separate payment via another method was also collected for the same transaction — and no refund has been issued.
- The POS, PMS, or billing system failed to void the card pre-authorization after cash, check, or another method was collected, and the merchant did not catch it during daily reconciliation.
- Staff processed the card without checking whether the order or invoice was already marked as paid in the system.
- The merchant cannot produce documentation showing only a single payment was received for the disputed transaction.

**Merchant is NOT liable when:**
- Records demonstrate that the Amex card was never actually settled — only a pre-authorization was placed, and the authorization was voided when the alternate payment was collected.
- The alleged alternate payment never arrived — for example, the bank wire was sent to the wrong account, the check bounced, or the OTA never remitted — and the Amex card was the only successful payment received.
- The cardholder is mistaken about which transaction was paid by alternate means — the dates, amounts, or merchant names do not match the disputed Amex charge.
- The "other payment" was a refund or store credit for a different transaction, not a payment for the transaction in dispute.

---

## Required Evidence

- **Bank statement or payment gateway settlement report** showing only one credit received for this specific transaction — matched to the Amex transaction amount, date, and reference number.
- **POS journal or transaction log** for the date of the transaction, showing the payment method(s) recorded at the time of sale.
- **Cash-out or end-of-day reconciliation report** confirming the cash drawer or check register shows no entry matching this customer's payment amount on this date.
- **Void confirmation** (if the Amex pre-authorization was voided when alternate payment was collected), including the void timestamp and authorization code.
- **Invoice or order record** showing only one payment line marked as received, with no second payment against the same order.
- **Property Management System report** (for hotels) showing the payment method used at checkout, the folio balance, and the final settlement method.
- **Statement from the merchant** explicitly asserting that no alternate payment was received for this order and that the Amex charge is the sole payment collected.

---

## Winning Strategy

The merchant's goal is straightforward: prove that only one payment was actually received for this transaction, and that the Amex card was that single and correct payment. Start by pulling reconciliation records for the transaction date. If the Amex charge is the only payment logged against this order or invoice, and no cash receipt, wire confirmation, or alternate payment appears in your records, present that evidence clearly and concisely.

If you did receive two payments in error, your only path to a favorable resolution is demonstrating that you have already refunded the duplicate charge. Show the refund transaction ID, timestamp, and confirmation. Amex expects merchants to self-correct dual-payment errors as soon as they are identified. Proactive refunds issued before the chargeback notification often cause the cardholder to withdraw the dispute entirely. Include the refund confirmation in your response whether the refund was processed before or after the chargeback was filed — Amex will review it and credit you once the refund is confirmed.

If the cardholder is simply wrong — they paid a different vendor or a different invoice by alternate means and are misidentifying your charge — submit a clear factual breakdown: the date of your Amex charge, what goods or services it was for, and documentation showing no alternate payment was collected from this cardholder for this specific transaction.

---

## Common Mistakes

**Failing to reconcile daily.** Merchants who do not run end-of-day reconciliation reports do not catch dual-payment errors within the window where a simple void or refund would prevent the chargeback entirely.

**Leaving card pre-authorizations open after collecting cash.** Front desk or service staff collect cash or check but forget to void the card pre-authorization. The PMS or payment system auto-settles the authorization at end of day or end of the holding period.

**Assuming a non-captured pre-auth won't settle.** Some merchants believe that if they don't manually "capture" a pre-auth, it will simply fall off. Many Amex pre-authorizations auto-capture if not explicitly voided within the settlement window. Always void explicitly — do not assume inaction equals cancellation.

**Submitting evidence for the wrong transaction.** If a cardholder has stayed multiple times or placed multiple orders, merchants sometimes pull reconciliation records for the wrong visit or order. Match the dispute to the specific Amex transaction ID and amount before gathering evidence.

**No documentation of alternate payment.** If the cardholder claims they paid cash but the merchant has no cash receipt and no reconciliation record, it becomes difficult to assert the Amex charge was the only payment — even if it genuinely was. Always issue cash receipts and reconcile against them daily.

---

## Timeline

| Milestone | Timeframe |
|---|---|
| Cardholder files dispute with Amex | Within 120 days of transaction date |
| Amex notifies merchant of chargeback | Within a few business days of dispute filing |
| **Merchant response deadline** | **20 calendar days from chargeback notification** |
| Amex issues decision after response | Typically 4–8 weeks |
| Pre-arbitration (if escalated by either party) | Additional 30 days per stage |

Amex gives merchants 20 calendar days to respond to a chargeback. Missing this deadline results in automatic acceptance of the chargeback and forfeiture of the right to dispute. If a dual-payment error is identified early — before the chargeback arrives — issuing a refund immediately is almost always faster and less expensive than waiting for the formal dispute process to force it.

---

## FAQs

**Q: The cardholder claims they paid cash, but I have no cash payment recorded for this customer. Who wins?**
A: If your cash reconciliation report and POS records show no cash transaction logged for this customer on this date, and your bank statement shows only the Amex credit for this amount, you have a strong case. Present your reconciliation report and Amex settlement record together. The burden rests on the cardholder to substantiate the cash payment claim — ideally with a cash receipt you issued. If you did not issue a cash receipt and the cardholder has no documentation, both parties are in a weak evidentiary position, but your bank record is typically the more objective source.

**Q: We discovered the dual payment ourselves and issued a refund before the chargeback arrived. Will the chargeback still proceed?**
A: If the refund was fully processed and settled before the chargeback notification date, Amex will typically see the credit and close the dispute in your favor. If the refund was issued after the chargeback was filed, include the refund transaction ID and settlement date in your response — Amex resolves in the merchant's favor once the refund is confirmed. Contact Amex proactively through your acquirer if you have processed a refund and a chargeback arrives simultaneously.

**Q: How is C14 different from a standard duplicate charge (Amex 4834)?**
A: Amex 4834 — Duplicate Processing — means the same Amex card was charged twice for the same transaction, with two card settlements appearing on the cardholder's statement. C14 means the transaction was paid once by Amex card and once by a completely different method — cash, wire, another card, etc. The evidence needed differs: for 4834, show only one Amex settlement; for C14, show that no alternate payment was collected and the Amex charge was the sole payment method used.

**Q: Our PMS auto-settled the card even though the guest paid cash at checkout. Is that our fault?**
A: Yes. The merchant is responsible for configuring the PMS to require explicit settlement confirmation and for training staff to void card authorizations when alternate payment is collected. Amex will hold the merchant liable for the duplicate charge in this scenario. The correct resolution is to immediately refund the Amex charge and update internal procedures to require a checkout settlement step that logs the payment method before the PMS can auto-settle any card on file.

---

## Key Takeaways

- C14 arises when two different payment methods are used for a single transaction — the Amex card plus cash, wire, check, another card, or another instrument — and the cardholder ends up paying twice.
- The merchant wins by proving only one payment was actually received — the Amex card — and that no alternate payment exists in their reconciliation records for this transaction.
- If two payments were genuinely received in error, refund the Amex charge immediately, include the refund confirmation in the dispute response, and update internal controls to prevent recurrence.
- Daily reconciliation across all payment channels is the primary prevention tool — catching dual payments within 24 hours prevents them from ever becoming chargebacks.
- C14 is fundamentally different from duplicate processing (4834 / Visa 12.6): C14 requires a different payment method; 4834 means the same card was charged twice.
