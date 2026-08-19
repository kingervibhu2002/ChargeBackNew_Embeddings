---
title: "NPCI UPI Dispute Code U003 — Customer Debited but Merchant Not Credited"
description: "Complete merchant guide to NPCI UPI dispute code U003: the most common UPI dispute type covering settlement failures, how UPI settlement works, NPCI reconciliation records, and the distinction from fraud disputes."
category: RuPay / NPCI
reason_code: "U003"
chargeback_type: "Customer Debited but Merchant Not Credited — Settlement Failure"
win_rate: N/A (both parties are victims — resolution is system-level)
last_updated: 2026-06-29
tags: [NPCI, UPI, U003, settlement-failure, debited-not-credited, PSP, reconciliation, T+0, India]
---

# NPCI U003 — Customer Debited but Merchant Not Credited

## What This Dispute Code Means

NPCI UPI dispute code U003 is the most common UPI dispute category by volume. It describes a specific settlement failure: the customer's bank account is debited (money leaves the customer's account), but the merchant's account never receives the credit. The customer loses money, the merchant never gets paid, and the order is in limbo.

This is critically different from fraud (U001, U005) and from merchant fault (U008, U009). In a U003 scenario, both the customer and the merchant are victims of a technical failure in the UPI payment infrastructure. No party acted in bad faith. The money is typically stuck somewhere in the payment chain — in the customer's bank's settlement queue, in the PSP's clearing system, or in NPCI's intermediary settlement layer.

U003 does not require the merchant to refund the customer or the customer to bear the loss. The responsibility for resolving U003 sits with the banks and PSPs involved in the failed transaction. However, the practical outcome — delayed or missing payment, uncertain order status, frustrated customer — creates real operational challenges for merchants.

---

## How UPI Settlement Works (And Where It Breaks)

Understanding UPI's settlement architecture is necessary to understand U003.

**Normal UPI transaction flow:**
1. Customer enters UPI PIN and initiates payment in their UPI app
2. Customer's UPI app sends payment request to Customer's PSP (e.g., PhonePe, Google Pay, Paytm)
3. Customer's PSP routes the request to Customer's Bank via NPCI
4. Customer's Bank debits the customer's account and sends a debit confirmation to NPCI
5. NPCI routes the credit instruction to Merchant's Bank via Merchant's PSP
6. Merchant's Bank credits the merchant's account
7. All parties receive transaction confirmation

**Where U003 failures occur:**
- Steps 4→5: NPCI receives the debit confirmation but the credit instruction is lost or delayed
- Steps 5→6: The credit instruction reaches the Merchant PSP but is not relayed to the Merchant Bank
- Steps 6→6: The Merchant Bank receives the credit instruction but fails to post it

In all of these cases, the customer's bank has already debited the account. NPCI sees a pending settlement. The merchant's account has no credit. The transaction is in an indeterminate state.

---

## NPCI's T+0 Settlement Mandate

One of NPCI's most important rules for UPI is the **T+0 settlement mandate** — UPI transactions should settle to the merchant's account on the same day as the transaction. This near-real-time settlement is one of UPI's core advantages over older NEFT-based payment systems.

However, T+0 settlement assumes all system components are functioning correctly. Network outages, PSP failures, bank core banking system maintenance windows, and high-volume periods (festival seasons, year-end) can cause settlement delays that trigger U003 complaints.

When settlement is delayed beyond the T+0 mandate:
- The customer's bank should initiate an auto-reversal (per T+1 mandate)
- Alternatively, settlement should complete on T+1 as a late settlement
- If neither occurs, the customer files a U003 complaint

---

## Merchant's Position in U003

The merchant's situation in a U003 is unusual: they are potentially both a claimant (they did not receive payment) and a party required to provide evidence (confirming whether the credit arrived).

**If the credit never arrived:**
The merchant has a claim against their acquiring bank for the missing settlement. The merchant did not receive payment and the order is unpaid. The merchant should:
1. Check payment gateway and bank account for the transaction
2. Confirm the credit is absent — not pending, not delayed, but absent
3. Contact the acquiring bank/PSP with the customer's UTR number and request a settlement investigation
4. Provide evidence of no credit received (bank statement, payment gateway ledger)

**If the credit eventually arrives late:**
U003 disputes sometimes resolve automatically when the delayed settlement finally posts. The merchant receives the credit (perhaps T+1 or T+2 instead of T+0), the customer sees the payment confirmed in their UPI app, and the dispute is moot. The merchant's role is simply to confirm receipt of the late credit.

---

## Evidence the Merchant Should Maintain for U003

| Evidence | Purpose |
|---|---|
| Bank account statement showing no credit | Confirms the credit did not arrive for the disputed UTR |
| Payment gateway settlement report | Cross-reference with bank statement — absence of the UTR in both confirms non-receipt |
| Customer's UTR (provided by customer or bank) | Links the customer's debit to the expected credit |
| Order record showing payment as "pending" or "failed" | Confirms the merchant's order system did not confirm payment |
| Communication timeline with acquiring bank/PSP | Documents when the issue was reported and any investigation steps taken |

---

## Distinction from Other UPI Dispute Codes

U003 is frequently confused with other codes. The distinctions matter for understanding who bears responsibility:

| Code | Customer Status | Merchant Status | Who Is at Fault |
|---|---|---|---|
| U003 | Debited | Not credited | System/PSP failure |
| U006 | Debited | Not credited | System — transaction was declined but debit processed |
| U008 | Debited | Credited | Merchant — goods not delivered |
| U002 | Double debited | Single credited | System — retry causing duplicate debit |

**U003 vs U006**: Both result in the customer being debited without the merchant receiving a credit. The difference is the transaction status: in U006, the transaction was explicitly declined (a failure response was generated) but the debit still occurred due to a race condition. In U003, the transaction appeared to succeed from the customer's side but the credit never propagated. The resolution path is similar, but the technical investigation differs.

---

## Bank's Obligation to Resolve U003

Under NPCI's framework, when a customer files a U003 complaint:

1. The customer's bank acknowledges the complaint within 24 hours
2. The bank investigates the settlement chain using the UTR and NPCI transaction records
3. If the credit can be confirmed as pending (stuck in the system), the bank coordinates with NPCI and the merchant's bank to release the pending credit
4. If the credit cannot be confirmed (transaction genuinely failed), the bank initiates an auto-reversal to the customer within 30 days
5. The merchant's bank simultaneously confirms with the merchant whether the credit was received

The merchant is not expected to initiate or manage this process — it is a bank-level investigation. However, the merchant's prompt response when their bank requests information significantly accelerates resolution.

---

## What Merchants Should Do Operationally When a U003 Occurs

**For the customer:** Do not dispatch goods for an order flagged as payment-pending due to a U003. The payment has not been confirmed. Contact the customer, explain the situation, and advise them to check with their bank. Do not assume the payment will eventually arrive.

**For your operations team:** Log the UTR provided by the customer, check your payment gateway and bank account, and contact your PSP with the UTR requesting a settlement status inquiry. Most PSPs have a dispute resolution desk for exactly this type of case.

**For reordering:** In high-volume B2C environments, some merchants hold the order in a "pending payment" status for 24–48 hours while the settlement investigation runs. If the credit does not arrive in that window, cancel the order and advise the customer to rebook once their bank has resolved the dispute and reversed the debit.

---

## Frequently Asked Questions

**Q: A customer says they paid us via UPI but we see no credit. We dispatched the goods anyway because the customer showed us the payment screenshot. Now they're filing U003 — who is responsible?**
A: This is a serious operational risk scenario. A UPI payment screenshot does not confirm payment — it shows the customer initiated a payment. Settlement must be confirmed by your payment gateway or bank account. If you dispatched goods without confirming receipt of funds, you bear the risk of loss if the settlement fails. For any order above a low threshold, always confirm the credit in your bank/gateway before dispatch.

**Q: Our PSP says the transaction "succeeded" on their end but we have no bank credit. What does this mean?**
A: This suggests the failure occurred between your PSP and your acquiring bank. Your PSP has a settlement record, but the credit did not reach your bank account. This is a PSP-to-bank settlement failure. Escalate with your PSP to identify whether the credit is pending in their settlement batch and request an urgent investigation with your acquiring bank.

**Q: How long should we wait for a U003 to resolve before canceling an order?**
A: If no credit is confirmed within 24–48 hours, treat the payment as failed and cancel the order. Do not hold inventory or dispatch goods. Advise the customer to work with their bank for a refund of their debit. Once the bank confirms either a late credit or a reversal, the customer can reorder with confidence.

**Q: If the settlement eventually arrives late (T+2 or T+3), do we need to do anything?**
A: Confirm receipt of the late credit with your bank/PSP. If the customer's bank also processed a reversal (refunding the customer) because the T+1 mandate was exceeded, and the credit then arrives, you may have received a credit you should return — since the customer already received their refund. Check with your acquirer immediately if both a late credit and a customer-facing auto-reversal have occurred for the same transaction.

**Q: We're a small merchant on a third-party UPI platform (aggregator). How do we handle U003 disputes?**
A: Contact your aggregator's merchant support team with the customer's UTR and the relevant order details. The aggregator's settlement infrastructure is responsible for passing credits through to you. Document your communications and the timeline. If the aggregator cannot resolve within 30 days, escalate to your business bank's grievance redressal mechanism.
