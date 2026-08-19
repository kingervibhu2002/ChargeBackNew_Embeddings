---
title: "Compelling Evidence: What It Is and How to Use It"
section: "02_Chargeback_Basics"
category: "Chargeback Basics"
document_type: "Reference"
keywords: ["compelling evidence", "CE3.0", "Visa Compelling Evidence 3.0", "chargeback evidence", "3DS authentication", "AVS CVV", "delivery confirmation", "fraud dispute evidence", "burden of proof chargeback"]
difficulty: "Beginner"
---

# Compelling Evidence: What It Is and How to Use It

In chargeback disputes, not all evidence is equal. A bare authorization code proves the transaction was approved by the network — it does not prove the cardholder authorized it. Issuers know this and dismiss merchant submissions that rely on authorization alone. "Compelling evidence" is the legal and operational standard that card networks use to define the quality of proof that can shift the burden of liability from the merchant back to the issuer. Understanding this standard — and the specific Visa Compelling Evidence 3.0 framework — is essential for merchants who want to win fraud-coded disputes.

## What Compelling Evidence Means

In the context of chargeback disputes, compelling evidence is documentation that definitively demonstrates one or more of the following:

1. The cardholder (or an authorized person) actually received the goods or services
2. The transaction was authenticated through a network-recognized method (3DS)
3. The same cardholder has made prior, undisputed transactions with your business under similar conditions — proving a legitimate ongoing relationship
4. The disputed transaction matches the cardholder's known device, IP address, billing address, and behavioral patterns from prior legitimate purchases

The key word is *definitively*. Compelling evidence does not just suggest the cardholder authorized the transaction — it makes it implausible that they did not. When compelling evidence is present, the burden of proof effectively shifts to the issuer and cardholder to explain why a claim of non-authorization or non-receipt is credible given the documentation.

## Visa Compelling Evidence 3.0 (CE3.0)

In April 2023, Visa introduced the Compelling Evidence 3.0 (CE3.0) update, which significantly changed how merchants can dispute Visa 10.4 (Other Fraud — Card Absent Environment) chargebacks. CE3.0 is the most important development in chargeback dispute strategy in years.

### The Core Requirement

Under CE3.0, a merchant can shift liability back to the issuer on a Visa 10.4 fraud dispute if they can demonstrate:

**Two or more prior undisputed transactions from the same cardholder that match specific data points with the disputed transaction.**

These prior transactions must:
- Have occurred at least 120 days before the disputed transaction (but no more than 365 days prior)
- Have never been disputed or charged back
- Match at least **two of the following four data elements** when compared to the disputed transaction:
  1. Device ID / device fingerprint
  2. IP address (or geolocation)
  3. Shipping address / delivery address
  4. Account login credentials (for logged-in transactions)

### Why CE3.0 Is Powerful

Before CE3.0, a cardholder claiming "I didn't make this purchase" was very difficult to rebut on a fraud dispute, even if your authentication data was strong. CE3.0 creates a mechanism where prior purchase history becomes direct evidence of authorization. If the same person (same device, same IP, same shipping address) bought from you twice before without complaint and then bought a third time and disputed it, CE3.0 lets you say: the evidence of the prior relationship makes the fraud claim implausible.

### CE3.0 Data Matching Requirements in Practice

For CE3.0 to apply, you need a system that retains, at the transaction level:
- Device fingerprint or browser fingerprint
- IP address at time of purchase
- Shipping address used
- Login session data (for account-based purchases)

Merchants who do not capture and retain this data at the transaction level cannot use CE3.0 — even if the cardholder is a long-term customer. This is why building this data retention into your platform before disputes arise is critical.

## Mastercard's Approach to Compelling Evidence

Mastercard does not have an equivalent to Visa CE3.0 as a formalized framework, but Mastercard's dispute rules similarly recognize that evidence of prior successful transactions, authentication data, and behavioral matching can support a merchant's position in fraud disputes.

Under Mastercard rules, merchants disputing fraud-coded chargebacks (most commonly in the 4853 and 4863 families) should provide:
- Authorization data including AVS and CVV match results
- Device fingerprint and IP address
- Any prior undisputed transaction history with the same cardholder and matching data points
- 3DS authentication data where applicable

Mastercard's arbitration panels consider the totality of evidence rather than applying a strict two-transaction formula like CE3.0, but the underlying logic is the same: documented behavioral consistency undermines fraud claims.

## Evidence Hierarchy: From Strongest to Weakest

Not all evidence is equally persuasive. When building a chargeback rebuttal, prioritize evidence in this order:

### Tier 1: Conclusive Authentication (Strongest)
- **3DS (3-D Secure) authentication data:** If the transaction was authenticated via 3DS2, liability shifts to the issuer for fraud disputes. You should rarely need to fight a 10.4 if 3DS authenticated. Present the authentication value (CAVV/AAV) and ECI value.
- **CE3.0 qualifying prior transactions:** Two or more prior undisputed transactions matching device/IP/shipping data, as described above.

### Tier 2: Strong Contextual Authentication
- **AVS + CVV match:** Address Verification Service match plus Card Verification Value match together significantly reduce the plausibility of a stolen-card fraud claim. Neither alone is sufficient; both together are strong supporting evidence.
- **Geo-IP matching billing address:** The IP address at time of purchase resolves to the same geographic area as the billing address on file.
- **Device fingerprint match to prior purchases:** The same device that made prior undisputed transactions placed the disputed order.

### Tier 3: Fulfillment Evidence
- **Signed delivery confirmation:** Carrier signature capture confirming a named individual received the package.
- **GPS-stamped, photo-at-door delivery:** Increasingly available from major carriers; places a timestamped photo at the delivery address.
- **Download logs with IP and timestamp:** For digital goods, a log showing the file or activation key was downloaded from the same IP used during checkout.
- **Account usage logs post-purchase:** Evidence the cardholder's account accessed, used, or activated the purchased product after the transaction date.

### Tier 4: Supporting Documentation (Weakest Alone)
- Order confirmation and shipping records
- Customer service interaction logs
- Terms of service acknowledgment at checkout
- Return/refund policy display on the checkout page

**What Is NOT Compelling Evidence:**
- A bare authorization approval code (proves the network approved the transaction, not that the cardholder did)
- An invoice or receipt without supporting authentication data
- An email order confirmation without IP, device, or delivery evidence
- A cardholder's prior purchases from a different device and address (not matching data points)

## When Burden of Proof Shifts with 3DS

3-D Secure authentication is the clearest liability shift mechanism in the payment ecosystem. When a transaction is fully authenticated via 3DS (ECI value of 05 for Visa, 02 for Mastercard), the issuer accepts liability for fraud. The merchant is protected from 10.4-type fraud chargebacks regardless of whether the cardholder later claims they did not authorize the transaction.

**Important nuances:**
- Attempted authentication (ECI 06/01) provides partial protection — it reduces the merchant's liability exposure but does not fully shift it
- 3DS does not protect against non-fraud chargebacks (not received, not as described, etc.)
- Biometric or one-time passcode 3DS2 authentication is stronger than legacy 3DS1

If you are not using 3DS on your e-commerce transactions, implementing it is the single highest-ROI fraud dispute prevention measure available to you.

---

## Frequently Asked Questions

**Q: Does an authorization approval code prove the cardholder authorized the transaction?**
A: No. An authorization code proves that the card network approved the transaction at the time of processing — it confirms the card had available credit and was not flagged at that moment. It does not confirm that the actual cardholder (not a fraudster using stolen card data) initiated the transaction. Issuers are well aware of this distinction and will not accept auth codes alone as compelling evidence.

**Q: How many prior transactions do I need to use CE3.0?**
A: Visa CE3.0 requires a minimum of two prior undisputed transactions. Those transactions must fall between 120 and 365 days before the disputed transaction and must match at least two of four specified data elements (device ID, IP address, shipping address, login credentials).

**Q: Can I use CE3.0 on any type of chargeback?**
A: No. CE3.0 applies specifically to Visa reason code 10.4 (Other Fraud — Card Absent Environment). It does not apply to consumer disputes such as 13.1 (not received), 13.3 (not as described), or processing errors. For those codes, the relevant evidence is fulfillment and product documentation.

**Q: I implemented 3DS but still received a 10.4 chargeback. Is that possible?**
A: Yes. If the transaction was authenticated with ECI 05/02 (full authentication), the issuer should not have filed a 10.4 chargeback — doing so is a network rule violation. In your representment, present the authentication data (CAVV, ECI value, XID) and note that the chargeback is invalid under network rules. You can also file a compliance claim against the issuer for filing an improper chargeback.

**Q: Should I present all available evidence or only the strongest evidence?**
A: Present all credible, relevant evidence organized in a logical hierarchy. More evidence is not harmful as long as it is clearly organized and labeled (Exhibit A, Exhibit B, etc.). Issuers reviewing representments appreciate clear organization — a 15-page dump of unlabeled documents is less effective than a 4-page packet with a clear structure and an index.
