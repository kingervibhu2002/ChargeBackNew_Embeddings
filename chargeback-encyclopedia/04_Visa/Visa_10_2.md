---
title: "Visa 10.2 — EMV Liability Shift: Non-Counterfeit Fraud"
section: "04_Visa"
category: "Visa Reason Codes"
network: "Visa"
reason_code: "10.2"
document_type: "Reason Code Reference"
keywords: ["EMV", "lost card", "stolen card", "non-counterfeit fraud", "liability shift", "10.2", "PIN", "signature"]
difficulty: "Intermediate"
---

# Visa 10.2 — EMV Liability Shift: Non-Counterfeit Fraud

## Definition

Visa reason code 10.2 covers EMV liability shift disputes involving non-counterfeit fraud — specifically, transactions made with a **lost, stolen, or never-received** genuine card (not a counterfeit) at a terminal that did not use chip technology to authenticate the transaction.

The key distinction between 10.1 and 10.2 is the card itself: in 10.1, the card presented was a counterfeit (cloned copy). In 10.2, the physical card presented was the real, authentic card — but it was in the hands of someone who stole or found it. Because the genuine card was used, magnetic stripe skimming is not the root cause. Instead, the fraud opportunity arose because the physical card was lost or stolen and the merchant failed to use chip authentication that might have been paired with a PIN requirement to verify the legitimate cardholder.

In regions where chip-and-PIN is standard (most of Europe and Asia), a lost or stolen card has much lower fraud value because the thief also needs the cardholder's PIN to complete a transaction. In chip-and-signature environments (common in the U.S.), the liability shift logic for 10.2 still applies, but the defense arguments differ slightly because signature alone is less conclusive proof of cardholder identity.

---

## How Non-Counterfeit Fraud Occurs

A cardholder loses their wallet or has their purse stolen. The thief now has the physical card. At a non-chip terminal (or a chip terminal where the clerk allows a swipe fallback), the thief presents the card and completes the purchase — no PIN required, and the forged or skipped signature goes unchallenged. The cardholder later notices the fraudulent charge and disputes it.

Unlike counterfeit fraud, there is no cloning involved — the card that swiped at the terminal was the cardholder's actual card. But if the terminal had required a chip read plus PIN, the thief would have been unable to complete the transaction. This is the policy rationale for shifting liability to the non-chip terminal operator.

**Common real-world scenarios:**
- A pickpocket steals a wallet. The thief uses the card at a non-EMV terminal at a retail store within hours of the theft, before the cardholder notices.
- A card is left behind at a restaurant. A dishonest employee uses it at a swipe-only terminal before returning the card or the cardholder notices.
- A card is found in a parking lot. The finder uses it at a gas pump that hasn't been upgraded to EMV.

---

## PIN vs. Signature: The Liability Nuance

In chip-and-PIN environments, if a merchant's terminal supports chip but only processes chip-and-signature (not chip-and-PIN), there is a debate about whether full liability shift protections apply. Visa's rules are nuanced here:

- **Chip-and-signature terminals:** Generally protected from 10.1 (counterfeit) liability. For 10.2, protection exists but may be challenged if the issuer argues PIN was required and not enforced.
- **Chip-and-PIN terminals:** Maximum protection for both 10.1 and 10.2, because successful PIN verification is the strongest evidence that the cardholder was present.
- **Magnetic stripe only:** Full liability exposure for both 10.1 and 10.2.

In the U.S., most EMV implementation is chip-and-signature for debit and credit. For signature debit transactions, the liability shift generally protects chip-capable merchants. For PIN debit specifically, if the transaction bypassed PIN and was processed as signature, liability may shift back to the merchant.

---

## Common Scenarios

- **Retail store with legacy POS:** A department store running old point-of-sale software processes a swiped transaction. A thief uses a stolen card. The merchant receives a 10.2 chargeback.
- **Chip terminal with swipe fallback enabled:** A terminal shows as EMV-capable in settings, but the chip reader is physically damaged and defaults to swipe. A lost card is used. The authorization data shows a fallback swipe — the merchant loses the 10.2 chargeback.
- **Staff-assisted swipe bypass:** A customer (actually a thief) claims the chip "doesn't work" and a well-meaning employee swipes the card manually. This is a fallback transaction and creates liability.

---

## Merchant Liability

As with 10.1, liability under 10.2 is determined primarily by the transaction entry mode in the authorization data:

- **Chip read confirmed (entry mode 05/07):** Merchant is protected. Liability stays with the issuer.
- **Magnetic stripe read or fallback (entry mode 90/80):** Liability shifts to merchant. The chargeback will almost certainly stand.

An additional nuance: if the transaction was a PIN debit transaction and PIN was bypassed, the merchant may face liability even if a chip reader was technically used, depending on acquirer agreement terms and Visa's specific rules at the time of the transaction.

---

## Required Evidence

**To dispute a 10.2 chargeback:**
- Authorization records showing EMV chip read entry mode (05 or 07).
- Terminal capability documentation (EMV certification).
- Any transaction logs confirming chip authentication completed.
- If applicable: documentation showing PIN was captured (for PIN debit transactions).

**Evidence that will not help:**
- Signed receipts (signature comparison does not override the liability shift rule).
- Security camera footage showing a person with the card (the card was genuine; the issue is authentication method, not identity).
- Cardholder ID check records (unless you can prove the ID matched a PIN-verified transaction).

---

## Winning Strategy

1. **Confirm the authorization entry mode immediately.** Pull your processor's transaction detail for the disputed transaction. If it shows chip read, you have a strong defense.
2. **Submit chip authentication evidence alongside the terminal certification.** Make the argument clearly: "The chip was read. The liability shift does not apply."
3. **If it was a PIN debit transaction,** confirm whether PIN was captured. Contact your processor for the PIN capture record.
4. **Write a concise rebuttal letter.** State the entry mode, attach the authorization record and terminal documentation, and cite the Visa rule that protects EMV chip transactions from 10.2 liability.

---

## When You Have No Defense

If the authorization record shows a swipe (entry mode 90 or 80), accept the chargeback. Do not fight it with:
- Signed receipts
- Transaction amount confirmation
- Verbal claims that the chip reader was working that day

None of these override the authorization data. Fighting unwinnable 10.2 chargebacks wastes representment fees and may increase your chargeback ratio, compounding the problem.

---

## Losing Mistakes

- **Submitting only the customer's signed receipt.** Irrelevant to the liability shift determination.
- **Claiming the terminal is EMV-capable without producing authorization data.** A capable terminal that wasn't used for chip reading provides no protection.
- **Confusing 10.2 with 10.1.** The defense strategy is the same, but understanding whether you're dealing with a cloned card or a stolen genuine card matters for your fraud prevention analysis.
- **Missing the response window.** Thirty days from notification. No exceptions.

---

## Prevention

- Ensure all terminals actively require chip insertion — disable magnetic stripe as the default where possible.
- Train staff never to bypass chip reading without a documented technical failure reason.
- For high-risk environments (unattended kiosks, outdoor terminals), implement PIN as a secondary authentication factor.
- Enable terminal monitoring to alert when a terminal falls into swipe-only mode due to hardware failure.
- Review your payment processor's fallback transaction reports regularly. Spikes in fallback transactions signal terminal problems creating liability exposure.

---

## Timeline

| Stage | Timeframe |
|---|---|
| Transaction date | Day 0 |
| Card reported lost/stolen | Varies — may be same day or weeks later |
| Dispute filed by cardholder | Within 120 days of transaction |
| Merchant response deadline | 30 days from chargeback notification |
| Pre-arbitration (if escalated) | 30 days from merchant response |

---

## Frequently Asked Questions

**Q: The customer signed the receipt. Doesn't that prove they were authorized?**
A: Not for liability shift purposes. The signature demonstrates the person had the card, but in a lost/stolen scenario the thief also has the card. The EMV chip plus PIN (or chip authentication) is the mechanism Visa relies on to verify the genuine cardholder. A signature alone is insufficient.

**Q: Our terminal has a chip reader, but the card in question was swiped because the chip didn't work. Are we still liable?**
A: Very likely yes. Magnetic stripe fallback transactions retain liability exposure even at EMV-capable terminals unless the chip failure was documented and the transaction was processed under legitimate fallback protocols. Some processors record fallback reason codes; check your transaction detail.

**Q: Can we dispute a 10.2 chargeback if the thief was caught and the transaction is documented in a police report?**
A: A police report showing the thief was caught may help in extraordinary circumstances, but it does not override the EMV liability shift rule under Visa's framework. The liability shift is a processing compliance rule, not a law enforcement outcome rule.

**Q: Is there a minimum transaction amount below which 10.2 doesn't apply?**
A: No. The liability shift applies regardless of transaction amount. Even a $5 transaction processed via swipe on a lost card can generate a 10.2 chargeback.

**Q: We're a B2B merchant and don't deal with individual consumers. Can we still get 10.2 chargebacks?**
A: Yes, if you process card-present transactions with business cardholders. Corporate card fraud does occur. The same EMV liability shift rules apply regardless of card type.

---

## Sample Rebuttal Points

Use these when your authorization data confirms a chip read:

- "The disputed transaction was processed as an EMV chip read transaction (entry mode 05, attached authorization record). The chip authentication process was completed successfully at time of sale."
- "Our terminal is EMV-certified, as documented in the attached terminal certification. The chip read entry mode in the authorization data confirms that chip authentication — not magnetic stripe — was used to process this transaction."
- "Under Visa's EMV liability shift policy, when a transaction is processed as a chip read at an EMV-capable terminal, liability for non-counterfeit fraud remains with the card issuer. We respectfully request this chargeback be reversed."
- "We have attached [processor name] transaction records, terminal certification, and the full authorization log for the transaction in question. All records confirm chip processing was completed."
