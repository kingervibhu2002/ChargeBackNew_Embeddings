---
title: "Cardholder: Rights, Roles, and Dispute Behavior"
section: "01_Payment_Ecosystem"
category: "Payment Ecosystem"
document_type: "Reference"
keywords: ["cardholder", "credit card", "debit card", "dispute rights", "chargeback window", "liability shift", "friendly fraud", "issuer protection", "Regulation E", "Fair Credit Billing Act", "FCBA", "cardholder rights"]
difficulty: "Beginner"
---

# Cardholder: Rights, Roles, and Dispute Behavior

The cardholder is the individual or entity that holds a payment card and initiates transactions. From a merchant's perspective, understanding cardholder rights and behavior is essential — because those rights directly translate into your chargeback exposure. Cardholders have strong consumer protections that networks and regulators have built over decades, and merchants bear the cost when those protections are exercised.

## Who Is a Cardholder?

A cardholder is any person authorized to use a payment card account. This includes:

- **Primary cardholders**: The person who applied for and owns the account.
- **Authorized users**: Additional users added to the primary account (a spouse, employee, or family member). Authorized users can initiate chargebacks on the primary account.
- **Corporate cardholders**: Employees issued corporate cards. The corporate entity typically has the dispute relationship with the issuer.

A cardholder presents their card — physically, digitally via NFC/wallet, or via stored credentials for recurring transactions — to initiate a purchase. Once a transaction is authorized and settled, the cardholder receives a statement entry. Disputes begin when the cardholder contacts their issuing bank to challenge a charge.

## Credit Cards vs. Debit Cards

The type of card determines the regulatory framework protecting the cardholder, which affects how disputes are processed.

### Credit Cards
Credit card disputes are governed by the **Fair Credit Billing Act (FCBA)** in the United States. Under the FCBA:

- Cardholders have **60 days from the statement date** on which the error appeared to dispute a charge.
- The issuer must acknowledge the dispute within 30 days and resolve it within two billing cycles (not to exceed 90 days).
- The cardholder is **not required to pay the disputed amount** while the investigation is pending.
- The cardholder's **maximum liability for unauthorized use** is $50, though most networks provide $0 liability under their own policies.

### Debit Cards
Debit card disputes are governed by **Regulation E** (Electronic Fund Transfer Act) in the U.S.:

- Notification timing is critical for debit: if the cardholder reports within **2 business days**, liability is capped at $50.
- Reporting between 2 and **60 days**: liability up to $500.
- After **60 days**: potentially unlimited liability.
- Despite these liability limits, most issuers provide zero-liability policies for debit cardholders on Visa/Mastercard branded cards, meaning they file chargebacks on behalf of customers even for transactions where the cardholder has higher regulatory liability.

### Prepaid Cards
Prepaid debit cards may have reduced protections depending on whether they are registered. Network-branded prepaid cards generally follow Visa/Mastercard dispute rules.

## Cardholder Rights Under Network Rules

Beyond regulatory protections, **card network operating rules** (Visa Core Rules, Mastercard Rules) grant cardholders significant dispute rights:

- **Dispute window**: Cardholders generally have up to **120 days** from the transaction date (or from the expected delivery date for goods/services) to initiate a dispute under Visa and Mastercard rules. Some reason codes allow up to **540 days** for certain scenarios.
- **No obligation to contact merchant first**: While issuers often ask cardholders whether they contacted the merchant, network rules do not require it. Issuers may file chargebacks without the merchant ever being informed of a complaint.
- **Provisional credit**: Issuers typically credit the cardholder's account immediately upon dispute filing, before the investigation concludes. The merchant's account is debited simultaneously.
- **Right to re-dispute**: If the merchant wins a representment, the cardholder and issuer may escalate to pre-arbitration and ultimately arbitration.

## How Issuers Protect Cardholders

Issuing banks are financially motivated to protect cardholders aggressively. Here is why:

- **Customer retention**: Cardholders who feel protected stay loyal to their card and bank.
- **Interchange revenue**: Active cardholders generate transaction fees for the issuer.
- **Regulatory compliance**: Issuers face regulatory scrutiny if they are seen as not protecting customers adequately.

In practice, this means issuers often give cardholders the benefit of the doubt. Dispute investigations may be brief. Provisional credit is provided quickly. Chargeback reason codes may be applied loosely. Merchants frequently find that chargebacks are filed for reasons that don't match the actual nature of the dispute.

## The Chargeback Window

The most important timing element for merchants to understand is the cardholder's dispute window:

- **Visa**: 120 days from the transaction date or the date goods/services were expected but not received, whichever is later. Maximum 540 days from the transaction date.
- **Mastercard**: 120 days from the transaction date or the date the cardholder was first informed of the charge.
- **American Express**: Up to 120 days, though Amex applies its own internal standards as both issuer and network.
- **Discover**: Similar to Visa/Mastercard, generally 120 days.

These windows are longer than most merchants expect. A customer who bought something four months ago can still file a chargeback today.

## Liability Shift

**Liability shift** is a critical concept that affects whether the merchant or issuer bears chargeback liability for fraudulent transactions:

- When a merchant uses **EMV chip** card acceptance (for card-present transactions), liability for counterfeit fraud shifts to the issuer if the fraudster used a chip card.
- When a merchant does **not** use chip card terminals, liability for counterfeit fraud rests with the merchant — even if the fraud was entirely the cardholder's issuer's failure to detect it.
- For **card-not-present (CNP) transactions online**, merchants can shift liability for fraudulent transactions by using **3D Secure (3DS)** authentication. If the issuer authenticates the transaction via 3DS and the transaction is later disputed as unauthorized, liability shifts to the issuer.
- Merchants who do not implement 3DS for online transactions retain liability for all unauthorized transaction disputes.

## Friendly Fraud: When Cardholders Abuse Dispute Rights

**Friendly fraud** occurs when a legitimate cardholder initiates a chargeback for a transaction they actually authorized and received. This is a significant and growing merchant problem:

- Estimates suggest **20-40% of chargebacks** are friendly fraud, though the actual rate is difficult to measure precisely.
- Common scenarios: a customer receives goods but claims they didn't, a subscription cardholder forgets they signed up, a family member uses the card without the account holder's awareness, or a customer disputes a transaction to avoid going through the merchant's return process.
- Friendly fraud is technically illegal (it is a form of bank fraud) but very rarely prosecuted.
- Merchants can fight friendly fraud in representment by providing evidence that the cardholder authorized and received the transaction.

Understanding cardholder rights and behaviors is not about limiting protections — it is about knowing the rules of the game so merchants can defend themselves appropriately within those rules.

---

## FAQs

**Q: Can a cardholder dispute a charge after 120 days?**
In most cases, no — card network rules impose a 120-day window from the transaction date or expected delivery date. However, some issuers may still accept disputes outside this window under Regulation E or their own policies, even if the network will not process a chargeback. If an issuer files a chargeback outside the valid window, the merchant can challenge it on procedural grounds.

**Q: Does a cardholder have to try to resolve the issue with me first before disputing?**
No. Card network rules do not require cardholders to contact the merchant. However, many issuers ask whether the cardholder attempted resolution. If they did not, this can sometimes be used in your representment. Merchants should always make their contact information prominent and their return/refund policies clear.

**Q: What is the difference between an unauthorized transaction dispute and a friendly fraud dispute?**
An unauthorized transaction dispute means a third party used the cardholder's account without permission (genuine fraud). A friendly fraud dispute means the cardholder themselves authorized and completed the transaction but files a chargeback claiming otherwise. Both arrive at the merchant as a "Fraud" category chargeback and require different evidence strategies to fight.

**Q: If I have a signed receipt, does that prevent chargebacks?**
A signed receipt is useful evidence, but it does not prevent a cardholder from filing a chargeback or guarantee a merchant win. It is one piece of compelling evidence in representment, but an issuer can still side with the cardholder based on other factors.

**Q: Why does a debit card dispute sometimes take longer to resolve than a credit card dispute?**
Regulation E requires specific investigation timelines for electronic fund transfers. If the issuer does not resolve a debit card dispute within the regulatory window, they must provide provisional credit to the cardholder. This timing pressure sometimes causes issuers to file chargebacks more quickly to preserve their rights, regardless of the underlying merits.
