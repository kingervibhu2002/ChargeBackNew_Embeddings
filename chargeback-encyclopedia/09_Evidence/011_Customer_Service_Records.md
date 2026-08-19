---
title: "Customer Service and CRM Evidence"
section: "09_Evidence"
category: "Evidence Library"
document_type: "Evidence Reference"
keywords: ["customer service records", "CRM evidence", "call logs", "chat transcripts", "email tickets", "dispute evidence", "proactive resolution", "friendly fraud signal", "return receipt"]
difficulty: "Beginner"
---

# Customer Service and CRM Evidence

## Why Customer Service Records Matter in Chargebacks

Customer service records reveal the true history of the merchant-cardholder relationship before, during, and after the disputed transaction. They answer the questions an issuer analyst most wants to understand: Did the cardholder complain before disputing? Did the merchant try to resolve the issue? Was a refund offered and declined? Was this dispute filed as a first resort rather than a last resort?

CRM and customer service evidence is particularly valuable in two scenarios:

1. **Friendly fraud:** If the cardholder never contacted your support team before filing a chargeback, or contacted you after the chargeback was filed, this pattern strongly suggests the dispute is not a genuine complaint but a tactical financial move.

2. **Legitimate complaint that escalated:** If the cardholder did contact you and you failed to resolve the issue adequately, your CRM records will reflect this — and issuers will use it against you. Honest assessment of your CRM records before submitting them is essential.

## Types of Customer Service Evidence

### CRM Notes and Case Records

A Customer Relationship Management (CRM) system (Zendesk, Salesforce Service Cloud, Freshdesk, HubSpot Service, Intercom, Gorgias) creates a timestamped record of every customer interaction. CRM notes are created by support representatives and may include:

- Summary of the issue reported.
- Steps taken by the support team.
- Resolution offered (replacement, refund, store credit, etc.).
- Outcome (issue resolved, customer declined refund, customer did not respond).
- Escalation notes if the issue was elevated to a supervisor.

**How to export and present:** Most CRM platforms allow export of individual case/ticket records as PDF or CSV. Export the full interaction timeline, including all notes and status changes. Annotate the key moments: complaint received date, resolution offered date, outcome.

### Live Chat Transcripts

Live chat systems (Intercom, Drift, Zendesk Chat, Tidio, LiveChat) generate verbatim transcripts of every conversation. These are valuable because:

- They are exact — no paraphrasing or interpretation.
- They are timestamped at message level, not just conversation level.
- They reveal exactly what the cardholder said and what the merchant representative said.
- They can demonstrate that the merchant offered a resolution the cardholder refused.

**Critical scenario — cardholder declines resolution:** If your chat transcript shows the merchant offered a full refund and the cardholder refused, then filed a chargeback for the same amount, this is strong evidence of bad faith. Include the chat transcript as an exhibit and highlight the refund offer and cardholder's rejection in your rebuttal letter.

**Critical scenario — cardholder accepts resolution:** If your transcript shows the cardholder agreed to a replacement shipment, then later filed a chargeback for the original order (potentially also receiving the replacement), this documents potential double recovery. Your rebuttal should include both the chat record (confirming agreement to resolution) and the replacement shipping record.

### Email Support Tickets

Email-based support tickets generate email threads that can be exported from your support platform. Present as described in 09_Evidence/009_Email_Evidence.md, with additional focus on:

- First contact date (to establish whether complaint preceded or followed chargeback).
- Content of the complaint (to compare against the chargeback claim).
- Merchant's response and resolution offer.
- Cardholder's final response (or non-response).

### Phone Call Logs and Recordings

If your support team operates via phone, call logs (call time, duration, phone number called from) and call recordings (where legally permitted) are evidence:

**Call logs:** Even without recordings, a call log showing the cardholder called your support line at a specific date and time demonstrates contact. The representative's CRM notes from the call provide the content.

**Call recordings:** In jurisdictions where call recording is legal (and where you have disclosed the recording to the cardholder), recordings can directly prove what was said. If the recording shows the cardholder agreed to a resolution or made statements inconsistent with their chargeback claim, this is very powerful evidence.

**Legal requirements:** Call recording laws vary. In the United States, one-party consent states allow recording without the other party's knowledge; two-party (all-party) consent states require disclosure. In the EU, GDPR governs call recording. Always comply with applicable laws. If you record calls, disclose it at the start with a standard message.

## What Issuers Look For in CRM Evidence

Issuer analysts review CRM evidence to answer two key questions:

**1. Did the merchant have an opportunity to resolve this before the chargeback?**

Issuers apply a "good faith" standard. A merchant who received a clear complaint about a defective product, failed to respond for two weeks, and then received a chargeback will have reduced credibility in the dispute. A merchant who responded within 24 hours, offered a refund, and was met with a chargeback before the refund processed will have very high credibility.

**2. Is the cardholder's complaint consistent with their chargeback claim?**

If the cardholder emailed your support team complaining that "the product arrived but it was the wrong color," and then filed a chargeback under "merchandise not received," the inconsistency is visible in your CRM records and can be used to demonstrate the chargeback reason is not the true complaint.

Common inconsistency patterns:
- Complained about quality → Chargeback coded as "not received."
- Complained about slow shipping → Chargeback coded as "not authorized."
- Requested a different product → Chargeback coded as "fraud."

These inconsistencies suggest the cardholder selected the dispute code most likely to succeed rather than the accurate code.

## Proactive Resolution Evidence

Some of the strongest CRM evidence a merchant can present shows proactive resolution attempts — reaching out to the cardholder before they complained:

- Post-delivery satisfaction check emails sent to all customers.
- Proactive contact after a shipping delay was detected.
- Proactive refund or credit offered for a known product defect.
- Customer success follow-up (for SaaS merchants) asking whether onboarding was successful.

This evidence demonstrates the merchant's good faith and reduces the credibility of claims that the merchant was unresponsive or negligent.

## Complaint Received After Chargeback Filed

This is a flagship friendly fraud indicator: the cardholder's first contact with your support team occurs after the chargeback has already been filed (and you have already received a chargeback notification).

The timeline would look like:
1. Transaction: March 15.
2. Chargeback notification received by merchant: April 10.
3. Cardholder first contacts support: April 12 (two days after chargeback).

This sequence is impossible to explain as a legitimate complaint path — legitimate customers who have a problem contact the merchant first, then escalate to a chargeback if the merchant fails to resolve it. A cardholder who goes to the bank first and then emails support afterward is creating a paper trail after the fact.

**How to present:** Include both the chargeback notification timestamp (from your acquirer or chargeback management platform) and the first CRM contact record. State clearly: "The cardholder's first contact with [Merchant] support was received on [Date], which is [X] days after the chargeback was filed on [Date]. The cardholder did not attempt to resolve this issue through the merchant prior to disputing."

## Return Receipt and Physical Return Documentation

If the cardholder returned goods as part of the dispute:

- **Return receipt:** Confirmation of receipt of the returned goods, including the condition of items received.
- **Inspection record:** If the returned item was inspected and found to be different from what was shipped (wrong item, missing components, damaged), this is evidence of return fraud.
- **RMA record:** Your Return Merchandise Authorization record shows when the return was authorized, by whom, and what the stated reason was.

If the returned item's serial number does not match what was shipped, include both the original shipment serial number record (from your shipping documentation) and the returned item's serial number in your evidence.

## Building a CRM Evidence Package

A well-organized CRM evidence exhibit should contain:

1. **Contact timeline summary:** Chronological list of all contacts between the cardholder and your support team. Date, channel (email/chat/phone), contact reason, and resolution status.

2. **Most relevant interaction records:** Full exports of the 1–3 most relevant tickets, chat transcripts, or call notes. Highlight key statements.

3. **Resolution documentation:** Evidence of any refund offered, replacement shipped, or resolution accepted.

4. **First contact timing analysis:** If relevant, a note comparing the chargeback date to the first customer contact date.

Keep the CRM exhibit focused — an analyst cannot process 50 pages of CRM data. Extract the relevant records, annotate them clearly, and include a one-paragraph summary in your rebuttal letter explaining what the CRM records show.

## Summary

Customer service and CRM records provide the narrative context that technical records (IP, device, authorization) cannot: they document whether the cardholder ever actually complained, what they complained about, and whether the merchant attempted resolution. When CRM records show the cardholder never contacted the merchant before disputing, or contacted the merchant after the chargeback was filed, this is strong friendly fraud evidence. When CRM records show a refund was offered and declined, this demonstrates the cardholder's preference for the chargeback mechanism over legitimate resolution — another friendly fraud indicator. Build a CRM practice that timestamps every customer interaction, records representative notes consistently, and exports cleanly to PDF for dispute submission.
