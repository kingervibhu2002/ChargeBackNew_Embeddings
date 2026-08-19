---
title: "Authorization and Authentication in Card Payments"
section: "01_Payment_Ecosystem"
category: "Payment Ecosystem"
document_type: "Reference"
keywords: ["authorization", "authentication", "3D Secure", "3DS", "approval code", "decline code", "AVS", "CVV", "card verification", "holds", "captures", "partial authorization", "pre-authorization", "EMV", "liability shift", "authorization request", "authorization response"]
difficulty: "Intermediate"
---

# Authorization and Authentication in Card Payments

Authorization and authentication are two distinct but related processes in the payment lifecycle. Together they determine whether a transaction proceeds, who bears fraud liability, and — critically for chargeback management — what evidence the merchant has to fight disputes. Many chargebacks can be prevented or defended more effectively by understanding how these processes work and ensuring they are implemented correctly.

## Authorization: Getting the Green Light

**Authorization** is the real-time process by which the issuing bank approves or declines a transaction before money changes hands. No funds move during authorization — it is simply a hold and a permission grant.

### The Authorization Request

When a cardholder initiates a payment, the merchant's terminal or gateway constructs an **authorization request message** (ISO 8583 format) containing:

- **Primary Account Number (PAN)**: The 16-digit card number (or token)
- **Expiration date**
- **Transaction amount**
- **Merchant ID (MID) and terminal ID**
- **Merchant Category Code (MCC)**
- **Transaction date and time**
- **CVV/CVC value** (for card-not-present)
- **AVS data** (billing address ZIP code and street number, for card-not-present)
- **3DS authentication data** (if applicable)

This message travels: merchant → gateway → processor → card network → issuer.

### The Authorization Response

The issuer's authorization system evaluates the request and returns a response containing:

- **Response code**: Approval (00) or a specific decline code
- **Authorization code** (approval code): A 6-character alphanumeric code confirming approval
- **AVS response code**: Indicating how well the billing address matched
- **CVV response code**: Match, No Match, or Not Processed

The response travels back through the same chain in milliseconds.

### Authorization Holds vs. Captures

- **Authorization (Hold)**: Creates a hold on the cardholder's available balance or credit. Funds are not yet transferred.
- **Capture**: The merchant submits the authorized transaction for settlement (either immediately or in a batch). Capture can be for the full authorized amount or a different amount (partial capture).
- **Pre-Authorization**: Used in hotels, car rentals, and restaurants where the final amount is unknown. A pre-auth hold is placed; the actual charge is captured later for the final amount.

**Chargeback implication**: If you authorize a transaction but never capture it, no chargeback can occur (there is no settled transaction). However, if you capture without a prior authorization — called a "forced transaction" or "post-authorization" — you lose chargeback protection and face significant liability.

### Holds and Incremental Authorizations

For variable-amount transactions (hotel stays, car rentals):
- An initial authorization hold is placed at check-in.
- **Incremental authorizations** extend the hold as additional charges accumulate.
- Final capture at checkout for the actual total amount.

Under Visa and Mastercard rules, merchants must follow specific procedures for pre-authorizations and incremental authorizations. Failure to do so can make resulting chargebacks much harder to fight.

## Authentication: Proving the Cardholder Is Legitimate

**Authentication** is the process of verifying that the person presenting the card credentials is the actual authorized cardholder. Authentication is distinct from authorization: authorization asks "does this card have funds?"; authentication asks "is the right person using this card?"

### Card-Present Authentication

For in-person transactions, authentication methods include:

- **EMV Chip**: The card's chip generates a unique cryptographic code for each transaction, making it nearly impossible to counterfeit. EMV is the dominant authentication method globally for card-present transactions.
- **PIN**: The cardholder enters a personal identification number known only to them. PIN provides strong authentication evidence.
- **Contactless/NFC**: Tap-to-pay using EMV contactless or digital wallets (Apple Pay, Google Pay). Digital wallets add biometric authentication (Face ID, fingerprint) on the device before tokenizing the card credential.
- **Signature**: Largely deprecated as an authentication method; card networks removed the signature requirement from most transaction types. Signature alone is weak evidence in chargebacks.
- **Magnetic stripe**: Legacy; the swipe transaction cannot verify card-present fraud. Merchants still using swipe-only terminals bear higher fraud liability.

### Card-Not-Present Authentication (Online/CNP)

For online and phone transactions, authentication is more challenging because the physical card is not present:

#### Address Verification Service (AVS)
AVS compares the billing address provided by the cardholder against the address on file with the issuer:
- **Full match (X or Y)**: ZIP code and street number both match — strongest AVS response.
- **Partial match (A or W)**: One element matches but not both.
- **No match (N)**: Neither ZIP nor street number matches.
- **Unavailable (U or G)**: Issuer does not support AVS or international card.

AVS does not prevent authorization — the issuer still approves or declines based on its own rules. But AVS response codes are valuable evidence in fraud chargeback representments. An AVS full match indicates the cardholder provided accurate billing information, which is inconsistent with "I didn't make this purchase" claims.

#### CVV/CVC Verification
The CVV (Visa's term) or CVC (Mastercard's term) is the 3-4 digit security code on the card:
- **CVV2 (Visa) / CVC2 (Mastercard)**: Printed on the back of the card; must be provided for CNP transactions.
- **CVV match**: Issuer confirms the code matches the card on file.
- **CVV no match**: The issuer may decline or approve with a no-match flag.

Merchants must request CVV for all CNP transactions. Note: after a transaction is authorized, the CVV **cannot** be stored (PCI-DSS prohibition). However, the CVV *match response* (match, no match, not provided) can be retained as evidence.

#### 3D Secure (3DS) Authentication

**3D Secure** (3DS) is a protocol developed by EMVCo (the joint venture of the major card networks) that adds an additional authentication step for online transactions. Current version: **3DS2**.

##### How 3DS Works
1. The cardholder initiates checkout on the merchant's website.
2. The merchant's gateway or 3DS SDK submits a 3DS authentication request with transaction data and device/browser fingerprint data.
3. The issuer's **Access Control Server (ACS)** evaluates the risk.
4. **Frictionless flow** (most transactions): The issuer authenticates silently using device fingerprint, purchase history, and risk scoring — no cardholder action required.
5. **Challenge flow** (higher-risk transactions): The cardholder is prompted to authenticate — enter a one-time password (OTP), use biometric verification, or answer security questions.
6. If authentication succeeds, the ACS returns an **Authentication Value (AV)** that is included in the authorization request.

##### Liability Shift with 3DS
This is the most important chargeback implication of 3DS:
- **3DS authenticated → liability shifts to issuer**: If a transaction is authenticated via 3DS and the cardholder later claims "I didn't do this" (fraud chargeback), the liability shifts from the merchant to the issuer. The merchant wins the chargeback automatically.
- **3DS attempted but issuer declines to authenticate → liability shifts to issuer**: Even if the issuer downgrades authentication, liability shifts because the issuer chose not to challenge.
- **No 3DS → merchant retains liability**: For all online fraud disputes without 3DS authentication, the merchant bears the financial loss.

##### 3DS and Conversion
3DS2's frictionless flow reduces the friction that plagued the original 3DS (which required a redirect and password, hurting conversion). Most modern 3DS2 implementations result in frictionless authentication 90%+ of the time for low-risk transactions.

## Decline Codes: What They Tell Merchants

When a transaction is declined, the issuer returns a decline reason code. Understanding these helps merchants identify fraud risk and avoid unnecessary retries:

| Code | Description | Chargeback Risk |
|------|-------------|-----------------|
| 05 | Do not honor (generic decline) | Low — issuer refused |
| 14 | Invalid card number | Low — bad PAN |
| 41 | Lost card | High — stolen card fraud risk |
| 43 | Stolen card | High — stolen card fraud risk |
| 51 | Insufficient funds | Low — legitimate decline |
| 54 | Expired card | Low — update card info |
| 57 | Transaction not permitted | Medium — MCC mismatch |
| 62 | Restricted card | Medium — geographic restriction |

**Critical rule**: Retrying a declined transaction multiple times is a violation of card network rules (especially for "Do Not Honor" declines) and generates **misuse of authorization fees** from Visa. Excessive retries on blocked transactions is a form of authorization misuse that can trigger network fines.

---

## FAQs

**Q: Does an approval code from the issuer protect me from a chargeback?**
Not completely. An approval code confirms the card had available funds and the issuer's real-time fraud system did not block the transaction. It does not confirm the cardholder authorized the purchase. You can receive an approval and still face a chargeback for "unauthorized transaction" if the card was stolen or the cardholder claims they didn't make the purchase.

**Q: Should I decline orders when AVS doesn't match?**
It depends on your risk tolerance and customer base. Full AVS mismatch (billing address doesn't match) on high-value orders is a red flag. Many merchants decline or manually review CNP orders with AVS mismatches. However, international cards frequently return "AVS unavailable" because many non-U.S. issuers don't support AVS, so blanket AVS-decline rules can harm international revenue.

**Q: Is 3D Secure required?**
3DS is mandatory for CNP transactions in the European Economic Area (EEA) under PSD2's Strong Customer Authentication (SCA) requirements. In the U.S., 3DS is optional but strongly recommended for merchants who want fraud liability shift. Some card networks and issuers are pushing for broader 3DS adoption globally.

**Q: What is the difference between a pre-authorization and a final charge?**
A pre-authorization places a hold on the cardholder's funds for an estimated amount. The final charge (capture) is the actual transaction. If the final amount differs significantly from the pre-auth amount, some issuers may challenge the transaction. Visa and Mastercard have rules about how much captured amounts can deviate from authorized amounts before additional authorization is required.

**Q: What happens if I process a sale without obtaining an authorization?**
Processing without authorization (a "forced sale") is a severe violation of network rules. You lose all chargeback protection, face potential fines from the card network, and can be held liable for the full amount. Always ensure every transaction has a valid authorization code before completing a sale.
