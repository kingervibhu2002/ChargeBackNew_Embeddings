---
title: "Amex C28 — Cancelled Recurring Billing"
section: "06_Amex"
category: "Amex Reason Codes"
network: "American Express"
reason_code: "C28"
document_type: "Reason Code Reference"
keywords: ["cancelled recurring billing", "subscription cancellation", "C28", "Amex chargeback", "recurring charge", "SaaS chargeback", "membership dispute", "easy cancellation", "Amex recurring rules"]
difficulty: "Intermediate"
---

## Overview

Amex reason code C28 — "Cancelled Recurring Billing" — is filed when a cardholder believes their subscription, membership, or recurring billing arrangement was cancelled, but their American Express card was charged again afterward. The dispute represents a failure point in the merchant-cardholder relationship: either the cancellation was valid and the merchant charged in error, or the merchant has no record of the cancellation and the charge was legitimate — but the cardholder disagrees.

C28 applies broadly to any recurring billing model: SaaS subscriptions, streaming services, gym memberships, magazine subscriptions, insurance premiums, box delivery services, online course memberships, and any other arrangement where a card is charged on a regular schedule. The code is Amex's equivalent of what other networks classify under cancelled recurring transaction disputes, but Amex applies stricter compliance standards than Visa or Mastercard — particularly around cancellation accessibility and disclosure at sign-up.

Amex's stricter posture on recurring billing means merchants who do not invest in robust cancellation infrastructure face persistent C28 chargeback exposure. A subscription merchant that makes cancellation difficult, fails to confirm cancellations, or lacks comprehensive cancellation logs will lose C28 disputes at a high rate regardless of whether the cardholder's claim is technically accurate. Compliance with Amex's recurring billing rules is a prerequisite to winning these disputes.

---

## Common Scenarios

**Valid cancellation with no merchant record.** The cardholder submitted a cancellation through the merchant's portal, email, or phone system, but the cancellation was not processed due to a technical error or staff oversight. The next billing cycle charged the card, and the cardholder disputes having never received a cancellation confirmation and seeing a charge they did not expect.

**Cancellation during billing cycle, charge for final period.** The cardholder cancels mid-cycle and expects immediate termination of charges. The merchant's terms specify billing continues through the end of the current billing period. The final period charge triggers a C28 because the cardholder considers it a post-cancellation charge — even though it falls within the agreed billing period.

**Failed self-service cancellation flow.** The cardholder attempted to cancel through the merchant's self-service portal, but a technical malfunction prevented the cancellation from completing — a broken "cancel" button, a form that failed to submit, or a flow that required additional confirmation steps the cardholder did not see. The cardholder believed cancellation was complete; the merchant has no record of it.

**Login-based cancellation not executed.** Cardholders sometimes navigate to account settings, intend to cancel, but exit before completing the final confirmation step. The cancellation was not submitted, the charge continues, and the cardholder disputes having "tried to cancel."

**Account downgraded, not terminated.** The cardholder cancelled one tier of service and was automatically moved to a different tier or a free plan rather than fully terminated. A subsequent charge — even at a different or reduced amount — triggers a C28 based on the cardholder's belief that the account was fully closed.

---

## Merchant Liability

**Merchant is liable when:**
- The cancellation was submitted and recorded in the merchant's system before the disputed charge date, and the charge was processed after the cancellation effective date.
- The cancellation was submitted through a channel the merchant accepts (email, portal, phone) but was not processed due to a merchant-side error.
- The cardholder contacted customer support to cancel and support staff failed to process the cancellation or route it appropriately.
- The cancellation flow was inaccessible, technically broken, or required unreasonable steps that prevented a reasonable person from completing the cancellation.

**Merchant is NOT liable when:**
- Comprehensive cancellation logs show no cancellation was submitted through any channel during the disputed period.
- The cardholder is disputing a final-period charge after a valid cancellation, and the billing-through-period terms were clearly disclosed at sign-up and confirmed in the cancellation confirmation email.
- The cardholder initiated a new subscription after cancelling and the disputed charges relate to the re-subscription period — these charges are authorized, not post-cancellation.
- The dispute covers charges from before the cancellation date — C28 applies only to post-cancellation charges, not charges from active periods.

---

## Required Evidence

- **Subscription system cancellation log** covering the disputed period, showing no cancellation event was submitted for this account — the log should include timestamps of all account events (sign-up, billing, upgrades, cancellations).
- **Email platform or CRM inbox record** showing no cancellation request email was received from the cardholder's address during the disputed period.
- **Account activity record** showing the account as "active" through the disputed billing date with usage activity during that period (logins, feature access, service consumption).
- **Original sign-up terms and conditions** showing the cardholder agreed at enrollment to: recurring billing, the charge frequency and amount, and the method by which cancellations must be submitted.
- **Pre-billing notification email** sent before the disputed charge (if applicable), showing the cardholder was notified of the upcoming charge and given an opportunity to cancel before it processed.
- **Cancellation confirmation sent to cardholder** (if cancellation was eventually processed), showing the effective date and that all future billing was stopped — relevant if the dispute covers a final-period charge.
- **Billing history** showing all charges to the account with dates, confirming the disputed charge falls within an active subscription period, not after a valid cancellation.

---

## Winning Strategy

The merchant's defense for C28 rests on three pillars: proving the cancellation was not submitted, showing the terms were disclosed, and demonstrating the account was actively used during the disputed period. Pull comprehensive cancellation logs and present them clearly — the log should cover the entire period leading up to the disputed charge, not just the specific billing date.

Supplement the log with account activity records. If the cardholder logged into the platform, accessed content, used features, or engaged with the service between the billing date and the date they claim to have cancelled, this activity is strong evidence that the account was legitimately active and the charge was not a post-cancellation error. Amex evaluators take usage logs seriously — a cardholder who used the product the week before the billing date and then claims the account was cancelled is in a weak evidentiary position.

Show that your cancellation process is compliant with Amex's accessibility requirements. Include a brief description — or screenshot — of your cancellation flow to demonstrate it is findable and operable within the normal account management interface. If Amex has reason to believe your cancellation process is deliberately obstructive, they will side with the cardholder regardless of the log evidence.

---

## Common Mistakes

**No cancellation confirmation emails sent.** Merchants who do not send immediate cancellation confirmation emails — with a reference number, effective date, and final billing date — create C28 disputes. Cardholders who have a confirmation in their inbox almost never file chargebacks; those who do not receive confirmation often dispute because they are genuinely uncertain whether the cancellation went through.

**Cancellation logs purged too quickly.** Subscription systems that delete records of cancelled accounts within 90 days leave merchants unable to respond to C28 disputes that arrive 4–6 months after the cancellation. Retain cancellation records for a minimum of 24 months.

**Making cancellation difficult.** Requiring customers to call during business hours, navigate through aggressive retention flows, or submit cancellation by postal mail are practices that Amex's merchant rules treat as unreasonable barriers to cancellation. These practices generate C28 disputes and are difficult to defend if the cardholder can demonstrate the cancellation process was inaccessible.

**Treating "pause" as equivalent to "cancel" in the cancellation flow.** If the account management page presents "pause subscription" as the first or most prominent option when a cardholder navigates to cancel, and the cardholder selects pause believing it is equivalent to cancellation, the resulting charge is defensible only with clear UI evidence showing "pause" and "cancel" were distinctly labeled.

**Billing through a disputed period without pre-billing notification.** Merchants who do not send pre-billing reminders before each renewal charge miss the most effective single prevention tool for recurring billing disputes. A 3–7 day advance notice email with a cancellation link captures most cancellation intent before the charge occurs.

---

## Timeline

| Milestone | Timeframe |
|---|---|
| Cardholder files dispute with Amex | Within 120 days of the disputed charge date |
| Amex notifies merchant of chargeback | Within a few business days of dispute filing |
| **Merchant response deadline** | **20 calendar days from chargeback notification** |
| Amex issues decision after response | Typically 4–8 weeks |
| Pre-arbitration (if escalated) | Additional 30 days per stage |

Amex's 20-calendar-day response deadline is notably shorter than Visa's and Mastercard's 30–45 day windows, giving recurring billing merchants less time to compile evidence. This makes proactive evidence retention — keeping cancellation logs, billing records, and sign-up terms accessible in a retrievable format — essential operational practice rather than an optional investment.

---

## FAQs

**Q: The cardholder cancelled in Month 5 of a monthly subscription but is disputing charges from Month 3 onward. Can they do that?**
A: No. C28 applies only to charges that occurred after a valid cancellation. Charges from the active subscription period — Months 3 and 4 — are legitimate and should not be included in a C28 dispute. Present your billing history clearly: show each monthly charge with date, the account as active during Months 3 and 4, and the cancellation date in Month 5. Amex should sustain the Month 3 and 4 charges; evaluate whether any Month 5 charge falls after the cancellation date.

**Q: Amex's rules require "easy cancellation." Does that mean we can't have any retention flow?**
A: Light retention flows are acceptable — asking "Are you sure?" or offering a discount before confirming cancellation is not prohibited. What is not acceptable is multi-step flows designed to confuse, contact requirements that are inaccessible (phone-only during limited hours), or mandatory waiting periods before a cancellation takes effect. The test is whether a reasonable customer could reliably cancel within a reasonable time investment. If the answer is no, the cancellation mechanism violates Amex's rules and weakens your C28 defense regardless of the log evidence.

**Q: The cardholder says they emailed us to cancel but we have no email. Who wins?**
A: If your email platform logs show no email received from the cardholder's address during the disputed period, and your CRM shows no cancellation submitted through any channel, you have strong evidence. Include the email log report as a dated, system-generated record. The cardholder's assertion without any evidence of sending — no sent-item timestamp, no read receipt, no follow-up — is difficult to substantiate. The more detailed your log evidence, the stronger your position.

**Q: How does Amex's stance on recurring billing differ from Visa and Mastercard?**
A: Amex is stricter on two dimensions: cancellation accessibility and response timelines. Amex explicitly requires merchants to offer easy, accessible cancellation — not just technically available, but practical for a typical cardholder. Amex also processes disputes faster and gives merchants only 20 days to respond (versus 30–45 for Visa/MC). Additionally, Amex cardholders tend to dispute more readily and more quickly when recurring charges appear unexpected. Merchants in recurring billing models should treat Amex's rules as the compliance baseline for their entire cancellation infrastructure, since meeting Amex standards typically means meeting Visa and MC standards as well.

---

## Key Takeaways

- C28 applies when a subscription or recurring charge was billed after the cardholder cancelled — or when the cardholder claims cancellation occurred and the merchant has no record of it.
- The merchant wins by producing comprehensive cancellation logs showing no cancellation was submitted, combined with account activity records demonstrating the service was actively used during the billed period.
- Amex has stricter recurring billing standards than Visa or Mastercard — merchants must offer accessible, easy cancellation or face losing C28 disputes regardless of log evidence.
- Sending immediate cancellation confirmations with a reference number and effective date is the single most effective C28 prevention tool — cardholders with a confirmation in their inbox rarely dispute.
- Retain cancellation records for a minimum of 24 months; Amex's dispute filing window means disputes can arrive many months after the original charge.
