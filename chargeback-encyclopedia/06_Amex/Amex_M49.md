---
title: "Amex Dispute Code M49 — Transaction Amount Discrepancy"
description: "Complete merchant guide to American Express dispute code M49: charged amount differs from authorized amount, signed receipt evidence, tip adjustment rules, decimal errors, and how to prove the correct charge."
category: Amex
reason_code: "M49"
chargeback_type: "Transaction Amount Discrepancy"
win_rate: High (with signed receipt); Low (without receipt or with calculation error)
last_updated: 2026-06-29
tags: [amex, M49, amount-discrepancy, tip-dispute, incorrect-amount, signed-receipt, processing-error, chargeback-defense]
---

# Amex M49 — Transaction Amount Discrepancy

## What This Dispute Code Means

American Express dispute code M49 is filed when the amount the cardholder was charged differs from the amount they believe they authorized. The cardholder may have a receipt showing one amount, but the charge on their Amex statement shows a higher (or in rare cases, lower) amount. This is a processing error dispute — the issue is not fraud and it is not a delivery problem, it is a discrepancy between what the cardholder agreed to pay and what was actually charged.

M49 disputes occur across industries but are most common in:

- **Restaurants and hospitality** — where tip adjustments can be contested
- **Service businesses** — where the final invoice differs from the initial estimate
- **Retail** — where decimal or tax calculation errors occur
- **Hotels** — where the final folio includes charges not anticipated at check-in
- **Rental businesses** — where post-rental charges exceed the authorization

The resolution path is clear: if your charge matches the signed or agreed amount, submit that proof. If an error occurred, correct it immediately.

---

## Root Causes of M49 Disputes

### Tip Adjustment Disputes (Restaurants)

Restaurant tip disputes are the most frequent source of M49 chargebacks. The sequence:

1. Cardholder receives a paper or digital receipt showing a pre-tip subtotal
2. Cardholder writes in a tip amount and signs
3. The restaurant enters the final total (subtotal + tip) into their POS
4. The settlement amount reaches the cardholder's statement

Disputes arise when:
- The tip amount entered by the restaurant differs from what the cardholder wrote (intentional or data entry error)
- The cardholder left the tip line blank and the restaurant added a gratuity
- An automatic gratuity was added on top of a tip the cardholder also wrote
- The cardholder added the tip incorrectly (math error) and disputes when they realize the total is higher than expected

### Decimal and Rounding Errors

A charge of $1,200.00 that should have been $120.00 — the classic decimal shift error. Or $10.80 instead of $10.08. These errors are immediately recognizable to the cardholder and always generate a dispute. They are almost always merchant-side data entry errors.

### Estimate vs. Final Invoice

Service businesses often provide estimates (auto repair, home services, legal work, construction) that the cardholder authorizes, with the understanding that the final amount may differ. When the final invoice significantly exceeds the estimate without documented change orders or supplemental authorizations, M49 follows.

### Tax Calculation Errors

Charging the wrong tax rate, applying a tax to a tax-exempt product, or calculating tax on the pre-discount rather than post-discount price can produce a charge that differs from what the cardholder expected.

### Hotel Folio Discrepancies

Hotels that authorize an estimated stay amount at check-in and settle for a higher amount (due to minibar charges, room service, or additional nights) may receive M49 disputes from cardholders who did not anticipate the additional charges.

---

## Evidence: The Signed Receipt

For point-of-sale transactions, the signed receipt is dispositive evidence for M49.

**What a valid signed receipt shows:**
- Transaction date and time
- Merchant name and location
- Card number (last four digits)
- Itemized charges (pre-tip subtotal)
- Tip amount (handwritten by cardholder)
- Total amount (subtotal + tip)
- Cardholder signature

If your signed receipt shows a total of $85.00 and you settled for $85.00, the M49 has no merit. Submit the signed receipt and request reversal.

**For digital/electronic receipts:**
- The electronic receipt record with timestamp
- The cardholder's digital signature or acceptance
- The total amount shown at the time of digital signing
- The settlement amount matching that total

---

## Authorization Record Comparison

Beyond the receipt, the authorization record shows the amount the card network initially approved. For M49 disputes, submit:

- The original authorization amount
- The settlement amount
- The signed receipt total

If all three match, the dispute has no basis. If the settlement amount exceeds the authorization amount beyond permissible tip adjustment thresholds, you may have a legitimate processing error to correct.

---

## Tip Adjustment Rules

Card networks, including Amex, have specific rules about how much a settlement amount can exceed the authorization amount for tip-accepting merchants:

- In the United States, the typical allowable tip adjustment is **up to 20% above the authorization amount** (some acquirers allow up to 25%)
- Tip adjustments beyond this threshold may be flagged or subject to dispute
- Adding a tip when the cardholder left the tip line blank (and no automatic gratuity was disclosed) is not permissible

For restaurants:
- Train staff to enter the tip amount from the receipt accurately — a $2.00 entry error on a $20 receipt is a 10% discrepancy that triggers M49
- For large-party automatic gratuity, disclose this clearly on the menu and on the check, and ensure the server does not process an additional line for discretionary tip on top of the mandatory gratuity

---

## How to Identify and Correct Errors Before They Become Disputes

**Daily reconciliation**: Compare the day's authorized amounts against settled amounts. Any settlement that differs from its authorization by more than the standard tip adjustment threshold should be investigated.

**Staff entry review**: For businesses with manual data entry of final totals (restaurants, salons, auto repair), audit a sample of daily entries for accuracy. A quality control check before batch settlement can catch errors before they reach the cardholder's statement.

**Electronic tip capture**: Point-of-sale systems that capture cardholder-entered tips digitally (on-screen) eliminate handwriting interpretation errors and provide an automatic log of the tip amount the cardholder approved.

**Clear itemization on receipts**: Ensure your receipt format clearly shows: subtotal, tax, tip (if applicable), and total. A receipt where total equals subtotal + tax + tip, with no ambiguity, reduces disputes significantly.

---

## When to Correct vs. When to Fight

**Correct the charge immediately when:**
- You identify a data entry error (decimal shift, wrong amount keyed)
- The settled amount exceeds the signed receipt total
- Automatic gratuity was added on top of a cardholder-written tip
- The final invoice significantly exceeded the estimate without documented authorization

Processing a corrective credit for the difference, along with providing the credit transaction ID to your acquirer, resolves most M49 disputes faster than building a rebuttal.

**Fight the dispute when:**
- Your signed receipt matches the settled amount exactly
- The cardholder's claimed "correct amount" does not match the receipt they signed
- The cardholder made an arithmetic error on the tip calculation and is disputing the correct total

---

## Frequently Asked Questions

**Q: The cardholder added $10 tip on their receipt but we charged $15. We claim the receipt was illegible and $10 looked like $15. What happens?**
A: This is a losing dispute. Handwriting interpretation is the merchant's risk, not the cardholder's. If the receipt is ambiguous, you must err on the side of the lower reading. The cardholder's written amount is the authoritative figure, not your staff's interpretation. Process a corrective credit for the $5 difference.

**Q: A cardholder left the tip line blank but signed. We added our standard 18% for parties of 6. Is this permissible?**
A: Only if you disclosed the automatic gratuity on the menu and on the check, and the disclosure was visible to the cardholder before they signed. A blank tip line plus a non-disclosed automatic gratuity that you added after the cardholder signed is not permissible. The M49 will succeed for the added amount unless you can show clear prior disclosure of the automatic gratuity policy.

**Q: A hotel guest disputes their folio because it includes a minibar charge they claim they did not consume. Is this M49 or a different code?**
A: This is M49 if the total charge differs from what was authorized at check-in. It may also overlap with C31 (not as described) or C08 (services not received) depending on how the cardholder frames the dispute. For minibar disputes, your evidence is the minibar inventory audit showing the items were consumed — before-and-after inventory records taken at check-in and check-out. Point-of-sale records for room service ordered through your system (timestamp, item, room number) are also useful.

**Q: The cardholder entered $50 tip on the digital screen, but the receipt we printed shows $500 due to a system error. We want to fight M49 — do we have a case?**
A: No — this is your system error and the charge is incorrect. Correct the amount immediately. However, you should preserve the digital tip entry record (the $50 approved by the cardholder) to demonstrate the error was technical rather than intentional, which may be relevant for your relationship with your POS vendor and potentially for limiting any penalty beyond the refund.

**Q: We charged the cardholder correctly but they dispute the total claiming they were told a different price verbally. How do we defend this?**
A: Submit the signed receipt showing the agreed total. Verbal price quotes that differ from the signed receipt are difficult for cardholders to substantiate. If you have a written estimate or price confirmation email that matches the final charge, include that as well. A signed receipt is the most reliable evidence of agreed price — it is why requiring signatures (even digital) on all transactions is important.
