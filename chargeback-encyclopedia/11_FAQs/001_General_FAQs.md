---
title: "General Chargeback FAQs for Merchants"
category: FAQs
doc_type: faq
audience: merchants
last_updated: 2026-06-01
tags: [chargeback, FAQ, general, merchant, dispute, basics]
---

# General Chargeback FAQs for Merchants

This document answers 25 of the most common chargeback questions merchants ask. Each answer is written to be direct and actionable, without assuming prior knowledge of the card network dispute system.

---

## Q1: What is a chargeback?

A chargeback is a forced reversal of a credit or debit card transaction, initiated by the cardholder's issuing bank on behalf of the cardholder. When a cardholder disputes a charge, the issuing bank debits the funds directly from the merchant's account and returns them to the cardholder while the dispute is being investigated. Unlike a refund, which is voluntary, a chargeback is compulsory — the merchant's account is debited automatically at the time the chargeback is filed, and the merchant must then submit evidence to challenge it. Chargebacks exist as a consumer protection mechanism required by card network rules (Visa, Mastercard, Amex, Discover).

---

## Q2: How is a chargeback different from a refund?

A refund is a voluntary transaction where the merchant returns money to the customer through the original payment method. A chargeback is an involuntary reversal initiated by the cardholder's bank without the merchant's agreement. With a refund, the merchant controls the process and can verify the return of goods or the customer's reason before issuing it. With a chargeback, the funds are taken from the merchant first, and the merchant must fight to recover them. Chargebacks also carry additional fees ($15–$100 per dispute), affect the merchant's chargeback ratio, and can result in account termination if they exceed network thresholds — none of which apply to voluntary refunds.

---

## Q3: How long do I have to respond to a chargeback?

Response deadlines depend on the card network. Visa disputes under VCR (Visa Claims Resolution) typically allow 30 calendar days from the chargeback date. Mastercard typically allows 45 calendar days. American Express is often 20 days. Your acquirer (the bank that processes your payments) may set internal deadlines shorter than the network deadline — always check the deadline on your chargeback notice, not a general rule. Missing the deadline forfeits your right to dispute and the funds are permanently lost to you, so monitoring your chargeback queue daily is critical.

---

## Q4: What happens if I don't respond to a chargeback?

If you do not respond within the deadline, the chargeback is automatically decided in the cardholder's favor and the funds are permanently reversed to the cardholder. You also retain the chargeback fee regardless of outcome. Non-response still counts against your chargeback ratio (the percentage of transactions disputed), which card networks monitor. A high chargeback ratio from uncontested disputes can push you into a monitoring program, ultimately threatening your merchant account. Even for small amounts where fighting seems impractical, consider submitting minimal evidence to register a response and keep your response rate above zero.

---

## Q5: Can I contact the cardholder directly during a chargeback?

Generally no, and you should not try. Once a cardholder has filed a formal dispute through their bank, all communication is supposed to flow through the dispute channel (issuer → acquirer → merchant). Contacting the cardholder directly can be seen as harassment, may violate card network rules, and could expose you to FDCPA or consumer protection liability depending on your jurisdiction. The one exception is if your acquirer or the card network's rules explicitly allow "goodwill resolution" — reaching out to offer a refund before the dispute is formally filed (as is done via Verifi CDRN or Ethoca alerts, which are pre-chargeback alert services). After the formal chargeback is filed, do not contact the cardholder.

---

## Q6: Why did I lose a chargeback I should have won?

Several reasons contribute to unexpected losses. The most common are: submitting evidence that doesn't directly address the reason code (e.g., using delivery proof for a "not as described" dispute); missing or unlabeled exhibits; submitting after the deadline; or relying on evidence that the issuer cannot independently verify (screenshots from your own systems with no external validation). Issuers also apply their own internal standards, which vary between banks. If you lost a dispute with strong evidence, review the rejection notice carefully for the specific reason cited, then consider whether pre-arbitration escalation is warranted.

---

## Q7: Can I blacklist a customer who filed a chargeback?

Yes, you can refuse future business from a cardholder who abused the chargeback process. Most platforms support blocking an email address, shipping address, or device from making future purchases. You cannot, however, charge a penalty, report them to credit bureaus, or take adverse action based solely on the fact that they filed a chargeback (which is a protected consumer right). Be cautious about blocking based solely on one chargeback — distinguish between customers who filed legitimate disputes and those with a clear pattern of abuse before placing them on an internal do-not-sell list.

---

## Q8: What is a chargeback ratio and why does it matter?

Your chargeback ratio is the percentage of your total monthly transactions that resulted in chargebacks. The standard formula is: number of chargebacks in a month ÷ number of transactions in the same month × 100. Visa measures dispute ratios at the 0.9% threshold (Standard) and 1.8% threshold (Excessive). Mastercard measures at 1% (100+ chargebacks) and 1.5% (300+ chargebacks). Exceeding these thresholds places you in a monitoring program, which carries monthly fines and the risk of losing your merchant account if you do not remediate within the program's review window.

---

## Q9: What is the MATCH list?

MATCH (Member Alert to Control High-Risk Merchants) is a database maintained by Mastercard and accessed by all major acquirers. If your merchant account is terminated for excessive chargebacks, fraud, or other violations, your acquirer is required to add you to the MATCH list. Once listed, nearly every acquirer will decline your application for a new merchant account. Listings remain on MATCH for 5 years and are extremely difficult to remove. The MATCH list is the most severe consequence of prolonged chargeback problems and the primary reason maintaining a compliant chargeback ratio matters.

---

## Q10: Can I charge a fee to customers who file chargebacks?

In most jurisdictions, you cannot charge a fee specifically for filing a chargeback. Chargebacks are a legal consumer right, and penalizing consumers for exercising that right can violate consumer protection laws. Some merchants include language in their Terms of Service reserving the right to pursue the cost of a chargeback (the dispute fee) through a collections process for cases that are clearly abusive, but this is legally complex and rarely practical to enforce for small amounts. If you want to deter chargebacks, focus on making voluntary refunds and customer service resolution easy and prominent.

---

## Q11: Why am I getting chargebacks on transactions from months ago?

Cardholder dispute filing deadlines are defined by card network rules and, in some cases, consumer protection laws. Under Visa's rules, a cardholder typically has up to 120 days from the transaction date (or 120 days from the expected delivery date for goods) to file a dispute. Mastercard allows similar windows. State and federal consumer protection laws can extend this further. Practically, this means you may receive a chargeback for a transaction that is 3–4 months old. This is why evidence preservation is critical: keep all transaction records, delivery confirmations, and correspondence for a minimum of 18–24 months.

---

## Q12: What is the difference between pre-arbitration and arbitration?

When a merchant submits a rebuttal (representment/Second Presentment) and the issuer still sides with the cardholder, the issuer files a pre-arbitration (Visa) or "second chargeback" (Mastercard). Pre-arbitration is a formal escalation signal: the issuer is saying the merchant's evidence was insufficient. The merchant can then accept the pre-arbitration (concede the dispute) or escalate to arbitration — the card network's final, binding adjudication. Arbitration is expensive ($250–$500 or more in filing fees) and the losing party typically pays additional fees. Only escalate to arbitration if the disputed amount is high and your evidence is very strong.

---

## Q13: Can I win a chargeback without tracking information?

Yes, but it is harder for physical goods. If you have no tracking number, you must rely on alternative delivery evidence: signed delivery confirmation, proof the cardholder's address is a package locker (USPS PO Box with parcel hold), or photographic delivery evidence. For high-value disputes, some carriers retain GPS coordinates of delivery events. You can also attempt to shift focus to authentication evidence (AVS, CVV, 3DS) to argue the transaction was authorized even if delivery proof is absent. For digital goods, tracking is irrelevant — use download logs, email delivery records, and IP geolocation instead.

---

## Q14: What is 3-D Secure and does it prevent chargebacks?

3-D Secure (3DS) is an authentication protocol that adds an additional verification step at online checkout, requiring the cardholder to authenticate directly with their issuing bank via a one-time passcode, biometric, or push approval. A fully authenticated 3DS transaction (ECI 05 for Visa, ECI 02 for Mastercard) shifts liability for fraud chargebacks from the merchant to the issuing bank. This means if a cardholder files a fraud dispute on a 3DS-authenticated transaction, the issuer is responsible — the merchant wins automatically. However, 3DS does not prevent non-fraud disputes (not received, not as described, cancelled recurring), which are not covered by the liability shift.

---

## Q15: How does friendly fraud work?

Friendly fraud occurs when a legitimate cardholder makes a purchase, receives and often uses the goods or service, then files a chargeback claiming they never authorized the transaction or never received the item. The "friendly" label is a misnomer — it is deliberate consumer fraud. It is common because: (1) many cardholders believe chargebacks are a guaranteed refund mechanism; (2) issuers typically side with their cardholder in disputes; and (3) merchants often do not respond to small-value disputes. To defend against friendly fraud, collect device fingerprints, IP addresses, post-delivery usage logs, and prior purchase history — all of which can demonstrate that the genuine cardholder made and benefited from the transaction.

---

## Q16: What happens after I submit my rebuttal?

After submission, your acquirer forwards your evidence package to the issuing bank. The issuer's chargeback analyst reviews your response, typically within 30–60 days. If the issuer accepts your representment, the funds are reversed back to your account. If the issuer rejects your representment, you receive a pre-arbitration notice (Visa) or second chargeback (Mastercard) and must decide whether to accept the loss or escalate to arbitration. The entire process from initial chargeback to final resolution can take 60–120 days for simple disputes and longer for arbitration cases.

---

## Q17: Does winning a chargeback lower my chargeback ratio?

Unfortunately, no. Your chargeback ratio counts every chargeback filed against you, regardless of outcome. A chargeback that you win through representment still counts as a chargeback in your ratio. This is why prevention — stopping chargebacks from being filed in the first place — is more effective than fighting them after the fact. Services like Verifi CDRN (Visa) and Ethoca Alerts (Mastercard) alert you before the formal chargeback is filed, giving you a chance to refund and stop the chargeback from ever entering the count.

---

## Q18: What is a retrieval request?

A retrieval request (also called an inquiry) is an older mechanism — now largely obsolete under Visa's VCR system — where an issuer asked the merchant for a copy of the transaction record before deciding whether to file a chargeback. Under Visa's current VCR framework, most retrievals are replaced by direct dispute filings. Mastercard still uses retrieval requests in limited situations. If you receive a retrieval request, respond promptly with the transaction receipt and documentation even if no chargeback has been filed yet. Failure to respond to a retrieval request often leads to an automatic chargeback.

---

## Q19: Can I fight a chargeback if I already issued a partial refund?

Yes. If you issued a partial refund, include the refund amount in your rebuttal and dispute only the remaining amount. Note in your letter that the partial refund was issued for [REASON] and that the remaining balance represents the valid portion of the transaction. Include the refund confirmation (ARN or credit reference number) as an exhibit. Card networks typically allow disputes for the net amount after any credits.

---

## Q20: What is a double refund?

A double refund occurs when a merchant voluntarily refunds a customer and the customer then also files a chargeback for the same transaction, resulting in the customer receiving the money twice. This is a form of consumer fraud. If you have already refunded a customer and then receive a chargeback for the same transaction, respond immediately with proof of the refund (the credit ARN and date) and request the chargeback be reversed. Include a letter explaining the double refund scenario. Card networks have clear rules against double recovery by cardholders.

---

## Q21: Do chargebacks affect my processing fees?

Indirectly, yes. A high chargeback ratio can push you into a high-risk merchant category, causing your processor to increase your interchange-plus or flat-rate pricing, add a rolling reserve, or require a dedicated high-risk payment processor with higher per-transaction fees. Being placed on a card network monitoring program (VDMP, Mastercard ECP) also adds monthly fines that function as an additional cost per chargeback transaction. Long-term, chronic chargeback problems can increase your effective cost of payment acceptance significantly.

---

## Q22: Can I be removed from the MATCH list?

Removal from the MATCH list before the 5-year expiration is extremely rare. The only grounds for removal are: the placement was made in error (factual mistake by the placing acquirer); the reason for placement no longer applies (e.g., a fraud conviction was reversed); or the cardholder disputes underlying the placement were overturned. To pursue removal, you must contact the acquirer that placed you on the list and provide evidence supporting the removal request. The placing acquirer has discretion — they are not obligated to remove you. Legal counsel specializing in payment disputes may be required.

---

## Q23: What is a chargeback fee?

A chargeback fee is a flat fee your acquirer or processor charges you each time a chargeback is filed against your account, regardless of whether you win or lose the dispute. Fees typically range from $15 to $100 per chargeback depending on your processing agreement and risk tier. High-risk merchants often face fees at the upper end of this range. The chargeback fee is separate from the disputed transaction amount — you pay the fee on top of losing the transaction value if you lose the dispute. Some acquirers also charge additional fees for pre-arbitration and arbitration filings.

---

## Q24: Is it worth fighting low-value chargebacks?

The decision depends on your win rate, average order value, and chargeback fee. A rough rule: if the disputed amount plus the chargeback fee exceeds the cost of preparing and submitting a response, it is worth fighting — especially if your evidence is strong. However, even low-value disputes are worth responding to because: (1) a non-response pattern signals to fraudsters that your business is easy to exploit; (2) every chargeback counts against your ratio regardless of outcome; and (3) some acquirers offer template-based response tools that reduce the effort cost of responding to small disputes. Consider the portfolio impact, not just the individual dispute economics.

---

## Q25: What is Visa's Compelling Evidence 3.0 (CE3.0)?

Visa's Compelling Evidence 3.0, effective April 2023, is a framework that allows merchants to challenge Visa 10.4 (fraud) chargebacks by demonstrating that the disputed transaction matches two or more prior undisputed transactions from the same cardholder. Specifically, the merchant must show that the disputed transaction shares at least two matching data elements — such as the same device fingerprint plus the same IP address, or the same shipping address plus the same device fingerprint — with two prior transactions that were not disputed within the preceding 365 days. If the CE3.0 criteria are met, the dispute effectively shifts liability back to the issuing bank. This framework significantly strengthens the merchant's hand in fighting friendly fraud on the Visa network.
