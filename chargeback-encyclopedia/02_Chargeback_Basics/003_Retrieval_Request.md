---
title: "Retrieval Request (Copy Request): What It Is and How to Respond"
section: "02_Chargeback_Basics"
category: "Chargeback Basics"
document_type: "Reference"
keywords: ["retrieval request", "copy request", "chargeback retrieval", "retrieval response", "retrieval window", "retrieval vs chargeback", "retrieval documents", "ignoring retrieval request", "auto chargeback", "retrieval deadline"]
difficulty: "Beginner"
---

# Retrieval Request (Copy Request): What It Is and How to Respond

A retrieval request is one of the earliest warning signs in the chargeback lifecycle — and one of the most commonly mishandled. Many merchants treat a retrieval request as routine paperwork when in fact it is an active dispute signal that, if ignored, automatically converts into a chargeback. Responding promptly and completely to retrieval requests is one of the most cost-effective chargeback prevention actions a merchant can take.

## What Is a Retrieval Request?

A **retrieval request** (also called a **copy request** in some network terminologies) is a formal request from a cardholder's issuing bank asking the merchant — via the acquirer — to provide documentation related to a specific transaction. The issuer sends the retrieval request because:

- The cardholder has contacted their bank to inquire about a transaction.
- The issuer wants to investigate before formally filing a chargeback.
- The issuer needs transaction documentation to complete its dispute assessment.
- The cardholder has claimed they don't recognize the transaction.

A retrieval request is **not** a chargeback. The disputed funds have not yet been reversed. This is the issuer's preliminary investigation step — and the merchant's best opportunity to resolve the dispute before it becomes a formal chargeback.

## Why Issuers Send Retrieval Requests

Not all issuers use retrieval requests — it is optional. Some issuers skip directly to filing a chargeback. When an issuer does send a retrieval request, the typical trigger scenarios are:

- **Cardholder inquiry**: The cardholder contacts the bank saying "I don't recognize this charge" or "I need more information about this transaction."
- **Large transaction value**: Higher-value disputes may warrant documentation review before the formal chargeback process begins.
- **Issuer fraud investigation**: The issuer suspects fraudulent activity and wants transaction documentation as part of a broader fraud investigation.
- **Regulatory requirement**: In some jurisdictions, issuers are required to give merchants an opportunity to provide documentation before filing a chargeback.

The retrieval request serves the issuer and the cardholder — but it also serves the merchant, because it is an opportunity to intervene before the formal chargeback is initiated.

## The Response Window

This is the most critical operational detail about retrieval requests: **there is a strict response deadline**.

- **Visa**: Typically 10 calendar days from the retrieval request date.
- **Mastercard**: Typically 20 calendar days.
- **Amex**: Typically 20 calendar days.
- **Discover**: Typically 20 calendar days.

Your acquirer or PSP may impose an even shorter internal deadline (e.g., responding to them 2–3 days before the network deadline). Always observe your acquirer's deadline, not just the network's.

**Consequence of missing the deadline**: If you do not respond within the window, the issuer receives no documentation. This typically results in an automatic chargeback being filed. You have converted an opportunity to prevent the chargeback into a guaranteed loss of at least the chargeback fee, plus the potential loss of the transaction amount.

## What Documents to Include in Your Response

A retrieval request response should be thorough, organized, and relevant. The issuer is looking for transaction evidence that confirms the legitimacy of the charge. Include:

### Core Transaction Documentation
- **Sales receipt or invoice**: The original transaction record showing the amount, date, and description.
- **Authorization approval code**: Proof the transaction was authorized by the issuer.
- **Cardholder signature** (for card-present): A signed receipt is strong evidence the cardholder was physically present and consented to the charge.

### For Card-Not-Present Transactions
Since there is no physical signature for online transactions, substitute with:
- **IP address and device fingerprint** at time of purchase
- **Email address used for the order**
- **Billing and shipping address provided**
- **AVS/CVV match response** from authorization
- **3DS authentication result** (if 3DS was used — this is powerful evidence)
- **Order confirmation email** sent to the customer's email address
- **Customer login records** showing account activity associated with the transaction

### For Delivery-Based Disputes
- **Tracking number and carrier name**
- **Delivery confirmation screenshot** from the carrier's website
- **Delivery date**
- **Delivery address** matching what the cardholder provided

### For Service-Based Transactions
- **Service agreement or contract**
- **Records of service delivery** (logins, usage records, access logs)
- **Customer communications** confirming satisfaction or acknowledging receipt

### Supporting Context
- **Merchant's return and cancellation policy** (demonstrated to be clearly disclosed at checkout)
- **Any prior customer communications** about the transaction
- **Evidence this customer has transacted with you before** (purchase history, account registration)

## Difference Between a Retrieval Request and a Chargeback

| Feature | Retrieval Request | Chargeback |
|---|---|---|
| **Who initiates** | Issuing bank | Issuing bank |
| **Funds reversed?** | No | Yes — immediately |
| **Chargeback fee charged?** | No | Yes |
| **Ratio impact** | No | Yes |
| **Merchant response required?** | Yes (recommended) | Yes (representment) |
| **Response window** | 10–20 days | 20–45 days |
| **Consequence of no response** | Automatic chargeback | Automatic loss |
| **Opportunity to prevent chargeback** | Yes | No (chargeback already filed) |

## What Happens After You Respond

Once you submit documentation to a retrieval request:

**Scenario A: Issuer accepts your documentation**
The issuer reviews your response and determines the transaction was legitimate. The cardholder's inquiry is resolved without a chargeback. You keep your funds, pay no chargeback fee, and your ratio is unaffected.

**Scenario B: Issuer files a chargeback anyway**
Your documentation did not resolve the issuer's concerns, or the cardholder's claim falls under a reason code that isn't addressed by the evidence you provided. A chargeback is filed. However, the documentation you submitted for the retrieval request becomes the foundation of your representment — you have a head start.

**Scenario C: Retrieval request was for compliance purposes**
Some retrieval requests are sent as part of the issuer's regulatory compliance processes (e.g., foreign transaction investigation). These may be resolved by simply confirming the transaction took place.

## Ignoring a Retrieval Request

Many merchants, especially those using PSPs or managing chargebacks manually, miss retrieval requests because:
- The notification was lost in email spam or portal notifications
- Staff turnover meant no one was assigned to monitor dispute queues
- The merchant assumed it was "just a request" and not urgent

**The consequence**: An automatic chargeback is generated. You now face the full chargeback process: funds reversed, fee charged, ratio impacted. The opportunity to prevent the chargeback is gone.

The cost of ignoring a retrieval request is exactly the same as the cost of losing a chargeback — because that is precisely what happens.

## Best Practices for Managing Retrieval Requests

1. **Monitor dispute queues daily**: Set up notifications so retrieval requests trigger immediate alerts.
2. **Assign ownership**: Designate specific team members to handle dispute and retrieval notifications.
3. **Respond to 100% of retrieval requests**: Even if you think the dispute has merit against you, respond. Provide whatever documentation you have. A partial response is better than no response.
4. **Keep transaction records accessible for 18+ months**: Card network rules require evidence retention for at least 13 months; 18 months is a safer standard given chargeback timeframes.
5. **Use your acquirer's dispute portal**: Most acquirers provide a portal where retrieval requests, chargebacks, and deadlines are tracked. Use it consistently.
6. **Respond early**: Don't wait until the last day. Submit documentation as soon as possible to allow the issuer maximum time to review before the chargeback window expires.

---

## FAQs

**Q: Does responding to a retrieval request guarantee I won't get a chargeback?**
No. The issuer may review your documentation and still file a chargeback. However, responding greatly reduces the probability of a chargeback being filed and ensures you have evidence ready if one is.

**Q: Can I see why the retrieval request was sent?**
Retrieval requests typically include a reason code or brief description of the cardholder's inquiry. This tells you what kind of dispute you're facing: unauthorized transaction, not received, not as described, etc. Tailor your response to address the specific claim.

**Q: Do all chargebacks start with a retrieval request?**
No. Issuers can skip the retrieval request and file a chargeback directly. This is increasingly common as dispute processing has become more automated. Never rely on receiving a retrieval request as a warning — monitor your dispute queues proactively.

**Q: How do I respond to a retrieval request if I no longer have the transaction records?**
This is a serious problem. If you cannot locate transaction records, respond with whatever you do have and explain the situation. However, this is why document retention policies are critical. Network rules require merchants to retain transaction records for a minimum period; many disputes become unwinnable simply because the merchant discarded the relevant records.

**Q: Is there a fee for receiving a retrieval request?**
Typically no — retrieval requests themselves do not carry a fee. However, if you fail to respond and a chargeback is generated, you then incur the standard chargeback fee ($15–$100). Some acquirers charge a small retrieval processing fee ($5–$15), but this is less common than chargeback fees.
