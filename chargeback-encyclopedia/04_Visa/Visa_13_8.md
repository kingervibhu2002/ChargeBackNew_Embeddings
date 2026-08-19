---
title: "Visa 13.8 — Original Credit Transaction Not Accepted"
section: "04_Visa"
category: "Visa Reason Codes"
document_type: "Reference"
keywords: ["Visa 13.8", "original credit transaction", "credit posted wrong account", "OCT chargeback", "credit transaction error", "credit to wrong card", "Visa OCT dispute"]
difficulty: "Advanced"
---

# Visa 13.8 — Original Credit Transaction Not Accepted

Visa reason code 13.8 is one of the rarest chargeback codes in the Visa system. It applies specifically to Original Credit Transactions (OCTs) — credits that are sent directly to a cardholder's account, not as a refund for a prior purchase but as a standalone credit origination. When that credit is not accepted by the issuer or is directed to the wrong account, the intended recipient may dispute the non-receipt through this code. Understanding when OCTs are used and why they fail is the key to both defending and preventing 13.8 chargebacks.

## What Is an Original Credit Transaction?

An Original Credit Transaction (OCT) is a payment flow that pushes funds directly to a cardholder's Visa account, bypassing the traditional purchase-then-refund structure. OCTs are used in:

- **Winnings payouts:** Online gambling platforms, sweepstakes, and prize platforms paying out winnings to a player's card
- **Insurance claim disbursements:** Insurers sending claim payments to a cardholder's account
- **Peer-to-peer money transfers:** Individuals sending money to another person's card
- **Gig economy payouts:** Platforms like ride-sharing or delivery apps disbursing earnings to workers' cards
- **Marketplace seller payouts:** E-commerce marketplaces paying sellers for their sales
- **Loan disbursements:** Lenders sending loan proceeds directly to a borrower's card

OCTs require specific Visa processing credentials (a Visa Direct originator relationship through an acquirer). Not all merchant accounts can process OCTs — this functionality is explicitly enabled and governed.

## What This Chargeback Means

A 13.8 chargeback arises in one of two scenarios:

### Scenario 1: Credit Posted to the Wrong Account
The OCT was processed with an incorrect account number — either through a data entry error, a data mapping issue in the payment system, or a file formatting error — and the credit went to the wrong person's account. The intended recipient never received the funds.

### Scenario 2: Credit Was Rejected by the Issuer
The issuer declined to accept the OCT for various reasons (account closed, account type not eligible for OCTs, velocity limit exceeded, or technical rejection). The credit was never posted to the cardholder's account despite being initiated.

In both scenarios, the intended recipient is out the funds and is seeking resolution through the dispute process.

## How OCT Errors Occur

### Manual Credit Entry Error
If account numbers are entered manually (in a payroll disbursement system or batch payment file), a transposed digit or incorrect account number sends the credit to a different cardholder's account.

### Batch File Formatting Error
OCTs submitted in bulk (payroll runs, insurance batch payments, marketplace payouts) are typically submitted as batch files. Column misalignment, encoding errors, or truncated fields can result in account numbers being corrupted in the batch, sending credits to wrong accounts.

### System Integration Data Mapping
When payout systems integrate with payment processors, data mapping errors can pull the wrong account number field from the payout database — sending credits to old account numbers, test accounts, or unrelated accounts.

### Account Status Changes
If the recipient's card account was closed or transitioned between the time the payout was initiated and the time it was processed, the issuer may reject the OCT. The rejected credit may not automatically return to the originator's account — it can become stranded in processing.

## Evidence to Submit When Defending

If you receive a 13.8 chargeback, your evidence strategy depends on the specific scenario:

### If the Credit Was Processed to the Correct Account

Submit:
- OCT transaction record showing the account number the credit was sent to
- Confirmation from your payment processor that the OCT was accepted and settled to the specified account
- Evidence linking the account number used to the intended recipient (the recipient's enrollment record, their account on file)

If your records show the credit was sent to the correct account and accepted, the chargeback may involve an issuer processing error. Your acquirer should work with the network to investigate why the credit is not reflected on the cardholder's statement.

### If the Credit Was Sent to the Wrong Account

Accept the chargeback. Initiate a recovery process:
- Contact your acquirer to attempt recovery of the misdirected credit from the account that incorrectly received it
- Reprocess the OCT to the correct account number
- Conduct a data quality review to identify the source of the account number error

Attempting to fight a 13.8 where the credit went to the wrong account is ineffective and ethically untenable — the intended recipient is owed their funds.

## Correction Steps

When a 13.8 situation is identified (whether through a chargeback or through your own monitoring), the correction process involves:

1. **Confirm the error:** Review your OCT submission records to identify whether the credit was sent to the correct or incorrect account number
2. **Contact acquirer immediately:** Your acquirer has visibility into the OCT processing and can help identify whether the credit was accepted, rejected, or misdirected
3. **Initiate a correction OCT:** If the credit must be reissued to the correct recipient, initiate a new OCT to the correct account number after confirming the incorrect account has been debited or the issue documented
4. **Accept the chargeback:** For misdirected credits, accept the chargeback so the incorrectly credited party's account is corrected through the network

## Prevention

### Account Number Validation Before OCT Submission

Implement Luhn check validation on all account numbers before OCT batch submission. Account numbers that fail the Luhn check are invalid and should not be submitted.

### Test Mode Payout Verification

For new payout integrations, test with small ($1) real-value OCTs to verified test accounts before processing bulk payouts. Confirm credits appear as expected before scaling.

### Payout Reconciliation

After each OCT batch run, reconcile the expected recipients against the submission file and processor confirmation:
- Number of credits submitted matches number accepted
- Total dollar amount matches
- Any rejected OCTs are identified and re-queued after correction

### Account Status Pre-Check

For recurring payout relationships (gig economy workers, subscription sellers), periodically validate that the registered account numbers remain valid and active. Many payment processors offer account validation services that confirm an account is open and accepting credits before you attempt an OCT.

---

## Frequently Asked Questions

**Q: How common are 13.8 chargebacks?**
A: Visa 13.8 is one of the least frequently filed chargeback codes in the Visa system. Most merchants who process only standard purchase transactions will never see a 13.8 — this code is limited to merchants with OCT processing capability (Visa Direct originators). If you are not an OCT originator, this code does not apply to your business.

**Q: What happens to the funds that went to the wrong account?**
A: If an OCT credits an account that was not the intended recipient, recovering those funds is difficult. The recipient may or may not be aware they received an unexpected credit. Your acquirer can work with the network to attempt a recovery, but there is no guarantee the funds can be clawed back from a cardholder who received them, especially if they have been spent. Prevention through data validation is far more effective than recovery.

**Q: We process insurance disbursements. Multiple claimants are reporting they did not receive credits. What do we investigate first?**
A: Start with your batch submission file — confirm the account numbers in the file match the claimants' registered account numbers. Then review the processor's acceptance report for that batch — did the OCTs process or were some rejected? If they processed, confirm the account numbers used were correct. Systemic non-receipt across multiple claimants typically indicates a batch file error, a data mapping problem, or a processor-side processing failure rather than individual account-level issues.

**Q: Can a cardholder file a 13.8 if they received a partial credit instead of the full expected amount?**
A: The specific scenario of partial credit receipt may fall under 13.8 or could relate to a processing error in the OCT amount field. The cardholder's recourse depends on the nature of the discrepancy. If the OCT was submitted for the full amount but only a partial amount was credited, investigate at the processor level — this may be a processor or network fee issue affecting the credited amount.

**Q: Do 13.8 chargebacks affect my chargeback ratio?**
A: Yes, like all chargebacks, 13.8 disputes are counted against your chargeback ratio by the network. For OCT originators processing large volumes of disbursements, maintaining data quality and preventing misdirected credits is essential not just for recipient satisfaction but for chargeback ratio management.
