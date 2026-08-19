---
title: "3-D Secure (3DS / 3DS2)"
section: "09_Evidence"
category: "Evidence Library"
document_type: "Evidence Reference"
keywords: ["3D Secure", "3DS", "3DS2", "liability shift", "ECI code", "CAVV", "frictionless flow", "Visa Secure", "Mastercard Identity Check", "Amex SafeKey", "chargeback evidence"]
difficulty: "Intermediate"
---

# 3-D Secure (3DS / 3DS2)

## What Is 3-D Secure?

3-D Secure (Three-Domain Secure) is an authentication protocol for card-not-present transactions that adds an additional identity verification step between cardholder and issuing bank. When a transaction is authenticated through 3DS, liability for fraud chargebacks shifts from the merchant to the issuing bank — making 3DS the single most powerful chargeback protection mechanism available to CNP merchants.

The "Three Domains" refer to the three parties involved:
1. **Acquirer Domain:** The merchant and its acquiring bank.
2. **Interoperability Domain:** The card network (Visa, Mastercard, Amex).
3. **Issuer Domain:** The issuing bank and cardholder.

3DS is branded differently by each network:
- **Visa:** Visa Secure (formerly Verified by Visa)
- **Mastercard:** Mastercard Identity Check (formerly SecureCode)
- **American Express:** Amex SafeKey
- **Discover:** ProtectBuy

## 3DS1 vs 3DS2: Key Differences

### 3DS Version 1 (Legacy)
3DS1, deployed in the early 2000s, was a significant liability protection tool but suffered from severe implementation problems. Every transaction required an explicit cardholder challenge — a pop-up redirect where the cardholder entered a static password. This "friction" caused:
- Checkout abandonment rates of 20–30%.
- Poor mobile experience (pop-ups often failed on mobile browsers).
- Merchant resistance to implementation.

3DS1 has been formally deprecated by Visa and Mastercard. Processing that uses 3DS1 in EMV 3DS (3DS2)-capable environments is not recommended.

### 3DS Version 2 (3DS2)
3DS2 (EMV 3DS), the current standard, fundamentally redesigned the protocol:

**Frictionless Flow:** The issuer receives up to 150+ data points about the transaction (device fingerprint, IP, purchase history, shipping address, behavioral data, prior transaction history) and makes an automated risk decision. If the issuer is satisfied the transaction is legitimate based on these data points, it authenticates the transaction without asking the cardholder to do anything — the cardholder completes checkout as normal, with no pop-up or redirect. This is the "frictionless" outcome and represents the majority of 3DS2 transactions.

**Challenge Flow:** When the issuer requires additional verification (unfamiliar device, unusual transaction, high-value purchase), it sends a biometric or OTP challenge to the cardholder. The challenge is embedded in the merchant's checkout flow (not a pop-up redirect), providing a much better user experience than 3DS1.

**Native Mobile Support:** 3DS2 includes an SDK for native mobile app integration, eliminating the browser-redirect failures of 3DS1.

The result: 3DS2 provides the same liability protection as 3DS1 with significantly lower conversion impact. Most industry data shows checkout conversion impact of under 1% with properly implemented 3DS2.

## Liability Shift Mechanism

The core commercial value of 3DS is the liability shift:

**Without 3DS:** If a cardholder disputes a CNP transaction as unauthorized fraud, the merchant is liable for the chargeback loss.

**With successful 3DS authentication (ECI 05):** If the cardholder disputes the transaction as unauthorized fraud, the issuing bank is liable — not the merchant. The chargeback is rejected, and the issuer absorbs the loss.

**With attempted 3DS authentication (ECI 06):** Partial liability protection. The merchant attempted 3DS, but the issuer did not participate or the cardholder did not complete authentication. This provides some liability protection depending on the network and specific circumstances.

**Important limitations of liability shift:**
- Liability shifts only for fraud dispute codes (unauthorized transaction). It does not protect against non-fraud disputes (item not received, not as described, cancelled recurring).
- The authentication must be complete before authorization, not after.
- The CAVV/AAV value from authentication must be included in the authorization request.

## ECI Codes Explained

ECI (Electronic Commerce Indicator) codes are returned after 3DS authentication and included in the authorization request. They tell the acquirer and network what level of authentication occurred.

| ECI Code | Visa Meaning | Mastercard Meaning | Liability |
|---|---|---|---|
| 05 | Fully authenticated — cardholder verified | Fully authenticated | Issuer liability |
| 06 | Authentication attempted — issuer or cardholder did not complete | Authentication attempted | Partial/shared |
| 07 | Not authenticated — 3DS not used | Not authenticated | Merchant liability |
| 01 | Mastercard: MasterCard SecureCode attempted | — | Partial |
| 02 | Mastercard: MasterCard SecureCode authenticated | — | Issuer liability |

For practical purposes: ECI 05 (Visa/Amex/Discover) or ECI 02 (Mastercard) is the target — this is full authentication with liability shift. ECI 06/01 provides partial protection. ECI 07 provides no protection.

## CAVV and Authentication Values

When 3DS authentication is successful, the issuer returns a **CAVV** (Cardholder Authentication Verification Value) for Visa or an **AAV** (Accountholder Authentication Value) for Mastercard. This is a cryptographic token that proves authentication occurred and that the specific issuer participated.

The CAVV/AAV must be included in the authorization request for the liability shift to apply. If you collect the CAVV but do not include it in the authorization, you lose the liability protection.

**Retain the CAVV/AAV** in your transaction records. Include it in your chargeback evidence package as proof of authentication.

## Using 3DS Authentication as Evidence

When a cardholder disputes a 3DS-authenticated transaction as unauthorized fraud, your response is straightforward:

**Evidence package for 3DS-authenticated disputes:**
1. Authorization record including the ECI code (05 or 06) and CAVV/AAV value.
2. Statement in rebuttal letter: "This transaction was authenticated through [Visa Secure / Mastercard Identity Check] 3D Secure protocol. The authentication result (ECI 05) and CAVV value [XXXX] are included in the authorization record (Exhibit A). Under [Visa / Mastercard] rules, liability for this dispute rests with the issuing bank."
3. Reference the specific network rule: For Visa disputes, reference Visa Core Rules section on 3DS liability. For Mastercard, reference the Chargeback Guide provisions on authenticated transactions.

An ECI 05 transaction with a valid CAVV is near-unassailable for fraud dispute codes. The issuer cannot argue the cardholder did not authorize — their own authentication system verified the transaction.

## 3DS2 Data Points for Fraud Detection

3DS2 passes extensive transaction context to the issuer's access control server. This data — not typically accessible to the merchant — is used by the issuer to make the frictionless/challenge decision:

- Device fingerprint and device category (mobile, desktop, tablet).
- Browser data (user agent, screen resolution, timezone, language).
- Billing and shipping address.
- Prior transaction history with the merchant (for repeat customers).
- Shipping address history.
- Transaction amount and currency.
- IP address and geolocation.
- Time since account creation with the merchant.

The issuer uses machine learning models that incorporate all of these signals to assess whether the transaction is consistent with known cardholder behavior. A transaction that matches established patterns (same device, same location, similar purchase amount) will typically receive frictionless authentication. An unusual transaction (new device, new country, unusually high amount) is more likely to receive a challenge.

## Exemptions from 3DS

Certain transaction types may be exempt from 3DS requirements under PSD2 (EU) and network rules, even in mandated 3DS environments:

- **Low-value transactions:** Below €30 (EU) or equivalent national thresholds, transactions may be exempt.
- **Trusted beneficiaries:** Cardholders who have whitelisted a merchant with their issuer.
- **Recurring transactions after initial auth:** Subsequent recurring charges after an authenticated initial transaction may be exempt.
- **Merchant-initiated transactions:** Transactions initiated by the merchant without cardholder participation (recurring billing) are often exempt from 3DS but may lose liability protection.
- **Corporate cards:** Transactions with certain corporate or lodging cards.

Exemptions should be applied strategically. In the EU (PSD2 environment), SCA (Strong Customer Authentication) is required unless an exemption applies. Misapplying exemptions can result in authorization declines.

## When 3DS Doesn't Help

3DS liability shift protects against fraud chargebacks only — not all dispute types. If a 3DS-authenticated transaction is disputed for:
- Item not received (Visa 13.1, MC 4855): 3DS does not help. Provide delivery evidence.
- Item not as described (Visa 13.3, MC 4853): 3DS does not help. Provide product description evidence.
- Cancelled recurring transaction (Visa 13.2): 3DS on initial auth may help show enrollment was authorized, but the recurring billing claim requires additional evidence.
- Credit not processed (Visa 12.7): 3DS does not help. Provide refund evidence.

3DS is exclusively a tool for fraud-related disputes. Non-fraud disputes must be defended with the appropriate evidence regardless of 3DS authentication status.

## Summary

3-D Secure 2.0 is the most powerful liability protection available to CNP merchants. Successfully authenticated transactions (ECI 05) shift fraud chargeback liability to the issuer, making the merchant financially harmless for authorized-dispute fraud. Proper implementation requires 3DS2 integration (not 3DS1), correct CAVV/AAV passthrough in the authorization request, and accurate ECI code handling. When a dispute arrives on an authenticated transaction, the CAVV and ECI code are your primary evidence and typically sufficient to reject the chargeback entirely for fraud dispute codes.
