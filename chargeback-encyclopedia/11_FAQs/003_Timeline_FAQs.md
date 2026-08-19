---
title: "Chargeback Timeline and Deadline FAQs"
category: FAQs
doc_type: faq
audience: merchants
last_updated: 2026-06-01
tags: [timeline, deadline, chargeback, response window, FAQ]
---

# Chargeback Timeline and Deadline FAQs

These 15 questions cover the timing of the chargeback process — from when a cardholder can file to how long the full cycle takes from dispute to resolution.

---

## Q1: How many days do I have to respond to a chargeback?

Response windows depend on the card network and are counted from the chargeback date (the date the dispute was formally filed by the issuing bank). Standard windows are: **Visa (VCR):** 30 calendar days; **Mastercard:** 45 calendar days; **American Express:** 20 calendar days; **Discover:** 30 calendar days. These are the network-level maximums. Your acquiring bank typically has an internal deadline that is 2–5 days shorter than the network deadline to allow processing time. Always use the deadline shown on your chargeback notification, not a generalized rule. For disputes managed through your acquirer's portal, the portal countdown timer reflects the acquirer's internal deadline.

---

## Q2: What happens if I miss the chargeback deadline?

If you miss the response deadline, your right to dispute is permanently forfeited for that transaction. The chargeback is resolved in the cardholder's favor, the funds are permanently reversed, and the chargeback fee is retained by your acquirer. There is no mechanism to submit a late response once the deadline has passed — the card networks do not allow extensions after expiration. The chargeback is still counted against your chargeback ratio. In rare cases where the deadline was missed due to a documented acquirer system failure (not merchant delay), you may have grounds to request the acquirer re-open the case, but this is exceptional and not guaranteed.

---

## Q3: How long does the chargeback process take from start to finish?

A straightforward dispute that the issuer resolves in your favor after a single representment typically takes 60–75 days from the initial chargeback date. Cases that proceed to pre-arbitration extend the timeline by another 30–45 days. Full arbitration cases (heard by the card network) can take 4–6 months from the initial chargeback date. During this entire period, your funds remain with the cardholder — you are effectively extending interest-free credit to the person who filed the dispute. Cases where the merchant accepts the loss (no representment) close in 30–45 days. The clock restarts at each stage, so escalated disputes are resolved over a 3–6 month window.

---

## Q4: When will my account be debited for a chargeback?

Your merchant account is debited for the disputed amount at the time the chargeback is filed by the issuing bank — typically 5–10 business days after the cardholder initiates the dispute with their bank. You do not receive advance notice before the debit; the chargeback notification and the account debit happen simultaneously or very close together. The chargeback fee is also debited at this time. If you win the representment, the funds are credited back to your account, but the chargeback fee is generally not refunded regardless of outcome.

---

## Q5: How long does the cardholder have to file a dispute?

The cardholder's filing window depends on the card network and the dispute type. Under Visa's rules, the standard window is **120 calendar days** from the transaction date for most dispute types, and 120 days from the expected delivery date for "not received" disputes (which can push the window to 540 days total from the transaction date if estimated delivery dates are used). Mastercard also uses a 120-day window from transaction date in most cases. Consumer protection laws in some jurisdictions (e.g., the Fair Credit Billing Act in the US) set a 60-day window from the billing statement date, which for credit cards typically adds another billing cycle. This is why merchants receive chargebacks on transactions that are 3–4 months old.

---

## Q6: Can I get an extension on my response deadline?

No. Card network rules do not provide for extensions, and acquirers cannot grant extensions on behalf of the network. If you anticipate difficulty responding in time (e.g., your evidence is at an off-site location, or a key staff member is unavailable), submit whatever evidence you have now and supplement with a note, then follow up with additional materials if the acquirer allows it before the formal deadline. Some acquirer portals allow multiple uploads before the deadline. Never miss the deadline waiting for perfect evidence — a partial response is better than no response. For ongoing operations, build a chargeback response process that does not depend on a single individual.

---

## Q7: How long does it take to hear back after I respond?

After you submit your representment, the acquirer forwards it to the issuing bank. The issuer has its own review period — typically 30–45 days for the first review, depending on the network. During this time, you will likely not receive any update. If the issuer accepts your representment, you will receive a credit notification from your acquirer (often called a "chargeback reversal" or "win notification"). If the issuer rejects your representment, you will receive a pre-arbitration notice. In total, expect 30–60 days to hear back after you submit. Monitor your acquirer's dispute management portal for status updates rather than waiting for email notifications, which can be delayed.

---

## Q8: What is the timeline for a pre-arbitration dispute?

After a representment is rejected, the issuer files a pre-arbitration notice. You typically have 30 days from this pre-arbitration date to accept (concede the dispute) or reject (escalate to arbitration). If you escalate, the arbitration filing must be submitted to the card network within the window specified by the pre-arbitration notice. Arbitration cases are then heard by the card network's arbitration body, which issues a binding decision — typically within 30–45 days of the arbitration filing. Total elapsed time from initial chargeback to arbitration decision: 4–6 months.

---

## Q9: Is there a deadline for the issuing bank to file the initial chargeback?

Yes. Issuers must file a chargeback within their own internal service levels after receiving the cardholder's dispute. Under Visa's VCR rules, issuers must file the chargeback within 30 days of receiving the dispute from the cardholder. However, issuers sometimes batch-file disputes, and the cardholder's 120-day filing window effectively sets the outer boundary. As a practical matter, merchants typically receive the chargeback notification 5–15 days after the cardholder files the initial dispute with their bank. The gap between when the cardholder reports the problem and when the merchant gets notified is one of the key reasons merchants need to move quickly once a chargeback notification arrives.

---

## Q10: Do deadlines change for international transactions?

Not significantly for card network deadlines, which are global standards. However, if your acquirer is in a different country from the issuer, transmission delays through correspondent banking or cross-border processing systems can occasionally affect how quickly you receive the chargeback notification. This effectively compresses your response window. Merchants processing significant international volumes should monitor chargeback queues more frequently and ensure their acquirer provides same-day notification of new chargebacks. Currency conversion chargebacks (where the cardholder disputes the exchange rate applied) may follow slightly different timing rules depending on the network.

---

## Q11: How long do I need to retain transaction records?

For chargeback defense purposes, retain all transaction records, delivery confirmations, customer communications, and order data for a minimum of **18 months** from the transaction date. Given the Visa 120-day filing window plus the 6-month representment and arbitration process, an 18-month retention period covers essentially all open dispute risk. For compliance and accounting purposes, most financial regulations require retention of at least **7 years** (US IRS, EU VAT, PCI DSS guidance). If you are subject to GDPR, note that data minimization principles require you to balance retention needs against cardholder privacy rights — retain only what is needed and document your legal basis for retention.

---

## Q12: What is the timeline for a Verifi CDRN or Ethoca alert?

Verifi CDRN (Visa) and Ethoca Alerts (Mastercard) are pre-chargeback services that notify merchants of a cardholder's dispute before the formal chargeback is filed. The alert is typically delivered within 24–72 hours of the cardholder contacting their bank. The merchant typically has **24 hours** to decide whether to refund (which stops the formal chargeback from being filed) or let the dispute proceed. This 24-hour window is your best opportunity to avoid the chargeback entirely — a refund issued within the alert window removes the dispute from the chargeback queue before it is counted against your ratio.

---

## Q13: At what point in the transaction lifecycle is a chargeback possible?

A chargeback can be filed after the transaction has cleared (settled). For authorization holds that are never settled (e.g., hotel pre-authorization released), no chargeback applies. Once a transaction settles — typically 1–3 business days after the authorization — it is eligible for dispute. The cardholder's filing window begins from the transaction date or the billing statement date, not from authorization. This means a same-day purchase that settles on day 2 can be disputed for up to 120 days following settlement (or 120 days from the delivery date for goods disputes).

---

## Q14: Does the deadline differ for physical vs. digital goods?

Yes, in one significant way. For disputes filed under "merchandise not received" (Visa 13.1, Mastercard 4853), the cardholder's filing window begins from the **expected delivery date**, not the transaction date. For digital goods with immediate delivery, the expected delivery date is effectively the purchase date, so the 120-day window starts immediately. For physical goods with extended shipping estimates (e.g., international shipping with a 30-day estimate), the 120-day cardholder window begins 30 days after purchase — effectively giving the cardholder 150 days from the transaction date to file. Always note the product's advertised delivery window on your order confirmation, as this date can affect when the merchant's defense must be filed.

---

## Q15: What is the fastest a chargeback dispute can be resolved in my favor?

In the best case, an issuer reviews your representment and decides in your favor within 10–15 business days. This happens when the evidence is very clear (e.g., 3DS full authentication on a fraud dispute — the issuer accepts immediately because liability has already shifted). In practice, most winning representments take 30–45 days to result in a credit back to your account. Same-day or next-day resolution is exceptionally rare. For Verifi/Ethoca alerts (pre-chargeback), issuing a refund within the alert window stops the dispute instantly — the chargeback is never filed and no waiting period applies. This is why pre-chargeback alert programs are the fastest path to dispute resolution.
