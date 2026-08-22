---
title: "NPCI UPI Dispute Code U001 — Transaction Not Done by Customer (Fraud)"
description: "Complete merchant guide to NPCI UPI dispute code U001: unauthorized UPI transactions, OTP fraud, SIM swap attacks, merchant evidence requirements, and merchant liability framework."
category: RuPay / NPCI
reason_code: "U001"
chargeback_type: "Transaction Not Done by Customer — Unauthorized UPI Transaction"
win_rate: High for merchant (liability typically with bank/PSP in authenticated transactions)
last_updated: 2026-06-29
tags: [NPCI, UPI, U001, fraud, unauthorized-transaction, OTP-fraud, SIM-swap, vishing, merchant-guide, India]
---

# NPCI U001 — Transaction Not Done by Customer (Fraud)

## What This Dispute Code Means

NPCI UPI dispute code U001 is filed when a customer reports that a UPI transaction was made without their knowledge or authorization. The customer is asserting that they did not initiate or approve the transaction and that the money that left their account was taken without their consent.

In the UPI ecosystem, "unauthorized" typically means one of several fraud mechanisms was used to access the customer's UPI account and extract funds. Unlike card fraud where a criminal can use stolen card numbers remotely, UPI fraud almost always involves some form of social engineering — the customer is manipulated into taking an action that facilitates the fraudulent transfer.

---

## How UPI Fraud Happens: The Mechanics of U001

Understanding UPI fraud mechanisms is essential for merchants to assess their evidence position.

### OTP-Based Vishing (Voice Phishing)

A criminal calls the customer impersonating a bank official, NPCI employee, or government representative. The criminal claims the customer's account needs "verification," their card will expire, they won a lottery, or their account was compromised. During the call, the criminal asks the customer to:
- Share the OTP sent to their registered mobile number
- Enter the UPI PIN on their phone while the criminal watches via screen share
- Approve a "collect request" sent to their UPI app (framed as a "refund" or "prize")

The customer complies, the criminal completes the transfer, and the customer only realizes what happened when they see the transaction on their bank statement.

### Screen Sharing Fraud

The criminal convinces the customer to install a remote access application (AnyDesk, TeamViewer, Quick Support) under the guise of providing technical support. Once screen sharing is active, the criminal watches the customer's UPI app, guides them to open a UPI app, and captures the UPI PIN as the customer enters it. The criminal then executes transactions directly.

### SIM Swap Fraud

A criminal obtains a duplicate SIM card by bribing a mobile carrier employee or submitting fraudulent documentation at a carrier store. With the duplicate SIM, the criminal receives all OTPs sent to the customer's registered mobile number. The criminal then uses these OTPs to authorize UPI transactions or reset UPI credentials.

### Collect Request Fraud

UPI allows one party to send a "collect request" to another requesting payment. Criminals send collect requests framed as "refund confirmation" or "verification credit" — when the customer approves the collect request, funds are transferred to the criminal.

### Malicious UPI App

Fake or compromised UPI applications capture UPI PINs and transaction data. These are less common but represent a growing fraud vector.

---

## Merchant's Position in U001 Disputes

The merchant's liability position in a U001 dispute depends critically on whether the UPI transaction was properly authenticated.

**Standard UPI authentication flow:**
1. Customer initiates payment (or approves a collect request)
2. UPI app sends a request to the bank with the customer's VPA and amount
3. Customer enters UPI PIN (6-digit PIN known only to the customer)
4. Bank verifies the PIN and authorizes the transaction
5. NPCI processes the settlement
6. Merchant receives funds

**If the UPI PIN was correctly entered:** The transaction was authenticated. The PIN is the customer's personal authentication factor — similar to a bank's view of a card PIN. Under NPCI's framework, a correctly authenticated UPI transaction is presumptively authorized. The bank's obligation shifts to investigating how the PIN was compromised (through the fraud types above).

**The merchant's position:** Merchants receiving funds from a properly authenticated UPI transaction are **generally not liable** for fraud disputes — they received payment through the legitimate payment infrastructure with all required authentication steps completed. The fraud liability typically sits with:
- The customer's bank (for failing to detect unusual transaction patterns)
- The PSP/UPI app provider (for inadequate fraud controls)
- The customer (if they knowingly shared their PIN or approved a collect request)

---

## Evidence the Merchant Should Maintain

While merchants are typically not directly liable in U001 disputes, they may be asked by their acquiring bank to provide evidence of the transaction:

**Transaction log showing:**
- UPI transaction reference number (UTR — Unique Transaction Reference)
- Amount and timestamp
- Customer's VPA (Virtual Payment Address) used for payment
- Merchant's VPA
- Authentication status (whether UPI PIN was verified successfully)
- NPCI transaction ID

**Order records:**
- The order or service that the UPI payment corresponds to
- Order confirmation sent to the customer
- Delivery records (if goods were dispatched)
- Service completion records (if services were rendered)

**NPCI and PSP communication:**
- Confirmation from your payment service provider that the transaction was processed normally
- NPCI settlement record confirming the funds were received

---

## Merchant's Obligation When Goods Were Delivered to a Fraudster

If a fraudulent UPI transaction funded an order and the merchant shipped goods to the address provided — and the cardholder's fraud claim is valid — the merchant faces a difficult situation:

- The UPI transaction may be reversed, debiting the merchant's settlement account
- The shipped goods are unlikely to be recovered
- The merchant must file a claim with their acquirer/PSP for the loss

**Best practices to minimize this exposure:**
- For high-value orders, verify delivery address against customer contact information
- Implement velocity checks: multiple high-value orders from the same VPA in a short window are suspicious
- For digital goods, implement delivery logging that can demonstrate the goods were delivered to the account associated with the VPA
- For physical goods, use signature-required delivery for orders above a threshold

---

## NPCI Fraud Reporting

When multiple U001 disputes involve the same fraud pattern (same VPA, same fraud mechanism, same timeframe), NPCI wants to know. Merchants and their acquirers can report fraud patterns to NPCI through their PSP's fraud reporting mechanism. This helps NPCI identify compromised VPAs and alert other PSPs.

Banks investigating U001 complaints are required to file NPCI fraud reports and coordinate with law enforcement. The RBI's cybercrime coordination cell (CERT-In) and local police cybercrime units handle UPI fraud investigations. <!-- NEEDS VERIFICATION: confirm CERT-In's specific role in UPI fraud investigation against real RBI/CERT-In documentation — this names a specific government body with a specific claimed function -->

---

## Frequently Asked Questions

**Q: A customer filed U001 claiming fraud, but our records show the goods were delivered to their registered address. What do we do?**
A: Submit delivery records (carrier POD or tracking confirmation showing delivery to the VPA-registered address) along with the UTR and transaction log. Delivery to the customer's own address undermines the fraud claim — a fraudster would have shipped to an alternate address. Your acquirer will use this evidence in the NPCI dispute response.

**Q: The fraud happened through a collect request the customer approved. Are we at fault?**
A: No. If the customer approved a collect request sent by your business through standard UPI channels, you are a legitimate payee. However, if your VPA or collect request mechanism was compromised and fraudulent collect requests were sent impersonating your business, contact your PSP immediately and report the incident to NPCI.

**Q: Our customer's funds were reversed after a U001 dispute was upheld. How do we recover?**
A: If you delivered goods or services in good faith on a properly authenticated UPI payment, and the payment was subsequently reversed due to a fraud claim, consult your acquiring bank about your recovery options. In some cases, delivery evidence supporting your position can be submitted to prevent the reversal. If the reversal occurs, your loss may be partially covered by transaction insurance if you carry it.

**Q: How quickly does NPCI investigate U001 disputes?**
A: Banks are required to resolve UPI disputes within 30 days of the complaint. <!-- NEEDS VERIFICATION: same 30-day mandate flagged in 000_RuPay_NPCI_Overview.md; verifying it once there covers this repetition too --> For clear technical failures, resolution may be faster. For complex fraud investigations, the full 30-day window is typically used.

**Q: What should merchants do if they see a suspicious UPI payment pattern — many transactions from the same VPA, unusual amounts or timing?**
A: Flag these immediately with your PSP and do not dispatch goods until you have verified the orders. Suspicious patterns may indicate a compromised account being used for mule transactions. Report the pattern to your PSP for escalation to NPCI's fraud monitoring team.
