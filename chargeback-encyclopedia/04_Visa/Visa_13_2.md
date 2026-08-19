---
title: "Visa 13.2 — Cancelled Recurring Transaction"
section: "04_Visa"
category: "Visa Reason Codes"
document_type: "Reference"
keywords: ["Visa 13.2", "cancelled recurring", "subscription chargeback", "recurring billing dispute", "cancellation not honored", "subscription cancelled", "recurring transaction Visa", "CRM cancellation logs"]
difficulty: "Beginner"
---

# Visa 13.2 — Cancelled Recurring Transaction

Visa reason code 13.2 applies to recurring billing disputes — situations where a cardholder claims their subscription or recurring charge was billed after they had already cancelled. It is one of the most contentious chargeback reason codes for subscription-based businesses because the dispute often turns on a single question: does the merchant have documented proof that no cancellation request was received?

## What This Chargeback Means

A 13.2 chargeback means the cardholder is asserting one of the following:

1. They cancelled their subscription or recurring agreement, but the merchant continued to charge them
2. The card they had on file expired and they did not authorize the updated recurring charge
3. The recurring billing amount changed from what was originally agreed, without their consent

The cardholder is not disputing that they ever had a relationship with the merchant. They are disputing that the relationship — and the associated billing authority — should have ended before the disputed charge occurred.

## The Central Evidence Question: Did a Cancellation Request Exist?

Everything in a 13.2 dispute revolves around whether the cardholder actually submitted a cancellation request that the merchant received and ignored, or whether no cancellation request was made and the cardholder changed their mind retroactively.

### If No Cancellation Request Was Received

Your evidence must demonstrate that your systems received no cancellation communication from this cardholder as of the disputed charge date. This is a negative proof — you are showing the absence of a record.

**Evidence to submit:**
- CRM log showing the cardholder's account status as active on the disputed charge date, with no cancellation notes or status changes
- Customer portal activity log showing no cancellation action was taken by the cardholder
- Email inbox search results showing no cancellation request email received from the cardholder's registered address
- Phone call logs showing no inbound call from the cardholder's registered phone number around the disputed period
- Subscription billing system export showing the subscription was active and in good standing at the time of the charge

**The rebuttal letter should state clearly:** "As of [charge date], our systems contain no record of a cancellation request from this customer. Attached is the account status log and customer support ticket history confirming the subscription was active."

### If the Cardholder Claims They Cancelled via a Method You Disagree With

Cardholders sometimes claim they cancelled by methods your policy does not recognize — for example, verbally asking a floor employee, emailing a personal address that is not the support inbox, or clicking an unsubscribe link from a promotional email (which is not a subscription cancellation). Address these scenarios directly:

- If your cancellation policy states that subscriptions must be cancelled via the account portal, customer support email, or phone number — and that policy was clearly displayed — submit the policy as evidence and note that no cancellation was received through any authorized channel.
- If the cardholder emailed a personal employee address, show that email was not directed to your support team and that your support team received no formal cancellation request.

## Your Cancellation Policy: What Visa Requires

Visa requires that merchants offering recurring billing make cancellation "easy to accomplish." Specifically:

- A clear, conspicuous cancellation mechanism must be available to the customer at all times
- The cancellation process must not require excessive steps or waiting periods
- Merchants cannot require customers to call a phone number exclusively during limited business hours as the only cancellation method if other channels are not available

If your cancellation policy creates unnecessary friction, you are at risk not just of losing 13.2 chargebacks but of Visa taking compliance action against your billing practices. Easy cancellation is a network requirement, not merely good practice.

## Evidence You Need to Win a 13.2

### The Cancellation Policy as Displayed at Sign-Up
Submit a screenshot of your checkout, sign-up page, or subscription terms page as it appeared at the time the cardholder enrolled — showing the recurring billing frequency, the cancellation terms, and how cancellation is initiated. This establishes informed consent and the contractual framework.

**Best practice:** Archive screenshots of your sign-up page and terms at every material update. If you cannot show how the page looked when the customer enrolled, you cannot establish what they agreed to.

### CRM / Customer Support Logs
Complete log of all customer interactions on the cardholder's account — emails received, support tickets, chat transcripts, phone call notes — showing no cancellation request at any point prior to the disputed charge.

### Portal Cancellation Records
If your subscription portal logs user actions (login timestamps, setting changes, cancellation submissions), provide the audit trail showing no cancellation was initiated.

### Subscription Agreement / Terms of Service Acknowledgment
Evidence that the cardholder acknowledged the recurring billing terms at enrollment — a signed agreement, a checked checkbox on the enrollment form, or an email confirming enrollment that outlines the billing frequency and cancellation process.

### Pre-Charge Reminder Emails
Visa recommends (and increasingly requires) that merchants send a reminder notification before each recurring charge — particularly for annual subscriptions where the billing interval is long enough that the cardholder may have forgotten. If you sent a reminder email before the disputed charge, include it as evidence that the cardholder had advance notice and an opportunity to cancel before being billed.

## When the Merchant Has No Defense

There are situations where 13.2 chargebacks are unwinnable and the appropriate response is to accept the loss:

- The cardholder has a cancellation confirmation — an email, a support ticket response, a portal confirmation — and you processed the charge anyway
- Your system logs show a cancellation request was received but the subscription was not deactivated due to a processing error
- Your customer service team acknowledged a cancellation verbally or in writing but billing continued
- The charge occurred after the card's expiration date without explicit cardholder consent for the updated card to be used in recurring billing

In these cases, the cancellation was legitimate and the charge was not authorized. Accept the chargeback, issue a refund, and fix the process failure that caused the continued billing.

## Billing Descriptor Clarity

Many 13.2 chargebacks arise not from actual cancellation disputes but from cardholders not recognizing the merchant's name on their statement — they assume the charge is unauthorized and dispute it as a cancelled recurring charge.

Ensure your billing descriptor (the name appearing on the cardholder's statement) matches your brand name exactly as customers know it. If your company is "Acme Software, LLC" but customers know you as "BuildFast Pro," your billing descriptor should say "BuildFast Pro" — not "ACMESFTWR*APPS."

---

## Frequently Asked Questions

**Q: A customer says they cancelled six months ago but never had a confirmation. We have no record of any cancellation. Who wins?**
A: If your records show no cancellation request was received — and you can document this with CRM logs, support ticket history, and portal activity — you have a strong position. Submit this documentation clearly. The burden is on the cardholder to demonstrate a cancellation was submitted; an uncorroborated memory of cancelling is not evidence. That said, if the cardholder has a forwarded email or screenshot showing they contacted your support, the dispute becomes much harder to defend.

**Q: Can I dispute a 13.2 if the customer is wrong about when they cancelled?**
A: Yes. If the cardholder's cancellation request was received after the billing date they are disputing — meaning the charge occurred before any cancellation was submitted — you are entitled to keep the funds for that billing cycle. Submit the cancellation request timestamp from your CRM alongside the billing date to show the charge preceded the cancellation.

**Q: What if my terms say cancellations must be made 30 days in advance?**
A: Notice period requirements are enforceable if they were clearly disclosed to the cardholder at enrollment. If your terms state "cancellations require 30 days notice" and that was disclosed and acknowledged, a cardholder who cancelled 10 days before the next billing date may be subject to one more billing cycle. Submit the signed or acknowledged terms showing this requirement. Note that Visa scrutinizes unreasonably long notice periods — 30 days is generally considered acceptable, 90 days is not.

**Q: Does sending a pre-billing notification email protect me from 13.2 chargebacks?**
A: It significantly reduces their frequency. If a cardholder receives a reminder email 7 days before billing, many will cancel through the provided link rather than disputing after the charge. For those who still dispute, the notification email demonstrates advance notice was given — which strengthens your position that the charge was not a surprise.

**Q: We use an account updater service that automatically updates expired card numbers. A cardholder says they let their card expire on purpose to stop billing. Is a 13.2 valid?**
A: This is a legitimate 13.2 scenario. Visa's account updater service is intended for customers who want to maintain their subscriptions through card changes — not to override a customer's intent to end billing by allowing their card to expire. If a cardholder allowed their card to expire without explicitly authorizing continued billing on a new card number, and you used account updater to continue charging, the 13.2 chargeback may be valid. Review your terms — explicit cardholder consent for account updater usage in your subscription is required.
