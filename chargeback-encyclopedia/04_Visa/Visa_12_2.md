---
title: "Visa 12.2 — Incorrect Transaction Code"
section: "04_Visa"
category: "Visa Reason Codes"
network: "Visa"
reason_code: "12.2"
document_type: "Reason Code Reference"
keywords: ["incorrect transaction code", "12.2", "credit processed as sale", "refund error", "transaction type"]
difficulty: "Beginner"
---

# Visa 12.2 — Incorrect Transaction Code

## Definition

Visa reason code 12.2 — Incorrect Transaction Code — applies when a transaction was processed using the wrong transaction type code. The most common manifestation is when a **credit (refund) is processed as a sale (purchase)** — instead of the cardholder's account being credited, it is charged again, effectively doubling the transaction instead of reversing it.

This is a processing error category, not a fraud category or consumer dispute. The cardholder is not claiming they didn't authorize anything — they're pointing out that the merchant used the wrong transaction type, resulting in an incorrect charge on their account.

---

## How Transaction Codes Work

Every card transaction carries a transaction type code that tells the payment network what kind of operation is being performed:

- **Sale (Purchase):** Money moves from cardholder to merchant. The cardholder's account is debited.
- **Credit (Refund):** Money moves from merchant to cardholder. The cardholder's account is credited.
- **Void:** A same-day cancellation of an authorization, before settlement.
- **Reversal:** A post-settlement adjustment to undo a transaction.
- **Pre-authorization:** Holds funds without capturing them.

When the wrong code is used — particularly when a refund is processed as a sale — the cardholder's account is charged instead of credited. This is both a financial error and a reason code 12.2 dispute trigger.

---

## How This Error Happens

### Manual Refund Processing Errors
In manual or semi-automated refund workflows, a staff member might select the wrong transaction type in the POS interface. "Sale" and "Refund" buttons that look similar, or a confusing UI, can lead to the wrong selection — especially under time pressure.

### System Configuration Bugs
Payment gateways or POS systems with misconfigured transaction type mappings may route refund requests through the sale path. This is particularly common after system updates or configuration changes where the refund function isn't properly tested.

### Batch Processing Errors
In batch processing environments, if refund records are included in the wrong batch type or formatted with incorrect transaction codes, the entire batch may process as sales rather than credits.

### Third-Party Integration Failures
When merchants use third-party accounting systems that send refund commands to their payment gateway via API, integration errors can result in the wrong transaction type being transmitted. The accounting system sends a credit command, but the API mapping translates it incorrectly.

### Manual Terminal Entry Mistakes
On terminals that require manual selection of transaction type, staff unfamiliar with the interface may select "sale" when intending to process a refund.

---

## Common Scenarios

- A clothing store processes a return. The cashier navigates to the wrong screen on the POS terminal and processes the return as a sale rather than a refund. The customer's card is charged again instead of credited. A 12.2 chargeback follows.
- A software company's payment gateway integration has a bug where refund API calls are mapped to sale transactions. All refunds processed during a two-week period after a system update were charged as sales. Multiple 12.2 chargebacks arrive simultaneously.
- A restaurant processes a full refund for a cancelled reservation. Due to a terminal configuration error, the transaction processes as a duplicate sale. The cardholder sees two charges and no credit on their statement.

---

## Merchant Liability

Merchants are fully liable for 12.2 chargebacks because this is an operational error — the merchant's system or staff used the wrong transaction type. The fix is straightforward: process the correct transaction (the actual refund credit), submit it as evidence, and acknowledge the error.

However, the financial exposure can be significant if the error went undetected and resulted in multiple charges instead of credits. In a batch processing error scenario, dozens of customers might have been charged rather than credited.

---

## Required Evidence

If you believe the chargeback was filed in error (i.e., the correct transaction code was used), provide:

- **Transaction records:** Complete processing records showing the transaction type code actually used.
- **Gateway logs:** System logs confirming the transaction was processed as a credit (not a sale).
- **Settlement records:** Bank settlement records showing a credit settlement, not a sale.

**If the error did occur and the refund was then correctly processed:**
- **Refund transaction record:** The correct refund/credit transaction ID and timestamp.
- **Cardholder account credit confirmation:** If available from your processor, documentation that the credit posted to the cardholder's account.

---

## Winning Strategy

For most 12.2 chargebacks, the winning strategy is immediate acknowledgment and correction, not dispute:

1. **Process the correct refund immediately.** If a sale was processed instead of a credit, issue the proper credit refund as soon as you identify the error — ideally before a chargeback even arrives.
2. **Submit the credit transaction record as evidence.** Show that you corrected the error. The chargeback should be withdrawn once the issuer confirms the credit posted.
3. **Document the processing error.** Note in your rebuttal that this was an operational error, it has been corrected, and the correct credit has been processed.

**For disputes where you believe no error occurred:**
- Pull your complete transaction records and submit them, clearly showing the transaction type code used was correct.

---

## Losing Mistakes

- **Not noticing the error before the chargeback arrives.** The best time to catch a 12.2 error is during daily reconciliation. If you compare expected credits to your settlement, you'll catch a credit-processed-as-sale error immediately.
- **Failing to process the corrective refund.** If you don't fix the error, the cardholder has no remedy other than the chargeback.
- **Processing the refund after the chargeback and submitting both as evidence.** The proper sequence is: chargeback received, refund already processed (or process it now), submit refund record as evidence. Don't process the refund and the chargeback response simultaneously without communicating clearly — it may appear that you're double-refunding.
- **Ignoring the root cause.** A system error that generated one 12.2 chargeback may have generated dozens more. Investigate immediately.

---

## Prevention

- **Daily reconciliation.** Compare expected credits (from your refund records) to actual settlement data. Credits that appear in your POS records but not in settlement — or that appear as debits rather than credits — signal a 12.2 error.
- **Separate refund workflow.** Ensure your POS or payment system has a clearly distinct and unambiguous path for processing refunds versus sales. UI design matters — color-coded buttons, confirmation screens, and two-step verification for refunds reduce errors.
- **Test refund processing after any system update.** Any time your payment software, gateway integration, or POS firmware is updated, test the refund workflow with a small real or test transaction before processing customer refunds.
- **Train staff on refund procedures.** New employees, part-time staff, and seasonal workers should receive explicit training on how to process refunds using the correct function on your POS system.
- **API integration testing.** If your accounting or order management system sends refund commands to your payment gateway via API, test the integration thoroughly — including edge cases and error conditions.

---

## Timeline

| Stage | Timeframe |
|---|---|
| Incorrect transaction processed | Day 0 |
| Cardholder notices wrong charge | Within 30–60 days (statement review) |
| Dispute filed with issuer | Within 120 days of transaction |
| 12.2 chargeback received | After issuer review |
| Merchant response deadline | 30 days from notification |

---

## Frequently Asked Questions

**Q: We made the mistake and already issued a correct refund. Do we still get a chargeback?**
A: You may still receive the chargeback if the issuer isn't aware that the corrective refund has already been processed. Submit the refund transaction record as evidence in your chargeback response. The issuer should withdraw the chargeback upon confirming the credit posted. If the timing works out and the refund posts before the chargeback is finalized, it may resolve automatically.

**Q: Can we void the incorrectly coded transaction instead of doing a refund?**
A: Voids only work on the same business day, before the batch is settled. If the error is caught before batch close, voiding the incorrect sale transaction and reprocessing as a credit (or simply voiding the erroneous transaction entirely) is the cleanest resolution. After the batch settles, a credit/refund is the only option.

**Q: What if the error was caused by our payment gateway's bug, not our staff's mistake?**
A: The chargeback liability still falls on the merchant initially. Resolve the cardholder's dispute first, then pursue the payment gateway vendor for reimbursement based on your service agreement. Document the technical error thoroughly — logs, timestamps, support ticket correspondence — to support your claim against the vendor.

**Q: A batch processing error caused the same problem for 50 customers. How do we handle this at scale?**
A: Process correct refunds for all 50 affected customers immediately. Contact your acquirer to explain the systemic issue. Proactive refunds may prevent many of the chargebacks from being filed at all — cardholders who receive an unexpected credit and a correction notice typically do not dispute the original error. Document every corrective refund and be prepared to submit batch evidence if multiple chargebacks arrive.

**Q: Does 12.2 affect my chargeback ratio?**
A: Yes. Any chargeback, regardless of reason code, counts toward your overall chargeback rate. Multiple 12.2 chargebacks from a systemic error can significantly spike your ratio if not caught quickly. This is another reason to catch and correct processing errors before they become chargebacks.

---

## Sample Rebuttal Points

When the correct credit has been processed:

- "This 12.2 chargeback arose from an operational processing error where a refund was incorrectly processed using a sale transaction code. We have identified and corrected the error. The correct credit transaction was processed on [date] under transaction ID [X]. We attach the credit transaction record confirming the correct amount was posted to the cardholder's account."
- "We acknowledge the transaction code error referenced in this chargeback. The error was corrected on [date]. The attached settlement records show a credit of $[amount] was processed and should have posted to the cardholder's account by [expected posting date]. We request this chargeback be withdrawn as the underlying error has been remediated."

When disputing that any error occurred:

- "We dispute the basis of this 12.2 chargeback. Our gateway records (attached) confirm the transaction was processed as a credit (refund), not a sale. The transaction type code in our system log is [X], indicating a credit transaction. We request the issuer review the transaction type code on their records and confirm whether a coding error actually occurred."
