---
title: "NPCI U007 — Wrong Amount Transferred"
section: "07_RuPay"
category: "RuPay / NPCI Reason Codes"
network: "RuPay / NPCI"
reason_code: "U007"
document_type: "Reason Code Reference"
keywords: ["NPCI", "UPI", "wrong amount", "U007", "amount discrepancy", "overcharge", "collect request"]
difficulty: "Beginner"
---

# NPCI U007 — Wrong Amount Transferred

## Overview

U007 is raised when the amount debited from the customer's bank account is different from the amount the customer intended to pay. This can happen through a merchant error (wrong collect request amount, misconfigured QR code) or a customer error (typed the wrong amount in a push payment).

Unlike U003 (technical failure) or U005 (fraud), U007 is typically an operational error by one of the parties — either the merchant sent the wrong amount in a collect request, or the customer entered the wrong amount when pushing a payment. NPCI's resolution depends on identifying who made the error.

## Common Scenarios

**QR code misconfiguration**: Merchant's payment QR code is programmed with an incorrect fixed amount. Customer scans and pays that amount without realizing it differs from the actual price. More common with static QR codes where the amount is pre-set.

**Collect request error**: Merchant sends a UPI collect request for the wrong amount (₹2,500 instead of ₹250 — decimal error). Customer approves without carefully checking the amount shown in their UPI app.

**Customer push payment error**: Customer initiates a push payment and types the wrong amount. Less common since most UPI apps display a confirmation screen, but typos happen.

**Dynamic pricing display error**: Merchant app shows one price, but the backend sends a collect request for a different amount (integration bug between ordering system and payment system).

**Currency display bug**: Amount shown in paise instead of rupees (or vice versa) in the merchant's integration.

## Merchant Liability

**Merchant is liable when:**
- The collect request was sent for the wrong amount
- The QR code had an incorrect fixed amount programmed
- The merchant's app/website showed one price but charged another
- The error was in the merchant's payment integration

**Customer is responsible when:**
- The customer typed the wrong amount in a push (send money) payment
- The collect request clearly showed the correct amount and customer approved it
- Customer approved the amount displayed in their UPI app without verifying

**How to determine fault**: NPCI checks the UPI collect request record — the amount in the collect request versus the amount debited. If they match, the error was in the collect request creation (merchant fault). If the customer pushed a custom amount, that is a customer-side issue.

## Required Evidence

**For merchants defending against U007:**
- Original collect request record showing the amount that was sent (from payment gateway logs)
- Order confirmation or invoice showing the correct price agreed upon
- Screenshot of merchant's checkout page at time of transaction (to verify correct amount displayed)
- Payment gateway transaction log showing amount sent matches the correct order value

**For customers filing U007:**
- NPCI transaction reference (UTR) showing the debited amount
- Merchant's invoice or receipt showing the correct amount that should have been charged
- Screenshot of UPI collect request approval screen (if available)

## Resolution Process

1. Customer reports U007 to their bank within 30 days of transaction <!-- NEEDS VERIFICATION: same 30-day mandate flagged in 000_RuPay_NPCI_Overview.md; recurs 2 more times below in this same file -->
2. Bank raises with NPCI; NPCI queries the merchant's PSP/acquiring bank
3. Merchant receives notification and must respond within 30 days
4. If merchant error confirmed: merchant must refund the difference (excess amount charged)
5. If customer error confirmed: dispute may be rejected; customer should resolve with merchant directly

**For a ₹X overcharge**, the merchant need only refund the excess (₹charged − ₹correct price), not the full transaction.

## Winning Strategy for Merchants

- Respond promptly with collect request records from your payment gateway
- Show that your collect request amount matches the agreed order value
- Provide the order details (items, prices, total) to prove correct amount
- If you made an error, refund the difference immediately — this resolves the dispute before NPCI escalation

## Recommended Merchant Practice: Preventing U007

- Always use **dynamic QR codes** that generate a new QR for each transaction with the exact order amount (not static QR codes with fixed amounts)
- Build **amount confirmation screens** in your checkout flow before sending the collect request
- Validate payment amounts in your backend before generating collect requests
- For high-value orders, send an additional SMS/email confirmation of the exact amount to the customer
- Test QR code integrations regularly, especially after software updates

## Timeline

| Milestone | Timeframe |
|-----------|-----------|
| Customer dispute filing | Within 30 days of transaction |
| Merchant response window | 30 days from NPCI notification |
| Bank resolution mandate | 30 days from complaint |
| Refund for merchant error | 5-7 working days after confirmation |

<!-- NEEDS VERIFICATION: confirm this 5-7 working day refund figure against real documentation -->

## FAQs

**Q: My customer approved a collect request that clearly showed the correct amount. Why am I getting a U007?**
This can happen if the customer's UPI app displayed a different amount than what the collect request contained (rare display bug). Provide your collect request record showing the correct amount — NPCI will cross-check with the UPI switch logs.

**Q: The customer typed the wrong amount in a push payment. Do I have to refund it?**
NPCI will determine fault by examining the transaction type. For push payments (customer-initiated), the customer typed the amount, making it customer-side error. However, voluntarily refunding overpayments and keeping underpayments builds trust and prevents disputes.

**Q: How do I prevent wrong amounts with QR codes?**
Switch to dynamic QR codes that generate a new code for each order with the exact amount pre-filled. Static QR codes with hardcoded amounts are a common source of U007 disputes.

**Q: What if I charged the wrong amount accidentally — should I just refund before NPCI gets involved?**
Yes — proactively refunding the excess amount (before the bank files with NPCI) is the fastest, cheapest resolution. The dispute is automatically closed when the refund is confirmed.

## Key Takeaways

- U007 disputes arise from amount mismatches — merchant collect request error or customer push payment typo
- NPCI determines fault by checking the original collect request record
- Merchant errors require refunding only the excess amount, not the full transaction
- Dynamic QR codes and amount confirmation screens prevent most U007 disputes
- Responding within 30 days with payment gateway logs is critical
