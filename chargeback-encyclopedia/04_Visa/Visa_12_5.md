---
title: "Visa 12.5 — Incorrect Amount"
section: "04_Visa"
category: "Visa Reason Codes"
document_type: "Reference"
keywords: ["Visa 12.5", "incorrect amount", "overcharged", "tip adjustment chargeback", "wrong amount charged", "decimal error", "unit pricing error", "Visa processing error"]
difficulty: "Beginner"
---

# Visa 12.5 — Incorrect Amount

Visa reason code 12.5 covers transactions where the amount charged to the cardholder differs from the amount the cardholder agreed to pay. This is a processing error code — meaning the merchant charged the right person, but for the wrong dollar amount. It is more common than most merchants expect, particularly in industries with tip adjustments (restaurants, salons) and variable pricing (quantity-based orders, metered services).

## What This Chargeback Means

A Visa 12.5 chargeback signals that the cardholder disputes the amount on their statement as different from what they authorized or agreed to. The cardholder is not claiming fraud or non-delivery — they are claiming arithmetic or entry error.

Common scenarios that trigger 12.5 disputes include:

### Tip Adjustments
A restaurant presents a cardholder with a receipt for $48.00. The cardholder adds an $8.00 tip and signs, making the total $56.00. However, the server or management adjusts the tip to $18.00 (or $80.00, if an extra zero was accidentally added), and the card is settled for $66.00 or $128.00. The cardholder sees the discrepancy on their statement and files a chargeback.

This is the single most common cause of Visa 12.5 chargebacks. Tip adjustment errors are pervasive in food service because tip entry happens manually by staff after the customer has already left the premises.

### Unit Pricing Errors
A merchant sells items priced individually but inadvertently applies a per-case price to a per-unit purchase, or vice versa. The cardholder authorized payment for 5 items at $12 each ($60 total) but was charged at $12 per dozen — a total of $720.

### Decimal Point Errors
An entry error moves the decimal: $23.50 becomes $2,350 or $235.00. These errors are particularly common in manual key-entry environments.

### Quantity Errors
The wrong quantity was entered at the point of sale: 10 units instead of 1, or 1 instead of 10 (in the opposite direction — but usually cardholders only dispute overcharges, not undercharges).

### Double Adjustment Errors
An original transaction is voided and re-processed, but both the original and the re-processed amount settle — effectively doubling the charge. (This can also trigger Visa 12.6 for duplicate processing.)

## Evidence You Need to Fight This Chargeback

To successfully dispute a Visa 12.5 chargeback, you need to demonstrate that the amount charged matches what the cardholder agreed to pay.

### Signed Receipt With Correct Amount
The original signed receipt showing the cardholder's signature on a document that clearly states the total amount you charged is your primary defense. If the cardholder signed a receipt for $66.00 (including a $10 tip on a $56 check), and you settled for $66.00, that signature is your evidence.

**Requirement:** The receipt must show both the pre-tip amount and the final amount in a way that makes the calculation clear.

### Order Confirmation at Time of Purchase
For e-commerce and MOTO transactions, the order confirmation email sent to the customer at the time of purchase, showing the exact amount charged, serves as evidence of agreed pricing.

### POS Transaction Record
Your POS system's transaction log showing the amount entered, any adjustments made, and the final settlement amount. This is internal documentation but can corroborate your claim.

### Itemized Invoice
For B2B or service transactions, a signed or accepted invoice showing the agreed pricing and quantities substantiates the billed amount.

## Tip Adjustment Rules and Industry Norms

Visa tip adjustment rules permit merchants in tip-eligible industries (restaurants, bars, salons, taxis) to adjust the authorized amount upward by the tip amount. However, the following rules apply:

- The final settled amount must not exceed the authorized amount by more than a network-defined threshold. In practice, most acquirers flag tip adjustments that exceed **20% above the authorization** (and some networks set the rule at 20% or a maximum of 20% in many U.S. states, though this varies).
- Tip adjustments must be made on the same transaction (same authorization), not as a new transaction.
- Internal controls (manager approval for adjustments above a threshold, end-of-shift tip journal reconciliation) are best practice for preventing unauthorized adjustments.

If your tip adjustment complied with network rules and the cardholder's signed receipt confirms the amount, you have a strong defense.

## When to Accept vs. Fight

**Accept the chargeback when:**
- You can verify that the amount charged was indeed incorrect (tip was mis-entered, decimal was wrong, unit pricing was applied incorrectly)
- You cannot locate the signed receipt or order confirmation showing the agreed amount
- The discrepancy between what you charged and what the cardholder agreed to is clear

**Fight the chargeback when:**
- You have a signed receipt from the cardholder explicitly authorizing the disputed amount
- Your POS records confirm the amount entered matches the amount settled
- The cardholder appears to have forgotten or is disputing a tip they did authorize

## Prevention

### Restaurant and Hospitality Environments
- Print pre-authorization and post-tip receipts and keep the merchant copy on file
- Implement tip entry review: a manager should review high-percentage tip adjustments
- Train staff that adding extra digits or adjusting tips to incorrect amounts is a termination-level offense and creates business liability
- Use a tip estimation prompt on your terminal that shows the server the percentage they are entering

### E-Commerce and MOTO
- Display the total amount in large, clear text on the final confirmation screen before the card is charged
- Send an order confirmation email immediately after purchase, showing the itemized total
- Implement decimal validation in your payment form to prevent entry errors

### All Environments
- Reconcile daily: compare authorized amounts to settled amounts and investigate any discrepancies before they become chargebacks
- Retain all signed receipts for a minimum of 24 months (beyond the 120-day dispute window plus buffer)

---

## Frequently Asked Questions

**Q: A customer is disputing a tip they voluntarily added to their receipt. Can I fight this?**
A: Yes. If you have the customer's signed receipt showing they wrote in the tip amount and signed the total, submit that receipt as your primary evidence. The customer's own signature on the correct total is compelling evidence that the amount was authorized. Many issuers will reverse a 12.5 chargeback when presented with a signed receipt showing the disputed amount.

**Q: My POS system automatically adds a service charge to large party orders. The customer is disputing it. Is this a 12.5?**
A: This can be a 12.5 (incorrect amount) or a 13.5 (misrepresentation) depending on the cardholder's claim. If the service charge was disclosed on the menu and the receipt shows it separately and clearly, you have a strong defense. If the charge was not disclosed before the cardholder ordered, you may lose the dispute on misrepresentation grounds regardless of whether the amount was accurately entered.

**Q: I made a decimal entry error and charged $1,200 instead of $120. What should I do?**
A: Immediately issue a refund for the difference ($1,080). Process the correct charge of $120 if the original payment needs to remain on file. Contacting the cardholder proactively — before they see the error on their statement — is both good customer service and significantly reduces the likelihood of a chargeback being filed.

**Q: The customer signed a receipt but the total includes an adjustment I made after they left. Is the signed receipt still valid evidence?**
A: This depends on whether the adjustment was within network tip adjustment rules. If the tip you entered was more than 20% above the authorized amount (or violated your acquirer's tip limits), the signed receipt for the pre-tip amount does not authorize the adjusted total, and the 12.5 chargeback is likely valid. If the tip was within normal bounds and the cardholder signed a receipt showing the estimated tip line, consult your acquirer.

**Q: Does Visa have a minimum amount threshold for 12.5 chargebacks?**
A: No. Unlike some fraud codes that require minimum transaction amounts to be eligible for chargeback, processing error codes including 12.5 can be filed on any transaction amount where a discrepancy exists. Even a $2 overcharge can technically support a 12.5 chargeback, though in practice issuers rarely process chargebacks for very small amounts due to the administrative cost.
