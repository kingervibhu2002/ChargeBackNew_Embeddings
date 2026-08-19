---
title: "Representment Guide: How to Build and Submit a Winning Chargeback Dispute"
section: "03_Chargeback_Lifecycle"
category: "Chargeback Lifecycle"
document_type: "Reference"
keywords: ["representment", "chargeback representment", "rebuttal letter", "chargeback evidence submission", "second presentment", "dispute evidence", "chargeback response", "exhibit labeling", "acquirer portal"]
difficulty: "Beginner"
---

# Representment Guide: How to Build and Submit a Winning Chargeback Dispute

Representment is the formal process by which you re-present a disputed transaction to the card network and issuer, accompanied by evidence and a written argument. It is your primary tool for recovering chargeback funds. A well-constructed representment package does not just submit documents — it tells a coherent story, anticipates the issuer's objections, and makes it easy for an overworked bank analyst to rule in your favor. A poor representment — even one backed by valid evidence — loses because the argument is unclear or the documents are disorganized.

## What Is Representment?

Representment literally means re-presenting the original transaction. When an issuer files a chargeback, they are saying: this transaction should not have been charged. Your representment says: here is why it should have been, and here is the proof.

Technically, you are asking your acquirer to re-present the transaction to the card network with documentation establishing that the chargeback was improper. The network routes your submission to the issuer, who reviews it and decides whether to accept your position or maintain the dispute.

Representment is not a negotiation — it is a formal evidentiary submission. There is no back-and-forth dialogue with the issuer. You submit once; they decide. This is why preparation and completeness matter so much.

## How to Submit: Through Your Acquirer

You do not submit representments directly to card networks or issuing banks. All submissions go through your **acquirer or payment processor**, who then packages and forwards your response through the appropriate network channels.

Most acquirers provide one of the following submission methods:

### Acquirer/Processor Web Portal
The most common method. Log in to your acquirer's merchant portal, locate the chargeback in the disputes dashboard, upload your documents, and submit your response before the deadline. Most major processors (Stripe, Adyen, Braintree, Chase Paymentech, etc.) offer this functionality.

### Acquirer Email Submission
Smaller acquirers may require you to email your complete evidence package to a disputes mailbox. Confirm receipt and follow up if you do not receive an acknowledgment.

### Third-Party Disputes Platform
If you use a chargeback management platform (Chargebacks911, Midigator, Kount, etc.), submissions typically route through that platform's integration with your acquirer.

**Critical:** Confirm with your acquirer which file formats are accepted (PDF is universally supported), maximum file size limits, and whether each piece of evidence should be a single combined PDF or separate files. Submission format errors can delay your response or cause rejection.

## Rebuttal Letter Structure

The rebuttal letter is the core of your representment. Evidence without argument leaves the issuer analyst to draw their own conclusions. The letter interprets the evidence and directly addresses the specific reason code.

### Section 1: Opening Statement

State clearly what you are claiming and summarize your position in two to three sentences.

*Example:* "We are disputing this chargeback because the customer's order was delivered to the address on file on [date], as confirmed by signed carrier delivery confirmation (Exhibit A). The transaction was authenticated via 3-D Secure (Exhibit B), and the customer's account history shows three prior undisputed purchases (Exhibit C), demonstrating a legitimate ongoing relationship."

### Section 2: Transaction Summary

Provide a factual recap of the transaction:
- Order date and time
- Items or services purchased
- Amount charged
- Shipping address (for physical goods) or delivery method (for digital goods/services)
- Payment method and card last four digits

This section is not argument — it is orientation. Give the reviewer the facts before the evidence.

### Section 3: Evidence Presentation

Walk through each piece of evidence, reference it by exhibit label, and explain what it proves in relation to the specific chargeback claim.

Do not just list the evidence — explain its significance. "Exhibit A shows the signed delivery confirmation" is weaker than "Exhibit A shows a signed delivery confirmation confirming that a package was received at the cardholder's billing address on [date], three days before the chargeback was filed."

Structure each exhibit reference as:
- What the exhibit is
- What it proves
- Why that proof is relevant to the specific reason code

### Section 4: Closing Statement

Restate your conclusion clearly: the chargeback should be reversed because [brief summary]. Invite the issuer to contact your acquirer with any questions. Do not be combative or emotional — issuers respond to professional, factual presentations.

## Labeling Exhibits: A Simple System That Works

A disorganized pile of screenshots and carrier confirmations loses cases. A clearly labeled exhibit system makes the analyst's job easy and signals that your submission is professionally prepared.

**Standard exhibit labeling system:**
- **Exhibit A:** Transaction authorization record / payment confirmation
- **Exhibit B:** 3DS authentication data (if applicable)
- **Exhibit C:** Delivery confirmation / carrier tracking
- **Exhibit D:** Product description or service terms as displayed at time of purchase
- **Exhibit E:** Customer communication logs (emails, chat transcripts)
- **Exhibit F:** Prior undisputed transactions (if using CE3.0)
- **Exhibit G:** Refund/cancellation policy as displayed

Always reference exhibits in your rebuttal letter by their label. The analyst should never have to search for what a document is — the letter should tell them.

## What Issuers Look For

An issuer's disputes analyst typically reviews dozens to hundreds of representments per day. They are looking for:

1. **Direct relevance to the reason code:** Evidence that speaks to the specific claim, not generic transaction records
2. **Clear, readable documents:** Legible screenshots, proper PDFs, no blurry photos
3. **Chronological logic:** Does the story make sense in sequence? Does the delivery date come after the ship date?
4. **Completeness:** No missing pieces that create doubt (e.g., tracking data that stops at a sorting facility, not at the door)
5. **Consistency:** Data that matches across documents (same name, same address, same amount)

## Common Submission Mistakes That Lose Cases

### Using the Wrong Evidence for the Reason Code
Submitting delivery tracking for a "cancelled subscription" dispute is irrelevant. Each reason code has a corresponding evidence framework. Use it.

### Submitting Illegible Documents
Blurry screenshots, PDFs scanned at 72 DPI, or screenshots cropped to hide key information are treated as no evidence. All documents must be clear enough to read comfortably on a screen.

### Missing the Deadline
A single day past the response deadline results in automatic loss with no recourse. Track deadlines in a dedicated disputes calendar — do not rely on email reminders alone.

### Providing Authorization Data as the Only Evidence
Authorization approval codes are routinely dismissed as insufficient by issuers. They prove the card was approved, not that the cardholder authorized the transaction.

### A Generic Rebuttal Letter Not Tailored to the Reason Code
A template letter that says "we completed the transaction and the customer received their order" without referencing the specific dispute claim signals a copy-paste response that issuers discount.

### Attaching Too Many Irrelevant Documents
More is not always better. An 80-page submission filled with tangentially related documents obscures your strongest evidence. Quality and relevance beat volume.

## Success Factors: What Consistently Wins

Based on industry data and network best practices, representments that succeed share these characteristics:

- **3DS authentication data** when available (strongest single factor in fraud disputes)
- **Signed delivery confirmation** for physical goods disputes
- **Exact IP address and device ID match** between the disputed and prior undisputed transactions
- **Timestamped customer communication** showing the merchant addressed the complaint before the chargeback was filed
- **Clear refund policy disclosure** at the checkout page for cancellation-related disputes
- **Usage evidence post-transaction** for digital goods (login records, activation, download logs)

## Deadline: Know It, Track It, Never Miss It

Representment deadlines are set by network rules and enforced absolutely. There are no extensions.

- **Visa:** Generally 30 days from the chargeback notification date
- **Mastercard:** Generally 45 days from the chargeback notification date
- **Amex:** Generally 20 days (tightest deadline)
- **Discover:** Generally 30–45 days

Your acquirer may impose an internal deadline several days earlier than the network deadline to give themselves time to package and submit your response. Always ask your acquirer for both the internal and network deadlines and work to the earlier one.

---

## Frequently Asked Questions

**Q: Can I call the issuing bank directly to discuss my representment?**
A: No. The chargeback dispute process is conducted entirely through the acquirer and card network channels. Merchants do not have direct communication rights with the issuing bank during a dispute. All communication flows through your acquirer.

**Q: What if I discover new evidence after I have already submitted my representment?**
A: Once your representment is submitted, you generally cannot amend it. If you receive a pre-arbitration notice after a failed representment, the pre-arb response is your opportunity to present the additional evidence. This is one reason why it is better to take extra days to gather complete evidence than to submit quickly with incomplete documentation.

**Q: How long does the issuer take to respond to my representment?**
A: Issuers have 30–45 days to respond depending on the network. During this period, the funds remain in dispute. If the issuer does not respond within their deadline, the representment is typically considered accepted and funds are returned to your account.

**Q: Should I include a cover page or index with my submission?**
A: Yes, for any submission with more than three exhibits. A one-page index listing each exhibit and what it contains takes two minutes to create and materially improves the analyst's ability to navigate your submission. It also signals a professional, organized merchant.

**Q: My acquirer submitted my representment incorrectly. What can I do?**
A: If your acquirer makes a formatting or procedural error in submitting your representment, contact them immediately. Some errors can be corrected before the issuer processes the submission. Document the error in writing. If the acquirer's mistake caused you to lose a winnable dispute, you may have grounds for a claim against the acquirer — consult legal counsel for high-value disputes.
