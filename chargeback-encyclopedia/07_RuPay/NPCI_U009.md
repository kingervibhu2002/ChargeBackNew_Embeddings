---
title: "NPCI U009 — Merchant Not Providing Refund"
section: "07_RuPay"
category: "RuPay / NPCI Reason Codes"
network: "RuPay / NPCI"
reason_code: "U009"
document_type: "Reason Code Reference"
keywords: ["NPCI", "UPI", "refund", "U009", "refund not received", "delayed refund", "merchant refund"]
difficulty: "Beginner"
---

# NPCI U009 — Merchant Not Providing Refund

## Overview

U009 is raised when a customer is entitled to a refund — due to returned goods, cancelled service, undelivered order, or a merchant's stated refund policy — but the merchant has not processed the refund within the expected timeframe.

This code focuses specifically on **refund disputes**, not delivery disputes (U008) or fraud (U001). The key trigger is that a refund obligation exists (either by merchant agreement or NPCI/RBI guidelines) but was not honored.

NPCI mandates specific refund timelines for UPI transactions. Merchants who miss these timelines risk U009 disputes even if they eventually intended to refund.

## NPCI Mandated Refund Timelines

Under NPCI guidelines and RBI directives:

| Refund Type | Maximum Timeline |
|-------------|-----------------|
| Auto-reversal for failed transactions | T+1 (next working day) |
| Merchant-initiated refund for cancellation | 5–7 working days |
| Refund for returned physical goods | 7 working days from return receipt |
| Refund for cancelled services | 5 working days from cancellation confirmation |

Customers can file a U009 dispute with their bank if the refund is not received within these windows.

## Common Scenarios

**Merchant agreed to refund but delayed**: Customer returned goods or cancelled a service. Merchant agreed to refund but didn't process it within 7 days. Customer files U009.

**Refund processed but not received**: Merchant processed the refund in their system, but it didn't reach the customer's account due to wrong VPA, failed transfer, or PSP issue.

**Partial refund dispute**: Merchant issued a partial refund (less than the full amount) but customer believes they are entitled to the full amount. Dispute over refund amount.

**Refund promised verbally but not initiated**: Customer service agent promised a refund during a call, but it was never processed in the payment system.

**Cancelled order refund delayed**: Customer cancelled an order immediately after placing it (before dispatch) but the merchant is slow to process the refund.

## Merchant Liability

**Merchant is liable when:**
- Refund was promised (written or verbal, supported by CRM/chat records) but not processed
- Goods were returned and received by the merchant but refund wasn't initiated
- Cancellation was requested within the merchant's stated policy window and no refund followed

**Merchant has a defense when:**
- Refund was processed — UTR/transaction reference for the refund payment exists
- Refund was processed but customer has not received it due to their bank's delay (NPCI can verify)
- Customer's return didn't meet the stated return policy conditions (clearly disclosed at time of purchase)
- Refund timeline was correctly communicated and hasn't yet expired

## Required Evidence

**When refund was processed:**
- UPI refund transaction ID / UTR for the refund payment
- Timestamp of refund initiation
- Customer's VPA that the refund was sent to
- Payment gateway refund confirmation record

**When disputing a refund obligation:**
- Refund/return policy displayed at time of purchase (screenshot, order confirmation email)
- Cancellation request records showing customer cancelled outside the policy window
- CRM records showing no refund was agreed upon
- Proof that goods were not returned (if return is required for refund)

## How to Avoid U009 Disputes

**Process refunds immediately**: As soon as a refund is agreed upon — whether through customer service, a return portal, or a cancellation — process it in your payment system the same day. A same-day or next-day refund virtually eliminates U009 risk.

**Confirm refund to customer**: Send an SMS or email with the refund transaction reference (UTR) as soon as it's processed. This gives the customer a reference and reduces follow-up complaints.

**Display refund timelines clearly**: On your returns/cancellation page, state the exact number of working days for refund processing. "Refunds within 5-7 working days" sets correct expectations.

**Use UPI for refunds (not NEFT/IMPS)**: UPI refunds are credited within hours; NEFT can take 1-2 days. Faster refunds mean fewer disputes.

**Build a refund tracking system**: Small merchants often lose track of pending refunds. A simple spreadsheet or CRM field marking "refund due by [date]" prevents missed refunds.

## Timeline

| Milestone | Timeframe |
|-----------|-----------|
| Customer's refund window expires | Per NPCI guidelines (5-7 working days) |
| Customer files U009 with bank | After refund window expires |
| NPCI notifies merchant | Within 7 days of bank receiving complaint |
| Merchant response window | 30 days from NPCI notification |
| Bank/NPCI resolution | 30 days from complaint |
| RBI Ombudsman escalation | If unresolved after 30 days |

## Resolution Options

1. **If refund was already processed**: Provide the refund UTR and timestamp. NPCI verifies in settlement records. Dispute closed.
2. **If refund was not processed**: Process it immediately upon receiving U009 notification. Provide UTR to NPCI. Dispute closed.
3. **If refund is disputed** (partial refund, outside return policy): Submit return policy evidence, CRM records. NPCI adjudicates based on merchant's documented policy.

## FAQs

**Q: I processed the refund 5 days ago but the customer says they haven't received it. What do I do?**
Provide the refund UTR to NPCI. They will query the beneficiary bank (customer's bank) to confirm receipt. If the refund was sent to the correct VPA, the customer's bank will confirm it's there. Delays on the customer's bank side are not the merchant's responsibility once the UTR is issued.

**Q: A customer filed U009 but they cancelled outside my return policy window. Do I have to refund?**
Not necessarily — if your return policy clearly states the conditions and timeline and the customer cancelled outside those terms, you can defend the dispute with your policy documentation. However, if the policy wasn't visible at checkout, NPCI may rule against you.

**Q: How do I handle a U009 if my customer service agent promised a refund by mistake?**
Honor it. If a CRM record or chat transcript shows your agent promised a refund, NPCI will see that as a binding commitment. Process the refund immediately to avoid escalation to NPCI/RBI.

**Q: Can I be penalized for multiple U009 disputes?**
Yes — repeated U009 disputes against the same merchant VPA can result in your acquiring bank flagging your account, increasing reserve requirements, or potentially flagging for NPCI review. Maintain a clean dispute record.

## Key Takeaways

- U009 is entirely preventable: process refunds promptly and keep records
- NPCI mandates 5-7 working day refund timelines — exceeding these triggers U009 rights
- Always send refund UTR to the customer immediately after processing
- If a refund was processed, the UTR is your complete defense
- Clear, visible return policies at checkout protect against unjustified U009 claims
