---
title: "Best Practices for Travel and Hospitality Merchants — Chargeback Prevention"
category: Best Practices
doc_type: industry-guide
industry: Travel, Hotel, Airline, Hospitality
audience: merchants
last_updated: 2026-06-01
tags: [travel, hotel, airline, hospitality, no-show, cancellation, best practices, chargeback]
---

# Best Practices for Travel and Hospitality Merchants: Chargeback Prevention

## The Travel Chargeback Landscape

Travel and hospitality merchants operate in one of the highest chargeback-volume industries. The combination of advance booking (time gap between payment and service), significant per-transaction values, non-refundable rates, and subjective service quality creates a high-risk environment. Key chargeback categories for this industry:

- **MC 4855 / Visa 13.1:** "I never received the service" — claimed no-shows, denied check-ins, cancelled flights.
- **MC 4853 / Visa 13.3:** "Service not as described" — room quality, flight experience below expectations.
- **MC 4837 / Visa 10.4:** Unauthorized booking — stolen card used to book travel.
- **MC 4853 (Recurring):** Disputed advance deposit or membership charges.

---

## Hotel and Lodging: Evidence Capture Best Practices

### At Check-In

The signed guest registration card is the most critical evidence document for hotel chargebacks. Every check-in must produce:

- **Signed registration card** showing the guest's name, room assignment, nightly rate, and acknowledgment of policies (charges, cancellation, no-show).
- **PMS entry** recording check-in date/time, room number, and staff member ID.
- **Pre-authorization record** for incidentals — the authorization code and amount authorized.
- **ID verification** — for high-value bookings, record that ID was presented (not the ID number itself, due to privacy rules).

Scan and archive registration cards digitally immediately after checkout. Physical cards should be retained for 18 months. A misfiled or destroyed registration card loses the most important piece of evidence for hotel dispute defense.

### During Stay

- Log any room changes or upgrades in the PMS with the reason (guest request, maintenance issue, etc.).
- Log any guest complaints received at the front desk with timestamps and resolution.
- Log key card access events if your PMS integrates with the door lock system — room entry records prove the guest occupied the room.
- Log loyalty program activity: points earned or redeemed during the stay. Loyalty points cannot be earned on a no-show.

### At Check-Out

- The guest signature or PIN on the checkout folio serves as acknowledgment of all charges.
- For express checkout (key drop, no-contact): retain the PMS checkout record with timestamp.
- Preserve the full folio (itemized charges) for 18 months.

---

## No-Show Policy and Cancellation Terms

No-show disputes are among the most common hotel chargebacks. Defense requires:

### Policy Disclosure

The no-show policy must appear in:
1. The booking page before the guest confirms the reservation.
2. The reservation confirmation email (verbatim, not just a link).
3. The pre-arrival reminder email.

A no-show policy that appears only in Terms of Service linked from the footer does not meet the disclosure standard. The policy language must be visible and specific: "Failure to cancel by [TIME] on [DATE] or failure to arrive will result in a charge of [AMOUNT/NIGHTS] to the credit card on file."

### Pre-Arrival Reminder

Send a pre-arrival reminder 48–72 hours before the check-in date including:
- The reservation details
- The cancellation deadline (if still applicable)
- The no-show policy
- A contact number to modify or cancel

This reminder email, and the ESP record showing it was delivered, is powerful evidence that the guest was notified of the policy immediately before the stay date.

### When No-Show Occurs

When a guest does not arrive:
1. Attempt to contact the guest via the phone number and email on the reservation.
2. Log the contact attempts with timestamps.
3. Hold the room until a defined time (e.g., midnight).
4. Record the no-show in the PMS with timestamp.
5. Apply the no-show charge per the disclosed policy.
6. Send a no-show confirmation email to the guest explaining the charge.

The contact attempts and the no-show PMS record are essential evidence if the guest later disputes the charge.

---

## Third-Party and OTA Booking Management

Bookings made through OTAs (Expedia, Booking.com, Hotels.com, Airbnb) create additional complexity:

- Verify that the OTA's displayed cancellation policy matches your hotel's actual policy — discrepancies create dispute liability.
- For OTA disputes, obtain the booking reference, guest name, card last four, and email address from the OTA and match to your property's records.
- Understand whether the OTA charged the guest (OTA merchant model) or your hotel charged the guest (agency model) — the chargeback will be routed to whichever entity processed the charge.
- If the OTA processed the charge, the chargeback dispute is the OTA's responsibility, not the hotel's — however, the hotel must cooperate in providing check-in records.

---

## Advance Deposit Handling

Hotels that collect advance deposits (partial or full payment at booking) must:

- Clearly disclose that the deposit is non-refundable (or state the refund policy) at the time of booking.
- Send a booking confirmation with the deposit amount and refund terms explicitly stated.
- Issue a separate folio entry for the deposit amount and the balance due at check-in.
- If the deposit is later applied to the stay, document the credit on the final folio.
- If the reservation is cancelled and the deposit is forfeited per policy, send a written confirmation of the forfeiture citing the policy the guest accepted.

---

## Airline and Transportation: Evidence Capture Best Practices

### PNR Documentation

The Passenger Name Record (PNR) in your reservation system is the central evidence document for airline disputes:

- Retain PNR records for 18 months after the flight date.
- The PNR should show: passenger name, itinerary, booking date, fare class, payment method, and fare rules.
- For disputes: export the full PNR with booking history (any changes or cancellations made) and the check-in / boarding status.

### Fare Rules and Cancellation Policy Disclosure

Non-refundable fare disputes are won or lost based on whether the fare rules were visible to the passenger at purchase:

- Display fare type (Refundable / Non-refundable) prominently on the fare selection page.
- Include the cancellation and change penalty in the booking summary before payment is confirmed.
- Include fare rules verbatim in the booking confirmation email.
- For OTA-booked tickets, obtain the OTA's fare rules display record if possible.

### Boarding Records

When a passenger boards, the boarding scan creates a record in the reservation system. This record (showing boarding gate, boarding time, seat number) is proof of travel. For disputes claiming non-travel:

- Export the boarding record from your reservation or DCS (departure control system) showing the boarding scan event.
- Include the PNR status report showing check-in completed and boarding confirmed.

### Flight Operations Evidence

When a passenger claims a flight was cancelled or significantly delayed to justify a refund:

- Obtain the flight operations record showing actual departure and arrival times.
- OAG, FlightAware, and airline internal operations records are accepted as flight status evidence.
- EU261/2004 (EC261) and DOT regulations govern refund rights for EU and US flights respectively — confirm whether the cancellation or delay triggers a regulatory refund obligation before defending the dispute.

---

## Signed Registration and Guest Communication Workflow

| Stage | Action | Evidence Created |
|---|---|---|
| Booking | Display and confirm cancellation/no-show policy | Booking page screenshot, confirmation email |
| Pre-arrival | Send reminder with policies | Reminder email + ESP delivery record |
| Check-in | Complete signed registration, PMS entry | Signed reg card, PMS record |
| During stay | Log complaints and room changes | CRM/PMS notes with timestamps |
| Check-out | Guest signs folio or express checkout logged | Signed folio or PMS checkout record |
| Post-stay | Retain records 18 months | Document archive |

---

## Corporate and Group Booking Management

Corporate and group bookings have additional chargeback risks:

- **Third-party billing authorization:** When a corporate card holder books rooms but a different person checks in, obtain a signed credit card authorization form from the cardholder before the stay.
- **Master bill disputes:** When multiple rooms are charged to a master folio, ensure each room has a signed registration. One unsigned registration in a group creates a gap in the evidence chain.
- **Direct billing agreements:** Maintain signed copies of direct billing agreements with corporate accounts, as these may be referenced if the corporation disputes charges.

---

## Chargeback Defense Quick Reference for Travel/Hotel

| Reason Code | Scenario | Key Evidence |
|---|---|---|
| MC 4855 (Hotel) | "I didn't check in" | Signed registration card, PMS record |
| MC 4855 (Hotel) | "I didn't authorize the charge" | Signed registration, pre-auth record |
| MC 4855 (No-Show) | No-show charge disputed | No-show PMS record, policy disclosure, contact attempt log |
| MC 4855 (Airline) | "I didn't travel" | PNR boarding record |
| MC 4855 (Airline) | "Flight was cancelled — I want a refund" | Operations record showing flight operated; or if cancelled, compliance with EC261/DOT refund rules |
| MC 4853 | "Not as described" | Booking confirmation (showing room type/rate), photo of room if available, maintenance logs |
| MC 4837 / Visa 10.4 | Unauthorized booking | 3DS auth record, CVV match, IP geolocation, delivery to cardholder's email |
