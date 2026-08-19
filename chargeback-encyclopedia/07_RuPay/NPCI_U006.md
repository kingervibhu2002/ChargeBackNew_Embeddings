---
title: "NPCI U006 — Transaction Declined but Amount Debited"
section: "07_RuPay"
category: "RuPay / NPCI Reason Codes"
network: "RuPay / NPCI"
reason_code: "U006"
document_type: "Reason Code Reference"
keywords: ["NPCI", "UPI", "declined", "debited", "U006", "failed transaction", "auto-reversal", "T+1"]
difficulty: "Beginner"
---

# NPCI U006 — Transaction Declined but Amount Debited

## Overview

U006 covers the scenario where a UPI transaction was declined or showed as failed in the customer's UPI app, but the customer's bank account was debited regardless. This is a pure technical failure — neither the merchant nor the customer did anything wrong.

This situation arises from network timeouts between the customer's bank (issuing bank), the UPI switch (NPCI infrastructure), and the merchant's PSP/acquiring bank. The debit happens at the issuing bank level, but the success confirmation never completes the round-trip to the UPI app, so the app displays the transaction as failed.

**Critically: In most U006 cases, the merchant does NOT receive the credit.** The money is stuck in transit in the NPCI settlement layer.

## Common Scenarios

**Network timeout**: The customer initiates a UPI payment. The issuing bank debits the account but the NPCI switch times out before sending the confirmation to the PSP. The UPI app shows failure; the bank account shows a debit.

**Bank CBS (Core Banking System) delay**: The bank's core banking system processes the debit but is slow to respond to NPCI. NPCI marks the transaction as failed due to timeout, but the debit has already been posted.

**App crash during transaction**: Customer's UPI app crashes or loses network mid-transaction. The payment was in-flight at the moment of crash — the bank debited but the app never received the final status.

**NPCI gateway congestion**: During high-traffic periods (festival sales, salary day), NPCI switches experience high load. Transactions time out on the NPCI side despite successful bank debits.

## Merchant Involvement

**In most U006 cases, the merchant receives nothing.** The merchant's PSP does not credit the merchant account because NPCI never confirmed the transaction as successful. So both the customer and the merchant are victims of the same system failure.

From a dispute perspective, this means the merchant typically does not need to take any defensive action — there is no payment to defend or refund. However, if your payment gateway shows the transaction as "pending" or "in-limbo," contact your PSP immediately to check NPCI's settlement file for that UTR.

## NPCI's Auto-Reversal Mandate

NPCI has strict rules for U006 situations:

- **T+1 reversal**: If a transaction is in an unresolved state (debit at issuer side, no credit at merchant side), NPCI mandates automatic reversal to the customer's account by end of the next working day (T+1)
- **No customer action required for auto-reversal**: The bank is obligated to reverse automatically; the customer does not need to file a formal dispute for this
- **If auto-reversal fails**: Customer should file a complaint with their bank. If unresolved in 30 days, escalate to the RBI Banking Ombudsman

## Required Evidence

Since this is a system failure, evidence requirements are minimal for the customer. For merchants who need to track:

- UTR (UPI Transaction Reference Number) — the unique identifier for every UPI transaction
- Transaction status from payment gateway (showing "failed" or "pending" — confirms no credit received)
- NPCI transaction status query result (available via PSP's NPCI API integration)
- Bank statement showing no credit for the disputed UTR

## Timeline

| Milestone | Timeframe |
|-----------|-----------|
| Transaction failure | Immediate (T+0) |
| NPCI auto-reversal mandate | T+1 (next working day) |
| Customer complaint to bank (if no auto-reversal) | Within 30 days of transaction |
| Bank resolution mandate | 5 working days from complaint |
| RBI Ombudsman escalation | If unresolved after 30 days |

## What Merchants Should Do

1. **Monitor your payment gateway dashboard** for transactions stuck in "pending" or "unknown" state — these are likely U006 candidates
2. **Contact your PSP immediately** for any transaction showing pending for more than 4 hours; request NPCI status check
3. **Do not fulfill the order** until the transaction status is confirmed as successful — delivering goods for a failed payment means a loss
4. **Communicate with the customer** if they contact you — explain the auto-reversal process and timeline
5. **Keep UTR records** for all transactions including failed ones — needed if the bank or customer escalates

## FAQs

**Q: The customer says they paid me but the transaction shows as failed — what do I do?**
Do not fulfill the order. Request the UTR from the customer. Check that UTR in your payment gateway — if it shows failed/declined, you received no funds. The customer's bank will auto-reverse the debit within T+1.

**Q: What if the auto-reversal doesn't happen and the customer blames me?**
Explain that this is a bank/NPCI system issue, not a merchant issue. Provide the customer with the UTR status from your payment gateway showing you received no credit. Direct them to file a complaint with their bank.

**Q: Can I receive a credit for a transaction that my gateway shows as failed?**
In rare cases, NPCI's settlement file may credit you even though the gateway reported failure. Check your bank statement against the gateway report daily. If you find an unexplained credit, do not spend it — report to your PSP to reconcile.

**Q: How do I prevent U006 disputes?**
You can't prevent NPCI system failures, but you can: (1) implement real-time webhook confirmation from your PSP before showing "payment successful" to customers, (2) use NPCI's transaction status API to verify before order fulfillment, (3) show customers a "pending — do not retry" message while the transaction resolves.

## Key Takeaways

- U006 is a pure technical failure — neither merchant nor customer is at fault
- In most cases, the merchant never received the payment
- NPCI mandates T+1 auto-reversal to the customer without any formal dispute needed
- Merchants should not fulfill orders until transaction is confirmed successful
- If auto-reversal fails, customer escalates to bank; bank escalates to NPCI
