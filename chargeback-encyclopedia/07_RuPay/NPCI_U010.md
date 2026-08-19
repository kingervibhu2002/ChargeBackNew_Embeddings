---
title: "NPCI U010 — Technical Error / System Failure"
section: "07_RuPay"
category: "RuPay / NPCI Reason Codes"
network: "RuPay / NPCI"
reason_code: "U010"
document_type: "Reason Code Reference"
keywords: ["NPCI", "UPI", "technical error", "U010", "system failure", "auto-reversal", "PSP failure", "bank CBS"]
difficulty: "Beginner"
---

# NPCI U010 — Technical Error / System Failure

## Overview

U010 is the catch-all code for UPI disputes caused by technical failures in the payment system — errors originating from the bank's core banking system (CBS), the PSP (Payment Service Provider), the UPI switch (NPCI infrastructure), or the merchant's payment integration.

Unlike fraud codes (U001, U005) or merchant fulfillment failures (U008, U009), U010 disputes arise from system-level failures beyond the control of either the customer or the merchant. The key characteristic is that **no party acted incorrectly** — the failure is in the technology stack.

NPCI's position on U010 is clear: the bank or PSP whose system failed bears the liability, not the customer. The customer must be made whole through auto-reversal or manual credit.

## Common Scenarios

**UPI server outage**: NPCI's payment switch experiences downtime during peak hours (salary day, festivals). Transactions initiated during the outage may debit customer accounts but fail to complete.

**Bank CBS timeout**: The customer's bank core banking system processes the debit but takes too long to respond to NPCI. The transaction times out and is marked failed, but the debit stands.

**PSP switch failure**: The merchant's payment service provider (Razorpay, PayU, Paytm, Cashfree) experiences a system error between receiving NPCI's confirmation and crediting the merchant account.

**2FA authentication timeout**: Customer receives and enters OTP correctly, but the bank's OTP verification system times out. Transaction is marked failed despite correct customer action.

**Settlement file corruption**: NPCI's daily settlement file has a technical error causing certain transactions to not settle. Merchants don't receive credit; customers are already debited.

**Network infrastructure failure**: ISP or telecom failure during the critical moment of transaction processing causes incomplete messages between the UPI system layers.

## Who Is Liable Under U010

Under NPCI's framework:

| Failed Component | Liable Party |
|-----------------|-------------|
| Customer's bank CBS | Issuing bank |
| NPCI UPI switch | NPCI / acquiring bank |
| Merchant's PSP system | PSP / acquiring bank |
| Merchant's own system | Merchant (rare — usually classified differently) |
| Telecom/network | Bank/PSP (they must ensure redundant connectivity) |

**The customer is never liable for U010** — they cannot control system failures.
**The merchant is rarely liable** unless the failure was in the merchant's own integration code.

## NPCI's Auto-Reversal Mandate

For U010 situations, NPCI has strict auto-reversal requirements:

- **T+1 reversal**: Any transaction in an unresolved state (debit confirmed at issuer, credit not confirmed at beneficiary) must auto-reverse by end of the next working day
- **No customer action required**: Auto-reversal is the bank's obligation, not the customer's right to claim
- **NPCI monitoring**: NPCI monitors unresolved transactions in its switch and initiates reversals automatically for most cases
- **If T+1 auto-reversal fails**: Customer files formal complaint with bank → bank raises with NPCI within 3 working days → NPCI resolves within 30 days

## What Merchants Should Do

For most U010 cases, **the merchant takes no direct action** — the failure is between the bank and NPCI. However:

1. **Monitor your payment dashboard for "pending" transactions** — these may be U010 candidates stuck in the settlement layer
2. **Contact your PSP immediately** for any transaction pending for more than 4 hours — request NPCI status check via API
3. **Do not fulfill orders** for transactions in pending/unknown state — if the transaction is being reversed to the customer, you should not have dispatched goods
4. **Keep UTR records** of all transactions including failed ones — needed if dispute queries arrive from banks
5. **Report system failures to your PSP** — if you experience a period of failed transactions, notify your PSP so they can raise with NPCI and ensure proper resolution

## NPCI Response Codes for Technical Errors

NPCI UPI uses specific response codes to indicate the type of failure. Key codes merchants and PSPs should recognize:

| Category | What It Means |
|----------|--------------|
| Timeout responses | Transaction didn't complete within the allowed window |
| System unavailable | NPCI or bank system was offline |
| CBS error | Bank's core system returned an error |
| Pending status | Transaction is in-flight — not yet resolved |

Your PSP should be able to provide the specific NPCI response code for any failed transaction, which helps categorize whether it's U010 or another code.

## Escalation Path if Auto-Reversal Fails

```
Customer's account not credited after T+1
          ↓
File complaint with issuing bank
          ↓
Bank raises with NPCI via UDIR portal (3 working days)
          ↓
NPCI investigates and resolves (within 30 days)
          ↓
If unresolved: RBI Banking Ombudsman
          ↓
RBI mandates resolution within 30 days
```

## Timeline

| Milestone | Timeframe |
|-----------|-----------|
| Transaction failure | T+0 (immediate) |
| NPCI auto-reversal mandate | T+1 (next working day) |
| Customer complaint if no reversal | Within 30 days of transaction |
| Bank resolution mandate | 30 days from complaint |
| RBI Ombudsman if unresolved | If bank fails to resolve in 30 days |

## Merchant Prevention Strategies

While merchants can't prevent NPCI or bank failures, they can reduce their exposure:

- **Use real-time webhook confirmation** from your PSP before showing "payment successful" — don't rely on polling
- **Implement idempotency keys** in your payment API integration to prevent double processing on retries
- **Use NPCI's Transaction Status API** to verify payment status before order fulfillment
- **Show "pending" status to customers** rather than "failed" immediately — give the auto-reversal time to work
- **Don't encourage immediate retries** — a customer retrying on a pending transaction may result in double payment and a U002/U004 dispute

## FAQs

**Q: My PSP says the payment failed but the customer says money was deducted. Who is right?**
Both can be correct simultaneously. The customer's bank debited the account, but the credit didn't reach your PSP — this is U010. Check your payment gateway's NPCI status API for that UTR. If it shows failed on your side, the money is in limbo and will auto-reverse to the customer by T+1.

**Q: Can I receive a credit for a transaction that my gateway shows as failed?**
Yes, occasionally. NPCI's settlement process sometimes credits the merchant even if the gateway reported a timeout. Check your bank statement daily against your gateway report. If you find an unexplained credit, hold it and notify your PSP — do not spend it until the dispute period (30 days) passes.

**Q: A customer is threatening to file a U010 complaint against me — what should I do?**
Explain that U010 is a bank/system issue, not a merchant issue. Provide them with the UTR status showing the transaction failed on the payment network side (not fulfilled by you). Direct them to their bank for the auto-reversal. You have no ability to credit them from the UPI layer — only the bank can reverse.

**Q: Is U010 common? Should I worry about it?**
U010 disputes are relatively uncommon compared to U003 or U008, and they generally don't result in merchant liability. However, during NPCI system outages or bank maintenance windows, a cluster of U010 disputes can appear. Monitoring your failed transaction rate and responding quickly to PSP queries during these periods is sufficient.

## Key Takeaways

- U010 is a system failure — neither customer nor merchant is typically at fault
- The bank or PSP whose system failed bears the liability
- NPCI mandates T+1 auto-reversal for unresolved transactions
- Merchants should not fulfill orders for transactions in pending/unknown state
- Most U010 cases resolve automatically without merchant action
- If auto-reversal fails, the customer escalates to bank → NPCI → RBI Ombudsman
