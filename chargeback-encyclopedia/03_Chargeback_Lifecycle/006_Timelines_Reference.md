---
title: "Chargeback Timelines Reference: Every Deadline by Network"
section: "03_Chargeback_Lifecycle"
category: "Chargeback Lifecycle"
document_type: "Reference"
keywords: ["chargeback deadline", "chargeback timeline", "response deadline", "Visa deadline", "Mastercard deadline", "Amex deadline", "Discover deadline", "dispute window", "calendar calculation chargeback"]
difficulty: "Beginner"
---

# Chargeback Timelines Reference: Every Deadline by Network

Missing a chargeback deadline by even one day means an automatic, irrecoverable loss — no matter how strong your evidence is. Card networks enforce these windows absolutely, without exceptions or appeals based on oversight. Every chargeback program, at every business, must maintain a deadline tracking system as its first operational requirement. This reference document provides every key timeline, by network, at every stage of the dispute process.

## Why Deadlines Are Absolute

In the chargeback ecosystem, deadlines are not guidelines — they are hard cutoffs built into card network rules. When a deadline passes without action:

- **Merchant response deadline missed:** The chargeback is automatically accepted. Funds are permanently debited from your account. No representment can be submitted after the deadline.
- **Pre-arb response deadline missed:** The pre-arbitration is automatically accepted. No escalation to arbitration is possible.
- **Arbitration filing window missed:** The pre-arb outcome is final. No arbitration is available.

There are no extensions, no grace periods, and no exceptions for holidays, weekends, or system outages unless the network itself issues a formal extension notice (which is extremely rare and only occurs in documented system failures). This is not a system designed with merchant convenience in mind — it is designed to prevent indefinitely open disputes. You must build around it.

## Cardholder Dispute Window

This is the window during which a cardholder can file a chargeback with their issuer after the original transaction. Once this window closes, the issuer cannot accept a new chargeback on that transaction.

| Network | Standard Window | Exceptions |
|---|---|---|
| Visa | 120 days from transaction date (or from when goods/services were expected) | Can extend to 540 days for recurring billing disputes or delayed delivery claims |
| Mastercard | 120 days from transaction date or date of last communication with merchant | Same practical maximum in most cases |
| American Express | 120 days from transaction date | Shorter in practice for some dispute types |
| Discover | 120 days from transaction date | Consistent with major networks |
| RuPay | 30–90 days depending on dispute type | Shorter windows than US networks |

**Practical note for merchants:** The 120-day window starts from when the cardholder *expected* to receive the goods, not necessarily the transaction date. For pre-orders, subscriptions, or delayed delivery, this window can extend further than merchants often expect. A cardholder who ordered a product in January for April delivery could dispute as late as August.

## Merchant Response Window (First Representment)

This is your most critical deadline — the window within which you must submit your representment evidence after receiving a chargeback notification from your acquirer.

| Network | Response Window | Notes |
|---|---|---|
| Visa | 30 days from chargeback notification date | Your acquirer may impose an internal deadline 5–7 days earlier |
| Mastercard | 45 days from chargeback notification date | Acquirer internal deadline often 7–10 days earlier |
| American Express | 20 days from chargeback notification date | Tightest deadline — act immediately upon receipt |
| Discover | 30–45 days from chargeback notification date | Varies by dispute type and acquirer |

**American Express is the fastest network and the least forgiving.** Amex operates its own issuing bank for most consumer cards, which accelerates its internal processing. Merchants with Amex chargebacks must treat every notice as urgent and submit within the first 10–15 days to leave room for acquirer processing.

## Pre-Arbitration Response Window

After the issuer files pre-arbitration (rejecting your representment), you have a narrow window to respond — either by accepting the loss or escalating to arbitration.

| Network | Pre-Arb Response Window | Notes |
|---|---|---|
| Visa | 10–30 days from pre-arb notification | Varies by acquirer's internal processing time |
| Mastercard | 30 days from pre-arb notification | Relatively consistent |
| American Express | 10–20 days | Typically shorter; confirm with acquirer |
| Discover | 20–30 days | Confirm exact window with acquirer |

## Arbitration Filing Window

If you decide to escalate from pre-arbitration to arbitration, there is a window within which your acquirer must formally file the arbitration case with the card network.

| Network | Arbitration Filing Window | Notes |
|---|---|---|
| Visa | 10 days after the pre-arb response deadline | The acquirer, not the merchant, files — so your instruction must arrive with time for the acquirer to act |
| Mastercard | 45 days after pre-arb deadline (varies) | Check current rules with acquirer |
| American Express | 10 days | Very tight; instruct acquirer immediately |
| Discover | 20 days | Confirm with acquirer |

**The arbitration filing window is deceptive.** It is the acquirer's filing window, not yours. You need to instruct your acquirer to escalate before their internal cutoff — which may be 2–5 days before the network deadline. The practical rule: decide to escalate and notify your acquirer the moment you receive the pre-arb notice.

## Compliance Filing Window

If filing compliance based on a procedural rule violation, the window runs from when you knew or could have known of the violation.

| Network | Compliance Filing Window |
|---|---|
| Visa | 10–45 days from the date of the violation or date you received notice of the violation |
| Mastercard | 45 days from the date of the rule violation |
| American Express | 20–30 days (confirm with acquirer) |

## Refund and Credit Timing Windows

These are often overlooked but equally important. Cardholders generally cannot file a chargeback on a transaction if a refund is still processing — but networks have rules about when a refund must post before a chargeback can be filed.

| Network | Cardholder Must Wait After Refund |
|---|---|
| Visa | 15 calendar days after the merchant issues a credit |
| Mastercard | 15 calendar days after the merchant issues a credit |
| American Express | 15–30 days |
| Discover | 15 days |

If a cardholder files a chargeback before this waiting period has elapsed after your refund, the chargeback may be procedurally improper — grounds for a compliance filing.

## Comprehensive Timeline Summary Table

| Stage | Visa | Mastercard | American Express | Discover |
|---|---|---|---|---|
| Cardholder dispute window | 120 days | 120 days | 120 days | 120 days |
| Merchant response deadline | 30 days | 45 days | **20 days** | 30–45 days |
| Pre-arb response window | 10–30 days | 30 days | 10–20 days | 20–30 days |
| Arbitration filing window | 10 days | 45 days | 10 days | 20 days |
| Compliance filing window | 10–45 days | 45 days | 20–30 days | Varies |
| Refund wait before chargeback | 15 days | 15 days | 15–30 days | 15 days |

## Calendar Calculation Tips

### How to Count Chargeback Days

Card network deadlines are counted in **calendar days** (not business days) unless your acquirer's agreement specifies otherwise. Saturdays, Sundays, and public holidays are included in the count.

**Step 1:** Identify the notification date on the chargeback notice — this is typically the date the notice was transmitted by your acquirer, not the date the issuer filed the chargeback.

**Step 2:** Add the applicable network deadline in calendar days. Day 1 is typically the day after the notification date, but confirm with your acquirer.

**Step 3:** If the deadline falls on a weekend or holiday, do not assume you get the next business day. Some acquirers enforce the calendar deadline regardless. Submit before the weekend/holiday, not after.

**Step 4:** Subtract your acquirer's internal processing time (typically 2–7 business days) from the network deadline to get your actual internal submission deadline.

**Practical example:**
- Chargeback notification received: March 1
- Visa deadline: 30 calendar days = March 31
- Acquirer internal deadline (5 business days early): March 24
- Your target submission date: March 17 (leaves a 5-day buffer before acquirer's cutoff)

### Building a Tracking System

At minimum, every chargeback management system should record:
1. Date the chargeback notice was received
2. Network (Visa/Mastercard/Amex/Discover)
3. Calculated acquirer internal deadline
4. Calculated network deadline
5. Actual submission date
6. Pre-arb notice date (if received)
7. Pre-arb response deadline
8. Decision outcome and date

Use calendar software to set reminders at notification date, 50% of the response window, and 3 days before the internal acquirer deadline. Do not rely on email alone.

---

## Frequently Asked Questions

**Q: I missed my representment deadline by two days. Is there any way to recover?**
A: No. Missing the representment deadline means the chargeback is automatically accepted with no recourse through the card network dispute system. The only theoretical avenue is if the acquirer made an error in reporting the deadline date — in that case, the acquirer may bear liability for the missed deadline. Document everything and consult your acquirer immediately.

**Q: Do chargeback deadlines pause if my acquirer's system is down?**
A: Generally, no — unless the card network issues a formal extension notice for a documented system-wide outage. Do not assume your acquirer's outage pauses the clock. If you cannot submit through the portal due to a system issue, escalate to your acquirer by phone and email immediately, documenting the outage. They may be able to process your submission manually within the window.

**Q: Why does American Express have such a short response window?**
A: American Express operates as both the card network and the issuing bank for most consumer cards. This integrated structure allows Amex to process disputes much faster than Visa or Mastercard, where multiple banks are involved. The 20-day window reflects their streamlined internal process — and it requires merchants to match that speed.

**Q: If a cardholder disputes a transaction 130 days after the purchase, is that valid?**
A: Not for most dispute types on most networks. The standard cardholder window is 120 days. However, the clock starts from when the cardholder expected delivery or service completion — not necessarily the transaction date. For delayed deliveries, subscriptions, or travel booked far in advance, the window may extend further. If you believe a chargeback was filed outside the allowable window, file a compliance case documenting the original transaction date and cardholder expected delivery date.

**Q: Can my acquirer give me more time to respond if I need it?**
A: No acquirer can extend the card network's hard deadline. Some acquirers have internal buffer periods built in — they set your internal deadline earlier than the network deadline — and they can sometimes "adjust" their internal deadline while still meeting the network's. Never rely on this. Always work to your earliest known deadline.
