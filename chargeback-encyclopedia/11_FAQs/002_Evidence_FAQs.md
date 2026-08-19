---
title: "Evidence and Submission FAQs for Merchants"
category: FAQs
doc_type: faq
audience: merchants
last_updated: 2026-06-01
tags: [evidence, submission, chargeback response, exhibits, documentation, FAQ]
---

# Evidence and Submission FAQs for Merchants

These 20 questions address the most common merchant uncertainties about what evidence to submit, how to present it, and what documentation actually moves the needle in a chargeback review.

---

## Q1: What evidence do I need for a fraud chargeback?

For a fraud chargeback (Visa 10.4, Mastercard 4837), the most effective evidence stack includes: (1) the authorization record showing AVS and CVV response codes; (2) a 3-D Secure authentication result if 3DS was used at checkout; (3) carrier delivery confirmation to the cardholder's billing or confirmed shipping address; (4) device fingerprint and IP address data captured at checkout, with geolocation tied to the cardholder's region; and (5) prior purchase history showing the same cardholder used this card without dispute. For digital goods, replace delivery tracking with download logs, activation records, and post-purchase account usage logs. The strongest single piece of evidence is a 3DS fully authenticated result (ECI 05/02), which shifts liability to the issuer.

---

## Q2: Does a CVV match help my chargeback response?

Yes, significantly. The CVV (Card Verification Value) or CVC2 is a 3–4 digit code printed on the physical card. It is not stored on the magnetic stripe and cannot be read from a skimmed card. A CVV match (response code M = match) means the person who entered the card details had access to the physical card itself. For card-not-present fraud disputes, a CVV match is one of the strongest authentication signals available, particularly when combined with a matching AVS response. However, a CVV match alone does not guarantee a win — issuers can still side with their cardholder even with a CVV match. Always pair it with delivery proof and device/IP evidence.

---

## Q3: What if my delivery was contactless (no signature)?

Many delivery services no longer require signatures for standard residential deliveries. If you have no signature, the carrier's electronic delivery confirmation (GPS-verified delivery event with timestamp and address) is typically acceptable. Some carriers also provide a photograph of the delivered package at the door — request this from the carrier if it is available. For high-value orders, proactively require signature confirmation at checkout (add the cost to the order or the shipping tier) to eliminate this gap. In a rebuttal, explicitly note that the service level selected at checkout does not require a signature and that the carrier's GPS delivery confirmation is the industry-standard proof of delivery for this shipment type.

---

## Q4: How do I prove a digital product was delivered?

Digital delivery is proven through a chain of server-generated events, not cardholder attestation. The standard evidence chain includes: (1) your email service provider's delivery log showing the email was successfully transmitted to the cardholder's inbox (with Message ID and timestamp); (2) the server download log showing the file was requested and downloaded to completion (with byte count, IP, and session timestamp); (3) a license key issuance and redemption record if applicable; and (4) post-delivery account activity (login or content access) from the same IP region as the cardholder. The key is that all of these are system-generated records — not self-created documents — and they form a verifiable chain that the issuer can recognize as credible.

---

## Q5: Can I use screenshots as evidence?

Yes, but with important caveats. Screenshots from third-party, independently verifiable sources are strong evidence: carrier tracking pages, Google Maps showing a delivery address, email service provider dashboards, and banking portals. Screenshots from your own internal systems are weaker because they can be fabricated and the issuer cannot independently verify them — these should always be accompanied by a printed system record, a data export, or a supporting third-party confirmation. Never submit manipulated or altered screenshots. Issuers who detect altered evidence will reject your dispute, flag your account, and may report the alteration to your acquirer.

---

## Q6: What is compelling evidence under Visa CE3.0?

Visa's Compelling Evidence 3.0 (effective April 2023) is a specific dispute defense framework for Visa 10.4 (fraud) chargebacks. Under CE3.0, a merchant can provide compelling evidence that the disputed transaction was made by the cardholder by demonstrating two qualifying prior transactions from the same card within the prior 120–365 days that share at least two of the following data elements with the disputed transaction: the same device fingerprint, the same IP address, the same email address, or the same shipping address. If the qualifying prior transactions had no associated disputes, the issuer is expected to accept the CE3.0 claim and decline the chargeback. CE3.0 was specifically designed to counter friendly fraud.

---

## Q7: How do I label exhibits in my response?

Label every document before submission. Assign sequential numbers ("Exhibit 1," "Exhibit 2," etc.) and add the label to the top-right corner of each document — physically stamp it if printing, or add a text overlay if submitting digitally. In your rebuttal letter, reference each exhibit by number where relevant ("Please refer to Exhibit 3: Carrier Tracking Record"). Create a cover sheet (evidence index) listing all exhibits in order with a brief description of each. Rename digital files to match: "Exhibit_1_Authorization_Record.pdf," "Exhibit_2_Tracking_Confirmation.pdf." Unlabeled exhibits are a top reason issuers reject evidence packages — the analyst cannot connect an unlabeled document to the argument in your letter.

---

## Q8: What format should I submit evidence in?

Submit all evidence as PDF documents whenever possible. PDFs are universally readable, can combine multiple documents into one file, and maintain their formatting across different systems. If your acquirer's portal requires a single PDF, merge all exhibits (in exhibit order) into one PDF with a cover page as the first document. Maximum file sizes vary by acquirer — typically 5–20 MB per submission. Avoid submitting Word documents, raw image files (.jpg, .png), or Excel spreadsheets as your primary documents; convert these to PDF first. If you must submit multiple files, name them clearly with exhibit numbers so the analyst reviews them in the correct sequence.

---

## Q9: How much evidence is too much?

Quality over quantity is the rule. Issuers have strict time limits for reviewing dispute responses — typically 5–10 minutes per case. Submitting 40 pages of loosely related documentation buries the key evidence and wastes the analyst's time. A concise, well-organized 8–15 page package (2-page rebuttal letter + 6–13 pages of labeled exhibits) is more effective than a 50-page dump. Include only documents that directly address the specific reason code claim. If a document does not directly prove your argument, omit it. If you have a very strong single piece of evidence (3DS authentication with ECI 05), make it Exhibit 1 and make it prominent.

---

## Q10: Can customer service chat logs help?

Absolutely — and they can be decisive in certain disputes. A chat log where the customer says "just received my order, love it!" dated after the alleged non-delivery is some of the strongest evidence for a 13.1 (not received) dispute. For 13.3 (not as described) disputes, a chat log where the customer had no complaints about product quality until they filed the chargeback weeks later shows the dispute is opportunistic. For 10.4 (fraud) disputes, a chat log where the cardholder discussed their order, asked about an add-on, or inquired about usage proves the account holder knew about and engaged with the transaction. Always export chat logs with timestamps and the customer's email address or account ID visible. Redact any unrelated personal information.

---

## Q11: What is an authorization record and how do I get one?

An authorization record (also called an authorization confirmation or payment gateway transaction detail) is the record generated when your payment processor contacts the issuing bank and the bank approves the transaction. It contains the authorization code, the AVS response, the CVV response, the timestamp, and the card number (last four digits). Your payment gateway or processor dashboard should allow you to export or print this record for any transaction. In Stripe, it appears in the payment detail view; in Braintree, in the Transaction Detail; in most acquirer portals, under "Transaction Search." This is typically Exhibit 1 in every fraud chargeback response.

---

## Q12: Should I include the customer's email address in my evidence?

Yes, but handle it carefully. The customer's email address is important because it demonstrates that the order confirmation, delivery email, and product access credentials were sent to a real, confirmed address associated with the cardholder's account. Include the email address in your rebuttal letter and in relevant exhibits. Be aware that some jurisdictions' data protection regulations (GDPR, CCPA) govern how personal data is shared with third parties in dispute proceedings. Email addresses and card numbers (last four only) are generally permissible to include. Full card numbers, dates of birth, and government ID numbers should not be included in chargeback submissions.

---

## Q13: Can I use social media posts as evidence?

In limited circumstances, yes. If a cardholder posted on social media about receiving or using a product they later disputed as "not received" or "fraudulent," a dated screenshot of the post can be relevant. This type of evidence is most powerful in friendly fraud cases. However, social media screenshots require careful presentation: include the URL, the date of the post, the username (and note that it matches the cardholder's name or email if you can establish the connection), and a verification method. Courts and issuers treat social media evidence as supplemental rather than primary — it supports other evidence but rarely stands alone.

---

## Q14: Does my return policy need to be in my evidence package?

Yes, for any dispute category related to dissatisfaction (13.3 not as described, 4853 services not rendered) or cancellation (13.2, 4853). The issuer needs to see that a valid dispute resolution mechanism was available to the cardholder before they resorted to a chargeback. Include a screenshot of your return/refund policy as displayed on your website at the time of purchase, and indicate where on your checkout page it was linked. Also include the policy text that appeared in the order confirmation email if applicable. A clearly disclosed, accessible return policy strengthens your position by demonstrating good faith and showing that the cardholder bypassed your resolution process.

---

## Q15: What is an AVS response code and which codes are best for disputes?

AVS (Address Verification Service) is a check where your payment gateway sends the billing address entered at checkout to the issuing bank, which compares it against the cardholder's address on file. The most important AVS response codes are: **Y** (full match — street address and ZIP both match), **Z** (ZIP matches, street does not), **A** (street matches, ZIP does not), and **N** (no match). For chargeback defense, **Y** (full match) is the strongest — it confirms the person entering card data had access to the cardholder's billing information. Partial matches (A or Z) provide moderate support. A response of **N** (no match) weakens your fraud defense, though it does not eliminate it if other evidence is strong.

---

## Q16: Should I include a cover letter or just submit documents?

Always include a cover letter (rebuttal letter). Documents alone — even strong ones — require interpretation. The rebuttal letter is your narrative: it identifies the reason code, states your position, walks the analyst through each piece of evidence, and explicitly requests reversal. Without a letter, the analyst must piece together your argument from disparate documents, which increases the risk that key points are missed. Think of the rebuttal letter as your attorney's opening argument, and the exhibits as the trial evidence. Both are required for a complete and professional response.

---

## Q17: Can I submit new evidence if my first response is rejected?

In limited circumstances. If the issuer rejects your representment and files a pre-arbitration (Visa) or second chargeback (Mastercard), you may submit additional evidence in your pre-arbitration response. However, the evidentiary standards are higher at pre-arbitration, and card networks generally expect that your best evidence was submitted in the initial representment. Submitting evidence that should have been included initially may appear as if you assembled it after the fact. The stronger practice is to submit your complete and best evidence package in the first representment — do not hold back evidence hoping to use it later.

---

## Q18: Is a signed Terms of Service agreement useful evidence?

Yes, particularly for subscription and recurring billing disputes (Visa 13.2, Mastercard 4853). A signed or accepted Terms of Service that clearly states the billing amount, frequency, and cancellation policy directly addresses the cardholder's claim that they did not know they were entering into a recurring arrangement. For disputes where the cardholder claims the product was not as described, a signed agreement that includes a description of the service scope can show the product matched what was promised. Acceptance records (IP address, timestamp, and "I Agree" checkbox) are more powerful than unsigned ToS documents, because they prove the specific cardholder reviewed and accepted the terms.

---

## Q19: What is the most common evidence mistake merchants make?

The most common mistake is addressing the wrong claim with the correct evidence. For example, submitting carrier tracking proof for a dispute filed under "not as described" (13.3) — delivery proof doesn't address the quality claim, so the issuer ignores it. Always read the reason code on your chargeback notice and understand what the cardholder is actually claiming before selecting your evidence. The second most common mistake is submitting unlabeled or disorganized documents. The third is missing the deadline. These three mistakes account for the majority of preventable merchant losses in chargeback disputes.

---

## Q20: How do I handle a chargeback when I have no evidence at all?

If you have genuinely no evidence, assess your options honestly: (1) If the chargeback amount is small and you have no evidence, it may be more economical to accept the loss than pay staff time to assemble a weak rebuttal. (2) If the amount is significant, extract whatever you do have — the authorization record, the order confirmation email, any IP log from your platform, the customer's account registration — and submit what is available with a clear rebuttal letter. Even partial evidence is better than none. (3) Going forward, implement evidence logging from day one: AVS/CVV capture, IP logging, email delivery tracking, and delivery confirmation are the baseline. Missing evidence is a process gap, not just a one-off problem.
