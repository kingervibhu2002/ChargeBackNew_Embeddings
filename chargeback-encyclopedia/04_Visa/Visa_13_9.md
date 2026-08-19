---
title: "Visa 13.9 — Non-Receipt of Cash or Load Transaction Value"
section: "04_Visa"
category: "Visa Reason Codes"
document_type: "Reference"
keywords: ["Visa 13.9", "ATM dispute", "cash not dispensed", "ATM chargeback", "prepaid card load", "ATM operator chargeback", "cash dispenser journal", "CCTV ATM evidence", "T+0 reversal"]
difficulty: "Advanced"
---

# Visa 13.9 — Non-Receipt of Cash or Load Transaction Value

Visa reason code 13.9 applies to two distinct scenarios: a cardholder who used an ATM and did not receive some or all of the cash they requested, and a cardholder who loaded value onto a prepaid card but the expected balance was not credited. These disputes place the ATM operator or prepaid load merchant in the role of the "merchant" defending the chargeback. Unlike most consumer purchase disputes, 13.9 defenses revolve around highly specific mechanical and log-based evidence — cash dispenser journals, CCTV footage, and vault reconciliation data.

## The Two Scenarios Covered by 13.9

### Scenario 1: ATM Cash Not Dispensed

The cardholder inserted their card, entered their PIN, requested a cash withdrawal, the transaction was debited from their account (and the ATM operator's account was credited), but the ATM did not physically dispense the cash — or dispensed less cash than the authorized amount.

This is a relatively common occurrence in ATM operations. ATMs can malfunction in several ways:
- **Short dispense:** The ATM dispenses fewer bills than the requested amount (e.g., a jam causes 3 of 5 bills to retract into the dispenser)
- **Complete non-dispense:** The ATM authorizes and debits the transaction but fails to dispense any cash (dispenser jam, empty cassette triggers after authorization)
- **Retraction:** The cash was presented at the dispense slot but the cardholder did not take it within the timeout window, and the ATM retracted the bills

In all of these cases, the cardholder's account was charged but they received no (or insufficient) cash.

### Scenario 2: Prepaid Card Load Not Credited

The cardholder paid to load value onto a prepaid card (a store-brand prepaid card, a general purpose reloadable card, a gift card), and the payment was processed and debited from their account, but the expected balance was never credited to the prepaid card.

This typically occurs due to:
- A processing failure between the payment terminal and the card program processor
- A timeout during the load transaction that resulted in the debit completing but the load failing
- A technical failure in the prepaid program infrastructure

## ATM Operator as the "Merchant"

In a 13.9 chargeback involving an ATM, the ATM operator is in the merchant position — they received the funds through the ATM transaction and are responsible for demonstrating that the cash was dispensed.

Most ATM operators are financial institutions (banks and credit unions) or independent ATM deployers (IADs). Their chargeback defense process runs through their acquiring bank (for IADs) or through their own bank's dispute resolution process (for bank-owned ATMs).

If you are an independent ATM deployer receiving 13.9 chargebacks, your defense relies entirely on the electronic records your ATM generates.

## ATM Evidence: What Your Machine Logs

### Cash Dispenser Journal Tape

The most critical evidence in an ATM 13.9 dispute is the cash dispenser journal — an electronic log maintained by the ATM's cash dispenser module that records:

- Each attempted dispense event
- The number of bills requested and the number actually dispensed
- Any jam, retract, or error events during the dispense cycle
- The cash cassette inventory before and after the transaction

For a disputed transaction, the journal tape should show whether the requested number of bills was successfully dispensed or whether an error or jam occurred during the dispense cycle. A journal showing "10 bills dispensed" on a $100 withdrawal request is evidence that the ATM functioned correctly. A journal showing "dispense attempt, 3 bills jammed, 7 bills retracted" is evidence of a malfunction — and the cardholder's chargeback is legitimate.

**Format:** ATM journals are typically generated as electronic logs exportable from the ATM management system. Request the journal for the specific transaction date, time, and ATM terminal ID.

### CCTV Footage

Many ATMs, particularly in indoor or bank-lobby locations, are covered by CCTV cameras. CCTV footage showing the cardholder's interaction with the ATM — specifically whether they received and took bills from the dispense slot — is powerful evidence.

**Evidence value:**
- Footage showing the cardholder receiving and pocketing bills: strong evidence the cash was dispensed and received
- Footage showing the cardholder walking away without bills appearing at the slot: supports the non-dispense claim
- Footage showing the cardholder at the machine but the dispense slot not showing cash: supports the non-receipt claim

**Practical limitation:** Not all ATMs are covered by cameras with adequate angles on the dispense slot. Camera availability varies widely. Submit footage when available; document its unavailability when it is not.

### Vault Reconciliation

ATM operators conduct regular vault balancing — comparing the expected cash balance in the ATM cassettes against the actual physical cash present. If an ATM short-dispensed on multiple transactions, the vault balance will show more cash than the transaction records indicate was dispensed.

For an individual 13.9 dispute, vault reconciliation data for the relevant ATM on the relevant date can corroborate the journal tape data. If the vault balance shows the expected amount (no excess cash), the dispense records are consistent with correct operation. If excess cash exists in the vault for that ATM, it may indicate short-dispense events occurred.

## T+0 Reversal Obligations

One important rule in ATM dispute handling: if an ATM transaction is debited but no cash is dispensed (a confirmed non-dispense event, as shown in the journal), the ATM operator has an obligation to reverse the transaction on the same processing day (T+0) — before the debit is finalized.

Many ATM management systems can be configured to automatically detect non-dispense events and initiate same-day reversals. When this system works correctly, the cardholder never sees the debit on their statement — the reversal posts alongside the debit in the same processing cycle.

When T+0 reversal systems fail (due to system timeout, communication failure, or misconfiguration), the debit settles without the corresponding reversal, resulting in the cardholder being charged for cash they never received — the classic 13.9 scenario.

## When the ATM Operator Wins vs. Loses

### ATM Operator Wins When:
- Journal tape clearly shows the full requested number of bills was dispensed
- CCTV footage corroborates the cardholder receiving cash from the dispense slot
- Vault reconciliation for the transaction date shows no excess cash (consistent with correct dispense)
- The cardholder filed the dispute after the ATM's T+0 reversal already corrected the transaction (duplicate claim)

### ATM Operator Loses When:
- Journal tape shows a dispense error, jam, or retraction event
- The requested number of bills does not match the dispense record
- T+0 reversal failed and the cardholder was charged for cash never received
- No journal tape is available for the disputed transaction (absence of evidence cannot overcome a cardholder's claim)
- CCTV footage shows no dispense event at the relevant time

## Prepaid Card Load Disputes

For prepaid card load disputes, the evidence is different:

**Evidence to submit:**
- Load transaction record from the terminal showing the transaction was completed
- Communication record between your load terminal and the prepaid card program processor, showing whether the load was confirmed
- If the load was not confirmed (timeout, error), the T+0 reversal should have been triggered — show whether the reversal was processed
- Prepaid card program's balance records showing whether the load was credited to the specific card

If your system can confirm the load was credited, submit that confirmation. If the load failed at the program processor level, accept the chargeback and work with your prepaid card program to investigate the load failure.

---

## Frequently Asked Questions

**Q: A cardholder says they got $100 instead of $200 from my ATM. My journal says $200 was dispensed. How do I handle this?**
A: Submit the ATM journal tape showing the full $200 dispense as your primary evidence. If CCTV footage covers the dispense slot and shows cash being taken, include that as well. The journal tape is the authoritative record of the ATM's dispense activity. In a dispute between the cardholder's claim and the journal tape showing full dispense, issuers generally accept the journal tape as decisive — unless the tape itself shows a discrepancy.

**Q: My ATM journal shows a "cassette empty" error occurred during the disputed transaction. What happened?**
A: A cassette-empty error during a transaction means the ATM attempted to dispense from an empty cassette, which would result in a non-dispense or short-dispense. If the transaction was authorized before the error was detected, the debit may have processed without dispensing cash. Accept the chargeback — the cardholder did not receive their cash — and configure your ATM management system to trigger automatic T+0 reversals when cassette-empty errors occur during active transactions.

**Q: We do not have CCTV at our ATMs. How do we defend without footage?**
A: Rely on the journal tape exclusively. The journal tape is the primary mechanical record of the ATM's operation and is the standard ATM dispute evidence in the absence of CCTV. If the journal shows full dispense, submit it and the vault reconciliation data. Most issuers accept a clean journal tape without CCTV. Note: installing even a basic camera covering the dispense slot significantly strengthens your long-term dispute defense capability.

**Q: A customer filed a 13.9 but our T+0 reversal had already processed. Does the chargeback still count?**
A: If the T+0 reversal processed correctly and the debit never finalized on the cardholder's statement, the chargeback should not have been filed — there was nothing to dispute. Submit evidence of the reversal transaction (timestamp and amount). If the reversal and the chargeback both processed, you are being double-debited — your acquirer should be able to offset the duplicate debit.

**Q: How do prepaid card load failures typically occur?**
A: Most prepaid load failures result from communication timeouts between the load terminal and the card program processor. The terminal sends the load request, the processor times out before confirming, and the terminal either finalizes the transaction (causing a debit without a load) or reverses it (ideal outcome). Configure your load terminals to implement a robust timeout-and-reversal protocol: if load confirmation is not received within a defined window, automatically reverse the debit before it settles.
