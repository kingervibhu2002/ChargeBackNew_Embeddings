---
title: "Compliance Filing: Challenging Procedurally Improper Chargebacks"
section: "03_Chargeback_Lifecycle"
category: "Chargeback Lifecycle"
document_type: "Reference"
keywords: ["compliance filing", "chargeback compliance", "Visa compliance", "Mastercard compliance", "procedural violation chargeback", "invalid chargeback", "wrong reason code chargeback", "compliance vs arbitration", "network rule violation"]
difficulty: "Advanced"
---

# Compliance Filing: Challenging Procedurally Improper Chargebacks

Most merchants know about representment and arbitration. Very few know about compliance filing — a separate dispute track that challenges not the merits of the transaction but the procedural validity of the chargeback itself. When an issuer violates card network rules in the process of filing or processing a chargeback, compliance is the tool that holds them accountable. Used correctly, it can recover funds faster and at lower cost than standard arbitration.

## What Is a Compliance Filing?

A compliance case is a formal challenge submitted to the card network alleging that the opposing party — almost always the issuing bank — violated a specific card network rule in the course of a chargeback dispute.

**Compliance is fundamentally different from standard arbitration:**

| Aspect | Arbitration | Compliance |
|---|---|---|
| What is challenged | The merits of the dispute (who is right on the facts) | The procedure (did the issuer follow network rules) |
| Basis for filing | Disputed evidence | Specific network rule violation |
| Cost | $250–$500+ per case | Varies by network; often $200–$400 |
| Applicable when | After pre-arb, on any dispute | Issuer violated rules at any stage |
| Outcome basis | Network weighs all evidence | Network applies rule violation test |

The compliance track exists because card network rules are detailed and precise. Issuers who do not follow them — either through error or opportunism — should not benefit from their own procedural violations.

## When to File Compliance

Compliance is appropriate when an issuer has committed a clear, documented violation of card network rules. Common violations that support compliance filings include:

### Invalid Chargeback Filing
The issuer filed a chargeback that does not meet the requirements for the reason code used. Each chargeback reason code has specific conditions that must be met before an issuer is permitted to file. For example:
- Filing a "not received" chargeback when the cardholder never contacted the merchant (required under some codes)
- Filing a fraud chargeback on a 3DS-authenticated transaction (liability shifted to issuer; chargeback is procedurally improper)
- Filing a chargeback more than 120 days after the original transaction (beyond the cardholder dispute window)

### Incorrect Reason Code
The issuer assigned a reason code that does not match the cardholder's stated complaint. This matters because the reason code determines your evidence requirements. If the issuer uses a fraud reason code when the actual complaint is "not as described," you prepared and submitted evidence for the wrong dispute — and the compliance process can address this.

### Missed Issuer Deadline
The issuer failed to act within their own required timeframes. If the issuer's response to your representment is filed after the network's allowed window, their continued assertion of the chargeback is a procedural violation.

### Re-Filing a Previously Resolved Dispute
If a chargeback was resolved in your favor and the issuer re-files the same dispute on the same transaction, this is a prohibited duplicate chargeback and grounds for compliance action.

### Chargeback on a Refunded Transaction
If you issued a full refund and the issuer subsequently files a chargeback on the same transaction, the chargeback is procedurally improper. The refund resolved the transaction.

### Pre-Arb Filed After Merchant's Representment Was Untimely — But Issuer Missed Their Own Deadline
Both sides have deadlines. When the issuer misses theirs at any stage, compliance can apply.

## Compliance Fees

Filing a compliance case incurs fees, which vary by network:

**Visa Compliance:**
- Filing fee: typically $200–$500 per case
- Loser-pays: If the network finds no violation, the merchant bears the fee. If the violation is upheld, the issuer bears the fee.

**Mastercard Compliance:**
- Similar fee structure: $200–$400 per case
- Outcome-dependent allocation

Unlike arbitration, compliance fees are lower because the review is narrower — the network is checking rule compliance, not weighing complex factual evidence.

## Visa vs. Mastercard Compliance Process

### Visa Compliance Process

Visa's compliance process is governed by the Visa Core Rules and Visa Product and Service Rules. To file compliance, the merchant (through the acquirer) must:

1. Identify the specific Visa rule that was violated, citing the exact rule number and provision
2. Submit documentation proving the violation (e.g., timestamps showing the issuer's late filing, authentication data showing 3DS liability shift)
3. Pay the compliance filing fee
4. Submit through the acquirer within the applicable compliance filing window (typically 10–45 days from the date the violation occurred or was discoverable)

Visa's compliance team reviews the case against the cited rule and issues a determination. If the violation is upheld, funds are recovered from the issuer and fees may be assessed against them.

### Mastercard Compliance Process

Mastercard's compliance process operates similarly. Compliance cases are filed through the acquirer referencing the specific Mastercard rule violated. Mastercard has explicit process timelines:

1. Compliance case submitted within 45 days of the rule violation
2. Mastercard review conducted by the Global Dispute Resolution team
3. Decision issued typically within 30–60 days
4. Funds and fees allocated per the ruling

**Important Mastercard nuance:** Mastercard distinguishes between "first-level compliance" (initial filing) and "second-level compliance" (appeal of a first-level decision). Second-level compliance carries additional fees and is reserved for cases where the first-level decision itself is believed to violate rules.

## When Merchants Use Compliance as a Strategic Tool

### Protecting 3DS-Authenticated Transactions
This is the most valuable compliance use case. If you have 3DS2 authentication data (ECI 05 for Visa, ECI 02 for Mastercard) and the issuer files a fraud chargeback, the chargeback violates the network's liability shift rules. Filing compliance — not standard arbitration — is often the correct response because the violation is clear and procedural, not factual.

### Recovering from Duplicate Chargebacks
If the same transaction is charged back twice — which occasionally happens through issuer error — the second chargeback is a network rule violation. Compliance resolves this faster than arbitration because there is no factual dispute; the timeline proves the duplicate filing.

### Correcting Expired Dispute Windows
Cardholders generally have 60–120 days from the transaction date (depending on the network and reason code) to file a chargeback. Issuers who file beyond this window are violating network rules. Document the original transaction date and the chargeback receipt date and file compliance.

### Addressing Refund Chargebacks
If you issued a full refund and a chargeback was subsequently filed on the same transaction, compliance resolves this conclusively — you have refund transaction proof and the chargeback is per-se improper.

## Outcomes of Compliance Filings

**Merchant wins:** The network upholds the rule violation. The issuer is required to reverse the chargeback. Funds are credited to the merchant. The issuer may be assessed the compliance fees.

**Merchant loses:** The network finds no clear rule violation (or the merchant's evidence of the violation is insufficient). The merchant bears the compliance filing fee. The underlying chargeback stands.

**Settlement:** Some compliance cases result in settlement where the issuer acknowledges the procedural error and reverses the chargeback without the network issuing a formal ruling.

## Compliance vs. Arbitration: Choosing the Right Track

If you are uncertain whether your situation calls for compliance or arbitration, apply this test:

- **Is the dispute about the facts (did the cardholder receive the goods, was the transaction authorized)?** → Arbitration
- **Is the dispute about whether the issuer followed the rules (wrong code, late filing, invalid chargeback on authenticated transaction)?** → Compliance

In some cases, both tracks are applicable — for example, an issuer who files a late chargeback on an unauthenticated disputed transaction. Here, compliance is typically the faster and cheaper first step. If compliance fails or does not fully resolve the dispute, arbitration remains available.

---

## Frequently Asked Questions

**Q: Can I file compliance at the same time as representment?**
A: Generally, no. Compliance is filed when a specific rule violation has occurred and can be documented. If the violation occurs at the time the chargeback is filed (wrong reason code, expired window), compliance can be filed in parallel with or instead of representment. Consult your acquirer on whether you should pursue compliance first, representment first, or both.

**Q: My issuer filed a chargeback on a transaction that was 3DS authenticated. Should I file compliance or representment?**
A: File compliance. The authentication data proves that liability shifted to the issuer under network rules. The chargeback is procedurally improper. Representment treats the dispute as legitimate and requires you to argue the facts; compliance challenges the chargeback's right to exist.

**Q: How do I know which specific Visa or Mastercard rule was violated?**
A: You need access to the applicable network rules documentation. Ask your acquirer's disputes team — most have compliance specialists who can identify the applicable rule citation. If you manage disputes in-house, Visa's core rules and Mastercard's transaction processing rules are available to registered members and their service providers.

**Q: Is there a time limit on filing compliance?**
A: Yes. Both Visa and Mastercard impose filing windows — typically 10–45 days from the date you knew or should have known of the violation. Missing the compliance filing window eliminates this option, leaving only standard arbitration.

**Q: Can the issuer file compliance against me?**
A: Yes. If the merchant's representment violates network rules (e.g., submitted evidence is fabricated or the representment is filed after deadline), the issuer can file compliance against the merchant. Compliance is a two-way tool, which is another reason why procedural compliance in your own representment submissions is critical.
