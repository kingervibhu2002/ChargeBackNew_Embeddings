---
title: "Amex C18 — No-Show / Cancelled Reservation"
section: "06_Amex"
category: "Amex Reason Codes"
network: "American Express"
reason_code: "C18"
document_type: "Reason Code Reference"
keywords: ["no-show", "cancelled reservation", "hotel chargeback", "cancellation policy", "C18", "Amex chargeback", "no-show fee", "OTA booking", "prepaid reservation", "hospitality dispute"]
difficulty: "Intermediate"
---

## Overview

Amex reason code C18 — "No-Show / Cancelled Reservation" — applies when a hotel, airline, or venue charges a no-show fee or cancellation penalty that the cardholder disputes. The cardholder either claims they cancelled within the allowable window and should not have been charged, or they dispute the fee as undisclosed and unexpected. C18 is one of the most common Amex dispute codes in the hospitality and travel industries, where prepaid rates, strict cancellation windows, and automated penalty charges are standard commercial practice.

The fundamental question in every C18 case is twofold: first, was the cancellation policy clearly disclosed to the guest at the time of booking; and second, was a valid cancellation received before the deadline? If the answer to both questions favors the merchant — policy was disclosed and no cancellation was received — the merchant has a strong case. If either element is missing, the dispute is difficult to win.

C18 applies broadly across hospitality and travel: hotel no-show fees, airline non-refundable fare disputes, event venue cancellation charges, and resort prepayment forfeitures. The code may also appear for early departure charges — where a guest checks in but leaves before the end of a non-refundable stay. Each of these sub-types shares the same evidentiary framework: documented policy disclosure plus documented absence of cancellation.

---

## Common Scenarios

**Hotel no-show with policy disclosed.** A guest reserves a hotel room, acknowledges a 48-hour cancellation policy at booking, fails to cancel in time due to a change of plans, and disputes the one-night no-show fee after receiving it on their Amex statement. The merchant has the confirmation email, a cancellation deadline, and no cancellation record — this is a winnable C18.

**Cardholder claims cancellation but no record exists.** The guest believes they cancelled via the hotel's website or by phone, but the hotel's PMS shows the reservation as active through the arrival date and no cancellation was processed. The cardholder may have called and reached voicemail, or used a third-party platform that did not relay the cancellation. This is the most contested C18 scenario and turns on whose records are more credible.

**Policy buried in booking fine print.** A cardholder books a non-refundable rate on a property's website where the cancellation policy appears only in the rate description footer or a terms-and-conditions pop-up, not as a clearly labeled field. The cardholder disputes the fee as undisclosed. Without a booking flow screenshot showing the policy prominently, this is a difficult dispute for the merchant.

**OTA cancellation mismatch.** A guest books through Booking.com or Expedia, cancels through the OTA app, and receives an OTA cancellation confirmation. The OTA's cancellation did not reach the hotel's PMS because the OTA's cancellation window was longer than the hotel's contracted cancellation period. The hotel charges a no-show fee. The guest disputes, believing they followed the correct process.

**Airline non-refundable fare dispute.** A cardholder purchases a non-refundable airline ticket and is charged a change fee or forfeits the ticket value after missing their flight. They dispute the charge under C18, claiming the fee was disproportionate or undisclosed.

---

## Merchant Liability

**Merchant is liable when:**
- The cancellation policy was not disclosed in the booking confirmation — it appeared only in a general terms-and-conditions page not shown during the booking flow.
- The cancellation deadline was expressed ambiguously (e.g., "before arrival" rather than a specific date and time).
- The cardholder submitted a valid cancellation through an OTA and the OTA acknowledged it — even if the hotel did not receive it, this is an OTA coordination failure and the merchant bears the customer-facing liability.
- The cancellation policy shown at booking was shorter or less restrictive than what was charged (e.g., policy said 24 hours but a 72-hour fee was imposed).
- The guest arrived and checked in but was charged a no-show fee — system errors generating a fee for a guest who was actually present.

**Merchant is NOT liable when:**
- The booking confirmation email clearly stated the cancellation deadline, the fee amount, and the method to cancel.
- The cardholder acknowledged a "non-refundable" or "strict cancellation" rate designation at booking.
- No cancellation was received through any channel — PMS, phone log, OTA dashboard, or email — before the cancellation deadline.
- The cardholder is disputing the fee on fairness grounds (e.g., they had an emergency) when the policy was clearly disclosed and no cancellation was submitted.

---

## Required Evidence

- **Booking confirmation email** sent to the cardholder at time of reservation, containing: cancellation deadline as a specific date and time, the no-show or cancellation fee amount, and instructions for how to cancel.
- **Signed registration card or digital check-in acknowledgment** (if the cardholder checked in for a prior stay using the same reservation flow) that references the cancellation policy.
- **Booking flow screenshots** showing the cancellation policy displayed before the cardholder entered payment information — including any checkbox or acknowledgment step confirming the cardholder accepted the policy.
- **PMS reservation log** showing the reservation status as "active" or "no-show" through the arrival date, with no cancellation event recorded.
- **Phone call log or CRM record** showing no incoming cancellation call was received from the guest's phone number during the cancellation window.
- **Email inbox record** showing no cancellation email was received from the guest's address during the applicable period.
- **OTA reservation dashboard export** (if booked via OTA) showing the reservation as uncancelled through the no-show date. If the OTA confirms the cardholder did not submit a cancellation, include that confirmation.
- **No-show fee charge record** matching the amount disclosed in the original booking confirmation.

---

## Winning Strategy

Build your response around three documented facts: the policy was disclosed, the cardholder accepted it, and no cancellation was received. Start with the booking confirmation email — it is the single most important document. If it contains a clear cancellation deadline, the fee amount, and cancellation instructions, you have the core of your defense.

Next, present the absence of a cancellation. Pull the PMS log, phone records, and OTA dashboard simultaneously. If none of these sources contain a cancellation event before the deadline, state this explicitly and attach the reports. Amex evaluators are looking for the same three things any reasonable reviewer would: policy shown, policy acknowledged, no cancellation submitted.

If the cardholder used an OTA to book, contact the OTA immediately when the chargeback arrives and request confirmation of whether a cancellation was submitted through their platform. If the OTA confirms no cancellation, obtain that in writing and include it in your response. If the OTA confirms a cancellation was submitted but not relayed to you, the dispute calculus changes — document whether the OTA's cancellation window matched your contracted cancellation terms and whether the OTA error was foreseeable.

For high-value stays or repeat-customer situations, consider whether a goodwill waiver of the fee costs less than the chargeback fee plus relationship damage. Many hospitality operators waive no-show fees for documented medical emergencies, extreme weather events, or long-term loyal guests — not because they are required to, but because the economics favor retention over recovery.

---

## Common Mistakes

**Ambiguous cancellation deadlines.** Confirmation emails that say "cancel 48 hours before arrival" rather than "cancel before 12:00 PM on [specific date]" are consistently problematic in disputes. Cardholders interpret "before arrival" differently. Always specify the exact date and time.

**No confirmation email archived.** Some small properties send confirmation emails via personal email accounts with no logging. If you cannot produce the email you sent, you cannot prove the cardholder saw the policy.

**OTA cancellation policy not synchronized with hotel policy.** The OTA shows a 24-hour free cancellation window, the hotel's policy is 72 hours. When a guest cancels within 24 hours of arrival, the OTA says "free cancellation" and the hotel charges a fee. This mismatch is the merchant's responsibility to prevent through correct rate plan configuration in the OTA extranet.

**No phone cancellation confirmation process.** If phone cancellation requests are accepted but no confirmation number is issued, the hotel has no way to prove a call did or did not include a cancellation request. Implement a verbal confirmation code for every cancellation handled by phone.

**Charging a fee not matching the disclosed amount.** If the booking confirmation said the no-show fee is "one night's room rate plus tax" and the charged fee includes additional charges, this discrepancy weakens the defense. The charged amount must match what was disclosed.

---

## Timeline

| Milestone | Timeframe |
|---|---|
| No-show occurs / cancellation fee charged | Arrival date or shortly after |
| Cardholder files dispute with Amex | Within 120 days of the transaction date |
| Amex notifies merchant of chargeback | Within a few business days of dispute filing |
| **Merchant response deadline** | **20 calendar days from chargeback notification** |
| Amex decision after merchant response | Typically 4–8 weeks |
| Pre-arbitration (if escalated) | Additional 30 days per stage |

The 20-calendar-day response window is strict. For hospitality operators managing multiple properties or high volumes of reservations, build a workflow to capture evidence the moment a no-show is recorded — PMS log, OTA dashboard status, phone records — so the evidence package is ready if a dispute arrives weeks later.

---

## FAQs

**Q: The guest says they called to cancel but I have no record of the call. How do I win this dispute?**
A: Submit your phone call log or phone system report showing no incoming call from the guest's registered number during the cancellation window. If the guest cannot provide a cancellation confirmation number or timestamp, their claim is difficult to substantiate. Implement a policy of issuing a verbal cancellation reference code on every cancellation call — this single practice eliminates most "I called to cancel" disputes because customers who received a code will use it and customers who never called have no code.

**Q: The guest had a documented medical emergency and could not travel. Should I fight the C18?**
A: This is a business decision rather than a purely legal one. If the guest provides documentation — a hospital record, physician's letter, or similar — consider a discretionary waiver. The cost of the no-show fee is almost always less than the value of a loyal guest and the reputational cost of being seen as inflexible. Many hotel brands maintain a compassionate waiver policy for genuine medical emergencies. Fighting a C18 where the cardholder has documented medical circumstances is winnable on technical grounds but poor for customer relationships.

**Q: We charged a no-show fee but the guest actually checked in at a different property we own. Does this affect the dispute?**
A: Yes, potentially. If the guest did arrive and stay (at another property you own), charging a no-show fee against their Amex is incorrect and you should refund it. If the guest mistakenly went to the wrong property and that is not your error, document clearly that the reserved property was not visited and the fee is valid under the disclosed policy.

**Q: An OTA sent a cancellation confirmation to the guest, but we never received it in our PMS. Who is liable for the no-show fee?**
A: You are, for the cardholder's Amex dispute. The OTA issued a valid cancellation confirmation to your guest, who reasonably believed the cancellation was complete. The fact that the OTA did not properly relay the cancellation to your PMS is a commercial issue between you and the OTA — you should pursue that with the OTA separately. For the chargeback, Amex will side with a cardholder who has a cancellation confirmation from the booking platform they used.

---

## Key Takeaways

- C18 is won by proving three things: cancellation policy was clearly disclosed, the cardholder accepted it, and no valid cancellation was received before the deadline.
- The booking confirmation email containing an explicit cancellation deadline, fee amount, and cancellation instructions is the single most critical document.
- OTA bookings create complexity: if the OTA issued a cancellation confirmation to the guest, Amex will typically side with the cardholder regardless of whether the cancellation reached the hotel's PMS.
- Ambiguous cancellation deadlines ("cancel before arrival") rather than specific dates and times are the leading cause of unwinnable C18 disputes.
- For documented medical emergencies and loyal guests, a discretionary refund is often better economics than fighting the chargeback through formal dispute resolution.
