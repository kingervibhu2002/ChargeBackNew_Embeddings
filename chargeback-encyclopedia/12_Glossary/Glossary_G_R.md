---
title: "Chargeback Glossary — G to R"
category: Glossary
doc_type: glossary
audience: merchants
last_updated: 2026-06-01
tags: [glossary, definitions, terminology, chargeback, payments, G-R]
---

# Chargeback Glossary: G to R

This glossary provides definitions for key terms in chargeback, payments, and dispute management. Terms are arranged alphabetically from G to R.

---

## G

**Gateway (Payment Gateway)**
A technology service that acts as an intermediary between a merchant's website or point-of-sale system and the payment processor/acquirer. The gateway encrypts and transmits card data, routes authorization requests to the card network, and returns responses to the merchant. Gateways also log transaction metadata (IP address, device, AVS/CVV response) that becomes evidence in chargeback disputes. Common gateways: Stripe, Braintree, Authorize.Net, Adyen, Square, PayPal. The gateway is not the same as the acquirer, though some companies (Stripe, Adyen) act as both gateway and acquirer.

**Gross Chargeback Rate**
The total number of chargebacks received in a month divided by the total number of transactions processed in the same month, expressed as a percentage. This is the primary metric card networks use to assess merchant compliance. Distinct from the "net chargeback rate" (which subtracts representment wins), the gross rate is what networks monitor for threshold compliance. Even chargebacks that a merchant wins through representment count in the gross rate.

---

## H

**High-Risk Merchant**
A merchant classification applied by acquirers and processors to businesses in industries with elevated chargeback or fraud rates, or those operating in legally complex sectors. Common high-risk categories include: adult content, gambling, firearms, pharmaceuticals, travel, subscription services, nutraceuticals, and cryptocurrency exchanges. High-risk merchants face higher processing fees, larger rolling reserves, stricter monitoring, and limited acquirer options. A merchant can also be classified high-risk individually based on their actual chargeback or fraud ratio, even if their industry is generally low-risk.

**Hold (Authorization Hold)**
A temporary reservation of funds on a cardholder's account created by an authorization request. A hotel pre-authorization hold, for example, secures funds without completing a charge. Holds are released (without charge) if the merchant does not submit a clearing transaction, or converted to a settled charge when the merchant completes the transaction. Authorization holds that are released do not result in charges and cannot generate chargebacks. Expired holds that are not cleared typically release within 3–10 business days depending on the issuer.

---

## I

**Interchange**
The fee paid by the acquirer to the issuing bank for each settled transaction, set by the card network. Interchange rates vary by card type (credit, debit, rewards), transaction type (card-present, CNP), industry (MCC), and transaction amount. Interchange is the largest component of a merchant's payment processing cost. Merchants do not pay interchange directly — it is collected by the acquirer and passed to the issuer. High-risk merchants often pay higher effective interchange rates due to their card type mix and risk profile.

**Issuer (Issuing Bank)**
The bank or financial institution that issues payment cards to cardholders and maintains the cardholder's credit or debit account. When a cardholder files a dispute, the issuer receives the complaint, decides whether to file a formal chargeback, and manages the dispute process on the cardholder's behalf. Examples: Chase, Bank of America, Citi, Capital One, Wells Fargo, Barclays. The issuer's chargeback analyst reviews the merchant's representment and issues the final first-level decision. The issuer is the merchant's adversary in the chargeback dispute process.

---

## L

**Late Presentment**
A chargeback reason code applied when a merchant submits a transaction for settlement after the allowable time limit (typically 30 days from the authorization date for Visa; varies by network). A Late Presentment chargeback occurs because the issuing bank's authorization hold may have expired by the time settlement is submitted, making the debit technically unauthorized. Merchants who process delayed settlement (e.g., booking deposits captured weeks before service delivery) should use a valid authorization obtained close to the settlement date, not an authorization from months earlier.

**Liability Shift**
The transfer of financial responsibility for a fraudulent transaction from one party to another, based on which party supported the strongest authentication technology. In EMV chip transactions, if the merchant uses a chip-enabled terminal but the issuer does not support EMV, liability shifts to the issuer. In 3-D Secure transactions, a fully authenticated result (ECI 05 for Visa, ECI 02 for Mastercard) shifts liability for fraud chargebacks from the merchant to the issuer. Liability shift means the merchant wins the fraud chargeback automatically and is not responsible for the disputed funds.

---

## M

**MATCH List (Member Alert to Control High-Risk Merchants)**
A database maintained by Mastercard and accessed by all major acquirers containing information about merchants whose accounts were terminated for serious violations including excessive chargebacks, fraud, money laundering, PCI breaches, or illegal activity. When an acquirer terminates a merchant account for qualifying reasons, it is required to submit the merchant's information to the MATCH list. Other acquirers check MATCH as part of their merchant onboarding process and will typically decline to open an account for any merchant on the list. MATCH listings remain for 5 years. See `004_MATCH_List.md` for comprehensive details.

**MCC (Merchant Category Code)**
A 4-digit code assigned by the card network and acquirer to classify a merchant's primary business type. MCCs affect interchange rates, fraud rules, and chargeback monitoring program thresholds. Common MCCs: 5411 (grocery stores), 5812 (restaurants), 5912 (drug stores), 7011 (hotels), 7922 (entertainment events), 5999 (miscellaneous retail). MCCs also affect how disputes are categorized — some reason codes are MCC-specific. Merchants in high-risk MCCs (gambling, adult) are subject to additional card network restrictions.

**MID (Merchant Identification Number)**
A unique identifier assigned by the acquirer to each merchant account. The MID is used in chargeback communications, monitoring program reporting, and acquirer-to-network data exchange. A merchant may have multiple MIDs for different brands, websites, or business divisions. Chargebacks are tracked and counted at the MID level. If a merchant in a monitoring program opens a new MID to reset their ratio, the card network can detect this and treat the new MID as a continuation of the old account.

**Monitoring Program**
A card network program that places a merchant under special oversight when their chargeback or fraud ratio exceeds defined thresholds. Monitoring programs include: Visa Dispute Monitoring Program (VDMP), Visa Fraud Monitoring Program (VFMP), and Mastercard Excessive Chargeback Program (ECP). Merchants in monitoring programs face monthly review, mandatory action plans, and escalating fines. Failure to remediate within the program window can result in account termination and MATCH list placement. See `15_Monitoring_Programs/` for detailed program descriptions.

---

## N

**Network (Card Network)**
The infrastructure and rule-setting body that connects issuers, acquirers, and merchants. Card networks define chargeback reason codes, dispute timelines, liability shift rules, and monitoring program thresholds. The four major card networks: Visa, Mastercard, American Express, Discover. Visa and Mastercard operate open-loop networks (any issuer/acquirer can participate); American Express and Discover operate closed-loop networks (they serve as both issuer and acquirer in many transactions). Network rules take precedence over acquirer policies in dispute proceedings.

**No Authorization**
A chargeback reason code applied when a merchant settles a transaction that was never authorized, or authorizes and settles for a different amount than originally approved. No authorization chargebacks typically occur when merchants process split transactions, charge amounts beyond the authorized hold, or process duplicate charges. Defense requires proof that a valid authorization code was obtained for the amount in question.

---

## P

**Pre-Arbitration**
The stage in Visa's dispute process that follows a merchant's rejected representment. When the issuer declines to accept the merchant's Second Presentment, the issuer files a pre-arbitration (or "pre-arb") indicating it wants to escalate the dispute. The merchant then has a final opportunity to accept the loss or escalate to card network arbitration. Pre-arbitration is not available for all reason codes and is subject to specific evidentiary and timing requirements. Accepting a pre-arbitration means conceding the dispute; rejecting it triggers arbitration with associated fees.

**Pre-Chargeback Alert**
A notification sent to a merchant before a formal chargeback is filed, typically delivered through Verifi CDRN or Ethoca. When a cardholder initiates a dispute with their bank, the alert service intercepts the notification and forwards it to the merchant in near-real-time. The merchant has a short window (typically 24 hours) to refund the cardholder and stop the chargeback from being filed. Pre-chargeback alerts allow merchants to resolve disputes without the formal chargeback entering their ratio count.

**Processor (Payment Processor)**
A company that handles the technical processing of card transactions between merchants, card networks, and banks. The processor routes transaction data, applies interchange fees, manages authorization responses, and handles batch settlement. Some processors also serve as acquirers; others are pure technology providers. Examples: Worldpay, Global Payments, Fiserv, TSYS. Processors are distinct from gateways (which handle the merchant-facing encryption and routing interface) though the two functions are often combined in the same company.

**PSP (Payment Service Provider)**
A company that provides merchants with the ability to accept card payments, often serving as both gateway and acquirer. PSPs aggregate multiple merchants under a single large merchant account. Examples: Stripe, Square, PayPal, Braintree. PSPs offer easier onboarding but typically less control over chargeback management than a direct acquirer relationship. When a PSP merchant has elevated chargebacks, the PSP can terminate the merchant's access to protect its aggregate account from network monitoring program consequences.

---

## R

**Reason Code**
A standardized code assigned by the card network to categorize the basis for a chargeback. Reason codes define what the cardholder is claiming and dictate what evidence the merchant must provide to challenge the dispute. Visa uses a numeric system (10.4, 13.1, 13.2, 13.3, etc.); Mastercard uses a 4-digit numeric system (4837, 4853, 4855, etc.). The reason code on the chargeback notice determines the entire defense strategy — submitting evidence that doesn't match the reason code claim is the most common merchant rebuttal error.

**Representment (Second Presentment)**
The merchant's formal challenge to a chargeback, submitted to the acquirer who forwards it to the issuing bank. A representment consists of a rebuttal letter and supporting evidence exhibits. A successful representment results in the issuing bank reversing the chargeback and crediting the funds back to the merchant. The term "representment" comes from the merchant "re-presenting" the original transaction with supporting documentation. Mastercard uses the term "Second Presentment"; Visa uses "Representment" under its VCR framework.

**Reserve Account (Rolling Reserve)**
Funds held by the acquirer as a security deposit against potential future chargeback losses. Rolling reserves are common for high-risk merchants. The reserve is calculated as a percentage (5–10%) of monthly gross processing volume, held for a specified period (typically 180 days), then released on a rolling basis. The reserve protects the acquirer from losses if the merchant's account is closed or the merchant cannot cover chargeback debits. Merchants with consistently low chargeback ratios can negotiate reduced or eliminated reserves.

**Retrieval Request**
A request from an issuing bank for a copy of a transaction record, used before a formal chargeback decision is made. Under Visa's current VCR framework, retrieval requests are largely obsolete — Visa processes most disputes as direct chargebacks without a prior retrieval. Mastercard still uses retrieval requests in some dispute scenarios. Failure to respond to a retrieval request typically results in an automatic chargeback. Retrieval requests do not result in fund debits but are a precursor to potential chargeback action and should be treated with urgency.
