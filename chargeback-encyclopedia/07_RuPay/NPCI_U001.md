---
title: "NPCI UPI Dispute Code U001 — Transaction Not Done by Customer (Fraud)"
description: "Reference guide to NPCI UPI dispute code U001: unauthorized-transaction dispute reasons (vishing, SIM swap, screen-sharing, collect-request fraud), merchant evidence requirements, UPI authentication, and RBI customer-liability considerations."
category: RuPay / NPCI
reason_code: "U001"
chargeback_type: "Transaction Not Done by Customer — Unauthorized UPI Transaction"
last_updated: 2026-08-22
tags: [NPCI, UPI, U001, fraud, unauthorized-transaction, OTP-fraud, SIM-swap, vishing, screen-sharing, collect-request-fraud, merchant-guide, India]
---

# NPCI U001 — Transaction Not Done by Customer (Fraud)

## What This Dispute Code Means

NPCI UPI dispute code **U001 — Transaction Not Done by Customer (Fraud)** relates to a customer's claim that the disputed transaction was not initiated by them.

The important distinction is between the **reason for the dispute** and the **ultimate outcome of the dispute**.

U001 identifies the nature of the customer's claim. It does not, by itself, establish that:

* fraud definitely occurred;
* the merchant caused the fraud;
* the customer is liable;
* the merchant is liable; or
* the transaction must ultimately be reversed.

The applicable UPI dispute process, participant responsibilities, transaction records, and other relevant circumstances determine how the dispute is handled.

For a chargeback investigation, U001 should therefore be understood as an **unauthorized-transaction dispute reason**, rather than as an automatic liability determination.

---

## UPI Fraud and Unauthorized Transactions

A customer may report a UPI transaction as unauthorized for a number of reasons.

Examples include:

* credentials or authentication information being compromised;
* social-engineering attacks;
* phishing or vishing;
* SIM-swap or mobile-number compromise;
* malicious or compromised applications;
* remote-access or screen-sharing attacks; or
* other forms of account or device compromise.

These are examples of possible fraud mechanisms. They are not separate meanings of the U001 reason code.

The actual mechanism involved in a particular transaction must be established from the available investigation and transaction records.

---

## OTP-Based Vishing

In a vishing attack, a fraudster impersonates a bank employee, government representative, payment provider, merchant, or another trusted organization.

The customer may be persuaded to disclose information or perform actions that enable a fraudulent transaction.

Examples of social-engineering approaches include claims that:

* an account requires verification;
* a payment or refund needs confirmation;
* a bank account or card is about to expire;
* a reward or prize is available; or
* suspicious activity has been detected on the account.

The presence of an OTP or other authentication event in a transaction record does not, by itself, describe how the customer interacted with the fraudster. The investigation must consider the circumstances surrounding the transaction.

---

## Screen-Sharing and Remote-Access Fraud

A fraudster may persuade a customer to install or use a remote-access application while pretending to provide technical assistance.

The fraudster may then observe activity on the customer's device or manipulate the device while the customer performs actions in a banking or UPI application.

Applications commonly associated with remote-access scams have included tools such as AnyDesk, TeamViewer, and other remote-support software.

For a U001 investigation, the existence of a remote-access application is a possible fraud indicator, not a definition of the reason code.

---

## SIM-Swap Fraud

In a SIM-swap attack, a fraudster obtains control of the victim's mobile number through an unauthorized SIM replacement or another form of mobile-number compromise.

Depending on the authentication and account-recovery mechanisms involved, control of the mobile number may assist a fraudster in accessing accounts or receiving transaction-related communications.

A SIM swap is therefore one possible mechanism behind an unauthorized-transaction complaint. It is not required for a transaction to fall under U001.

---

## Collect-Request Fraud

UPI supports payment requests in which a payer is asked to approve a transaction.

Fraudsters may attempt to manipulate customers into approving a payment request by presenting it as:

* a refund;
* a reward;
* an account-verification transaction;
* a service request; or
* another legitimate-looking payment.

A customer later reporting such a transaction may still describe the transaction as unauthorized or fraudulent.

The investigation should distinguish between the technical transaction event and the circumstances under which the customer interacted with the request.

---

## UPI Authentication

Authentication information is an important part of investigating disputed UPI transactions.

A transaction record may contain information indicating that the applicable UPI authentication process was successfully completed.

However, authentication and customer intent should not automatically be treated as identical concepts.

For example, an unauthorized-transaction investigation may need to consider whether:

* authentication credentials were compromised;
* the customer's device was compromised;
* the customer was deceived into performing an action;
* a third party controlled or accessed the device; or
* other circumstances affected how the transaction was initiated.

The applicable NPCI and banking rules should be used when determining the consequences of the authentication information.

---

## Merchant's Position in a U001 Dispute

A merchant receiving a U001 dispute should treat it as a formal claim that the customer did not initiate the transaction.

The merchant's response should be based on the transaction and order records available through its payment infrastructure and internal systems.

Relevant records may include:

* merchant transaction records;
* UPI transaction references;
* order records;
* payment status;
* fulfillment records;
* delivery records;
* refund records;
* customer communications; and
* records obtained from the merchant's PSP or acquiring institution.

The merchant should not assume that the reason code alone determines the outcome.

Similarly, a customer allegation alone should not be interpreted as proof that the merchant acted fraudulently.

---

## Transaction Records

A merchant may maintain transaction information such as:

* merchant transaction ID;
* order ID;
* UPI transaction reference;
* RRN or other transaction reference;
* transaction amount;
* transaction timestamp;
* merchant VPA;
* payer information where legitimately available;
* transaction status;
* payment response;
* refund status; and
* settlement information.

The exact information available depends on the merchant's PSP, acquiring arrangement, payment gateway, and UPI integration.

---

## Order and Fulfillment Records

Where a UPI transaction is associated with a commercial order, the merchant should retain appropriate records showing the relationship between the payment and the underlying order.

Examples include:

* order creation time;
* order amount;
* products or services purchased;
* order status;
* cancellation status;
* fulfillment status;
* refund status; and
* customer account information maintained as part of the merchant's normal business process.

These records can help establish what transaction or service was associated with the disputed payment.

---

## Delivery Records

For physical goods, merchants may maintain:

* shipment tracking information;
* carrier delivery confirmation;
* proof of delivery;
* delivery timestamp;
* recipient information where legitimately collected;
* delivery address; and
* failed-delivery or re-attempt records.

For digital products or services, relevant records may include:

* account activation;
* download or access events;
* service-consumption records;
* fulfillment logs; and
* other records showing delivery of the service.

Delivery or fulfillment records are evidence relating to the underlying commercial transaction. They do not, by themselves, establish that the customer personally initiated the disputed UPI payment.

---

## Merchant and PSP Records

Some transaction information may be available only through the merchant's PSP, payment gateway, acquiring institution, or other payment participant.

Depending on the integration, these records may contain information relevant to:

* transaction processing;
* authentication;
* transaction status;
* payment response;
* settlement;
* reversal;
* refund; and
* dispute processing.

The merchant should obtain and preserve the records required by its applicable payment-provider and dispute process.

---

## Customer Liability and RBI Framework

NPCI dispute processing and RBI's customer-protection framework should not be treated as the same set of rules.

RBI's framework for unauthorized electronic banking transactions establishes circumstances in which a customer's liability may be zero, limited, or otherwise determined according to the circumstances of the transaction and the timing of the customer's notification.

For example, RBI states that zero customer liability can arise in certain cases involving bank negligence or deficiency, and in certain third-party-breach situations where the customer reports the unauthorized transaction within the prescribed period. RBI also addresses cases where customer negligence, such as sharing payment credentials, contributes to the loss. <!-- NEEDS VERIFICATION: confirm the exact prescribed reporting window and these liability categories against the actual current RBI circular on customer protection in unauthorised electronic banking transactions -->

The RBI framework also states that the burden of proving customer liability in an unauthorized electronic banking transaction lies with the bank. <!-- NEEDS VERIFICATION: confirm this burden-of-proof statement against the actual current RBI circular text -->

These customer-protection provisions should not be simplified into a general rule that successful UPI authentication automatically makes the customer liable, or that a U001 dispute automatically makes the merchant liable.

The applicable regulatory and network rules must be applied to the circumstances of the individual transaction.

---

## Reporting an Unauthorized Transaction

Customers who identify an unauthorized transaction should report it to their bank or relevant payment provider through the applicable fraud-reporting mechanism.

RBI requires banks to provide channels for reporting unauthorized electronic transactions and to take immediate steps to prevent further unauthorized transactions after receiving a report.

The timing of the customer's report can be relevant to the applicable customer-liability framework.

---

## NPCI Dispute Processing

NPCI maintains dispute and chargeback procedures for UPI transactions, including reason codes, dispute flags, participants, response responsibilities, and applicable processing timelines.

These procedures may be modified through NPCI circulars, addenda, and other operating instructions. NPCI publications contain structured information such as transaction type, dispute flag, reason code, reason-code description, TAT, parties that can raise or respond, fund movement, and adjustment reporting.

Consequently, the meaning and processing requirements applicable to a historical transaction should be determined using the NPCI rules applicable to the relevant transaction and dispute date.

A current rule should not automatically be applied to an older transaction if NPCI subsequently changed the applicable procedure.

---

## TAT and Resolution

A U001 dispute should not be assumed to have a single universal resolution period for every unauthorized UPI transaction.

Different timelines can apply to different parts of the overall process, including customer reporting, bank investigation, NPCI dispute processing, participant response, settlement or adjustment, and customer compensation.

RBI's unauthorized-electronic-transaction framework states that a bank's complaint-resolution and customer-liability determination process must operate within the bank's board-approved policy and not exceed 90 days from receipt of the complaint. <!-- NEEDS VERIFICATION: confirm this 90-day figure and "board-approved policy" framing against the actual current RBI circular -->

This RBI customer-complaint timeline should not be confused with an NPCI-specific dispute-processing TAT, which is separately governed by NPCI's own operating rules. <!-- NEEDS VERIFICATION: same 30-day NPCI dispute-processing figure flagged in 000_RuPay_NPCI_Overview.md applies here if a specific NPCI TAT for U001 is asserted elsewhere -->

---

## Merchant Fulfillment After a Disputed Transaction

A common scenario is:

1. A customer makes or receives a UPI payment.
2. The merchant receives confirmation of payment.
3. The merchant fulfills the order.
4. The customer subsequently reports the transaction as unauthorized.
5. A U001 dispute is raised.

In such cases, the merchant should preserve the records associated with both the payment and the underlying order.

For physical goods, this may include shipment and delivery records.

For digital goods or services, this may include activation, access, download, or service-completion records.

The existence of fulfillment records does not independently establish that the customer initiated the payment. Their relevance depends on the circumstances and the applicable dispute process.

---

## Fraud Patterns and Merchant Monitoring

Merchants may encounter recurring fraud patterns involving:

* unusual transaction velocity;
* repeated high-value transactions;
* unusual order timing;
* abnormal account activity;
* unusual delivery patterns;
* suspicious refund activity; or
* transactions that do not correspond normally with customer or order behaviour.

Merchants may use appropriate fraud-monitoring and risk-management controls to identify such patterns.

These controls are merchant risk-management practices and should not be interpreted as NPCI requirements unless an applicable NPCI rule explicitly establishes such a requirement.

---

## Frequently Asked Questions

**Q: What does U001 mean?**
U001 represents the Transaction Not Done by Customer (Fraud) scenario in the UPI dispute context — a customer's assertion that they did not initiate the disputed transaction.

**Q: Does U001 automatically mean that the merchant is liable?**
No. U001 identifies the dispute reason. It does not, by itself, establish the final liability outcome. The applicable NPCI dispute process, transaction records, participant responsibilities, and relevant regulatory requirements must be considered.

**Q: Does U001 automatically mean that the bank or PSP is liable?**
No. The ultimate allocation of responsibility depends on the applicable rules and the circumstances established during the investigation. The reason code itself should not be treated as a complete liability determination.

**Q: Does successful UPI authentication prove that the customer authorized the transaction?**
Successful authentication is important transaction evidence, but the chargeback investigation should distinguish technical authentication from the broader question of how the transaction was initiated and whether the customer intended the transaction. The applicable NPCI and regulatory rules determine how authentication information should be treated in the dispute.

**Q: Can a U001 dispute involve OTP fraud?**
Yes. OTP-related social engineering can be one mechanism through which a customer's account or payment credentials become compromised. However, OTP fraud is not itself the definition of U001.

**Q: Can a U001 dispute involve SIM-swap fraud?**
Yes. SIM-swap or mobile-number compromise can be associated with unauthorized electronic transactions. It is one possible fraud mechanism rather than a requirement for U001.

**Q: Can a U001 dispute involve screen-sharing fraud?**
Yes. A compromised device or remote-access session can be involved in an unauthorized transaction. The actual circumstances should be established through the available investigation and transaction records.

**Q: Does delivery to the customer's address prove that the customer made the UPI payment?**
No. Delivery records can establish that the merchant fulfilled an order, but they do not independently establish who initiated or authorized the payment.

**Q: What should a merchant retain for a U001 dispute?**
The merchant should retain records that establish the payment and the associated commercial transaction, including transaction records, order records, fulfillment records, delivery records where applicable, refund information, and relevant PSP/acquirer records. The exact information required depends on the applicable dispute process and the merchant's payment arrangement.

**Q: Is there a universal 30-day resolution requirement for U001?**
Not as a general statement. NPCI dispute-processing timelines and RBI customer-complaint/customer-liability timelines are different concepts and should be sourced from the applicable rule or regulation. RBI's framework for unauthorized electronic banking transactions provides a maximum 90-day period for complaint resolution and customer-liability determination under the bank's applicable board-approved policy framework. <!-- NEEDS VERIFICATION: same 90-day figure as flagged above -->

**Q: Should a merchant assume that a U001 dispute will be lost if no additional information is available?**
The reason code alone is insufficient to predict the outcome. The dispute should be evaluated using the applicable NPCI process and the transaction information available from the merchant, PSP, acquiring institution, and other relevant participants.

**Q: Is U001 the same as every type of UPI fraud?**
No. U001 identifies a particular dispute reason concerning a transaction that the customer says they did not initiate. Other UPI dispute codes can represent different transaction or dispute circumstances and should not be treated as interchangeable with U001.

---

## Important Interpretation Notes

U001 should be read as a **reason for dispute**, not as a standalone conclusion about liability or fraud.

In particular:

* A customer's U001 claim is an allegation that the customer did not initiate the transaction.
* Authentication information is part of the transaction evidence but should be interpreted within the applicable rules.
* Fraud mechanisms such as vishing, SIM swap, remote access, and malicious applications are possible scenarios rather than definitions of U001.
* Merchant fulfillment records describe what happened after the payment and do not independently establish who authorized the payment.
* NPCI dispute-processing rules and RBI customer-protection rules address different aspects of the overall dispute.
* TATs should be taken from the applicable NPCI or RBI rule rather than inferred from the reason code.
* Historical transactions should be evaluated using the NPCI rules applicable to the relevant transaction/dispute period.

The deterministic fight/refund assessment for U001 is maintained separately from this encyclopedia document, in `decision_rules.py`. This document explains the domain concept; the application's decision engine determines the operational response using its own controlled evidence vocabulary and rules.
