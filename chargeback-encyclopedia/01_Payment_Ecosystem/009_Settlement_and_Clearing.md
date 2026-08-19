---
title: "Settlement and Clearing: How Merchant Funds Move"
section: "01_Payment_Ecosystem"
category: "Payment Ecosystem"
document_type: "Reference"
keywords: ["settlement", "clearing", "batch settlement", "interchange", "T+1", "T+2", "funding timeline", "merchant funding", "dispute settlement", "reserve holds", "net settlement", "clearing file", "settlement interruption", "chargeback settlement"]
difficulty: "Intermediate"
---

# Settlement and Clearing: How Merchant Funds Move

Settlement and clearing are the back-office processes through which card transaction data is converted into actual money transfers. For merchants, understanding these processes is essential because chargebacks directly interrupt and reverse the settlement flow — and understanding how funds are held, transferred, and recovered gives merchants insight into why chargebacks feel so financially impactful.

## Clearing: The Accounting Step

**Clearing** is the process of exchanging transaction information between issuers and acquirers through the card network so that the correct financial obligations can be calculated. Clearing is essentially accounting — determining who owes whom, and how much.

### How Clearing Works

1. **Batch submission**: Throughout the day, merchants accumulate authorized but uncaptured transactions. At the end of the business day (or at a configured interval), the merchant's terminal or gateway submits a **batch file** to the acquirer containing all transactions to be settled. This batch submission triggers the capture of each transaction.

2. **Acquirer processing**: The acquirer validates the batch, computes the net amount owed to the merchant (gross transaction volume minus fees, chargebacks, and refunds), and forwards the transaction data to the card network.

3. **Network clearing**: The card network (Visa, Mastercard, etc.) processes the clearing file, sorting transactions by issuer. Each issuer receives a net position — the total it owes to or is owed by the network for the day's transactions. This is a multilateral netting process, meaning the network aggregates all issuers and acquirers to compute net flows rather than processing each transaction individually.

4. **Interchange calculation**: During clearing, the network applies interchange fees to each transaction based on the card type, MCC, and transaction environment. The interchange amount is deducted from the acquirer's net position and credited to the issuer's position. This is how issuers earn revenue on each transaction.

### Clearing Timelines

- **Standard clearing**: Most transactions clear within **T+1** (one business day after the transaction date).
- **Batch cutoff times**: If a merchant misses the batch cutoff, transactions don't clear until the next business day, delaying funding by 24 hours.
- **International transactions**: Cross-border clearing can take an additional day (T+2) due to currency conversion and international banking correspondent networks.

## Settlement: Money Actually Moving

**Settlement** is the actual transfer of funds between financial institutions. Once clearing has determined what each party owes, settlement moves the money.

### Settlement Process

1. **Network settlement instructions**: After clearing, the card network issues net settlement instructions to a **settlement bank** (or directly to the Federal Reserve for U.S.-based settlement). These instructions specify which institutions owe money and which receive money.

2. **Interbank fund transfer**: Settlement occurs via wire transfer through the banking system. In the U.S., this typically runs through the Federal Reserve's Fedwire system or CHIPS (Clearing House Interbank Payments System).

3. **Acquirer-to-merchant funding**: Once the acquirer receives settled funds from the network, it credits the merchant's linked bank account. This step adds the acquirer's internal processing time to the timeline.

### Funding Timelines for Merchants

| Acquirer/PSP | Typical Funding Timeline |
|---|---|
| Direct acquirer (standard) | T+1 to T+2 |
| Stripe | 2 business days (standard), instant with premium |
| Square | Next business day (standard), instant with premium |
| PayPal | 1-3 business days to linked bank |
| High-risk merchant account | T+3 to T+7 |
| Manual review accounts | Variable, potentially weeks |

Merchants on accelerated funding programs (same-day or instant payouts) pay an additional fee for faster access to settled funds.

## Net Settlement: What Merchants Actually Receive

Merchants do not receive the gross transaction amount. The net amount deposited is:

```
Gross Transaction Volume
- Interchange Fees (paid to issuer, set by network)
- Network Assessment Fees (paid to card network)
- Acquirer/Processor Discount Rate (acquirer margin)
- Chargeback Amounts (debited when chargebacks occur)
- Chargeback Fees (per chargeback fee)
- Refund Amounts (previously processed refunds)
+ Previous Reserve Releases (if applicable)
= Net Settlement Amount
```

This net calculation happens either within the clearing/settlement cycle or separately through a monthly statement reconciliation, depending on the acquirer's billing model.

## How Disputes Interrupt Settlement

Chargebacks are fundamentally a reversal of a previously settled transaction. When a chargeback is filed:

### Immediate Debit
The card network processes the chargeback reversal, which flows from the issuer back through the network to the acquirer. The acquirer immediately debits the merchant's account for the **chargeback amount plus the chargeback fee**. This debit occurs on the next settlement cycle after the chargeback is received.

### Effect on Settlement Files
Chargebacks appear in the merchant's settlement data as negative entries. For merchants processing high volumes, chargeback debits can offset a significant portion of gross transaction volume in a settlement period.

### Pre-Settlement Chargebacks
In rare cases, a chargeback can be filed before a transaction fully settles. If the issuer files a chargeback on a transaction that is still in the clearing pipeline, the network can intercept the transaction before it funds to the merchant, effectively preventing the money from ever being deposited.

## Reserve Holds: Funds Withheld at Settlement

Acquirers use **reserve holds** to protect against chargeback losses. During the settlement process, the acquirer withholds a portion of the merchant's gross volume before depositing net funds:

### Rolling Reserve at Settlement
For merchants with rolling reserves:
- Each batch settlement is reduced by the reserve percentage (e.g., 5%).
- Reserved funds are segregated in a reserve account held by the acquirer.
- Funds released after the reserve period (e.g., 90 days) appear as credits on subsequent settlement statements.

### Reserve Fund Usage
If a chargeback exceeds the merchant's current account balance:
1. The acquirer draws from the reserve account.
2. The debit is recorded against the reserve balance.
3. Subsequent reserve contributions replenish the reserve.

### Reserve Account Interest
Reserve accounts are generally not interest-bearing for the merchant. The acquirer holds these funds as non-interest-bearing collateral. Some merchants negotiate for interest on reserves, but this is uncommon.

## Batch Settlement Best Practices

Proper batch settlement practices reduce chargeback risk and improve dispute outcomes:

- **Settle daily**: Batch transactions every day. Delays in settlement extend the time between authorization and capture, which can lead to authorization expiry issues.
- **Match capture amounts to authorization amounts**: Capturing an amount significantly different from the authorized amount (especially higher) without a new authorization is a network rule violation and chargeback risk.
- **Avoid split settlements**: Splitting a single transaction into multiple settlements is prohibited by network rules.
- **Close batches before midnight**: Late batches may be treated as next-day transactions, creating date mismatches that complicate dispute documentation.

## Currency Conversion and DCC

For merchants accepting international cards:
- Currency conversion occurs during clearing. The network applies exchange rates to convert the transaction amount from the merchant's currency to the cardholder's billing currency.
- **Dynamic Currency Conversion (DCC)** allows merchants to offer cardholders the option to pay in their home currency at point of sale. DCC transactions processed at the merchant's terminal carry different interchange rates and different chargeback characteristics (DCC-specific reason codes exist).

---

## FAQs

**Q: Why does my daily bank deposit sometimes differ from my expected amount?**
Your deposit reflects net settlement: gross transactions minus interchange, processing fees, refunds, chargebacks, and reserve withholdings. Check your settlement report for a breakdown. Unexpected shortfalls often indicate chargeback debits that processed on the same day.

**Q: Can a chargeback be filed against a transaction that hasn't settled yet?**
Yes, in some cases. Issuers can file chargebacks against transactions still in the clearing pipeline. When this happens, the network may intercept the transaction pre-funding. From the merchant's perspective, the money never arrives rather than being debited after arrival.

**Q: What happens to interchange fees when a chargeback is won?**
If a merchant wins a chargeback (the funds are returned via representment), the interchange fees originally charged on the transaction are typically not reinstated. The chargeback fee is also not refunded in most cases. Some acquirers refund the chargeback fee on a win; confirm with your acquirer.

**Q: How long can an acquirer hold reserve funds after I close my merchant account?**
Acquirers typically hold reserve funds for 90–270 days after account closure, depending on the reserve agreement terms. This holding period covers any chargebacks that may be filed against transactions processed before closure (chargebacks can be filed up to 120 days after the transaction date, and the reserve must cover that window). Ensure you understand the reserve release schedule before closing an account.

**Q: Why does it take longer to receive funds for card-not-present transactions than card-present?**
The funding timeline itself is usually the same (T+1 or T+2). However, CNP transactions carry higher fraud risk, so some acquirers apply additional review holds to CNP batches, or require new merchants to demonstrate low chargeback rates before reducing hold periods. High-risk CNP merchants may face extended funding delays as a risk management practice.
