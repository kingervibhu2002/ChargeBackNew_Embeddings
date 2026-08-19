---
title: "Address Verification Service (AVS)"
section: "09_Evidence"
category: "Evidence Library"
document_type: "Evidence Reference"
keywords: ["AVS", "address verification", "AVS codes", "AVS match", "chargeback evidence", "billing address", "international cards", "CNP fraud prevention"]
difficulty: "Beginner"
---

# Address Verification Service (AVS)

## What Is AVS?

The Address Verification Service (AVS) is a fraud detection tool used in card-not-present (CNP) transactions that compares the billing address provided by the customer at checkout against the billing address on file with the card issuer. It is one of the most widely used and most misunderstood fraud controls in e-commerce.

AVS does not block a transaction or guarantee its legitimacy. It is a verification signal — a data point that informs the merchant's risk decision. The merchant decides whether to accept, review, or decline based on the AVS response; the payment networks simply provide the comparison result.

AVS is a U.S.-centric service. It was developed and is most reliably available for cards issued by U.S. banks. International card availability is significantly more limited and less reliable.

## How AVS Works Technically

When a customer enters a billing address at checkout, that address data (specifically the numeric portion of the street address and the ZIP code) is transmitted to the issuing bank as part of the authorization request. The issuer's system compares these values against its records and returns an AVS response code.

The comparison is limited to:
- **Numeric street address:** The house or building number only (not the street name). "123 Main Street" contributes only "123" to the AVS check.
- **ZIP code:** The 5-digit ZIP code only (not city or state).

Neither the street name, city, nor state is included in the comparison. AVS is a narrow check, not a full address verification.

The authorization and AVS response typically complete in 1–3 seconds. The AVS result is returned in the authorization response alongside the authorization code.

## AVS Response Codes

Different payment networks and processors use slightly different code sets, but the major codes follow this standard structure:

| Code | Meaning | Risk Level |
|---|---|---|
| Y | Full match — street address and ZIP both match | Lowest risk |
| A | Address match only — street address matches, ZIP does not | Medium risk |
| Z | ZIP match only — ZIP matches, street address does not | Medium risk |
| N | No match — neither street address nor ZIP match | High risk |
| U | Unavailable — issuer does not support AVS or information not available | Elevated risk |
| R | Retry — system unavailable; retry later | Neutral — retry |
| G | Global/international — card issued outside the U.S., AVS not applicable | Elevated for high-value orders |
| S | Service not supported — issuer not an AVS participant | Elevated risk |
| E | Ineligible — transaction type not eligible for AVS | Neutral |
| W | Whole ZIP match — 9-digit ZIP matches, address does not | Low-medium risk |
| X | Exact match — 9-digit ZIP and address both match | Lowest risk |

### What Each Code Means for Merchant Risk

**Y (Full Match):** The customer provided the correct street number and ZIP code. This is the expected result for a legitimate cardholder. Most merchants process Y matches without additional friction.

**A (Address Match):** The street number is correct but the ZIP does not match. Could indicate the customer entered a wrong ZIP, uses a different ZIP for the same address, or (less commonly) the issuer has an outdated record. Worth a manual review for high-value orders.

**Z (ZIP Match):** The ZIP is correct but the street number does not match. Similar risk profile to A. Common for apartment buildings where customers forget the unit number, or for customers with multiple addresses. Manual review recommended for high-value orders.

**N (No Match):** Neither element matches. This is the most fraud-associated code. A fraudster who has stolen card data but not the billing address will produce an N code. For most merchants, N should trigger decline or manual review, especially for new customers and high-value orders.

**U (Unavailable):** The issuer cannot provide an AVS response — either because the bank does not participate in AVS, the card type does not support it (prepaid cards, some international cards), or a system issue. This is NOT a match or no-match; it is a non-response. Process based on other risk signals.

**G (Global/International):** The card is issued by a non-U.S. bank. U.S. AVS cannot check international issuer databases. For international orders, rely on other fraud controls (3DS, fraud scoring, device fingerprint) rather than AVS.

## When AVS Is Checked

AVS is checked at authorization — the initial approval request to the card network. It is not checked again at settlement. If you authorize a transaction and then settle it days later, the AVS result reflects the state at authorization time.

Key implications:
- Pre-authorization holds (hotel, car rental) check AVS at the initial auth, not at settlement.
- Recurring billing transactions after the initial setup typically do not re-check AVS.
- Incremental authorizations (adding to an original auth) may or may not include AVS depending on the transaction type and processor configuration.

## Limitations of AVS

Understanding AVS limitations prevents over-reliance on this tool:

**Limited to numeric elements:** AVS only checks house number and ZIP. A fraudster who knows "the address is something on Elm Street in 90210" can guess that "123, 90210" might produce a match without knowing the actual address.

**International cards:** AVS is not available or is unreliable for cards issued outside the United States, Canada, and UK (with UK using a different system). Approximately 40% of global card transactions cannot be verified via U.S. AVS.

**Prepaid cards:** Many prepaid cards do not have a registered billing address and return U or S codes regardless of what address is entered.

**Issuer data quality:** If the issuer has an outdated address on file (the customer moved and did not update their account), a legitimate customer may receive an N code even though they are genuine.

**Fraudsters with complete data:** A fraudster who purchased complete cardholder profiles (name, card number, CVV, billing address) from a dark web market will produce a Y match just as a legitimate cardholder would. AVS cannot distinguish this.

## How to Use AVS as Chargeback Evidence

AVS response data should be included in your chargeback rebuttal as supporting evidence — it demonstrates your fraud screening practices and the legitimacy signals present at authorization.

**Including AVS in your evidence:**
- Pull the authorization response record from your payment gateway or processor portal.
- Note the AVS response code and its meaning.
- State clearly in your rebuttal letter: "The billing address provided by the customer matched the issuer's records (AVS code Y), indicating the cardholder had access to the billing address on file."
- Combine with CVV response for a stronger authorization evidence package.

**Issuer perspective:** A Y or X AVS match combined with a CVV match shows the customer provided correct billing address and card verification data. This does not prove authorization, but it shifts the question toward the cardholder's ability to provide accurate card data.

## AVS Match Does NOT Guarantee No Chargeback

This is the critical misconception: AVS Y does not protect merchants from chargebacks. AVS is a fraud indicator, not a liability protection mechanism.

A perfect AVS match provides:
- A positive fraud signal at time of transaction.
- Supporting evidence in a chargeback rebuttal.
- A slightly reduced probability of fraud.

AVS does not provide:
- Liability protection (unlike 3DS).
- Absolute proof of authorization.
- Protection from friendly fraud, non-receipt disputes, or quality disputes.

3DS authentication provides actual liability protection. AVS provides supporting evidence only.

## Best Practice: Reject N Codes for High-Risk Orders

Most chargeback mitigation experts recommend the following AVS policy:

- **Y, X:** Process normally.
- **A, Z, W:** Process with additional scrutiny for orders over your high-risk threshold. Consider step-up verification (manual review, order hold, customer callback).
- **N:** Decline or require manual review for all orders above a de minimis threshold. The fraud rate on N-coded transactions is significantly higher than on Y-coded transactions.
- **U, S, G:** Process with additional fraud controls (fraud scoring, 3DS if available). Do not rely on AVS as a control.
- **R:** Retry once; if still R, treat as U.

Your specific thresholds should be calibrated to your customer base, average order value, and dispute rate. A merchant with a predominantly international customer base cannot apply the same AVS rules as a domestic-focused merchant.

## Summary

AVS is a foundational fraud control for CNP transactions that provides useful fraud signals at authorization time and supporting evidence in chargeback rebuttals. Its effectiveness is highest for domestic U.S. cards and lowest for international cards, prepaid products, and sophisticated fraud where the fraudster has complete cardholder data. Use AVS as one layer of a multi-factor fraud control system — never as a standalone control — and include AVS response data as supporting evidence in every applicable chargeback rebuttal.
