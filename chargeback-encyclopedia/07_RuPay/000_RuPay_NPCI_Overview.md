---
title: "RuPay and NPCI Dispute Process — Complete Overview"
description: "Comprehensive guide to the RuPay card network and NPCI UPI dispute process: India's domestic payment ecosystem, auto-reversal rules, chargeback timelines, ombudsman escalation, how NPCI disputes differ from Visa/Mastercard, the distinction between an informal refund request and a formal NPCI dispute, and what payment data can and cannot prove."
category: RuPay
type: Overview
last_updated: 2026-08-19
tags: [rupay, NPCI, UPI, India, dispute-process, chargeback, auto-reversal, payment-network, merchant-guide, banking-ombudsman, evidence, fulfillment-data]
---

# RuPay and NPCI Dispute Process — Complete Overview

## India's Domestic Payment Network: RuPay and NPCI

The National Payments Corporation of India (NPCI) is a not-for-profit organization established in 2008 under the guidance of the Reserve Bank of India (RBI) and the Indian Banks' Association. NPCI was created to consolidate and integrate India's retail payment systems under a single umbrella, reducing dependence on international networks and enabling affordable, scalable payment infrastructure for India's massive population.

**RuPay** is NPCI's flagship card payment network — India's domestic equivalent of Visa and Mastercard. Launched in 2012, RuPay cards are issued by Indian banks and accepted on NPCI's network infrastructure. RuPay has grown to become the largest card network in India by number of cards issued, largely through government programs like Jan Dhan Yojana (basic banking access for the unbanked) and Pradhan Mantri Kisan Samman Nidhi (farmer benefit disbursements).

**UPI (Unified Payments Interface)** is NPCI's real-time payment rails — a separate but related infrastructure enabling instant bank-to-bank transfers through mobile apps. UPI is not a card network; it operates on VPA (Virtual Payment Address) identifiers rather than card numbers. However, NPCI governs both RuPay and UPI, and disputes on both rails flow through NPCI's dispute resolution framework.

---

## RuPay vs. UPI: Two Different Rails

Merchants and consumers often conflate RuPay and UPI because both are NPCI products and because many UPI apps allow users to link RuPay credit cards for UPI credit payments. However, they are distinct:

| Dimension | RuPay | UPI |
|---|---|---|
| Transaction type | Card-based (POS, e-commerce) | Bank account to account transfer |
| Identifiers | Card number, CVV, expiry | VPA (Virtual Payment Address) |
| Settlement | Card payment settlement cycle | Near-instant (T+0 mandate) |
| Dispute codes | RuPay-specific chargeback codes | NPCI UPI codes (U001–U010) |
| Cardholder authentication | PIN/OTP at POS or online | UPI PIN (6-digit) set by user |

This overview addresses both RuPay card disputes and UPI transaction disputes, as both are governed by NPCI's framework.

---

## NPCI's Role in Dispute Resolution

NPCI functions as both the network operator and the dispute arbitrator for transactions on its rails — similar in some ways to American Express's closed-loop structure. Unlike Visa and Mastercard, which set rules that member banks implement, NPCI directly mandates dispute resolution timelines and processes that all participating banks must follow.

**Banks are obligated to:**
- Resolve disputes within **30 days** of the complaint being filed
- Process auto-reversals within **T+0 or T+1** (same day or next business day) for failed transactions that meet auto-reversal criteria
- Report unresolved disputes to NPCI through the NPCI dispute management system

Merchants are less directly involved in NPCI's dispute framework than in Visa/Mastercard disputes. In most NPCI dispute scenarios, the dispute is between the customer's bank (issuing bank) and the merchant's bank (acquiring bank), with NPCI arbitrating. The merchant's role is primarily to provide settlement records, transaction confirmation, or delivery evidence to their bank.

---

## UPI Dispute vs. Merchant Refund Request: Two Different Events

Not every customer complaint about a Google Pay, PhonePe, or other UPI app payment is a formal NPCI dispute — conflating the two leads merchants to either over-react to routine customer service messages or under-react to something that's already escalated.

**If the payment succeeded and the customer's issue is with the merchant** — wrong item, item not as described, wants to cancel, wants a refund for a legitimate reason — this is a **private commercial matter between the customer and the merchant**. The customer's own UPI app providers say as much: for a successful payment, the customer's first step is to contact the merchant directly for a refund, not their bank. Nothing here routes through NPCI unless the merchant refuses or fails to resolve it.

**A formal NPCI dispute (one of the U-codes) only exists when something went wrong at the payment layer itself**, or when a legitimate refund request goes unresolved long enough that the customer escalates to their bank instead of the merchant:

- Money moved but the merchant never received it (U003), or moved more than once (U002, U004) — a payment-mechanics failure, nothing to do with the merchant's service.
- The merchant did not deliver what was paid for, or refuses a refund the merchant already agreed was owed (U008, U009) — this is exactly the case where an unresolved customer-service issue *becomes* a formal dispute.
- The transaction itself was never authorized by the customer (U001, U005) — fraud, not a service complaint at all.

**Practical implication for merchants**: treat a customer's "where's my order?" or "I want a refund" message through chat, app support, or a marketplace inbox as a customer-service ticket to resolve directly — not as a dispute notice to wait out. There is no bank, NPCI case, or formal deadline attached to it yet. Resolving it promptly at this stage is also the best way to prevent it from ever becoming a U008/U009 dispute against the merchant's account later.

---

## Merchant Response Window

For RuPay card disputes that reach the merchant acquiring bank, merchants typically have **30 days** to respond — consistent with NPCI's broader 30-day resolution mandate for banks. However, acquirers may impose tighter internal deadlines.

For UPI disputes (U001–U010), the dispute mechanism is primarily bank-to-bank via NPCI's chargeback/dispute system. Merchants are usually involved only if the dispute reaches the stage where the acquiring bank needs evidence of the transaction (delivery confirmation, service records, or settlement data).

---

## Auto-Reversal Rules: T+0 and T+1

One of NPCI's most important consumer protections is the auto-reversal mandate for failed transactions. When a UPI transaction fails technically (network timeout, PSP failure, system error), NPCI mandates:

- **T+0**: Auto-reversal should be initiated the same day as the failed transaction
- **T+1**: Auto-reversal must be completed by the next business day

These timelines mean that disputes categorized as U006 (Transaction Declined but Amount Debited), U003 (Customer Debited but Merchant Not Credited), and U010 (Technical Error) should resolve automatically without manual dispute intervention in most cases. When auto-reversal fails, the customer files a formal complaint with their bank, and the NPCI dispute mechanism is triggered.

Merchants should be aware of auto-reversals because they affect their settlement reconciliation — an auto-reversal will appear as a debit against the merchant's settlement for a transaction that the merchant may have already recorded as a credit.

---

## UPI Dispute Reason Codes (U001–U010)

NPCI's UPI dispute codes cover the primary categories of UPI transaction failures and disputes:

| Code | Description |
|---|---|
| U001 | Transaction Not Done by Customer (Fraud) |
| U002 | Duplicate Transaction |
| U003 | Customer Debited but Merchant Not Credited |
| U004 | Customer Account Debited Multiple Times |
| U005 | Fraudulent Transaction (broad classification) |
| U006 | Transaction Declined but Amount Debited |
| U007 | Wrong Amount Transferred |
| U008 | Goods or Services Not Delivered |
| U009 | Merchant Not Providing Refund |
| U010 | Technical Error / System Failure |

The most common codes in terms of dispute volume are U003 (settlement failure) and U006 (declined but debited), which are largely technical failures rather than fraud or merchant service disputes.

---

## How NPCI Disputes Differ from Visa and Mastercard

Understanding these differences is critical for merchants operating in India alongside international card acceptance.

**1. Merchant involvement is less direct.** Visa and Mastercard disputes typically flow directly to the merchant's acquiring bank and then to the merchant for a response. NPCI disputes are primarily bank-to-bank resolutions — many disputes resolve before the merchant is ever asked for evidence.

**2. Auto-reversal eliminates many disputes.** NPCI's T+0/T+1 auto-reversal mandate means that technical failure disputes (U006, U010, U003) often resolve automatically within hours or days, without formal dispute filings. Visa and Mastercard have no equivalent automatic reversal mechanism.

**3. Settlement is near-instant.** UPI operates on near-real-time settlement, meaning the acquirer receives funds almost immediately when a UPI transaction succeeds. This speed creates different failure modes (network timeouts during settlement handoff) compared to card networks where settlement occurs in batch cycles.

**4. Fraud disputes have different authentication.** UPI transactions are authenticated by a 6-digit UPI PIN known only to the customer. When fraud occurs on UPI (U001, U005), it typically involves social engineering — criminals trick customers into sharing OTPs or UPI PINs, or into approving collect requests. This is different from CNP card fraud where card data is compromised without the customer's involvement.

**5. NPCI dispute timelines are shorter.** The 30-day overall resolution mandate (from complaint to resolution) is more aggressive than Visa/Mastercard's multi-round process that can extend 4–6 months including arbitration.

---

## Indian Banking Ombudsman Escalation

When a customer's dispute is not resolved within 30 days by their bank — or when the resolution is unsatisfactory — customers can escalate to the **Reserve Bank of India Banking Ombudsman**. The Ombudsman's office handles complaints about banking services including payment transactions, and has authority to direct banks to resolve disputes and pay compensation.

Merchants are not direct parties in Ombudsman proceedings, but ombudsman complaints generate regulatory pressure on banks, which in turn may pressure merchants' acquiring banks for faster resolution. An escalated ombudsman complaint can result in forced credits to customers that then become chargebacks against merchants.

**Practical implication**: Indian merchants should treat customer complaints about transaction failures or non-delivery seriously and resolve them quickly. Unresolved customer complaints that reach the ombudsman stage create regulatory risk for the merchant's acquiring bank, which the acquirer will then direct toward the merchant.

---

## What Your Payment Data Can and Cannot Prove

A UPI app or PSP only ever sees the payment layer of a transaction — it has no visibility into whether the merchant actually fulfilled the order. Knowing this boundary matters when preparing evidence for a dispute, because the two categories of record live in entirely different systems.

**What UPI/NPCI transaction data can prove:**
- The UTR (UPI Transaction Reference) and NPCI case ID
- Amount and timestamp
- Payer and payee VPA
- Transaction status (success, failed, reversed)
- Which bank the funds settled to

**What it cannot prove — because it was never part of the payment record:**
- What was ordered (SKU, product, or service description)
- Whether the order shipped, and which courier handled it
- Proof of delivery (signature, GPS-confirmed drop, photo at door)
- Whether a service was actually rendered
- Whether a refund promised outside the payment rail (store credit, replacement) was honored

A UTR proves a payment happened. It proves nothing about whether the merchant did what the payment was for. For a U008 (goods or services not delivered) or U009 (merchant not providing refund) dispute, the acquiring bank and NPCI have only the payment-layer record — the merchant is the only party who can supply the fulfillment-layer evidence, and it has to come from the merchant's own order management, logistics/courier, or CRM systems, not from the payment gateway or PSP. See the Evidence section of this encyclopedia for what counts as acceptable proof of delivery and service completion.

---

## Merchant Obligations Under the NPCI Framework

Merchants processing UPI and RuPay payments have specific obligations:

- **Accept payments and issue acknowledgment**: Every successful payment must be acknowledged with a receipt or order confirmation
- **Process refunds within NPCI timelines**: For UPI, refunds should be processed within 5–7 business days of the refund request
- **Maintain transaction records**: Transaction logs must be retained for at least 6 months (and practically for 18–24 months to respond to late disputes)
- **Cooperate with bank disputes**: When an acquiring bank requests transaction evidence to respond to an NPCI dispute, provide it within the requested timeframe
- **Display refund policies**: Refund and return policies must be accessible to customers at point of sale or on the merchant website

---

## Frequently Asked Questions

**Q: A customer messaged me on Google Pay/WhatsApp saying they never got their order. Is that a chargeback?**
A: Not yet. That's a customer-service message, not a formal NPCI dispute — the customer contacted the merchant directly, which is exactly the right first step for a successful payment where the issue is with the merchant's fulfillment, not the payment itself. Resolve it directly (ship, refund, or explain) the same way you would any support ticket. It only becomes a formal U008/U009 dispute if it goes unresolved and the customer escalates to their bank instead.

**Q: My acquiring bank asked for proof of delivery on a UPI dispute. Can't they just check the transaction record?**
A: No — the transaction record only proves the payment happened (UTR, amount, timestamp, status). It has no visibility into whether you shipped anything. Proof of delivery has to come from your own order management or courier/logistics system, not from NPCI, your PSP, or your acquiring bank — none of them were ever party to the fulfillment side of the transaction.

**Q: My customer filed a UPI complaint with their bank. When will I know about it?**
A: You will typically learn about UPI disputes only if the dispute reaches your acquiring bank and the bank requests transaction evidence. For auto-reversal disputes (technical failures), you may never be formally notified — the bank system handles it. For merchant-fault disputes (U008, U009), your acquirer will contact you for evidence or may directly debit your settlement account.

**Q: Can a merchant fight a UPI dispute the same way as a Visa chargeback?**
A: The process is different. NPCI disputes are primarily a bank-level process. Merchants provide evidence to their acquiring bank, which submits it through NPCI's dispute resolution system. There is no direct merchant-to-issuer communication as in Visa/Mastercard disputes. Your key contacts are your acquirer and your payment service provider (PSP).

**Q: What is the difference between a RuPay chargeback and a UPI dispute?**
A: A RuPay chargeback follows a card-network dispute process similar to (but simpler than) Visa/Mastercard. A UPI dispute follows NPCI's UPI-specific dispute codes (U001–U010) and the auto-reversal framework. The underlying transaction rails are completely different, and the dispute mechanics reflect those differences.

**Q: Does NPCI have a monitoring program for merchants with high dispute rates?**
A: NPCI does track merchant dispute rates and works with acquiring banks to address merchants with elevated dispute or fraud activity. High-risk merchants may face additional compliance requirements, increased settlement reserves, or termination of payment acceptance privileges.

**Q: Are UPI transactions covered by the same consumer protection as card transactions?**
A: Yes — RBI regulations provide consumer protection for UPI transactions equivalent to card transactions. Banks are obligated to resolve disputes, process auto-reversals, and compensate customers for bank-error disputes. The regulatory framework may vary slightly from the network-rule framework of Visa/Mastercard, but the consumer protection outcomes are broadly similar.
