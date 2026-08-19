---
title: "Rebuttal Template — Visa Reason Code 10.4 (SaaS / Subscription)"
category: Rebuttal Library
doc_type: template
reason_code: Visa 10.4
dispute_type: Card Absent – Other Fraud
channel: SaaS, Subscription Software
audience: merchants
last_updated: 2026-06-01
tags: [Visa, 10.4, fraud, SaaS, subscription, rebuttal, template, login, usage]
---

# Rebuttal Template: Visa Reason Code 10.4 — Card Absent Environment / Other Fraud (SaaS / Subscription)

## About This Template

SaaS and subscription software merchants face Visa 10.4 disputes when a cardholder or their bank claims a subscription charge was unauthorized. The defense strategy for SaaS differs from single-purchase digital goods because the evidence must show not only that the account was created and accessed, but that the service was actively used throughout the billing period — meaning the cardholder (or someone with their permission) operated the software.

This template covers subscription-based SaaS: project management tools, CRM systems, accounting software, cloud storage, HR platforms, productivity apps, and similar services.

---

## Pre-Submission Checklist

- [ ] Authorization code and payment processor record for the disputed charge
- [ ] Account sign-up record: timestamp, email, IP address, registration form data
- [ ] Usage logs: logins, feature interactions, API calls, data processed
- [ ] Login history covering the disputed billing period
- [ ] Feature-level usage showing the service was consumed (not just logged in)
- [ ] Onboarding completion record (tutorial, setup wizard, data import)
- [ ] Any support tickets or communications submitted by the account user
- [ ] Subscription confirmation email sent at signup
- [ ] Prior billing history if the dispute covers a renewal charge

---

## Rebuttal Letter Template

---

**[MERCHANT NAME]**
[Merchant Address]
[Merchant Email]
Merchant ID: [MID]

Date: [DATE]

Re: Chargeback Dispute — Case No. [CASE NUMBER]
Reason Code: Visa 10.4 — Card Absent Environment / Other Fraud
Transaction Date: [TRANSACTION DATE]
Transaction Amount: [AMOUNT]
Cardholder Name: [CARDHOLDER NAME]
Card Number (Last 4): [XXXX]

---

**To the Chargeback Review Team,**

[MERCHANT NAME] respectfully disputes Chargeback Case [CASE NUMBER] under Visa Reason Code 10.4. The charge of [AMOUNT] on [TRANSACTION DATE] represents a [initial/renewal] subscription payment for [PRODUCT NAME], a [description: e.g., "cloud-based project management platform"]. We submit evidence demonstrating that the account was created by the cardholder, the service was actively used throughout the billing period, and the charge was legitimate.

---

### Section 1: Transaction Summary

| Field | Value |
|---|---|
| Transaction Date | [DATE] |
| Transaction Time (UTC) | [TIME] |
| Transaction Amount | [AMOUNT] |
| Authorization Code | [AUTH CODE] |
| Card Number (Last 4) | [XXXX] |
| AVS Response | [CODE — Description] |
| CVV Response | [M — Match / Not Collected] |
| Transaction / Invoice ID | [ID] |
| Account Email | [ACCOUNT EMAIL] |
| Subscription Plan | [PLAN NAME — e.g., "Professional Monthly, $99/mo"] |
| Billing Period | [START DATE] to [END DATE] |

---

### Section 2: Account Sign-Up Records

The account associated with this subscription was created on [SIGNUP DATE] using the email address [EMAIL]. The sign-up process required entering valid card details, agreeing to the Terms of Service, and confirming the subscription via email.

**Sign-Up Record:**

| Field | Value |
|---|---|
| Account Email | [EMAIL] |
| Account Created | [DATE AND TIME] |
| Registration IP | [IP ADDRESS] |
| IP Geolocation | [CITY, STATE, COUNTRY] |
| Signup Method | [Direct / Google OAuth / SSO] |
| Email Confirmation | Sent [DATE] — Confirmed [DATE] |
| Terms of Service Agreement | Accepted [DATE AND TIME] at [IP] |
| Card Added | [DATE] — Last 4: [XXXX] |

The cardholder confirmed their email address and accepted our Terms of Service, which clearly state the subscription billing amount and frequency.

Please refer to **Exhibit 1**: Account Registration Record.
Please refer to **Exhibit 2**: Subscription Confirmation Email.

---

### Section 3: Login History During Disputed Billing Period

The account was actively logged into throughout the billing period covered by the disputed charge. Below is a representative summary of login activity from [START DATE] to [END DATE]:

| Date | Login Time (UTC) | IP Address | Device/Browser |
|---|---|---|---|
| [DATE] | [TIME] | [IP] | [DEVICE] |
| [DATE] | [TIME] | [IP] | [DEVICE] |
| [DATE] | [TIME] | [IP] | [DEVICE] |
| [DATE] | [TIME] | [IP] | [DEVICE] |
| [DATE] | [TIME] | [IP] | [DEVICE] |
| ... | ... | ... | ... |

Total login sessions during the billing period: **[NUMBER]**
Total active days: **[NUMBER] of [TOTAL DAYS] days in the billing period**

The login IPs are consistent with the cardholder's billing address and geographic region. No anomalous or foreign login locations were detected.

Please refer to **Exhibit 3**: Full Login History Export.

---

### Section 4: Feature Usage During Disputed Period

Active use of the platform's core features demonstrates that the account holder was genuinely consuming the service, not merely logging in passively.

**Feature Usage Summary ([BILLING PERIOD]):**

| Feature / Action | Usage Count | Last Used |
|---|---|---|
| [Feature 1 — e.g., "Projects Created"] | [COUNT] | [DATE] |
| [Feature 2 — e.g., "Tasks Completed"] | [COUNT] | [DATE] |
| [Feature 3 — e.g., "Reports Generated"] | [COUNT] | [DATE] |
| [Feature 4 — e.g., "Files Uploaded (GB)"] | [COUNT/SIZE] | [DATE] |
| [Feature 5 — e.g., "Team Members Invited"] | [COUNT] | [DATE] |
| [Feature 6 — e.g., "API Calls Made"] | [COUNT] | [DATE] |

[DESCRIBE SPECIFIC MEANINGFUL ACTIVITY — e.g., "The account holder created 12 projects, added 4 team collaborators, and generated 8 custom reports during the disputed billing period."]

Please refer to **Exhibit 4**: Feature Usage Report.

---

### Section 5: Support Interactions (If Applicable)

[INCLUDE IF THE USER CONTACTED SUPPORT. OTHERWISE DELETE.]

The account holder submitted [NUMBER] support request(s) during the subscription period, confirming active engagement with the service:

| Date | Support Channel | Topic |
|---|---|---|
| [DATE] | [Email / Chat / Phone] | [SUBJECT — e.g., "How to export CSV report"] |
| [DATE] | [Email / Chat / Phone] | [SUBJECT] |

Please refer to **Exhibit 5**: Customer Support Ticket Log.

---

### Section 6: Prior Billing History

[INCLUDE FOR RENEWAL CHARGES. DELETE FOR INITIAL CHARGES.]

This charge is not the first billing on this account. The card was successfully billed on prior dates without any dispute, demonstrating the cardholder's awareness of and consent to the recurring subscription:

| Invoice Date | Amount | Authorization Code | Disputed? |
|---|---|---|---|
| [DATE] | [AMOUNT] | [AUTH CODE] | No |
| [DATE] | [AMOUNT] | [AUTH CODE] | No |
| [DATE] | [AMOUNT] | [AUTH CODE] | No |

The cardholder accepted [NUMBER] prior charges totaling [AMOUNT] over [DURATION] of active subscription use without raising a dispute.

Please refer to **Exhibit 6**: Billing History Report.

---

### Section 7: Closing

The evidence above establishes that [CARDHOLDER NAME]'s account was created with their card and email address, confirmed via email verification, actively used for [NUMBER] login sessions and [FEATURE ACTIVITY] during the disputed billing period, and previously billed without dispute. The charge of [AMOUNT] was legitimate and fully earned.

[MERCHANT NAME] respectfully requests that Chargeback Case [CASE NUMBER] be reversed and the amount of [AMOUNT] be restored to our merchant account.

Sincerely,

[YOUR NAME]
[YOUR TITLE]
[MERCHANT NAME]
[EMAIL] | [PHONE]

---

## Evidence Index

| Exhibit | Document | Purpose |
|---|---|---|
| Exhibit 1 | Account Registration Record | Proves cardholder created account |
| Exhibit 2 | Subscription Confirmation Email | Proves billing terms were communicated |
| Exhibit 3 | Login History Export | Proves account was accessed throughout billing period |
| Exhibit 4 | Feature Usage Report | Proves service was actively consumed |
| Exhibit 5 | Support Ticket Log | Proves cardholder engaged with merchant post-signup |
| Exhibit 6 | Billing History | Proves prior successful charges on same card |

---

## Merchant Notes

- Usage logs are the backbone of every SaaS 10.4 defense. Ensure your platform logs feature-level events (not just logins) to a secure, exportable store from day one of each subscription.
- If an account has team members (multi-seat SaaS), include the list of collaborators added by the primary account holder. Adding collaborators is strong evidence of genuine use.
- OAuth signups (Google, Microsoft) often carry additional identity signals — include the linked identity provider email if it matches the card billing email.
- For annual subscription disputes: if the disputed charge is for a year where the cardholder used the service for 6+ months before filing, that usage history is your strongest argument. Include monthly usage summaries.
