---
title: "Card Not Present (CNP) Fraud"
section: "08_Fraud"
category: "Fraud Encyclopedia"
document_type: "Fraud Reference"
keywords: ["CNP fraud", "card not present", "e-commerce fraud", "BIN attack", "AVS", "CVV", "3DS liability shift", "10.4", "4837", "dark web", "data breach"]
difficulty: "Beginner"
---

# Card Not Present (CNP) Fraud

## What Is Card Not Present Fraud?

Card Not Present (CNP) fraud occurs when a fraudster uses stolen payment card data to make purchases in environments where the physical card does not need to be presented — primarily e-commerce, mail order, telephone order (MOTO), and recurring billing transactions.

CNP fraud is the dominant form of payment fraud globally. As chip-and-PIN (EMV) technology has made in-person card fraud increasingly difficult and expensive, criminals have shifted to CNP channels, where the physical security features of the card (EMV chip, hologram, magnetic stripe) are irrelevant. Only the card data — the 16-digit card number, expiration date, and CVV2 code — needs to be known, not possessed.

The EMV Liability Shift of 2015 in the United States effectively eliminated most card-present fraud at chip-enabled terminals. The result was a dramatic reallocation of fraud to CNP channels. CNP fraud now accounts for approximately 75–80% of all card fraud losses in the United States and UK.

## Why CNP Fraud Dominates

The economics of CNP fraud favor the criminal:

- **Data is abundant:** Hundreds of millions of card numbers with full card data (PAN, expiry, CVV) are available on dark web markets, obtained through data breaches, phishing, and skimming operations.
- **Stolen card data is cheap:** A single card record with CVV typically costs $5–$20 on dark web markets. Even a low success rate generates positive ROI on bulk card data.
- **Remote operation:** CNP fraud can be executed from anywhere in the world. Fraudsters in Eastern Europe, West Africa, and Southeast Asia routinely target US, UK, and EU merchants without physical proximity.
- **Automation:** Fraud tools (bots, automated checkout scripts, carding forums) allow single operators to process hundreds of fraudulent transactions per hour.
- **No physical risk:** Unlike in-person card fraud (which requires physical card manufacturing or presence at a terminal), CNP fraud carries no risk of physical apprehension at point of sale.

## How Fraudsters Obtain Card Data

### Data Breaches
Large-scale breaches of merchant, payment processor, and healthcare databases have exposed billions of card records. Notable breaches (Target 2013, Home Depot 2014, Marriott 2018, Capital One 2019) each exposed tens or hundreds of millions of card records. Breached data is sold on dark web marketplaces (Joker's Stash, BidenCash, and others) or used directly by the breach perpetrators.

### Phishing and Social Engineering
Fraudsters send emails impersonating banks, e-commerce platforms, or government agencies, directing victims to fake sites that capture card details. SMS phishing ("smishing") uses similar tactics via text message. Voice phishing ("vishing") involves phone calls.

### Card Skimmers
Physical devices attached to ATMs, gas pumps, or point-of-sale terminals capture magnetic stripe data and PINs. This data is primarily used for cloned card fraud, but the card numbers are also sold for CNP use.

### Formjacking and Magecart Attacks
Malicious JavaScript injected into merchant checkout pages captures card data as customers type it, transmitting it to fraudster-controlled servers in real time. These attacks target merchants' own websites and are invisible to the cardholder and often to the merchant.

### Dark Web Markets and Carding Forums
Card data not obtained directly is purchased from criminal marketplaces that aggregate and resell stolen data from all sources above. Cards are often organized by issuing bank, country, card type, and estimated credit limit for buyer convenience.

## BIN Attacks in CNP Context

BIN (Bank Identification Number) attacks — systematic testing of all valid card numbers within a known BIN prefix — are a CNP-specific fraud technique. Because the merchant's checkout page is accessible remotely, it can be targeted with automated scripts that cycle through card number combinations until valid ones are identified. (See 004_Card_Testing.md for full BIN attack coverage.)

## Fraud Tooling: How CNP Attacks Are Executed

**Automated checkout bots:** Scripts that populate merchant checkout forms programmatically, testing card data at high speed without human interaction.

**Residential proxy networks:** Legitimate home internet connections (often unknowingly recruited into botnet proxies) mask the fraudster's true IP address and geographic location, bypassing IP-based fraud controls.

**Antidetect browsers:** Browser environments designed to present clean, unique device fingerprints that do not match known fraud infrastructure and bypass device-based fraud detection.

**Carding forums:** Online communities (typically on Tor or invite-only clearnet forums) where fraudsters share techniques, sell card data, and discuss which merchants have weak fraud controls.

**Drop services:** Networks of "drops" — individuals who receive fraudulently ordered goods at their address in exchange for a cut of the value, then forward or sell the goods. Drops provide the physical delivery addresses fraudsters need for physical goods CNP fraud.

## Impact Statistics

- CNP fraud accounts for approximately $10 billion in annual losses in the United States alone (Nilson Report).
- E-commerce CNP fraud rates range from 0.3% to over 1.5% of gross merchandise value depending on merchant category and fraud controls.
- Every $1 in CNP fraud costs merchants approximately $3.36 after chargebacks, fees, and operational costs (LexisNexis True Cost of Fraud Study).

## Merchant Defense Strategies

### Address Verification Service (AVS)
AVS checks the billing address provided at checkout against the issuer's records. A full AVS match (street number and ZIP) is a positive indicator. A non-match should trigger review or rejection for high-risk orders. AVS does not prevent all CNP fraud — fraudsters who have the cardholder's billing address (from phishing or breach data) can pass AVS — but it filters the most casual fraud.

### CVV2 Verification
Requiring CVV2 at checkout filters fraudsters who have card numbers from database breaches that did not include CVV data (many breach datasets are magnetic stripe reads that do not include CVV2, which is only printed on the card). A CVV2 match indicates the fraudster has more complete card data. Note: storing CVV2 post-authorization is prohibited by PCI DSS.

### 3D Secure (3DS / 3DS2)
3DS authentication shifts liability from the merchant to the issuer on successfully authenticated transactions. If the cardholder later disputes a charge that was authenticated via 3DS (ECI 05 or 06), the issuer — not the merchant — bears the fraud loss. This is the most powerful liability protection available in CNP. See 004_3D_Secure.md for full coverage.

### Velocity Limits
Rate-limit the number of transaction attempts per IP address, device fingerprint, billing address, or card BIN within a time period. Velocity limits disrupt bulk automated fraud operations.

### Device Fingerprinting
Identify and track devices across sessions. Devices associated with prior fraud attempts, multiple failed payment attempts, or multiple account identities are high-risk indicators.

### Real-Time Fraud Scoring
Deploy machine learning-based fraud scoring at checkout. Enterprise solutions (Kount, Signifyd, Forter, Riskified) evaluate hundreds of signals simultaneously — device, IP, behavioral, velocity, consortium history — in milliseconds to assign a fraud probability score that enables automated approve/review/decline decisions.

### Order Rules for High-Risk Scenarios
Implement rules that trigger review or decline for high-risk order characteristics:
- Shipping to a freight forwarder or reshipping address.
- High-value order from a new customer with no purchase history.
- Mismatched billing and shipping countries.
- High-velocity purchases from the same IP.
- IP geolocation significantly different from billing address country.

## Chargeback Codes for CNP Fraud

| Network | Code | Description |
|---|---|---|
| Visa | 10.4 | Other Fraud — Card Absent Environment |
| Mastercard | 4837 | No Cardholder Authorization |
| Amex | FR2 | Fraud — Card Not Present Transaction |
| Discover | UA02 | Fraud — Card Not Present |

Code 10.4 (Visa) and 4837 (Mastercard) are the primary CNP fraud dispute codes. These codes indicate the cardholder claims they did not authorize the transaction — the most common presentation of CNP fraud chargebacks.

## Liability Shift With 3DS

When a transaction is authenticated through 3DS (full authentication, ECI 05), liability for fraud chargebacks shifts from the merchant to the issuing bank. This means:
- If the cardholder disputes a 3DS-authenticated transaction as unauthorized fraud, the issuer — not the merchant — absorbs the loss.
- The merchant is protected from CNP fraud chargebacks on 3DS-authenticated transactions.
- Liability shift does not apply to non-fraud dispute reasons (item not received, not as described).

3DS2's frictionless flow (available when the issuer has sufficient authentication confidence from risk signals) provides liability protection without requiring the cardholder to complete a challenge, minimizing conversion impact.

## Summary

CNP fraud is the defining challenge of e-commerce commerce. The shift from card-present to card-absent fraud has been systematic and structural, driven by EMV adoption eliminating in-person fraud. Merchant defense requires layered controls: AVS and CVV2 at authorization, real-time fraud scoring at checkout, 3DS authentication for liability protection, and velocity controls to disrupt automated attacks. Merchants who invest in these layers shift fraud losses off their books and onto issuers (via 3DS liability shift) or onto fraudsters (via prevention).
