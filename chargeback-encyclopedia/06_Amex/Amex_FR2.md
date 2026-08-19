---
title: "Amex Dispute Code FR2 — Fraud — EMV Counterfeit"
description: "Complete merchant guide to American Express dispute code FR2: counterfeit card fraud at non-EMV terminals, liability shift rules, authorization data evidence, and terminal compliance."
category: Amex
reason_code: "FR2"
chargeback_type: "Fraud — EMV Counterfeit"
win_rate: Very Low (without chip read confirmation)
last_updated: 2026-06-29
tags: [amex, FR2, EMV, counterfeit-fraud, chip-liability-shift, terminal-compliance, chargeback-defense]
---

# Amex FR2 — Fraud — EMV Counterfeit

## What This Dispute Code Means

American Express dispute code FR2 is Amex's equivalent of Mastercard's reason code 4870 and Visa's reason code 10.4 — a counterfeit card fraud dispute triggered by the EMV chip liability shift. FR2 is filed when a cardholder reports that a fraudulent transaction was made using a counterfeit version of their card, and the merchant processed that transaction by reading the magnetic stripe rather than the EMV chip.

The liability shift logic is identical across networks: EMV chip technology prevents counterfeit fraud by generating a unique, non-reusable cryptogram for each transaction. When a merchant has a chip-capable terminal and uses it to read the chip, counterfeit card data is useless — the criminal cannot replicate the chip's cryptographic output. When a merchant uses a swipe-only terminal (or a chip-capable terminal in fallback/swipe mode), the magnetic stripe's static data is used, and that data can be cloned. Merchants who accept swipe transactions on chip-capable cards absorb the resulting fraud losses.

---

## The Amex EMV Liability Shift Timeline

American Express implemented its EMV liability shift in the United States on **October 1, 2015** — the same date as Visa and Mastercard. The liability shift applies to:

- **Domestic transactions** in the US, EU, and most international markets
- **Card-present transactions only** — counterfeit fraud in CNP environments operates under different rules (see FR2 and F24)
- **Merchants whose terminals lack chip capability** or whose chip-capable terminals processed the transaction via magnetic stripe

The liability shift does NOT apply to:
- Transactions where no chip-capable card was presented (magnetic-stripe-only cards)
- ATM transactions (ATMs have their own separate liability shift timeline)
- Fuel dispensers with approved extensions (the fuel dispenser liability shift had a delayed timeline)

---

## How Counterfeit Card Fraud Happens at Point of Sale

Understanding the fraud mechanism helps explain why chip reading matters:

1. A criminal installs a skimming device on a payment terminal, ATM, or card reader (often at fuel stations, restaurants, or self-checkout kiosks)
2. The skimmer reads and records the magnetic stripe data from legitimate cards
3. The criminal encodes this stolen data onto a blank card (a "white card" or cloned card)
4. The cloned card is used at swipe-accepting merchant terminals to make purchases
5. The real cardholder sees fraudulent charges and disputes them
6. Amex files FR2 chargebacks against the merchants where the cloned card was used

The fraud victim merchants are not the same merchants where skimming occurred — criminals typically use cloned cards far from the skimming location to reduce detection risk.

---

## Authorization Data: The Core Evidence

FR2 disputes are resolved through authorization record data, not through documents written after the fact. When your acquirer sends you an FR2 dispute notification, your first step is to request the full authorization record for the disputed transaction from your acquirer.

The authorization record contains a **Point of Service (POS) Entry Mode code** that reveals how card data was captured:

| Entry Mode Code | Meaning |
|---|---|
| 05 | Contact chip (EMV) — chip was read |
| 07 | Contactless chip (NFC/tap) — equivalent protection |
| 90 | Magnetic stripe read |
| 80 | Chip fallback to magnetic stripe |

If your authorization record shows **entry mode 05 or 07**, the chip was read and Amex cannot hold you liable under FR2. The dispute should be reversed upon submission of this evidence.

If your authorization record shows **entry mode 90 or 80**, you processed a swipe transaction on a chip card. The FR2 liability applies.

Additionally, a successful chip read will produce an **Application Cryptogram (AC)** in the authorization data — an unforgeable proof that the genuine chip was present. If this cryptogram is present and verifiable, the FR2 cannot stand.

---

## Evidence to Submit for FR2

**If chip was read (terminal supports EMV):**
- Full authorization record showing POS Entry Mode 05 or 07
- EMV Application Cryptogram from the authorization data
- Terminal configuration documentation showing EMV chip reading is enabled
- Statement from your acquirer confirming chip transaction capability

**If you believe the fraud allegation is incorrect (no transaction occurred at your terminal):**
- Transaction records showing no transaction for the disputed amount on the disputed date
- Terminal logs showing no matching transaction
- Signed statement from terminal operator

---

## Why Merchants Cannot Argue Their Way Out of FR2 Without Chip Data

Some merchants respond to FR2 by writing compelling rebuttal letters describing their physical security, their camera systems, or their staff training. This is not relevant to the FR2 determination. The liability shift is binary: chip read or not chip read. No amount of narrative explanation changes the authorization entry mode code. Save your effort for disputes where evidence quality can swing the outcome.

---

## Prevention: Achieving EMV Compliance

The permanent solution to FR2 liability is chip-capable terminal infrastructure. Action items:

1. **Audit all terminal hardware** — confirm each device has an EMV chip reader (card insertion slot, not just swipe slot)
2. **Confirm EMV software certification** — chip reading requires certified payment application software; contact your acquirer or terminal vendor to verify your terminals are certified
3. **Enable chip-first behavior** — configure terminals to prompt chip insertion rather than swipe; many terminals can be set to reject swipe on chip cards
4. **Monitor fallback rates** — if your terminals frequently fall back from chip to swipe (due to damaged chips or dirty readers), clean or replace them; high fallback rates trigger acquirer alerts
5. **For fuel merchants** — confirm your EMV upgrade was completed; fuel dispenser liability shift timelines differ from indoor POS and some extensions have now expired

---

## Frequently Asked Questions

**Q: My terminal has a chip reader but it was broken that day, so the customer swiped. Am I liable for FR2?**
A: Yes. The liability determination is based on the authorization entry mode, not on the reason why a particular mode was used. A broken chip reader that causes fallback to swipe creates FR2 liability. Keep backup terminals available and service chip readers promptly to avoid this scenario.

**Q: Can I fight FR2 if I can prove my store has cameras and we would have detected a counterfeit card?**
A: No. Camera footage and physical security evidence are not relevant to the EMV liability shift determination. The rule is objective: chip read = issuer liability; swipe on chip card = merchant liability. There is no subjective argument available.

**Q: What if I process Amex through OptBlue? Does FR2 work the same way?**
A: Yes. The FR2 dispute code and EMV liability shift rules are Amex network rules and apply regardless of whether you process through OptBlue or a direct Amex agreement. The dispute workflow may come through your acquirer, but the liability determination is the same.

**Q: The customer inserted their card but the chip failed to read after three attempts, so we swiped as fallback. Is this FR2 liability?**
A: Potentially yes. "Fallback" to magnetic stripe processing on a chip card is a known fraud vector. Amex (and other networks) have rules governing when fallback is permissible and when it still creates merchant liability. If fallback occurred legitimately (documented chip read failures), some acquirers can assist with a fallback dispute response — but success is not guaranteed. The better prevention is maintaining terminal hardware to minimize chip read failures.

**Q: How many FR2 chargebacks before Amex flags my account?**
A: Amex does not publish specific thresholds, but multiple FR2 chargebacks in a short period will attract attention from Amex's fraud risk team. A cluster of FR2 disputes in the same timeframe can also indicate a skimming incident at your location — inspect your terminal hardware immediately if you receive multiple counterfeit fraud disputes.
