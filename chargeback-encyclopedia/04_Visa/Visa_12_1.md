---
title: "Visa 12.1 — Late Presentment"
section: "04_Visa"
category: "Visa Reason Codes"
network: "Visa"
reason_code: "12.1"
document_type: "Reason Code Reference"
keywords: ["late presentment", "12.1", "submission deadline", "30 days", "hospitality", "car rental", "batch delay"]
difficulty: "Beginner"
---

# Visa 12.1 — Late Presentment

## Definition

Visa reason code 12.1 — Late Presentment — applies when a merchant submitted a transaction for processing and settlement more than the allowed number of days after the authorization was obtained. Visa's standard rule requires merchants to submit (present) transactions within **30 days** of the authorization date. Submitting after this window means the authorization has expired and the transaction may be challenged.

Late presentment chargebacks occur because Visa's rules require timely submission of transactions so cardholders can track their spending, issuers can maintain accurate account records, and the payment lifecycle operates predictably. When a merchant submits a transaction weeks or months after it occurred, the cardholder may have already closed the account, used the available credit balance for other purposes, or simply not recognized an old charge — creating confusion and the grounds for a dispute.

---

## Why the 30-Day Rule Exists

The 30-day presentment window is designed to balance two needs: giving merchants a reasonable time to process transactions (particularly in complex industries like hospitality, car rental, and medical services where the final amount may not be known until well after the initial authorization) while protecting cardholders from stale charges appearing unexpectedly on statements.

An authorization approval represents the issuer's commitment to honor a transaction as of the approval date — not indefinitely into the future. Over time, a cardholder's financial circumstances may change: they may have cancelled the card, the credit limit may have been reduced, or the account may have been flagged. An old authorization provides no guarantee that the same funds are still available.

---

## Industry-Specific Vulnerabilities

### Hospitality (Hotels and Resorts)
Hotels are among the most common recipients of 12.1 chargebacks. The typical scenario: a hotel obtains an authorization at check-in for the estimated stay amount. The guest stays for several weeks (corporate stays, extended vacations, long-term recovery), and the final folio is not settled until after the 30-day window has passed. This is particularly common for:
- Extended stay guests
- Groups and events where master folios close weeks after the last checkout
- Damage or incidental claims discovered after checkout

**Hospitality solution:** Obtain a new authorization for the outstanding balance before the 30-day window expires on the original authorization. Hotels can request new authorization increments during extended stays.

### Car Rental
Similar to hospitality, car rental companies often discover damage, additional charges, or excess mileage fees after the vehicle is returned — sometimes long after the return date. If the original authorization window has expired before these charges are submitted, the resulting transaction is subject to 12.1.

**Car rental solution:** Document damage and assess additional charges promptly. Obtain a new authorization for additional charges within the authorization window.

### Service Businesses
Contractors, consultants, and service businesses that bill for projects may capture card information during project initiation but not submit payment until project completion — potentially months later. The original authorization will have expired long before settlement.

### B2B and Wholesale
Large commercial transactions may involve extended payment terms and billing cycles that clash with the 30-day presentment window.

---

## Common Scenarios

- A hotel guest checks in on January 1st with a $500 authorization. They stay for 40 days and check out on February 10th. The hotel submits the final charge on February 12th — 42 days after the original authorization. The 12.1 chargeback arrives.
- A car rental company notices a dent on a returned vehicle two weeks after the customer checked out. By the time the damage assessment is completed and the charge is processed, it's been 35 days since the original authorization.
- A contractor takes a $2,000 deposit authorization on a card in November. The project completes in January and the contractor submits the balance payment — 70 days after authorization. A 12.1 chargeback follows.
- A software company bills for an annual subscription but delays processing due to an internal accounting backlog. The transaction settles 45 days after the original authorization.

---

## Merchant Liability

Merchant liability under 12.1 is strong. If the transaction was genuinely submitted beyond the 30-day window, the chargeback will almost certainly stand. The presentment date and authorization date are both electronically recorded — there is no ambiguity.

However, there is a narrow exception: if the issuer approved the late presentment without objection (the transaction cleared and was settled), and the cardholder disputes it only after the fact, the defense depends on the specific timing and the issuer's handling.

---

## Required Evidence

Evidence to dispute a 12.1 chargeback:

- **Presentment timestamp:** Confirm the exact date the transaction was submitted for settlement. If your records show it was within 30 days of authorization, you have a defense.
- **Authorization date records:** The date and time of the original authorization approval.
- **Reauthorization records:** If you obtained a new authorization before the 30-day window expired on the original, the new authorization date resets the clock. Submit both authorization records.
- **Cardholder agreement:** If the cardholder specifically agreed to delayed billing (common in some service industries), the signed agreement may support your case — though it doesn't override Visa's presentment rules.

**Evidence that does not help:**
- Proof that the goods or services were delivered
- Signed receipts for the original transaction
- Customer acknowledgment of the charge

---

## Winning Strategy

1. **Calculate the exact days between authorization and submission.** If you're within 30 days, your dispute is straightforward — submit your authorization and settlement records showing the dates.
2. **If you re-authorized before the window expired,** use the new authorization date as your baseline. Document the reauthorization clearly.
3. **For hospitality:** Show the check-in/check-out timeline, demonstrate that the original authorization was still within window at checkout, or document any interim reauthorizations.
4. **Consider pre-emptive refund.** If a late presentment chargeback arrives for a genuinely late transaction, weigh whether the amount justifies the representment effort. The representment will very likely fail if the submission was clearly outside 30 days.

---

## Losing Mistakes

- **Submitting transactions in batches weekly or monthly.** This is a common operational error. Daily batch submission is the standard — batch every day, and authorization windows won't expire.
- **Not reauthorizing for extended hospitality stays.** Hotels that don't update and reauthorize during long stays will consistently hit 12.1 issues.
- **Assuming the cardholder won't notice.** Cardholders reviewing statements frequently flag transactions that appear unexpectedly long after the service was provided.
- **Fighting a clear late submission.** If the dates show a 45-day gap between authorization and settlement, accept the chargeback.

---

## Prevention

- **Batch daily.** Submit your batch every business day. Daily submission ensures transactions are settled while authorizations are fresh.
- **Monitor authorization age.** Some POS and payment gateway systems flag authorizations approaching their expiration date. Enable these alerts.
- **Reauthorize for extended transactions.** For hospitality, car rental, and other sectors with potentially delayed settlements, implement procedures to reauthorize for any transaction where settlement will exceed 30 days.
- **Train staff on presentment timelines.** Accounting and billing staff should understand that authorization dates create deadlines, not just records.
- **Use capture-at-time-of-service.** Wherever possible, capture and submit the transaction on the same day the service is delivered rather than billing in arrears.

---

## Timeline

| Stage | Timeframe |
|---|---|
| Authorization obtained | Day 0 |
| Visa's standard presentment window | 30 days from authorization |
| Late submission occurs | Day 30+ |
| Cardholder disputes charge | Within 120 days of transaction date |
| 12.1 chargeback received | After issuer review |
| Merchant response deadline | 30 days from notification |

---

## Frequently Asked Questions

**Q: Is the 30-day rule absolute, or are there exceptions for certain industries?**
A: Visa's standard is 30 days, but some industry-specific rules provide extended windows for certain transaction types (e.g., cruise lines, airlines, and some lodging transactions may have different rules under specific programs). Verify with your acquirer whether your industry has any authorized extensions. Do not assume extensions exist — confirm them contractually.

**Q: We processed a new authorization before the 30 days were up. Does the old authorization still create 12.1 risk?**
A: If you settled against the new authorization (not the old one), you are protected. Ensure that your settlement records reference the new authorization code, not the expired original. Your processor may require specific procedures to close the old authorization and settle against the new one.

**Q: The cardholder agreed to pay later when they received the goods. Does that help?**
A: A cardholder's agreement to pay later doesn't override Visa's presentment rules. If you want to bill after delivery, structure it as a recurring billing or installment arrangement with proper authorization mechanics, not as a delayed presentment of an original authorization.

**Q: We had a system failure that delayed our batch submission. Can we use that as a defense?**
A: A documented system failure that caused the delay may support your case in a pre-arbitration context, but Visa's rules don't formally provide a system-failure exception. If you can document the failure clearly (error logs, processor support tickets, outage records) and the delay was minimal (a few days past 30, not weeks), it may be worth presenting. No guarantee of success.

**Q: How far back can a 12.1 chargeback be filed?**
A: Cardholders can dispute a transaction within 120 days of the transaction date (or 120 days from when they discovered the issue). The 12.1 code specifically addresses the submission timing, not the cardholder's dispute timing. Both constraints apply independently.

---

## Sample Rebuttal Points

For disputes where submission was within 30 days:

- "We dispute this 12.1 chargeback because the transaction was presented for settlement within Visa's required 30-day window. Our authorization was obtained on [date] and the transaction was submitted for settlement on [date] — a period of [X] days, within the allowable 30 days. Authorization and settlement records are attached."

For reauthorization cases:

- "The original authorization obtained on [date] was supplemented by a reauthorization obtained on [date] (within the original 30-day window). The transaction was settled against the reauthorization, which had been obtained before the original authorization window expired. Both authorization records are attached for review."

For hospitality:

- "The guest's stay extended from [check-in date] to [check-out date]. A reauthorization was obtained on [date] to cover the extended stay, within the authorization window. The final settlement was submitted on [settlement date], within 30 days of the most recent authorization. Supporting records are attached."
