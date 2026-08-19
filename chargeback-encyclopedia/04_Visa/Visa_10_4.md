---
title: "Visa 10.4 — Other Fraud: Card-Absent"
section: "04_Visa"
category: "Visa Reason Codes"
network: "Visa"
reason_code: "10.4"
document_type: "Reason Code Reference"
keywords: ["fraud", "CNP", "card not present", "unauthorized", "10.4", "AVS", "CVV", "3DS", "3D Secure", "CE3.0", "friendly fraud", "digital goods"]
difficulty: "Intermediate"
---

# Visa 10.4 — Other Fraud: Card-Absent (CNP)

## Definition

Visa reason code 10.4 is the most common fraud chargeback code facing online and telephone-order merchants. It applies when a cardholder reports that they did not authorize a card-not-present (CNP) transaction — meaning a purchase made online, by phone, or by mail where the physical card was not presented to the merchant.

The cardholder's claim is straightforward: "I didn't make this purchase." The issuer accepts that claim and files a chargeback. The burden then falls on the merchant to prove the cardholder did authorize the transaction — or to show that the transaction matches the profile of a genuine purchase by the legitimate cardholder.

What makes 10.4 particularly complex is the **friendly fraud** dimension. Research consistently estimates that 40–80% of "unauthorized transaction" claims are actually cases where the legitimate cardholder made the purchase and is now falsely claiming they didn't. Children making purchases on a parent's card, buyers with remorse, or deliberate chargeback abuse all generate 10.4 disputes that are not genuine fraud. Visa's CE3.0 framework was specifically designed to help merchants fight these cases.

---

## Why 10.4 Is the Most Common CNP Fraud Code

Card-not-present fraud is structurally different from card-present fraud. Without the physical card, there is no chip authentication, no signature, and no visual ID check possible. The cardholder's card number, expiration date, and CVV are the primary verification tools — and these can all be stolen through phishing, data breaches, or purchased on dark web marketplaces.

The scale of CNP fraud has grown sharply with e-commerce. Every data breach exposes millions of card numbers. Automated bots test stolen credentials across thousands of merchants per hour. The merchant bears the fraud liability for CNP transactions because card networks determined that merchants who choose to accept card-not-present orders accept the associated fraud risk — unlike card-present fraud where terminal technology can authenticate the card.

---

## Common Scenarios

- **Genuine unauthorized transaction:** A cardholder's card number was stolen in a data breach. A fraudster uses it to buy electronics online. The merchant ships the goods to a different address. The cardholder disputes the charge.
- **Account takeover:** A fraudster gains access to the cardholder's online shopping account and uses the stored payment method to place an order. The cardholder claims they didn't authorize it.
- **Friendly fraud:** A cardholder makes a purchase, receives the goods, and then disputes the charge as "unauthorized" to get a free product. This is fraud committed by the cardholder against the merchant.
- **Family dispute:** A spouse or child uses the cardholder's account without explicit permission. The primary cardholder disputes the charge, not realizing or not wanting to admit the family connection.
- **Digital goods dispute:** A cardholder purchases in-game currency, streaming credits, or software downloads. They later claim they didn't authorize it — sometimes after consuming the digital goods.

---

## AVS and CVV Match: What They Prove and What They Don't

**CVV2 (Card Verification Value):** The three-digit code on the back of the card is a basic security check confirming the person ordering had access to the physical card (or the data from it). A CVV match is a helpful signal but does not prove the legitimate cardholder authorized the transaction — stolen card data often includes the CVV.

**AVS (Address Verification System):** AVS checks whether the billing address provided at checkout matches the address on file with the issuer. A full AVS match (address and ZIP code) provides stronger support for authorization. However, a mismatch doesn't automatically mean fraud, and a match doesn't guarantee legitimacy.

**What these signals do:** Contribute to a pattern of evidence suggesting the legitimate cardholder was the one transacting. No single signal is proof.

**What they don't do:** Override a cardholder's denial of authorization or constitute conclusive proof. You need multiple consistent signals to build a compelling case.

---

## 3D Secure Authentication and the Liability Shift

**3D Secure (3DS)** — implemented as Visa Secure (formerly Verified by Visa) — is the most powerful tool merchants have against 10.4 chargebacks. When a transaction is authenticated through 3DS and the cardholder completes authentication successfully (entering a one-time passcode, biometric confirmation, or other authentication method), **liability for fraud shifts from the merchant to the issuer**.

This is the CNP equivalent of the EMV chip liability shift. A fully authenticated 3DS transaction cannot be successfully charged back under 10.4 when the issuer authenticated the cardholder. The merchant is protected.

**Important 3DS nuances:**
- If 3DS is attempted but the issuer issues a "soft decline" or the cardholder fails authentication, the liability shift does not fully apply.
- If 3DS authentication results in a "frictionless flow" where the issuer approves without cardholder interaction, liability protection still applies but may be reviewed more carefully.
- If the merchant does not request 3DS authentication, they bear full fraud liability.
- Some card types and transaction types have exceptions — always verify with your payment processor.

**Recommendation:** Implement 3DS on all e-commerce transactions where operationally feasible. The small percentage of customers who abandon checkout due to 3DS friction is almost always less costly than unchallenged fraud liability.

---

## Visa Compelling Evidence 3.0 (CE3.0)

Introduced in April 2023, CE3.0 is specifically designed to fight friendly fraud on 10.4 chargebacks. It allows merchants to dispute a 10.4 chargeback by demonstrating that the disputed transaction matches the profile of prior **undisputed** transactions made by the same cardholder with the same merchant.

### CE3.0 Requirements

To invoke CE3.0, the merchant must produce evidence of at least **two prior undisputed transactions** completed by the same device/cardholder within **120 to 365 days** before the disputed transaction. The matching criteria must include at least two of:

- Same device ID or device fingerprint
- Same IP address (or IP address in the same geographic range)
- Same delivery address
- Same account login email or username
- Same payment credential linked to the same account

If the merchant can satisfy these requirements, liability shifts to the issuer — even if the cardholder insists they didn't authorize the disputed transaction. The logic: the same person who made previous purchases (that they never disputed) is the person who made the current purchase.

### CE3.0 Data Infrastructure Requirements

CE3.0 only works if you have the data. This means merchants must collect and store:
- Device fingerprint or device ID at checkout
- Customer IP address at time of purchase
- Login email or account identifier
- Shipping/delivery address
- Transaction timestamps and amounts for all purchases (including undisputed ones)

Merchants who don't collect this data cannot leverage CE3.0. It is strongly advisable to implement device fingerprinting and IP logging as a baseline fraud management practice.

---

## Delivery Proof: Physical and Digital Goods

### Physical Goods
- Carrier tracking showing delivery to the billing address (or confirmed delivery to an address provided by the cardholder at checkout).
- Signature confirmation for high-value shipments.
- GPS delivery confirmation from carriers like UPS or FedEx.
- Delivery to same address as prior undisputed orders (CE3.0 supporting evidence).

### Digital Goods
- Download or access logs showing the specific IP address and device that accessed or downloaded the product.
- Timestamp of first access.
- Activity logs showing usage after the download (game play, logins, streaming activity).
- Email delivery confirmation to the cardholder's registered email address.
- If account-based: login records showing the account associated with the card was actively used post-purchase.

Digital goods are particularly vulnerable to friendly fraud because there is no physical delivery to prove — the fraudster consumes the goods and disputes the charge. This is why access logs and IP-based evidence are critical.

---

## Merchant Liability

Merchants bear full fraud liability for 10.4 chargebacks unless:
- 3DS authentication was completed (liability shifts to issuer).
- CE3.0 compelling evidence applies (liability shifts to issuer).
- The transaction was processed under specific exemptions (merchant-initiated transactions, certain low-risk transactions).

Without 3DS or CE3.0, the standard 10.4 chargeback is a merchant loss unless the merchant can build a compelling evidence case through documentation — delivery proof, IP/device matching, and prior undisputed transaction history.

---

## Required Evidence Checklist

- [ ] Order confirmation with cardholder details
- [ ] IP address and device fingerprint at time of order
- [ ] AVS and CVV match results from authorization
- [ ] 3DS authentication result (if applicable) — authentication value, CAVV, ECI indicator
- [ ] Delivery confirmation (tracking number, carrier record, signature)
- [ ] For digital goods: download/access logs with IP and timestamp
- [ ] Customer communication history (order confirmation email, shipping notification)
- [ ] Prior undisputed transactions from same device/IP/email (CE3.0)
- [ ] Customer account records (creation date, login history, order history)

---

## Winning Strategy

1. **If 3DS was used:** Submit the 3DS authentication data (CAVV, ECI indicator). The chargeback should be automatically reversed — document the liability shift clearly in your rebuttal.
2. **If CE3.0 applies:** Pull the prior undisputed transaction data, match at least two identifiers, and submit a formal CE3.0 response documenting the match per Visa's CE3.0 requirements.
3. **If no 3DS and no CE3.0:** Build the best circumstantial evidence package — delivery proof, IP/device match, email delivery, AVS/CVV match results, and any other consistent signals. These won't guarantee a win but create a compelling case.
4. **Focus on delivery to billing address.** If goods were shipped to the cardholder's billing address and delivered successfully, document this prominently.

---

## Losing Mistakes

- **Not implementing 3DS.** This is the single biggest mistake CNP merchants make. 3DS eliminates most 10.4 fraud liability.
- **Shipping to an address different from the billing address without additional verification.** Shipping to a different address is a red flag, and if fraud occurs, you bear the loss.
- **Not collecting device and IP data.** Without this data, CE3.0 is unavailable.
- **Fighting a genuine fraud transaction.** If a third party truly stole the card number, accept the chargeback. Fighting genuine fraud wastes resources and may offend the victimized cardholder.
- **Missing the response deadline.** Thirty days from notification. Automate alerts.

---

## Timeline

| Stage | Timeframe |
|---|---|
| Transaction processed | Day 0 |
| Cardholder dispute filed | Within 120 days of transaction |
| Chargeback issued to merchant | Within 30 days of issuer filing |
| Merchant response deadline | 30 days from notification |
| CE3.0 or standard response submitted | Within merchant response window |

---

## Frequently Asked Questions

**Q: The customer used the correct CVV and AVS matched. Why am I still getting a 10.4 chargeback?**
A: CVV and AVS matches confirm the person had the card data, but they don't prove the legitimate cardholder authorized the transaction. Stolen card data (from breaches) includes CVV and billing address. These signals strengthen your case but don't override a cardholder's denial of authorization.

**Q: The customer received and used the product — how can they claim fraud?**
A: This is friendly fraud. Evidence of usage (login records, download logs, activity after purchase) is critical for digital goods. For physical goods, delivery to the billing address is your best defense. CE3.0 is the most powerful tool for repeat friendly fraudsters.

**Q: We don't use 3DS because we're worried about cart abandonment. Is that reasonable?**
A: The tradeoff exists, but for most merchants the abandonment rate from 3DS is smaller than the fraud and chargeback costs of not using it. Modern 3DS 2.0 has significantly reduced friction with risk-based authentication — many low-risk transactions go through frictionless flow. Analyze your fraud rates and abandonment rates together.

**Q: Can CE3.0 be used for every 10.4 chargeback?**
A: No. CE3.0 requires prior undisputed transactions from the same cardholder/device. First-time buyers have no prior transaction history to match. CE3.0 is most effective for merchants with repeat customers and robust data collection.

**Q: What is the ECI indicator and why does it matter?**
A: The Electronic Commerce Indicator (ECI) is a value returned by the 3DS authentication process indicating the authentication outcome (e.g., ECI 5 = fully authenticated, ECI 6 = authentication attempted). Your payment processor includes this in authorization data. ECI 5 with a valid CAVV is the strongest evidence of 3DS liability shift.

---

## Sample Rebuttal Points

**For 3DS-authenticated transactions:**
- "This transaction was fully authenticated via Visa Secure (3D Secure). The CAVV [value] and ECI indicator [value] confirm authentication was completed by the issuer. Under Visa's liability shift rules for authenticated transactions, liability rests with the issuing bank. We request immediate reversal of this chargeback."

**For CE3.0 compelling evidence:**
- "We are invoking Visa Compelling Evidence 3.0. The disputed transaction matches two or more prior undisputed transactions by the same cardholder based on: [Device ID match — same device fingerprint as orders on [dates]]; [IP address match — same IP address used on prior undisputed orders]. Evidence documentation is attached per CE3.0 submission requirements."

**For delivery proof:**
- "The order was shipped to [billing address] via [carrier] with tracking number [X]. Carrier records confirm delivery on [date] at [time]. Delivery was made to the cardholder's billing address as provided at checkout. We respectfully request the chargeback be reversed on the basis of confirmed delivery."
