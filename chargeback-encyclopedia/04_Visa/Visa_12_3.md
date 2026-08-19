---
title: "Visa 12.3 — Incorrect Currency"
section: "04_Visa"
category: "Visa Reason Codes"
network: "Visa"
reason_code: "12.3"
document_type: "Reason Code Reference"
keywords: ["incorrect currency", "12.3", "DCC", "dynamic currency conversion", "currency dispute", "travel", "foreign currency"]
difficulty: "Intermediate"
---

# Visa 12.3 — Incorrect Currency

## Definition

Visa reason code 12.3 applies when a cardholder disputes a transaction because the wrong currency was used to process the charge — most commonly when a transaction was processed in a currency other than the one the cardholder agreed to at the point of sale. The most frequent trigger for 12.3 chargebacks is **Dynamic Currency Conversion (DCC)**, a service that allows cardholders to pay in their home currency when transacting abroad — but only when the cardholder explicitly consents.

If a DCC transaction was completed without the cardholder's informed consent, or if the currency conversion was applied without disclosure of the exchange rate and fees, the cardholder has grounds to dispute the transaction under 12.3.

---

## What Is Dynamic Currency Conversion (DCC)?

DCC is a service offered at the point of sale (primarily at hotels, restaurants, and retail merchants in tourist destinations, and at international ATMs) that allows a foreign cardholder to see the transaction amount converted into their home currency before paying. Instead of paying in the local currency and having their bank apply the conversion, the cardholder pays in their home currency at the merchant's terminal.

On the surface, DCC sounds convenient — travelers can see exactly what they're paying in familiar terms. In practice, DCC rates are typically less favorable than the rates Visa or the cardholder's bank would apply, and merchant providers often receive a commission from DCC transactions. This creates an incentive for merchants to encourage or even covertly apply DCC without proper disclosure.

**DCC is only legitimate when:**
- The cardholder is clearly informed of the currency conversion.
- The exchange rate and any fees are displayed.
- The cardholder explicitly chooses to pay in their home currency.
- The cardholder could have chosen to pay in the local currency.

If any of these conditions are not met, a 12.3 chargeback is likely valid.

---

## Visa DCC Rules and Disclosure Requirements

Visa's rules on DCC are strict. Merchants offering DCC must:

1. **Offer the choice.** The cardholder must be given the option to pay in the local currency or their home currency. The choice must be genuine — pre-selecting DCC without giving the cardholder an opportunity to opt out is a violation.
2. **Display the exchange rate.** The rate used for the conversion must be shown to the cardholder before they commit.
3. **Disclose any fees.** Any additional fees or margin applied as part of the conversion must be disclosed.
4. **Obtain explicit consent.** The cardholder must affirmatively select DCC. A signature or button press is typical.
5. **Print disclosure on the receipt.** The receipt must show the original local currency amount, the conversion rate, and the converted home currency amount.

Merchants who offer DCC through terminal software must ensure their terminal provider has configured DCC to comply with these requirements.

---

## Other Currency Error Scenarios

Beyond DCC disputes, 12.3 can also apply in these situations:

- **Merchant processes in wrong currency by mistake.** A merchant whose terminal is misconfigured processes a transaction in a currency they did not intend (e.g., a US merchant whose terminal is inadvertently set to Canadian dollars charges a US cardholder in CAD).
- **Currency settings error in e-commerce.** An online merchant's payment page shows prices in one currency but the payment gateway is configured to process in a different currency. The cardholder expects to pay in USD but is charged in EUR.
- **ATM currency error.** An international ATM offers DCC but does so in a confusing or deceptive manner, and the cardholder disputes the currency used.

---

## Common Scenarios

- A tourist at a hotel in Paris is presented with a terminal showing the charge in USD rather than EUR. The terminal pre-selected DCC without offering the choice. The cardholder later disputes the charge because they did not agree to the currency conversion and received a worse exchange rate.
- An international e-commerce merchant's website is configured to charge in GBP but displays prices in USD on product pages. A US customer believes they're paying $50 USD; they're charged £50 GBP. A 12.3 chargeback follows.
- A cardholder at an international ATM selects to withdraw cash but inadvertently consents to DCC through a confusing screen that presented the DCC option without clear disclosure of the rate. They dispute the currency used.
- A restaurant in a tourist area applies DCC to all foreign cards automatically without asking. Multiple 12.3 chargebacks arrive from tourists who never consented to paying in their home currency.

---

## Merchant Liability

Merchants are liable for 12.3 chargebacks when:
- DCC was applied without proper disclosure and explicit cardholder consent.
- The terminal was misconfigured to process in the wrong currency.
- The cardholder was not given a genuine choice of currency.

Merchants may successfully defend a 12.3 chargeback when:
- The cardholder explicitly chose DCC and a signed/confirmed receipt shows the choice.
- The exchange rate and fees were disclosed clearly.
- The cardholder agreed to the currency shown at the time of the transaction.

---

## Required Evidence

To defend a 12.3 chargeback, you need to demonstrate the cardholder consented to the currency:

- **DCC consent record:** A signed receipt, electronic signature, or terminal-captured consent showing the cardholder chose DCC with disclosure of the conversion rate.
- **Terminal configuration records:** Showing your terminal is properly configured for DCC with compliant consent flow.
- **Receipt copy:** Showing both the local currency amount and the converted amount, exchange rate, and any fees.
- **Cardholder communication:** Any correspondence where the currency was discussed or confirmed.

For non-DCC currency errors:
- **Corrected transaction documentation:** If you processed in the wrong currency by mistake and have already issued a corrective credit, document this.
- **Terminal configuration logs:** Showing the correct currency was configured at the time of the transaction (to demonstrate no error occurred).

---

## Winning Strategy

1. **Show the DCC consent.** If you have a signed receipt or terminal log showing the cardholder selected DCC with full disclosure, submit this as your primary evidence. Make it visually clear — highlight the portion showing the cardholder's choice and the exchange rate disclosure.
2. **Submit DCC-compliant receipt.** A receipt showing both currencies, the exchange rate, and explicit selection of the home currency is strong evidence.
3. **If the currency error was technical,** document the configuration, acknowledge the error, and submit any corrective action taken (corrective refund in the right currency, configuration fix).
4. **For DCC program participants,** confirm your DCC provider's compliance documentation with your acquirer and include it in your response.

---

## Losing Mistakes

- **No consent documentation.** Applying DCC without keeping records of the cardholder's choice means you cannot defend the 12.3 chargeback.
- **Pre-selecting DCC.** Terminal software that defaults to DCC without presenting a genuine choice violates Visa's rules and is indefensible.
- **Not showing the exchange rate.** Even if the cardholder chose DCC, failure to disclose the rate is a compliance violation.
- **Misconfigured terminals.** Merchants who do not regularly audit their terminal currency settings create ongoing exposure to 12.3 chargebacks.

---

## Prevention

- **Implement proper DCC consent flow.** Work with your DCC provider or terminal vendor to ensure the consent screen offers a genuine choice, displays the exchange rate, and captures explicit acceptance.
- **Train staff on DCC.** Staff should know how to present the DCC choice to cardholders, explain what DCC means, and ensure the cardholder's choice is properly recorded.
- **Regular terminal audits.** Check currency settings on all terminals periodically. This is especially important after software updates.
- **E-commerce currency configuration.** Ensure your payment gateway currency matches the currency displayed on your website. Test transactions from different countries to verify the currency presented is consistent.
- **Receipt review.** Periodically review transaction receipts to confirm they include correct currency information and DCC disclosure when applicable.

---

## Timeline

| Stage | Timeframe |
|---|---|
| Transaction processed in incorrect/unconsumed currency | Day 0 |
| Cardholder receives statement | Within 30 days |
| Cardholder disputes currency issue | Within 120 days of transaction |
| 12.3 chargeback received | After issuer review |
| Merchant response deadline | 30 days from notification |

---

## Frequently Asked Questions

**Q: The cardholder signed the DCC receipt. Can they still dispute it?**
A: A signature on a DCC receipt is strong evidence of consent, but the cardholder can still dispute if they argue they were misled about what they were signing, or if the disclosure was inadequate. The best defense is a receipt that clearly shows: the local currency amount, the converted home currency amount, the exchange rate applied, any fees, and a clear indication the cardholder chose DCC.

**Q: We don't offer DCC, but we received a 12.3 chargeback. What happened?**
A: The chargeback may have been filed because the transaction was processed in an unexpected currency — perhaps due to a terminal misconfiguration, a payment gateway error, or the cardholder's issuer applied an unexpected conversion. Pull your transaction records to confirm what currency was used and compare to what the cardholder expected.

**Q: DCC made us extra revenue through the conversion spread. Do we have to stop offering it?**
A: You can continue offering DCC, but only in strict compliance with Visa's disclosure and consent rules. Coercive or non-disclosed DCC is both a 12.3 chargeback risk and a Visa rule violation that can result in your DCC program being terminated. Legitimate DCC with proper disclosure generates far fewer disputes.

**Q: Is DCC always bad for the cardholder?**
A: DCC is generally less favorable for the cardholder than paying in local currency and letting their bank handle the conversion, because DCC rates typically include a higher spread and fees. However, some cardholders prefer DCC for the certainty of knowing the exact amount in their home currency. The key is that the choice must be genuine and informed.

**Q: Can 12.3 apply to online transactions?**
A: Yes. If an e-commerce merchant charges in a currency different from what was displayed at checkout, or if the payment gateway applies an unexpected currency conversion, a 12.3 chargeback may follow. Always ensure your website displays prices and your payment gateway processes in the same currency.

---

## Sample Rebuttal Points

For DCC disputes with consent documentation:

- "The cardholder elected to pay in [home currency] using our Dynamic Currency Conversion service at the time of this transaction. The attached receipt confirms: the local currency amount of [local amount], the conversion rate of [rate], and the cardholder's selected home currency amount of [home amount]. The cardholder's choice is documented on the receipt."
- "Our terminal's DCC consent log (attached) shows the cardholder was presented with a choice between [local currency] and [home currency] at [timestamp]. The cardholder selected [home currency], confirming explicit consent. The exchange rate of [rate] was disclosed at the time of selection."

For non-DCC currency configuration errors:

- "We acknowledge that this transaction was processed in [incorrect currency] due to a terminal configuration error. We have issued a corrective credit of [correct amount] in [correct currency] on [date]. The credit transaction record is attached. We request the chargeback be withdrawn as the underlying error has been corrected."
