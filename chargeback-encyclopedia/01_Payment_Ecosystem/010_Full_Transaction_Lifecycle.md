---
title: "Full Transaction Lifecycle: From Click to Funding"
section: "01_Payment_Ecosystem"
category: "Payment Ecosystem"
document_type: "Reference"
keywords: ["transaction lifecycle", "payment flow", "authorization", "authentication", "capture", "clearing", "settlement", "funding", "chargeback flow", "what can go wrong", "payment steps", "end-to-end payment", "payment processing steps"]
difficulty: "Beginner"
---

# Full Transaction Lifecycle: From Click to Funding

Every card transaction passes through a predictable sequence of steps from the moment a customer initiates payment to the moment funds land in the merchant's bank account. Understanding this complete lifecycle helps merchants identify where problems originate, why chargebacks occur at specific points, and what evidence exists at each stage to support dispute resolution.

## Overview: The Seven Stages

1. Customer Initiates Payment
2. Authentication
3. Authorization
4. Capture
5. Clearing
6. Settlement
7. Funding

A chargeback can occur **after funding** and effectively reverses the entire flow. Understanding each step illuminates why.

---

## Stage 1: Customer Initiates Payment

**What happens**: The customer selects a payment method and enters card credentials at the merchant's checkout (online) or presents their card at a terminal (in-store).

**Data involved**:
- Card number (PAN), expiration date, CVV (for CNP)
- Billing address (for CNP, used in AVS)
- Device fingerprint, IP address, browser data (for online)

**Technical process**:
- Online: The payment gateway captures the card data via a hosted payment page or JavaScript tokenization. Card data is immediately tokenized — the raw PAN is replaced with a non-sensitive token before being stored or transmitted.
- In-store: The EMV chip card interacts with the terminal, generating a cryptographic transaction code unique to this specific transaction.

**What can go wrong**:
- Cardholder enters incorrect card data → authorization will fail.
- Merchant stores raw PAN data → PCI-DSS violation, significant fraud risk.
- Checkout page is down → customer cannot complete purchase; no transaction occurs.
- Malicious script on checkout page (Magecart attack) → card data stolen, used for future fraud chargebacks.

---

## Stage 2: Authentication

**What happens**: Before or during authorization, the system verifies that the cardholder is who they claim to be.

**In-store**: EMV chip verification occurs between the card and terminal. For PIN-authenticated transactions, the cardholder enters their PIN.

**Online (3D Secure)**: The merchant's gateway submits a 3DS authentication request. The issuer's Access Control Server evaluates hundreds of risk signals. For most low-risk transactions, authentication completes silently (frictionless flow). For higher-risk transactions, the cardholder receives an OTP or biometric challenge.

**Authentication result**:
- **Authenticated**: Issuer confirms cardholder identity. Liability for fraud chargebacks shifts to issuer.
- **Attempted**: Authentication was attempted but issuer didn't participate. Some liability shift still applies.
- **Failed**: Cardholder failed authentication. Merchant should decline to process.
- **Not authenticated**: No 3DS used. Merchant retains full fraud liability.

**What can go wrong**:
- Merchant doesn't implement 3DS → all online fraud liability stays with merchant.
- False challenge — cardholder abandons during OTP step → cart abandonment, lost sale.
- 3DS timeout → transaction falls through without authentication data.
- Incorrect MID configuration → wrong authentication data submitted to authorization.

---

## Stage 3: Authorization

**What happens**: The authorization request (including authentication data if applicable) travels from the merchant terminal/gateway → processor → card network → issuer. The issuer evaluates and returns an approval or decline in 1–3 seconds.

**Issuer evaluation factors**:
- Available credit or account balance
- Real-time fraud scoring
- AVS and CVV match results
- Geographic and behavioral risk signals
- Velocity checks (too many transactions in a short window)

**Authorization response**:
- **Approved**: Issuer returns a 6-character approval code. Funds are placed on hold.
- **Declined**: Issuer returns a decline code (see 008_Authorization_and_Authentication for code reference).

**What can go wrong**:
- Authorization is approved but card was stolen → fraud chargeback later. The approval code does not confirm the authorized cardholder made the purchase.
- Authorization approved for wrong amount → capturing a different amount creates chargeback risk.
- Duplicate authorization sent → merchant may accidentally charge twice. Double-billing chargebacks result.
- Authorization expires before capture → if a merchant captures after the authorization has expired (typically 7 days for most card types, 30 days for hotel/rental), the capture lacks authorization backing and creates chargeback exposure.

---

## Stage 4: Capture

**What happens**: The merchant submits the authorized transaction for payment. This is the formal claim of the funds. Capture can happen immediately (at authorization) or later (for hotels, rentals, subscriptions billed after service delivery).

**Two models**:
- **Auth + immediate capture**: Authorization and capture happen simultaneously (common in e-commerce). The transaction is authorized and captured in a single step.
- **Auth + delayed capture**: Authorization creates a hold; capture occurs later when the transaction amount is confirmed (hotel checkout, subscription billing date, fulfillment-based billing). A delay between auth and capture must comply with network rules on authorization validity periods.

**What can go wrong**:
- Capture amount exceeds authorization amount significantly → misuse of authorization; chargeback risk.
- Capture without prior authorization (forced sale) → network rule violation, full chargeback liability, potential fines.
- Merchant captures a declined or expired authorization → will likely fail in clearing and may result in chargebacks.
- Multiple captures for one authorization → duplicate billing chargebacks.

---

## Stage 5: Clearing

**What happens**: The merchant's terminal or gateway submits a batch of captured transactions to the acquirer, typically at end of day. The acquirer forwards the batch to the card network. The network processes the clearing file, determines interchange fees, and routes payment obligations to each issuer.

**Timeline**: T+0 to T+1 (same day or next business day after capture/batch submission)

**What can go wrong**:
- Merchant fails to submit batch → transactions don't clear, revenue delayed. Recurring failure to batch is a network rule violation.
- Batch submitted with incorrect merchant data → transactions may be rejected during clearing.
- Currency conversion errors → incorrect amounts posted to cardholder statements, triggering billing error chargebacks.
- Transaction date mismatch → clearing date differs significantly from authorization date, creating documentary confusion in disputes.

---

## Stage 6: Settlement

**What happens**: After clearing determines what each party owes, actual fund transfers occur between financial institutions via the banking system. The issuer funds the network settlement position. The network funds the acquirer. Settlement is typically a net process — the acquirer receives the net of all transactions across all issuers for the day.

**Timeline**: T+1 to T+2

**What can go wrong**:
- Chargeback received during clearing interrupts settlement → funds reversed before merchant receives them.
- Reserve withholding reduces expected deposit → merchant confuses reserve deduction with processing error.
- Acquirer technical issues → settlement delayed. Merchant should contact acquirer if funding doesn't arrive within expected timeframe.

---

## Stage 7: Funding

**What happens**: The acquirer credits the merchant's linked bank account with the net settlement amount (gross volume minus interchange, processing fees, chargebacks, refunds, and reserve withholdings).

**Timeline**: Typically T+1 to T+2 for standard accounts; same day or next day for premium funding programs.

**What can go wrong**:
- Merchant's linked bank account has incorrect details → ACH transfer fails; re-deposit delay of 3–5 business days.
- Acquirer places a funding hold on the account → funds withheld due to elevated chargeback risk, fraud indicators, or suspicious volume spike.
- Account closed by acquirer → remaining funds held in reserve; release timeline extends 90–180 days.

---

## Post-Funding: The Chargeback Reversal

A chargeback occurs **after funding**. The customer has received their goods or services, the merchant has been paid, and then the cardholder disputes the transaction. The chargeback flows in reverse:

1. Cardholder → Issuer: Dispute filed, provisional credit granted.
2. Issuer → Card Network: Chargeback message transmitted.
3. Card Network → Acquirer: Acquirer debited.
4. Acquirer → Merchant: Merchant account debited, notification sent.
5. Merchant → Acquirer → Network → Issuer: Merchant has the opportunity to submit representment evidence.

From the merchant's perspective, the money was earned, deposited, and then forcibly taken back. This is why the term "forced reversal" accurately describes a chargeback — it is not a voluntary refund but a compelled return of funds driven by the card network's rules.

---

## Timeline Summary

| Stage | Timing | Party Responsible |
|---|---|---|
| Authentication | Real-time (ms) | Merchant + Issuer |
| Authorization | Real-time (1–3 sec) | Issuer (decision), Merchant (initiates) |
| Capture | Immediate to 7–30 days | Merchant |
| Clearing | T+0 to T+1 | Acquirer + Network |
| Settlement | T+1 to T+2 | Network + Issuer |
| Funding | T+1 to T+2 | Acquirer |
| Chargeback window | Up to 120 days post-transaction | Cardholder/Issuer |
| Merchant response | 20–45 days from chargeback notice | Merchant |

---

## FAQs

**Q: At what stage is chargeback risk highest?**
Chargeback risk is inherent once a transaction is authorized and captured. However, risk factors are established much earlier — during authentication (whether liability shift applies) and at the point of sale (whether terms and policies were clearly disclosed). Strong practices at each early stage reduce chargeback probability and improve dispute win rates.

**Q: If authorization was approved, why can the transaction still be charged back?**
Authorization confirms the card had funds and the issuer's fraud system didn't block it in real time. It does not confirm the cardholder authorized the purchase. A stolen card can be authorized successfully. 3DS authentication is the mechanism that provides stronger cardholder identity verification and shifts liability.

**Q: How long after I receive funds can a chargeback occur?**
Up to 120 days from the transaction date for most reason codes under Visa and Mastercard rules. For services not yet rendered (e.g., future travel, subscriptions), the window may begin from the expected service date. A customer who purchased in January can file a chargeback in April.

**Q: What evidence is generated at each lifecycle stage that I can use in a dispute?**
Authorization: authorization code, AVS/CVV response, 3DS authentication data. Capture: capture timestamp, amount. Delivery/fulfillment: delivery confirmation, IP logs, email records, usage logs. All of these are valuable pieces of compelling evidence in representment.

**Q: Can I stop a chargeback from occurring once I know a customer is unhappy?**
Proactive customer service is the most effective chargeback prevention. If you know a customer is dissatisfied, contact them before they file a dispute. Offering a refund or resolution directly costs less than a chargeback (no chargeback fee, no ratio impact). Once a chargeback is initiated, it must run through the formal dispute process — you cannot "cancel" it, but you can respond and potentially win it.
