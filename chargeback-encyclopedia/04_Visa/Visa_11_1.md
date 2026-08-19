---
title: "Visa 11.1 — Card Recovery Bulletin"
section: "04_Visa"
category: "Visa Reason Codes"
network: "Visa"
reason_code: "11.1"
document_type: "Reason Code Reference"
keywords: ["card recovery bulletin", "11.1", "hot card", "pick-up", "authorization", "CRB"]
difficulty: "Beginner"
---

# Visa 11.1 — Card Recovery Bulletin

## Definition

Visa reason code 11.1 applies when a merchant completed a transaction using a card that was listed on Visa's **Card Recovery Bulletin (CRB)** — a list of cards that have been reported as lost, stolen, compromised, or otherwise flagged for non-acceptance. By accepting a card on the bulletin, the merchant bypassed a critical fraud prevention check that was specifically designed to stop that card from being used.

The Card Recovery Bulletin is a legacy concept from the pre-digital era of payment processing, when merchants would receive printed lists of bad card numbers to check manually. In the modern era, the CRB function is primarily executed electronically — when a merchant submits an authorization request, the issuer automatically checks whether the card is flagged and declines if it is. In properly functioning modern payment systems, 11.1 chargebacks are extremely rare because the authorization system performs the CRB check automatically.

However, 11.1 chargebacks still appear in scenarios involving manual authorization, offline transactions, or system failures where the electronic CRB check was bypassed.

---

## History: What Was the Card Recovery Bulletin?

Before the internet and real-time authorization systems, card acceptance was a manual process. A cardholder would present their card, and the merchant would manually check a printed list — the Card Recovery Bulletin — published regularly by Visa, listing card numbers that should not be accepted. These were cards reported as stolen, over-limit, or compromised.

Merchants were contractually required to check the bulletin before completing transactions above certain floor limits. Failing to check, or accepting a card knowingly listed on the bulletin, transferred fraud liability to the merchant.

Today, this bulletin check is automated. When a merchant sends an authorization request to their acquirer and on to Visa and the issuer, the issuer's system instantly checks whether the card is in a non-acceptance status. If it is, the authorization is declined. In a properly functioning modern payment system, a card on the "hot list" never gets authorized in the first place.

---

## When 11.1 Chargebacks Still Occur

### Voice/Manual Authorizations
When a merchant calls for a voice authorization (e.g., due to terminal failure), the process relies on a phone call to an authorization center. If the authorization agent provides an approval code but the card is on the CRB (due to a processing delay or communication failure), the transaction may proceed and later result in an 11.1 chargeback.

### Offline Transactions
Some payment systems queue transactions for processing when connectivity is restored. If a card is flagged between the time of the offline transaction and when it is submitted for processing, the transaction may be declined or flagged post-hoc, and an 11.1 dispute may follow.

### Floor Limit Transactions
In environments with floor limits (where transactions below a certain amount can be completed without authorization), a flagged card might be used for a below-floor-limit purchase. The CRB check doesn't happen because no authorization was requested.

### Processing System Failures
In rare cases, system failures at the acquirer or processor level may cause authorization requests to route incorrectly, resulting in approvals for cards that should have been declined.

---

## Common Scenarios

- A merchant experiences an internet outage and processes several transactions in offline mode. By the time the batch is submitted, one of the cards has been reported stolen and is on the CRB. The card's issuer files an 11.1 chargeback.
- A small retailer with a manual imprinter and a floor limit processes a $40 sale without calling for authorization. The card was reported stolen the day before and listed on the CRB. The retailer receives an 11.1 chargeback.
- A hotel's POS system fails during a busy check-in period. Staff call for voice authorizations. Due to a communication issue, one authorization is approved despite the card being flagged. The hotel receives an 11.1 dispute.

---

## Merchant Liability

Merchants who accept a card listed on the Card Recovery Bulletin bear full liability for any resulting fraud. The rationale is simple: the network provided a mechanism to flag dangerous cards, the merchant bypassed it (intentionally or due to system failure), and the fraud occurred as a result.

In modern automated processing, accepting a CRB card is almost always a result of system failure, not merchant negligence. However, the liability still transfers to the merchant or, in some cases, to the processor whose system failed to reject the transaction.

**Merchants have essentially no defense** if the transaction involved a card that was genuinely on the CRB at the time of the transaction — except in cases where the CRB listing occurred after the transaction was completed (which would make the 11.1 filing invalid).

---

## Required Evidence

If you wish to dispute an 11.1 chargeback, the primary defense is demonstrating that the card was **not on the CRB at the time of the transaction** and was added only afterward. Evidence includes:

- **Transaction timestamp:** Precise time the transaction was completed.
- **Authorization record:** Confirmation that an authorization was obtained at the specific time of transaction.
- **CRB listing timestamp:** If obtainable from your processor or from Visa, the exact time the card was added to the CRB. If the CRB listing was added after your transaction timestamp, the chargeback is invalid.
- **Processor logs:** Records showing the authorization was submitted and approved in real time, prior to any CRB flag being placed.

In practice, obtaining a CRB timestamp is difficult for merchants — this data is held by Visa and issuers. Work with your acquirer to request this information as part of the dispute.

---

## Winning Strategy

1. **Verify the authorization timestamp.** If you obtained a valid authorization approval before the card was placed on the CRB, you have a legitimate defense.
2. **Request CRB timing data through your acquirer.** Your acquirer can request clarification from Visa on when the card was specifically flagged.
3. **If the chargeback resulted from your system's offline processing,** document the system outage, the time range of offline transactions, and when the batch was submitted. This establishes the context for any timing discrepancy.
4. **If it was a floor limit transaction** (no authorization obtained), the defense is very weak. Accept the chargeback and update your authorization practices to require authorization for all transactions regardless of amount.

---

## Losing Mistakes

- **Processing transactions without authorization.** Floor limit transactions processed without any authorization check have no defense against 11.1.
- **Using offline mode without understanding the fraud risk.** Offline transactions are a known risk for merchants — batch submission after a connectivity outage exposes you to cards that were flagged during the outage.
- **Not keeping precise transaction timestamps.** If you can't prove your transaction was completed before the CRB listing, you cannot make the timing defense.

---

## Prevention

- **Always require real-time authorization.** In modern payments, every transaction should route through the electronic authorization system. Disable or strictly limit offline mode where possible.
- **Minimize floor limits.** If your terminal allows floor limit transactions, set the floor limit to $0 — requiring authorization for all transactions.
- **Monitor authorization responses carefully.** Declined transactions are declined for a reason. Train staff never to force-complete a transaction after an authorization decline.
- **Voice authorization training:** If staff call for voice authorizations, ensure they understand that the approval code must be obtained before completing the sale, and that they record the code accurately.
- **System redundancy:** Ensure backup connectivity (cellular data backup) so that offline processing is a last resort of minutes rather than hours or days.

---

## Timeline

| Stage | Timeframe |
|---|---|
| Transaction processed | Day 0 |
| Card reported / added to CRB | Near Day 0 (may be before or after) |
| Issuer detects CRB breach | Upon transaction settlement |
| 11.1 chargeback filed | Within 120 days of transaction |
| Merchant response deadline | 30 days from chargeback notification |

---

## Frequently Asked Questions

**Q: I got an authorization approval. How can the card have been on the CRB?**
A: Normally, authorization approval means the card was not flagged at the time the request was submitted. If you received a genuine real-time authorization approval and are now receiving an 11.1 chargeback, this is potentially an error or a system timing issue. Work with your acquirer to request the CRB listing timestamp — your pre-authorization approval should protect you.

**Q: What is the "pick up" response code and how does it relate to 11.1?**
A: A "pick up" response code (response code 04) from an authorization means the card is flagged and the merchant should retain (confiscate) the card if it is physically presented. This is the live CRB check working as intended. If you receive a pick-up response, do not complete the transaction and, if safe to do so, retain the card and contact your acquirer.

**Q: Is 11.1 still relevant in the age of contactless and digital payments?**
A: As a practical matter, genuine 11.1 chargebacks are rare in modern payment environments because real-time authorization eliminates most CRB breaches automatically. The code remains active and relevant primarily for scenarios involving offline processing, voice authorization, and floor limit transactions.

**Q: Can I recover the goods if the transaction results in an 11.1 chargeback?**
A: If the transaction involved physical goods and you know the customer identity, you may have recourse through civil claims. However, if the card was fraudulently used by a thief, recovery is typically impossible. Your recourse is to accept the chargeback loss and strengthen your authorization systems.

**Q: My processor's system failed and approved a CRB card. Can I recover the loss from my processor?**
A: This depends on your merchant processing agreement and the specific circumstances. Processor liability for system failures varies. Document the failure thoroughly and consult your agreement — if the processor's system malfunction caused the CRB card to be approved, there may be a contractual remedy.

---

## Sample Rebuttal Points

For cases where authorization was obtained before the CRB listing:

- "The transaction in question was processed with a valid authorization approval obtained at [timestamp]. We request documentation of the exact time the card was added to the Card Recovery Bulletin to confirm our authorization predates the CRB listing."
- "Our authorization records (attached) confirm approval code [X] was obtained at [time], prior to any reported card compromise. A transaction authorized before a CRB listing was placed should not be subject to 11.1 dispute rules."
- "We respectfully request that the issuer provide the CRB listing timestamp for the card ending in [last 4]. If our authorization timestamp predates the listing, this chargeback should be reversed per Visa dispute rules."
