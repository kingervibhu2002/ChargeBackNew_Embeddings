---
title: "Chargeback Glossary — A to F"
category: Glossary
doc_type: glossary
audience: merchants
last_updated: 2026-06-01
tags: [glossary, definitions, terminology, chargeback, payments, A-F]
---

# Chargeback Glossary: A to F

This glossary provides definitions for key terms in chargeback, payments, and dispute management. Terms are arranged alphabetically from A to F.

---

## A

**Acquirer (Acquiring Bank)**
The financial institution or payment processor that maintains the merchant's bank account and receives card transaction proceeds on the merchant's behalf. The acquirer is responsible for routing transaction data to the card networks, funding the merchant's account after settlement, and handling chargeback notifications and dispute communications. Examples: Chase Merchant Services, Worldpay, Stripe (as acquirer), Adyen. The acquirer is the merchant's direct relationship in the card payment ecosystem.

**Acquirer Reference Number (ARN)**
A unique 23-digit reference number assigned to every settled card transaction by the acquiring bank. The ARN is the primary identifier used in dispute proceedings to trace a specific transaction through the card network. Merchants should always include the ARN in chargeback submissions to ensure the dispute is linked to the correct transaction. The ARN is available in the acquirer's transaction report or payment gateway dashboard.

**Authorization**
The process by which a merchant's payment terminal or gateway submits a transaction request to the issuing bank asking for approval to charge the cardholder's account. An approved authorization reserves the specified amount on the cardholder's available credit or debit balance. Authorization does not transfer funds — it only holds them. Settlement (clearing) is the subsequent step that actually moves money from the cardholder's account to the merchant. A transaction that is authorized but never settled does not result in a charge and cannot be disputed.

**Authorization Code**
A 6-character alphanumeric code returned by the issuing bank to confirm that an authorization has been approved. The authorization code is proof that the bank approved the transaction at the time of the request and is a required element in most chargeback rebuttal submissions. A declined authorization does not produce an authorization code. The authorization code is also called an "approval code."

**AVS (Address Verification Service)**
A fraud prevention service that compares the billing address submitted at checkout with the address on file at the issuing bank. The card network returns a response code indicating whether the street address, ZIP code, both, or neither matched. Common response codes: Y (full match — address and ZIP), A (address match, ZIP mismatch), Z (ZIP match, address mismatch), N (no match), U (unavailable). AVS is a CNP (card-not-present) fraud signal. A full match (Y) is valuable evidence in chargeback rebuttal. AVS does not block transactions; it informs a risk decision.

**AVS Response Code**
The single-letter code returned by the issuing bank in response to an AVS inquiry. The most important codes for chargeback defense: Y (both ZIP and street match — strongest), Z (ZIP match only), A (street match only), N (no match — weakens fraud defense), U (service unavailable — common for international cards). Response codes are logged in the payment gateway authorization record and should be included in every fraud chargeback rebuttal.

---

## B

**Batch Settlement**
The process by which a merchant submits all authorized transactions from a day's trading to the acquirer for final settlement (fund transfer). Batch settlement typically occurs once daily at the end of the business day. During batch settlement, authorization holds are converted to actual debits on the cardholder's account. Transactions that are authorized but not included in a batch settlement do not clear and are not eligible for chargeback. Settlement timing is important for chargeback timing calculations: the cardholder's dispute window begins from the settlement date, not the authorization date.

**BIN (Bank Identification Number)**
The first 6 digits of a payment card number that identify the issuing bank and card type (Visa, Mastercard, Amex), card category (debit, credit, prepaid, commercial), and country of issuance. BINs are used in fraud screening to identify unusual purchase patterns (e.g., a US merchant processing a transaction from a foreign BIN) and in chargeback routing (to identify which issuing bank filed the dispute). BIN data is publicly available through BIN lookup databases and is captured in every transaction record. Also called IIN (Issuer Identification Number) under the newer ISO standard.

---

## C

**Card Not Present (CNP)**
A transaction where the physical card is not present at the point of sale — typically an online, phone, or mail order transaction where only the card number, expiry, and CVV are provided. CNP transactions carry higher fraud risk than card-present transactions because the merchant cannot verify the card physically. The majority of chargeback fraud disputes arise from CNP transactions. CNP merchants rely on AVS, CVV, 3-D Secure, and device/IP intelligence as authentication signals.

**Card Present**
A transaction where the physical card is present at the point of sale, typically processed via chip (EMV) or contactless (NFC). A chip-read, PIN-verified card-present transaction results in liability shifting to the issuing bank for fraud chargebacks — the merchant is protected. A swipe-only (magnetic stripe) transaction in a chip-capable terminal does not receive this liability shift. Card-present merchants have significantly lower fraud chargeback exposure than CNP merchants.

**Cardholder**
The individual whose name appears on the payment card and whose account is linked to the card. In a chargeback context, the cardholder is the person who initiates the dispute with their issuing bank. The cardholder may or may not be the person who actually made the purchase (in the case of stolen card fraud, the cardholder is a victim; in friendly fraud, the cardholder is the purchaser).

**Chargeback**
A forced reversal of a card transaction initiated by the cardholder's issuing bank on behalf of the cardholder. When a chargeback is filed, the issuing bank debits the disputed amount from the merchant's account and credits it to the cardholder, pending the outcome of the dispute. Chargebacks are governed by card network rules (Visa, Mastercard, Amex) and are categorized by reason code. Merchants can challenge chargebacks through representment (also called Second Presentment). Chargebacks that are not challenged or are lost result in permanent fund reversal plus a chargeback fee.

**Chargeback Fee**
A flat administrative fee charged by the acquirer to the merchant each time a chargeback is filed, regardless of whether the dispute is won or lost. Typical chargeback fees range from $15 to $100 per dispute. High-risk merchants and those in monitoring programs pay fees at the upper end of this range. The fee is debited from the merchant's account simultaneously with the chargeback debit. Some acquirers waive chargeback fees for merchants with very low dispute ratios as an incentive; most do not.

**Chargeback Ratio**
The percentage of a merchant's total transactions in a given month that resulted in chargebacks. The standard formula: (number of chargebacks in the month) ÷ (number of transactions in the month) × 100. Visa's standard threshold is 0.9%; Mastercard's is 1.0% (at 100+ chargebacks). Ratios are calculated monthly by card network using the merchant's Merchant ID (MID). Exceeding thresholds triggers placement in a monitoring program with associated fines.

**Chargeback Threshold**
The chargeback ratio level defined by card networks above which monitoring programs are triggered. Visa thresholds: Early Warning (0.65%), Standard (0.9%), Excessive (1.8%). Mastercard thresholds: 1.0% at 100+ chargebacks (Chargeback Monitored Merchant — CMM), 1.5% at 300+ chargebacks (Excessive Chargeback Merchant — ECM). Exceeding a threshold initiates a monitoring period with deadlines for merchants to remediate, accompanied by escalating fines.

**Clearing**
The post-authorization process by which transaction data is submitted to the card network for processing and settlement. During clearing, the issuing bank confirms the transaction and the acquirer's account is credited. Clearing typically occurs within 1–3 business days of authorization. A transaction must clear (settle) before it can be subject to a chargeback. "Clearing date" is sometimes used interchangeably with "settlement date."

**CNP (Card Not Present)**
See "Card Not Present."

**Compelling Evidence (CE3.0)**
Visa's Compelling Evidence 3.0 framework (effective April 2023) allows merchants to challenge Visa 10.4 (fraud) chargebacks by demonstrating that the disputed transaction is linked to the same cardholder who made prior undisputed transactions. The criteria require two undisputed prior transactions within the prior 365 days, sharing at least two data elements (device fingerprint, IP address, shipping address, or email) with the disputed transaction. CE3.0 enables the merchant to transfer liability back to the issuer in friendly fraud cases.

**Compliance (Dispute Compliance)**
A specific type of dispute filing used when a card network rule has been violated — for example, if a merchant processed a transaction without proper authorization. Compliance cases are distinct from standard chargebacks in that they relate to rule violations rather than cardholder claims. Compliance filings carry their own reason codes and timelines.

**CVV (Card Verification Value)**
A 3-digit (or 4-digit for Amex) security code printed on a payment card. Also known as CVV2 (Visa), CVC2 (Mastercard), CID (Amex). The CVV is not encoded on the magnetic stripe and is not stored by merchants (PCI DSS prohibits this). For card-not-present transactions, collecting and verifying the CVV provides evidence that the person entering the card data had physical possession of the card. A CVV match (response M) is an important element of the fraud defense in chargeback rebuttals. A CVV mismatch (N) is a red flag that the card number was obtained without the physical card.

---

## D

**Decline**
The issuing bank's rejection of an authorization request. Declines can be hard (card reported stolen, closed account) or soft (insufficient funds, temporary hold, velocity limit). A declined transaction does not result in a charge and is not eligible for chargeback. Excessive declines may indicate a fraud signal (e.g., fraudster testing stolen cards). Decline codes are returned by the issuing bank and logged in the payment gateway record.

**Descriptor**
See "Billing Descriptor" (cross-referenced). The merchant name and contact information that appears on the cardholder's statement for each transaction. A clear, recognizable descriptor reduces "unauthorized" disputes where customers don't recognize their own purchases.

**Dispute**
The formal process by which a cardholder challenges a transaction with their issuing bank. A dispute may be resolved by the bank without becoming a formal chargeback (e.g., the merchant refunds before the chargeback is filed), or it may escalate into a chargeback when the bank initiates a fund reversal. "Dispute" and "chargeback" are often used interchangeably, though technically a dispute is the cardholder's claim and a chargeback is the bank's action.

---

## E

**EMV (Europay, Mastercard, Visa)**
The global standard for chip-based payment cards. EMV chip transactions generate a unique cryptographic code for each transaction, making it extremely difficult to counterfeit or replay. For card-present EMV transactions processed through a chip-enabled terminal, liability for fraud chargebacks shifts to the issuing bank (or to the party — merchant or issuer — that does not support EMV). Merchants who run chip cards through the magnetic stripe reader (swipe) instead of the chip reader forfeit the liability shift and are responsible for fraud losses.

---

## F

**First Presentment**
The initial clearing and settlement of a transaction — the original charge as submitted by the merchant to the card network. If the issuing bank files a chargeback against a First Presentment, the merchant can challenge it with a Second Presentment (representment). First Presentment is the merchant's initial position; representment is the merchant's rebuttal.

**Fraud Monitoring Program**
A card network program that monitors merchant accounts for excessive fraud levels (as measured by fraud-to-sales ratio). Visa's fraud monitoring program is VFMP (Visa Fraud Monitoring Program); Mastercard's is the Fraud Excessive Program component of the ECP. Fraud monitoring programs are distinct from chargeback monitoring programs — fraud programs measure the dollar value of fraud chargebacks relative to sales volume, while chargeback programs measure the count ratio. Merchants in both monitoring programs face compounding fines.

**Friendly Fraud**
A chargeback filed by the legitimate cardholder who actually made and received the purchase. Also called "first-party misuse." Common patterns: cardholder claims non-delivery of a received item; cardholder claims non-authorization of a purchase they made; cardholder claims a subscription was cancelled when it was not. Friendly fraud is the largest and fastest-growing category of chargeback losses for e-commerce merchants. Defense relies on prior purchase history, delivery evidence, usage logs, and IP/device consistency.
