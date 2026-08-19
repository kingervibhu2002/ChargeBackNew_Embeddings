---
title: "Visa 10.3 — Other Fraud: Card-Present"
section: "04_Visa"
category: "Visa Reason Codes"
network: "Visa"
reason_code: "10.3"
document_type: "Reason Code Reference"
keywords: ["card-present fraud", "10.3", "imprint", "swipe", "counterfeit", "non-EMV", "signature comparison"]
difficulty: "Intermediate"
---

# Visa 10.3 — Other Fraud: Card-Present

## Definition

Visa reason code 10.3 covers fraudulent card-present transactions that do not fall within the specific EMV liability shift categories (10.1 and 10.2). This is the "catch-all" fraud code for in-person transactions where fraud occurred but the EMV shift mechanism isn't the primary dispute basis — typically because the transaction was processed via magnetic stripe swipe or manual imprint without chip involvement, and the circumstances don't neatly fit the counterfeit or lost/stolen card classifications of 10.1 and 10.2.

In practice, 10.3 applies when the cardholder claims they did not authorize a card-present transaction and the specific fraud category (counterfeit vs. lost/stolen) is either unclear or not the issuer's primary contention. It also encompasses older transaction types — manual imprints, knucklebuster transactions, and swiped transactions — that predate or bypass EMV infrastructure.

Understanding 10.3 requires grasping the hierarchy of Visa's fraud codes: 10.1 and 10.2 are the specific EMV liability shift codes. When fraud doesn't fit those specific EMV-shift criteria but was clearly card-present, 10.3 is the applicable code.

---

## What Transactions Does 10.3 Cover?

### Manual Imprint Transactions
Some merchants — particularly in low-connectivity environments, at markets, or during system outages — use mechanical card imprinters (sometimes called "knucklebusters") that physically press the embossed card number onto a paper slip. These transactions have no electronic authorization trace and rely entirely on the paper record. If fraud occurs in this context, 10.3 applies.

### Swiped Transactions at Non-EMV Terminals
When a card is swiped (not dipped) at a terminal that is not EMV-capable, and the fraud doesn't clearly align with 10.1's counterfeit focus, the issuer may file 10.3. This is more common for older retail terminals, independent merchant systems, or merchants in regions with incomplete EMV rollout.

### EMV Fallback Transactions
In some instances, if a chip card technically fails at an EMV terminal and falls back to magnetic stripe, but the issuer contends the fraud doesn't fit the EMV liability shift model (perhaps because the card is new or the circumstances are atypical), 10.3 may be filed instead of 10.1 or 10.2.

### Imprint Without Valid Authorization
Transactions where the merchant obtained a manual imprint but failed to get electronic authorization — or where the authorization was obtained fraudulently (e.g., using a stolen authorization code) — can result in 10.3 disputes.

---

## Common Scenarios

- A street market vendor uses a manual imprinter to capture card data during an event where connectivity is unavailable. Later, the cardholder disputes the charge claiming they never made the purchase. The vendor receives a 10.3 chargeback.
- A small restaurant swipes cards on an old magnetic stripe terminal and doesn't require ID. A fraudster uses a card they've stolen, and the cardholder disputes after the purchase. The restaurant receives 10.3.
- During a system outage, a hotel processes manual imprints. A fraudster uses a card and checks out before the imprint is verified. The dispute arrives as 10.3.
- A merchant's POS system has a bug that allows a chip card to be swiped without chip fallback documentation. The resulting transaction is processed as a swipe. Fraud occurs and is disputed under 10.3.

---

## The Signature Comparison Defense

Unlike 10.1 and 10.2 chargebacks where the chip read (or lack thereof) is the primary determinant, 10.3 disputes sometimes allow the merchant to use **signature comparison** as a defense — particularly for manual imprint transactions.

If the merchant has:
- A paper receipt or imprint slip with the customer's signature
- And the signature reasonably matches the signature on the back of the card (or a comparison sample)

...the merchant can argue that the cardholder was present and authorized the transaction. This is a weaker defense than chip authentication data but is sometimes effective in clear cases where the signature match is obvious and the transaction circumstances are well-documented.

**Important caveat:** Signature comparison is increasingly deprioritized as a fraud defense. Many issuers have abandoned signature verification as a cardholder authentication mechanism. If the cardholder firmly denies being present, a signature match rarely wins the chargeback outright — but it does contribute to a compelling evidence argument alongside other documentation.

---

## Merchant Liability

Merchants face significant liability exposure under 10.3 for any non-EMV-chip card-present transaction. The key liability factors:

- **Manual imprint without authorization:** High liability. The merchant cannot demonstrate any electronic authentication occurred.
- **Swipe-only transaction at legacy terminal:** High liability. Same as EMV shift logic — chip would have protected the merchant.
- **Swipe fallback at an EMV-capable terminal (undocumented):** High liability. Without documentation of the chip failure, it looks like a deliberate bypass.
- **Swipe fallback at an EMV-capable terminal (documented):** Moderate liability. Legitimate technical fallback may be defensible but is not guaranteed to win.

---

## Required Evidence

To mount a defense against a 10.3 chargeback, gather:

- **Original transaction receipt** with cardholder signature (if applicable).
- **Imprint slip** showing the card's embossed number and cardholder signature (for manual imprint transactions).
- **Authorization record** showing the authorization code obtained at time of sale.
- **Terminal logs** confirming the transaction type and entry mode.
- **Chip failure documentation** if the transaction was a fallback (some POS systems log this automatically).
- **ID verification records** if your staff checked customer identification (note: not a guaranteed defense, but adds weight).
- **CCTV footage** showing a person physically present at the terminal at the time of the transaction (useful to establish presence, though not conclusive for authorization).

---

## Winning Strategy

1. **Assess the transaction type.** Was it a chip read, a swipe, a fallback, or an imprint? Your defense options depend on this.

2. **For swipe/imprint transactions:** Gather everything — signed receipt, authorization code, any ID documentation, and any camera evidence. Build a narrative that the cardholder was physically present and authorized the transaction.

3. **Compare signatures.** If you have a signed receipt and the card itself bears a signature panel (or you photographed the card back), note the similarity in your rebuttal. Submit both images clearly labeled.

4. **Leverage authorization data.** Even for a swiped transaction, a clean authorization approval with matching address data or CVV2 confirmation can support your case. If authorization was approved and AVS matched, document this.

5. **Show the cardholder's history.** If this customer has made previous purchases at your location without dispute, that history of relationship can be cited (though it doesn't override fraud claims).

6. **Consider whether to fight.** 10.3 chargebacks on small transactions may not be worth the representment effort. Weigh the transaction amount against the time and fees of filing a response.

---

## Losing Mistakes

- **Failing to obtain authorization at the time of sale.** An imprint without a valid authorization code is indefensible.
- **Not keeping signed receipts.** Paper records are your primary defense for imprint and swipe transactions. A missing receipt is a missing defense.
- **Claiming the customer was "obviously present" without documentation.** Verbal arguments without evidence don't survive review.
- **Filing a representment without a signed receipt.** If you claim the transaction was authorized, you need the authorization artifact — verbal descriptions won't suffice.
- **Swiping chip cards without documenting the reason.** If a chip card was swiped at your terminal, document why at the time of the transaction.

---

## Prevention

- **Upgrade to EMV.** The most effective prevention against all 10.x chargebacks is operating chip-capable terminals that require chip reads. This eliminates most 10.3 exposure.
- **Require authorization for all transactions.** Even for manual imprint transactions, always obtain a valid voice authorization code before completing the sale.
- **Train staff on signature verification.** While not foolproof, staff who compare signatures catch obvious discrepancies.
- **Keep all signed receipts.** Store paper transaction records for at least 18 months in a retrievable format.
- **Install CCTV at checkout.** Camera coverage of the payment terminal provides supporting evidence if disputes arise.
- **Implement transaction velocity checks.** Multiple high-value transactions in quick succession from the same card at the same terminal is a fraud indicator.

---

## Timeline

| Stage | Timeframe |
|---|---|
| Transaction processed | Day 0 |
| Cardholder discovers fraud | Days to months later |
| Dispute filed with issuer | Within 120 days of transaction |
| Chargeback received by merchant | Within 30 days of issuer filing |
| Merchant response deadline | 30 days from chargeback notification |
| Pre-arbitration escalation | If merchant response rejected |

---

## Frequently Asked Questions

**Q: How is 10.3 different from 10.1 and 10.2?**
A: 10.1 covers counterfeit fraud at non-chip terminals (cloned card used). 10.2 covers lost/stolen card fraud at non-chip terminals (genuine card in thief's hands). 10.3 is the broader fraud code for card-present fraud that doesn't fit those specific EMV liability shift scenarios — typically manual imprint transactions, older swipe-only scenarios, or fraud circumstances where the EMV shift isn't the central issue.

**Q: Can I win a 10.3 chargeback with just a signed receipt?**
A: Possibly, but it's a weaker defense. A signed receipt shows someone was present and signed, but if the cardholder firmly denies the transaction and there are no other supporting details (authorization code, matching address, prior relationship), the issuer may side with the cardholder. A signed receipt is better than nothing but not a guaranteed win.

**Q: My customer paid with a chip card but we accidentally swiped it. Is this a 10.3 chargeback?**
A: It could be filed as 10.1 or 10.3 depending on the issuer's characterization of the fraud. Either way, the defense (or lack thereof) is similar — you need chip read evidence to avoid liability, and a swipe of a chip card generally results in merchant liability.

**Q: Does filing a police report help with a 10.3 chargeback?**
A: Generally not for chargeback purposes. Police reports document criminal activity but don't resolve the dispute liability question. However, if fraud was clearly at your location and you cooperated with law enforcement, it may demonstrate good faith. The chargeback decision is based on Visa rules, not police reports.

**Q: Are manual imprint transactions still legal?**
A: Yes, manual imprint transactions are still permitted under card network rules, though they are rare and carry high fraud liability. They're primarily used as a last resort in no-connectivity situations. Always obtain a voice authorization code alongside any imprint transaction.

---

## Sample Rebuttal Points

For transactions with signed receipts and authorization codes:

- "The disputed transaction was completed as a card-present sale. The attached signed receipt (dated [date]) reflects the cardholder's signature at point of sale, and the authorization code [code] confirms electronic approval was obtained."
- "We obtained authorization code [X] at the time of transaction through our payment processor. The authorization was approved, indicating no fraud alert was present on the card at the time of sale."
- "The attached signed receipt shows the cardholder's signature. The signature on the receipt appears consistent with card records. We respectfully submit this evidence demonstrates the cardholder was physically present and authorized this transaction."
- "Our terminal records, attached herein, confirm this transaction was completed at [terminal ID] at [time]. The authorization data reflects card acceptance. We request this chargeback be reversed based on the evidence of cardholder authorization."
