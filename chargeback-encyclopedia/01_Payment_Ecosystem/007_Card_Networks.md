---
title: "Card Networks: Visa, Mastercard, Amex, Discover, and Global Networks"
section: "01_Payment_Ecosystem"
category: "Payment Ecosystem"
document_type: "Reference"
keywords: ["card network", "Visa", "Mastercard", "American Express", "Amex", "Discover", "RuPay", "JCB", "UnionPay", "network rules", "interchange fees", "network arbitration", "chargeback rules by network", "card scheme"]
difficulty: "Beginner"
---

# Card Networks: Visa, Mastercard, Amex, Discover, and Global Networks

Card networks are the infrastructure and rule-setting authorities that make global card payments possible. They are often misunderstood — many merchants confuse card networks with banks or processors. Understanding the distinct role of each network, and how they differ in their chargeback rules, is essential for merchants who accept multiple card brands.

## What Card Networks Do (and Don't Do)

### What They Do
- **Set the rules**: Card networks publish comprehensive operating regulations (Visa Core Rules, Mastercard Rules) that all issuers, acquirers, merchants, and processors must follow. These rules govern everything from how transactions are authorized to how disputes are adjudicated.
- **Operate the rails**: Networks maintain the technical infrastructure (switching networks) that route authorization requests and responses between issuers and acquirers globally.
- **Set interchange**: Networks establish interchange fee schedules that define how much the issuer earns from each transaction.
- **Arbitrate disputes**: When merchants and issuers cannot resolve a dispute at the chargeback or representment level, card networks serve as the final arbitrator.
- **Monitor for fraud and compliance**: Networks run monitoring programs (Visa VDMP/VFMP, Mastercard MATCH/MMSP) that flag merchants and acquirers with excessive chargebacks or fraud rates.

### What They Don't Do
- **Hold or move money directly**: Networks are clearinghouses for rules and data, not funds. Actual money movement occurs through banks and settlement institutions.
- **Issue cards**: Cards are issued by issuing banks under network licenses.
- **Hold merchant accounts**: Merchant accounts are held by acquiring banks, not networks.

## Visa

**Model**: Four-party (cardholder ↔ issuer ↔ Visa network ↔ acquirer ↔ merchant)

**Scale**: The world's largest card network by transaction volume. Visa processes over 200 billion transactions annually.

### Visa Chargeback Framework
Visa overhauled its dispute system with the **Visa Claims Resolution (VCR)** framework, launched in 2018. Key features:
- **Two dispute categories**: Fraud (Category 10xx) and Non-Fraud (Category 11xx, 12xx, 13xx).
- **Allocation vs. Collaboration workflows**: Some disputes are automatically resolved by Visa's systems (Allocation); others require manual collaboration between merchant and issuer (Collaboration).
- **Compelling Evidence 3.0 (CE3.0)**: Visa's current evidence standard allows merchants to defeat fraud chargebacks by providing two prior non-disputed transactions from the same device and same billing/shipping details.
- **Merchant response window**: Typically 30 days to respond to a chargeback.
- **Chargeback monitoring**: Visa VDMP (Visa Dispute Monitoring Program) — Early Warning at 0.65% ratio, Standard at 0.9%, Excessive at 1.8%.

### Visa Network Fees
Visa charges fees to issuers and acquirers for network access, processing, and participation. These fees are separate from interchange (which issuers earn) and processing fees (which acquirers/processors charge). Common Visa fees include: VisaNet access fees, misuse of authorization fees, and international service assessment fees.

## Mastercard

**Model**: Four-party (same structure as Visa)

**Scale**: Second largest global network; particularly strong in Europe and emerging markets.

### Mastercard Chargeback Framework
Mastercard uses a **Dispute Resolution Initiative** framework. Key features:
- **Reason code structure**: Organized into categories — Fraud (4853-related), Authorization (4808), Point of Interaction (4834), and Customer Disputes (4853, 4855, 4859, 4860, 4863).
- **Chargeback timeframe**: 120 days from transaction date or from the date the cardholder was first notified.
- **Merchant response window**: Typically 45 days (more generous than Visa's 30-day standard).
- **Chargeback monitoring**: Mastercard Excessive Chargeback Program (ECP) — Early Warning at 1.0%, Excessive at 1.5% (with at least 100 chargebacks/month). Note: Mastercard calculates ratio using the current month's chargebacks against the current month's transactions.

### Mastercard vs. Visa Ratio Calculation
This is a critical difference: Visa calculates chargeback ratio using prior month transactions in the denominator; Mastercard uses current month transactions. The same number of chargebacks can appear at different ratios depending on which network is calculating.

## American Express (Amex)

**Model**: Historically three-party (Amex is both issuer and network). Now a hybrid — Amex issues cards and sets network rules, but also licenses third-party issuers.

**Chargeback Framework**:
- Amex manages disputes internally as both issuer and network (for its own-issued cards).
- Amex's dispute process is often faster to resolve but can be less transparent for merchants.
- **Inquiry stage**: Amex frequently sends "inquiries" before filing a formal chargeback, giving merchants an opportunity to resolve before the formal process begins.
- **Response window**: Typically 20 days for inquiry responses, 20 days for chargeback responses.
- **Merchant recourse**: More limited than Visa/Mastercard formal dispute chain; Amex's internal processes can be opaque.

**Amex-specific fee structures**: Amex typically charges merchants higher discount rates than Visa/Mastercard (historically 2.5-3.5% vs. 1.5-2.5%), reflecting its premium cardholder base and higher average transaction values.

## Discover

**Model**: Three-party model similar to Amex; Discover is issuer and network.

**Chargeback Framework**:
- Discover's dispute rules closely mirror Mastercard's (Discover entered into a network acceptance agreement with Mastercard).
- Reason codes and timeframes are similar to Mastercard but with Discover-specific nuances.
- Discover is smaller than Visa/Mastercard in volume; chargebacks from Discover cards are proportionally less common for most merchants.

## RuPay

**Model**: India's domestic card network, operated by NPCI (National Payments Corporation of India).

**Chargeback Framework**:
- Used primarily for transactions within India.
- Chargeback rules follow NPCI's dispute management framework, which is broadly similar to Visa/Mastercard but with India-specific regulatory requirements (RBI guidelines).
- For merchants outside India accepting RuPay cards (via co-branding with Discover/JCB), the foreign network's rules generally apply.

## JCB (Japan Credit Bureau)

**Model**: Japanese card network with international reach through co-branding with Discover.

**Chargeback Framework**:
- JCB operates its own dispute rules for JCB-issued transactions.
- For international acceptance, JCB has co-branding agreements with Discover, meaning merchants that accept Discover typically accept JCB under the same terminal setup.
- Dispute processes for JCB transactions processed outside Japan often follow Discover's framework.

## UnionPay

**Model**: China's dominant card network, the world's largest by number of cards issued.

**Chargeback Framework**:
- UnionPay operates primarily on China's domestic payment rails with its own dispute framework under PBOC (People's Bank of China) regulations.
- For international transactions processed outside China, UnionPay has agreements with other networks (Discover in the U.S.).
- Chargeback processing for international UnionPay transactions is more complex and depends on the specific acceptance agreement in place.

## How Networks Arbitrate Disputes

When a dispute cannot be resolved between issuer and merchant through the standard chargeback-representment cycle, it escalates to the card network for **arbitration** (or "compliance" for procedural violations). The network's arbitration process:

1. Both the issuer and the acquirer (on behalf of the merchant) submit their evidence packages to the network.
2. The network's internal review team evaluates the evidence against the network's own rules.
3. The network issues a binding decision — typically within 30–45 days.
4. The losing party (issuer or acquirer/merchant) pays the disputed amount **plus** arbitration fees ($250–$500 or more).
5. The network's decision is final — there is no further appeal within the card system.

## Interchange: The Network's Revenue Engine

**Interchange** is the fee paid from the merchant's acquirer to the cardholder's issuer on every transaction. It is the primary revenue source for issuers and is set by card networks on fee schedules published (and updated) periodically.

Interchange rates vary by:
- Card type (credit vs. debit, rewards vs. standard, corporate vs. consumer)
- Merchant category code (MCC)
- Transaction environment (card-present vs. card-not-present)
- Authentication method (EMV chip, contactless, 3DS)

Understanding interchange matters for chargebacks because processing fees, reserve calculations, and chargeback economics all connect back to interchange as a baseline cost.

---

## FAQs

**Q: Do I need to follow the rules of every card network separately?**
Yes. Visa, Mastercard, Amex, and Discover each publish their own operating regulations with distinct dispute rules, timeframes, and reason codes. If you accept all four brands (which most merchants do), you must be prepared to handle disputes under each network's specific framework.

**Q: Which network has the most merchant-friendly chargeback rules?**
This varies by situation, but Mastercard's 45-day response window is more generous than Visa's 30-day standard. Visa's CE3.0 compelling evidence standard can be powerful for merchants with detailed transaction records. Amex's internal process can sometimes be resolved faster but with less formal appeal rights.

**Q: Why do I pay different rates for different card types at the same network?**
Interchange is tiered by card type and merchant category. Premium rewards cards carry higher interchange because issuers fund the rewards program from that interchange revenue. Debit cards carry lower interchange (regulated in the U.S. under the Durbin Amendment for regulated issuers). Your effective blended rate is the weighted average of all card types your customers use.

**Q: Can a card network fine my business directly?**
Card networks do not typically fine merchants directly. Fines flow through the acquiring bank. Your acquirer may pass those fines through to you as charges on your merchant statement. If your acquirer absorbs fines related to your account, they may use those fines as grounds for account termination.

**Q: Does UnionPay follow the same chargeback rules as Visa for a transaction processed in the U.S.?**
Not exactly. For UnionPay transactions processed in the U.S. through the Discover network (via co-branding), Discover's dispute framework generally applies. For transactions processed directly on UnionPay rails (less common in the U.S.), UnionPay's own rules apply. Always confirm with your acquirer or PSP which framework governs UnionPay transactions in your specific setup.
