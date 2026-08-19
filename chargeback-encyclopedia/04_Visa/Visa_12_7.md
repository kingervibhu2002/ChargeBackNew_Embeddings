---
title: "Visa 12.7 — Invalid Data"
section: "04_Visa"
category: "Visa Reason Codes"
document_type: "Reference"
keywords: ["Visa 12.7", "invalid data chargeback", "missing transaction data", "invalid transaction fields", "merchant ID chargeback", "auth code invalid", "terminal ID", "transaction data requirements"]
difficulty: "Intermediate"
---

# Visa 12.7 — Invalid Data

Visa reason code 12.7 is a processing error code filed when a transaction submitted for settlement contains missing, incorrect, or invalid data fields required under Visa's transaction processing rules. Unlike most chargeback codes where the cardholder initiates a complaint, 12.7 chargebacks are often identified by the issuer's automated processing systems detecting a transaction that fails data validation — even before the cardholder is aware of any problem. For merchants, 12.7 chargebacks signal a systemic data quality issue that, if not corrected, can generate chargebacks across many transactions simultaneously.

## What This Chargeback Means

Every transaction submitted through the Visa network must include specific required data fields. When one or more of these fields is absent, malformed, or contains an invalid value, the issuer can file a 12.7 chargeback because the transaction does not meet Visa's data integrity standards for a valid settled transaction.

Critically, 12.7 does not require that the cardholder deny the purchase or claim fraud. The chargeback is based on data integrity — the transaction record itself is defective, regardless of whether the underlying purchase was legitimate.

## Required Transaction Data Fields

The following fields are required in every properly formatted Visa transaction settlement record. Any missing or invalid field can trigger a 12.7 chargeback:

| Field | Description |
|---|---|
| **Merchant ID (MID)** | The unique identifier assigned to the merchant by the acquirer |
| **Terminal ID (TID)** | Identifies the specific terminal or point of sale where the transaction originated |
| **Authorization Code** | The approval code returned by the issuer at authorization time |
| **Transaction Date** | The date the transaction was processed (must match the authorization date within allowable variance) |
| **Transaction Amount** | The settled amount (must match or fall within network rules relative to the authorized amount) |
| **Card Expiration Date** | The expiration date from the card presented |
| **Card Acceptor Name/Location** | Merchant name and location as registered with the acquirer |
| **Transaction Currency Code** | ISO currency code for the transaction amount |
| **Acquirer Reference Number (ARN)** | Unique identifier assigned to the transaction by the acquiring bank |

For card-not-present (e-commerce, MOTO) transactions, additional fields such as electronic commerce indicator (ECI) and CVV2 result code may be required.

## How Data Corruption and Invalid Data Occur

### Electronic vs. Manual Processing Failures
Electronic processing (EMV chip, NFC/contactless, magnetic stripe read) captures transaction data automatically and accurately. Manual key entry introduces error risk at multiple points: incorrect MID entered, wrong date typed, authorization code misread and transcribed incorrectly.

### Legacy System Integration Gaps
Older POS systems may not support all required data fields in modern Visa transaction formats. A system that was compliant with Visa's 2015 data requirements may not properly populate fields added in subsequent rule updates.

### Software Bugs in Payment Integration
When merchants integrate a shopping cart, ERP, or custom payment workflow with a payment gateway, bugs in data mapping logic can result in required fields being sent as null, empty strings, or placeholder values rather than valid data.

### Batch File Formatting Errors
Merchants submitting fixed-format or CSV batch files to processors can produce invalid data through column alignment errors, character encoding issues, or truncated field values. A MID of "123456" truncated to "12345" in a misconfigured column is an invalid MID.

### Authorization Code Not Properly Captured
In some legacy or fallback manual environments, the authorization code (the numeric code from a voice authorization, for example) is handwritten on the voucher and later entered manually. Transcription errors produce invalid authorization codes that will not match the issuer's records.

### Time and Date Synchronization Failures
A terminal with an incorrect system clock can submit transactions with dates that predate or significantly postdate the actual transaction, creating invalid date fields that trigger automated rejection.

## Evidence to Submit When Disputing

If you receive a Visa 12.7 chargeback, your representment should demonstrate that the transaction data was in fact valid.

### Corrected Transaction Record With Valid Data
Produce the complete, corrected transaction record showing all required fields populated correctly. This should come from your payment system's database or gateway — not a manually reconstructed document.

**Key documents:**
- Authorization record from your gateway or processor showing the valid auth code, MID, TID, amount, and date as they were submitted
- Batch settlement confirmation showing the transaction was submitted with valid, complete data
- Any electronic receipt showing the fields at the time of transaction

### Authorization Response Record
The authorization response from the issuing bank is strong evidence — it demonstrates that the issuer approved the transaction with the data as submitted. If the issuer approved an authorization and then files a 12.7 on the same data fields, there is an inconsistency in their position.

### Gateway or Processor Confirmation
A statement from your payment gateway confirming that the transaction was submitted with all required fields and was accepted by their systems for forwarding to the network.

## Prevention: Data Validation Before Submission

The most effective prevention for 12.7 chargebacks is validating transaction data completeness at the point of submission — before it reaches the network.

### Pre-Submission Data Validation
Implement automated validation checks in your payment system that verify all required Visa fields are populated and valid before any transaction batch is submitted. Transactions failing validation should be held and flagged for review rather than submitted in an incomplete state.

### Maintain Current System Certification
Visa periodically updates its transaction data requirements. Ensure your POS software, payment gateway, and acquirer integration are current with the latest Visa specifications. Outdated system certifications are a common source of 12.7 chargebacks when new required fields are introduced.

### Terminal Time Synchronization
Configure all payment terminals to synchronize with a network time server (NTP) at least daily. Date/time discrepancies between the terminal and the network are a common and easily preventable source of invalid transaction date fields.

### Staff Training for Manual Environments
In any environment where manual key entry or voice authorization is used, train staff to transcribe authorization codes carefully and verify the transaction record before submission. Implement a double-check process for manually entered authorization codes.

### Regular Batch Audit
After each settlement batch submission, review the batch confirmation report for rejected or flagged transactions. A transaction rejected by the network for invalid data must be corrected and resubmitted within the same settlement cycle or it may need to be voided and re-authorized.

---

## Frequently Asked Questions

**Q: Why would an issuer file a 12.7 if they already approved the authorization?**
A: This is a legitimate inconsistency. The authorization approval confirms the card had sufficient credit and was not blocked at that moment. The 12.7 filing at settlement occurs when the settlement data does not match or properly reference the earlier authorization — for example, if the authorization code in the settlement record does not match what the issuer has on file for that transaction. This most commonly occurs when settlement is processed a day or more after authorization and the authorization has expired or been altered.

**Q: Can a 12.7 chargeback affect multiple transactions at once?**
A: Yes. If the invalid data issue is systemic — a batch file formatting error, a software bug, or a time synchronization failure — every transaction submitted with the same error will generate a 12.7 chargeback. Systemic 12.7 chargebacks that affect many transactions simultaneously can spike your chargeback ratio rapidly and trigger monitoring program enrollment. Treat any 12.7 chargeback as potentially indicating a broader data quality problem, not just an isolated incident.

**Q: My gateway says the transaction was valid, but I still received a 12.7. What happened?**
A: The data may have been valid when your gateway received it, but modified or corrupted during transmission to the acquirer or during batch processing. Request a raw transaction log from your gateway showing exactly what was transmitted to the acquirer, and compare it to what the acquirer submitted to the network. Discrepancies in this chain indicate where the data corruption occurred.

**Q: Is there a way to correct the transaction data and resubmit rather than fighting the chargeback?**
A: Generally, once a 12.7 chargeback is filed, the representment process is used to demonstrate the data was valid — not to resubmit corrected data. However, if the error is correctable and the cardholder is cooperative, voiding the original transaction and reprocessing with correct data (obtaining fresh authorization) may be a cleaner resolution than fighting the chargeback.

**Q: How long should I retain transaction data to defend against 12.7 chargebacks?**
A: Retain complete transaction records — including authorization records, settlement confirmations, and batch reports — for a minimum of 24 months. The cardholder dispute window is 120 days, but processing disputes, representments, and potential arbitration can extend the active dispute period well beyond that. Many payment regulations require 5–7 year retention for audit purposes, which provides more than adequate chargeback defense coverage.
