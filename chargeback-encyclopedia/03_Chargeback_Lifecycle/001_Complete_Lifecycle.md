---
title: "The Complete Chargeback Lifecycle: End-to-End Guide"
section: "03_Chargeback_Lifecycle"
category: "Chargeback Lifecycle"
document_type: "Reference"
keywords: ["chargeback lifecycle", "chargeback process", "chargeback stages", "representment", "pre-arbitration", "arbitration", "chargeback timeline", "dispute process", "what happens in a chargeback"]
difficulty: "Beginner"
---

# The Complete Chargeback Lifecycle: End-to-End Guide

A chargeback involves at minimum four parties — the cardholder, the issuing bank, the card network, and the merchant's acquiring bank — and can pass through up to seven distinct stages from the original sale to final resolution. Most merchants see only one piece of this process: the notification. Understanding the full lifecycle helps you respond strategically at each stage, meet every deadline, and know when a dispute is truly over.

## Stage 1: The Sale

**Who acts:** Merchant and cardholder  
**Timeline:** Day 0

The transaction begins when a customer presents card credentials (physically, online, or by phone) and the merchant initiates a payment request. At this moment, the data elements that will define the entire dispute — card number, device, IP address, billing address, AVS/CVV match results — are captured or not captured. Merchants who fail to capture this data at point of sale have no foundation for compelling evidence if a dispute later arrives.

**What the merchant must do:**
- Capture and retain all authorization data
- Collect device fingerprint and IP address for card-not-present transactions
- Display clear terms of service, refund policy, and product descriptions
- Ensure 3DS authentication is triggered where applicable

## Stage 2: Authorization

**Who acts:** Merchant's acquirer, card network, issuing bank  
**Timeline:** Seconds after transaction initiation

The acquirer sends the transaction request through the card network (Visa, Mastercard, etc.) to the issuer. The issuer approves or declines based on available credit, fraud scoring, and card status. An authorization approval code is returned.

**Important:** Authorization approval does not prevent chargebacks. The issuer's approval at this stage is a real-time risk assessment, not a waiver of the cardholder's right to dispute.

## Stage 3: Settlement

**Who acts:** Merchant, acquirer, card network, issuer  
**Timeline:** Day 0–2

The merchant submits the authorized transaction for settlement (usually through end-of-day batch processing). Funds are transferred from the issuer through the network to the acquirer, who deposits them into the merchant's account net of fees.

**What the merchant must do:**
- Settle promptly (delays between authorization and settlement can itself be grounds for a chargeback under some codes)
- Retain settlement batch records

## Stage 4: Customer Complaint

**Who acts:** Cardholder and issuing bank  
**Timeline:** Day 1 through Day 60–120 (cardholder dispute window)

The cardholder contacts their bank claiming a problem with a transaction. Common triggers: item not received, item not as described, unrecognized charge, cancelled subscription still billed, or unauthorized transaction (fraud). In some cases, the cardholder never contacts the merchant first — they go directly to their bank.

The issuing bank conducts a brief review. If the complaint qualifies under network dispute rules, the bank proceeds to file a formal chargeback. Many issuers now file chargebacks within 24–48 hours of a cardholder complaint, giving merchants no opportunity to resolve the issue directly before a dispute is opened.

**What the merchant must do:**
- Maintain accessible customer service so cardholders can reach you before filing with their bank
- Issue refunds proactively for clear-cut cases to prevent the chargeback from being filed

## Stage 5: Issuer Investigation and Chargeback Filed

**Who acts:** Issuing bank  
**Timeline:** Day 1–120 from original transaction

The issuer assigns a chargeback reason code and debits the disputed amount from the acquiring bank. The funds are provisionally returned to the cardholder. This is when the chargeback officially enters the merchant's world.

The chargeback notification is transmitted through the card network to your acquirer, who then notifies you — typically within 2–5 business days of the issuer filing.

## Stage 6: Merchant Notification

**Who acts:** Acquirer, merchant  
**Timeline:** Within 2–5 business days of issuer filing

Your acquirer sends you a chargeback notice containing:
- The chargeback reason code
- The original transaction details (date, amount, last four digits)
- The cardholder's stated reason for the dispute
- Your response deadline

**This is the moment your clock starts ticking.** Response windows are typically 20–30 days from the date of the notice — not from the date you read it. A chargeback notice that sits unopened in a shared email inbox for 10 days has cost you nearly half your response window.

**What the merchant must do:**
- Acknowledge receipt immediately
- Retrieve the original transaction data, including all authentication and fulfillment records
- Decide whether to fight (representment) or accept (absorb the loss)

## Stage 7: Merchant Decision — Fight or Accept

**Who acts:** Merchant  
**Timeline:** Within the response window (typically 20–30 days)

This is the strategic decision point. Evaluate:
- Is the claim legitimate? (If yes, accept and improve processes)
- Do you have compelling evidence to counter the claim?
- Is the transaction amount large enough to justify the cost of fighting?
- Is this a repeat abuser?

Accepting the chargeback means no action — the funds remain with the cardholder. Fighting means preparing and submitting a representment package.

## Stage 8: Representment (Second Presentment)

**Who acts:** Merchant, acquirer  
**Timeline:** Within merchant response window (typically 20–30 days from notification)

The merchant submits a representment — a formal re-presentation of the original transaction accompanied by a rebuttal letter and supporting evidence. This is submitted through your acquirer's portal or directly to the acquirer's disputes team, who packages and submits it to the card network and issuer.

Your representment contains:
- A rebuttal letter structured around the specific reason code
- All relevant evidence (labeled as exhibits)
- A clear statement of what you are claiming (the transaction was authorized, goods were delivered, etc.)

**Timeline from this point:** The issuer has 30–45 days to review and respond.

## Stage 9: Issuer Review and Decision

**Who acts:** Issuing bank  
**Timeline:** 30–45 days after merchant's representment submission

The issuer reviews your evidence and decides one of three things:
1. **Accept the representment:** The chargeback is reversed. Funds are returned to your account. Case closed.
2. **File pre-arbitration:** The issuer re-asserts the dispute (see Stage 10).
3. **No response:** Issuer silence past their deadline typically means the representment is accepted.

## Stage 10: Pre-Arbitration (Second Chargeback)

**Who acts:** Issuing bank  
**Timeline:** Within 30–45 days of your representment

If the issuer files pre-arbitration, you receive another notice from your acquirer. Your options are now:
- **Accept the loss:** Funds are permanently debited; case closed.
- **Escalate to arbitration:** Pay the arbitration filing fee and submit the case to the card network for a binding decision.

This is typically the last practical decision point for most merchants. Arbitration fees ($250–$500+) and the risk that the loser pays make escalating a significant financial commitment.

## Stage 11: Arbitration

**Who acts:** Card network (Visa or Mastercard)  
**Timeline:** 45–90 days from arbitration filing

The card network reviews all documentation from both sides and issues a binding ruling. There is no further appeal within the network system. The losing party pays all arbitration fees plus the disputed amount.

Merchant win rates at arbitration are lower than at representment (approximately 30–45%). Arbitration is appropriate only for high-value cases with very strong evidence.

## Stage 12: Compliance Filing (Alternative Path)

**Who acts:** Merchant or issuer  
**Timeline:** Parallel track to arbitration

If the dispute involves a procedural rule violation (wrong reason code, missed deadline, improper filing), the aggrieved party can file a compliance case rather than standard arbitration. Compliance cases are resolved faster and with lower fees but are limited to procedural violations, not substantive dispute merits.

## Stage 13: Write-Off

**Who acts:** Merchant  
**Timeline:** Final resolution

If arbitration is lost or all deadlines are missed, the chargeback amount is permanently debited from your account. At this stage, the loss is recorded in your accounting as a chargeback write-off. Review what went wrong in your processes to prevent recurrence.

---

## Frequently Asked Questions

**Q: How long can a chargeback process take from start to finish?**
A: A straightforward chargeback where the merchant accepts without fighting can resolve in 30–60 days. A disputed case that goes through representment, pre-arb, and arbitration can take 6–9 months from the original transaction date to final resolution.

**Q: At what stage does my chargeback ratio get affected?**
A: Your chargeback ratio is affected the moment the issuer files the chargeback (Stage 5). Fighting the dispute and winning does not remove the chargeback from your ratio count — it only recovers the funds. The count remains regardless of outcome.

**Q: Can I contact the cardholder directly to resolve a chargeback?**
A: Once a chargeback is filed, direct contact with the cardholder is generally not appropriate and does not change the formal dispute process. If the cardholder contacts you voluntarily and agrees to withdraw the dispute, they must do so through their issuer. Do not offer additional refunds or credit as part of this process without legal guidance, as it can create complications.

**Q: What happens if my acquirer goes out of business while a dispute is in progress?**
A: Card network dispute rights follow the transaction, not the acquirer. If your acquirer fails, their portfolio is typically acquired by another processor who inherits the dispute obligations. Contact the card network directly if your acquirer becomes unresponsive.

**Q: Is there any stage after arbitration where I can appeal?**
A: Card network arbitration decisions are final within the network system. A merchant may potentially pursue legal action against the cardholder outside the network system, but this is costly, rarely practical for consumer transactions, and should only be considered for high-value commercial disputes with strong fraud evidence.
