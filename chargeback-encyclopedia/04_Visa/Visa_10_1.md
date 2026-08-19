---
title: "Visa 10.1 — EMV Liability Shift: Counterfeit Fraud"
section: "04_Visa"
category: "Visa Reason Codes"
network: "Visa"
reason_code: "10.1"
document_type: "Reason Code Reference"
keywords: ["EMV", "chip card", "counterfeit fraud", "liability shift", "10.1", "skimming", "non-chip terminal"]
difficulty: "Intermediate"
---

# Visa 10.1 — EMV Liability Shift: Counterfeit Fraud

## Definition

Visa reason code 10.1 covers counterfeit fraud at the point of sale — specifically, situations where a fraudster used a cloned or counterfeit version of a cardholder's chip card to make a purchase. The counterfeit card is created by stealing the card's magnetic stripe data (typically through skimming devices) and encoding that stolen data onto a blank card.

The reason this code exists as a liability shift mechanism is directly tied to EMV chip technology. A genuine EMV chip card generates a unique cryptographic code for every single transaction — a code that cannot be replicated from the magnetic stripe data alone. If a merchant's terminal reads the chip, it will detect that a counterfeit card lacks a valid cryptographic response and will decline the transaction. If the merchant's terminal does not support chip reading — or if the clerk bypassed the chip and swiped the card instead — the counterfeit card can succeed. In that scenario, the terminal owner (the merchant) bears liability for the resulting fraud.

This is the core of the EMV liability shift: Visa and the card networks shifted fraud liability from issuers to merchants who had not upgraded to EMV-capable terminals, creating a financial incentive to adopt chip technology.

---

## What Is Counterfeit Fraud?

Counterfeit fraud occurs when a criminal creates an unauthorized copy of a payment card. The most common method is **skimming** — attaching a hidden device to a card reader (gas pump, ATM, retail terminal) that secretly reads and records magnetic stripe data from cards as they are swiped. The criminal then encodes that stolen data onto a blank card, creating a physical counterfeit.

Before EMV, counterfeit fraud was extremely difficult to stop at the point of sale because the magnetic stripe contained static data — the same data every time. A perfect copy of the stripe was functionally identical to the original card. EMV chips solve this by generating dynamic authentication data for each transaction. A counterfeit card made from stolen stripe data cannot replicate the chip's cryptographic response, so an EMV-capable terminal will reject it.

Skimming operations range from solo criminals with off-the-shelf equipment to sophisticated organized crime rings targeting hundreds of terminals simultaneously. Gas station pumps, outdoor ATMs, and unstaffed kiosks are the most common targets due to reduced oversight.

---

## How the EMV Liability Shift Works

Prior to October 2015 (the U.S. EMV liability shift deadline), fraud liability for counterfeit transactions generally rested with the card issuer. After October 2015, Visa changed the rule: if a chip card is used at a non-chip terminal (or a chip card is swiped instead of dipped at a chip-capable terminal), liability for any resulting counterfeit fraud shifts to the merchant's acquirer, and by extension, to the merchant.

**Liability shift conditions for 10.1:**
- The cardholder's card has an EMV chip.
- The transaction was processed via magnetic stripe swipe (not chip read).
- The transaction is later disputed as counterfeit fraud.

If all three conditions are met, the merchant is liable. The issuer will file a 10.1 chargeback, and the merchant has an extremely limited ability to fight it.

**Exception — chip-and-PIN liability:** At terminals that accept chip but only support signature (not PIN), additional liability rules apply. For most U.S. transactions, chip-and-signature is sufficient to protect the merchant from 10.1 chargebacks.

---

## Common Scenarios

- A gas station that has not updated its pump card readers still runs magnetic stripe transactions. A fraudster uses a cloned card at the pump. The legitimate cardholder later disputes the charge. The gas station receives a 10.1 chargeback.
- A retail store's primary chip terminal breaks. Staff fall back to swiping cards on an old magnetic stripe reader during the busy period. A counterfeit card is used. The store is liable even though it normally accepts chip.
- A small restaurant uses a legacy POS system that has not been updated. A waiter swipes cards tableside. A cloned card is used and later disputed.

---

## Merchant Liability

Merchant liability under 10.1 is near-absolute when the terminal did not process a chip read. Your acquirer will almost always uphold the chargeback if:
- Authorization records show a magnetic stripe read ("fallback transaction"), not a chip read.
- The transaction entry mode in the authorization data reflects swipe, not EMV.

The only meaningful defenses involve proving that the chip was actually read — which means the authorization data must reflect an EMV chip read entry mode. If the data shows a swipe, there is no defense.

---

## Required Evidence (If Disputing)

Because 10.1 falls under the Allocation workflow, automated system data determines liability. Evidence that may support a merchant dispute includes:

- **EMV chip read confirmation:** Authorization records showing transaction entry mode as chip (entry mode codes 05 or 07 in the authorization data).
- **Terminal capability data:** Documentation showing the terminal is certified EMV-capable and was functioning on the date of the transaction.
- **Chip decline log:** If the chip was attempted and fell back to stripe due to a chip error (legitimate fallback), documentation of that technical failure.
- **Cardholder presence documentation:** Signed receipt, ID check documentation (though this helps less than chip data).

**Critical note:** If your authorization data shows a swipe entry mode, no amount of paper receipts or signed slips will overcome the liability shift. The chargeback will stand.

---

## Winning Strategy

The only reliable way to win a 10.1 chargeback is to demonstrate that the chip was read. This requires:

1. **Pull the original authorization record** from your payment processor. Look at the transaction entry mode field. Entry mode 05 (chip read) or 07 (chip read, card not retained) indicates a chip transaction and supports your defense.
2. **Document your terminal's EMV certification.** Your payment processor or terminal manufacturer can provide certification documentation showing your terminal is EMV-compliant.
3. **Submit both pieces of evidence** with a clear rebuttal letter explaining that the chip was read and the liability shift therefore does not apply.

If you win on this basis, the issuer must absorb the fraud liability — the transaction was properly processed and the chip authentication should have caught the counterfeit.

---

## Losing Mistakes

- **Fighting a swipe transaction.** If the authorization data shows a magnetic stripe read, accept the chargeback. Do not waste representment fees arguing about signatures or customer service.
- **Submitting only a signed receipt.** A signature does not override the EMV liability shift. Chip read data is what matters.
- **Ignoring terminal maintenance.** A terminal that shows as EMV-capable in settings but has a broken chip reader will process fallback swipes — and those will all be your liability if fraud occurs.
- **Missing the 30-day deadline.** 10.1 chargebacks fall under the Allocation workflow with strict timelines. Missing the response window means automatic loss.

---

## Prevention

- Ensure all terminals are EMV-certified and actively reading chips. Test chip functionality regularly.
- Disable or remove magnetic stripe fallback at unstaffed terminals (self-checkout, outdoor kiosks, fuel pumps) where practical.
- Upgrade outdoor payment terminals (gas pumps) — the liability shift for fuel dispensers was extended but eventually took full effect. All fuel pump operators should now be EMV-compliant.
- Immediately report and replace any terminal with a malfunctioning chip reader. Conduct swipe transactions on a broken terminal only as a last resort and document each instance.

---

## Timeline

| Event | Timeframe |
|---|---|
| Transaction date | Day 0 |
| Cardholder disputes transaction | Up to 120 days post-transaction |
| Issuer files 10.1 chargeback | Typically within 30 days of dispute |
| Merchant response deadline | 30 days from chargeback notification |
| Escalation to pre-arbitration | If merchant response rejected |

---

## Frequently Asked Questions

**Q: My terminal has a chip reader but the customer's card wouldn't read the chip, so we swiped it. Are we liable?**
A: Potentially, yes. Magnetic stripe fallback transactions carry the same liability as if no chip reader existed. Some processors allow documented chip failure to qualify as a defense, but this is not universally accepted. Always document legitimate chip failures in your POS system at the time of the transaction.

**Q: We checked the customer's ID. Does that help with a 10.1 chargeback?**
A: No. ID verification is not a defense for EMV liability shift chargebacks. The issuer's position is that a chip terminal would have detected the counterfeit card regardless of whether ID was checked.

**Q: The transaction happened over a year ago. Can the issuer still file a 10.1 chargeback?**
A: Visa's standard dispute window is 120 days from the transaction date (or from when the cardholder discovered the fraud). Disputes filed outside this window are invalid and can be rejected by the acquirer.

**Q: We're a small business and can't afford new chip terminals right now. What should we do?**
A: Accept that magnetic stripe transactions carry counterfeit fraud liability and price that risk into your business model. Prioritize upgrading high-volume, high-ticket terminals first. Contact your payment processor — many offer subsidized or leased EMV terminals.

**Q: Can a counterfeit card ever succeed at an EMV terminal?**
A: Extremely rarely, and typically only due to processing defects or sophisticated attacks. The dynamic authentication data generated by an EMV chip makes successful counterfeiting at a chip terminal functionally impossible with current technology.

---

## Sample Rebuttal Points

When you have chip read data supporting your defense, include these points in your rebuttal letter:

- "The transaction referenced in chargeback [ID] was processed as an EMV chip read transaction. The authorization record (attached) reflects transaction entry mode 05, confirming the card's chip was successfully read."
- "Our terminal is EMV-certified [certification document attached]. The chip read generates cryptographic authentication data that would have detected a counterfeit card. The transaction passed chip authentication at the time of sale."
- "Under Visa's EMV liability shift rules, liability rests with the card issuer when a chip card is successfully authenticated at an EMV-capable terminal. We request that this chargeback be reversed and liability returned to the issuer."
- "We request the issuer provide the authorization entry mode from their records to confirm this was processed as a chip transaction, as our processing data reflects."
