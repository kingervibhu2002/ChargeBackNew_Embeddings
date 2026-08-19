---
title: "Digital Goods Fraud"
section: "08_Fraud"
category: "Fraud Encyclopedia"
document_type: "Fraud Reference"
keywords: ["digital goods fraud", "no physical delivery", "account credentials", "in-game items", "software keys", "download logs", "activation records", "gaming fraud", "SaaS fraud", "streaming fraud"]
difficulty: "Intermediate"
---

# Digital Goods Fraud

## What Is Digital Goods Fraud?

Digital goods fraud occurs when fraudulent transactions are made for products that are delivered electronically — software licenses, game credits, streaming access, account credentials, in-app purchases, e-books, music, video content, or SaaS subscriptions — rather than physical goods. The defining characteristic is that there is no physical delivery to document.

Digital goods merchants face the highest chargeback rates of any commercial category. According to Chargebacks911 industry benchmarks, digital goods sectors (gaming, streaming, SaaS, adult content, digital media) routinely see dispute rates 3–5x higher than physical goods e-commerce. This elevated risk stems from structural characteristics of digital delivery: goods are delivered instantly and irreversibly, there is no shipping delay that allows fraud detection, and there is no physical item to return or recover.

## Why Digital Goods Are High-Risk

**Instant and irreversible delivery:** Once a software key is displayed, a credential set is sent, or a download link is activated, the goods are delivered. There is no time to intercept delivery after fraud is detected, unlike physical goods where you can hold a shipment.

**High resalability:** Digital goods with intrinsic cash value (game currency, gift cards, software keys) are immediately resaleable on secondary markets. A fraudster who successfully purchases $500 in game credits with a stolen card can convert them to cash within hours.

**No physical evidence of receipt:** Unlike delivered packages, there is no signature, carrier tracking, or GPS confirmation of delivery. The merchant's evidence is entirely log-based, which many issuers are less familiar with and less inclined to accept.

**Chargebacks arrive quickly:** Because digital goods are delivered instantly and used immediately, chargebacks arrive faster than in physical goods transactions. The legitimate cardholder may notice the charge the same day.

**Account takeover amplification:** Fraudsters who take over gaming, streaming, or SaaS accounts can immediately monetize high-value assets (rare in-game items, accumulated credits, stored subscription value) by transferring them out. The account holder files a chargeback for transactions they did not make within a compromised session.

## Types of Digital Goods Fraud

### Account Credentials Fraud
Fraudsters purchase subscription accounts (Netflix, Disney+, Spotify, gaming platforms) with stolen cards, then sell the credentials on secondary markets. The cardholder disputes the charge. The merchant has delivered a working account — but to a fraudster who immediately changed the password and sold access.

Evidence challenge: you can show the account was activated and used, but if the fraudster changed the account email and password, the usage evidence may not link to the original cardholder's device.

### In-Game Items and Currency
Online games with player-to-player economies (Fortnite V-Bucks, Roblox Robux, FIFA Ultimate Team coins, World of Warcraft gold, CS:GO skins) are prime fraud targets because:
- Digital currency is immediately transferable within game ecosystems.
- Rare items can be liquidated on third-party marketplaces (G2G, PlayerAuctions) for real money.
- Some game currencies are sold at a discount on grey markets funded by stolen card purchases.

### Software License Keys
Software keys (Windows licenses, Adobe Creative Cloud, antivirus subscriptions) purchased with stolen cards and sold in bulk on discount software sites. These sites sometimes unknowingly traffic in fraudulently obtained keys, which are later revoked when the chargeback is processed.

### SaaS Platform Abuse
SaaS platforms face:
- Free trial fraud (covered in 007_Subscription_Fraud.md).
- Data scraping: fraudster subscribes, scrapes proprietary database content, then disputes.
- Competitive intelligence: pays for access to premium features to reverse-engineer functionality, then disputes.
- Account credential resale: purchases team plan, invites fraudulent users, disputes.

### Streaming and Media Fraud
Stolen cards used to purchase premium streaming content (sports packages, pay-per-view events, adult content). The content is consumed in real time, the card is disputed, and the merchant cannot "undeliver" the stream.

## Evidence Requirements for Digital Goods Disputes

Because there is no physical delivery evidence, digital goods merchants must build their entire rebuttal around electronic records. These records must be comprehensive, timestamped, and directly linkable to the transaction being disputed.

### IP Address at Purchase
Capture and log the IP address at the exact moment of purchase. In your dispute response:
- State the IP address.
- Show its geolocation (ISP, city, country).
- Note whether it matches the cardholder's billing address region.
- Flag if a VPN or proxy was detected.

### Download Logs
If the product involves a download:
- Log the download timestamp.
- Log the IP address of the downloading device.
- Log the device type and browser.
- If the download link is unique per purchase (preferred), show when it was first accessed.

### Activation Records
For software requiring activation:
- Record the activation timestamp.
- Record the machine fingerprint or hardware ID.
- Record the IP address at activation.
- Show that the license was activated and has not been revoked.

### Login and Usage Logs
For account-based services (SaaS, streaming, gaming):
- Show all login events after the purchase date: timestamp, IP, device.
- Show specific usage events (content played, features accessed, API calls made).
- Show the account email used at login matches the email provided at purchase.

This usage data is the strongest possible evidence for digital goods disputes. A login record showing the cardholder's email address logged in from their normal IP address and device three days after the purchase date, and then proceeded to watch 4 hours of content, is nearly impossible to refute.

### Device Fingerprint
Capture and store the device fingerprint at purchase. Link it to any prior purchases from the same device. If the same device fingerprint was used for authenticated prior purchases that were never disputed, this is compelling evidence that the cardholder knew about and used the account.

### Email Confirmation Metadata
Retain the email confirmation sent to the cardholder:
- Timestamp of send.
- Email address sent to.
- Whether the email was opened (if your email service tracks opens).
- Any click-through events (clicking the download link, activation link, or "access your account" link).

## Industry-Specific Chargeback Codes

| Industry | Visa Code | Mastercard Code | Common Dispute Reason |
|---|---|---|---|
| Gaming | 10.4, 13.1 | 4837, 4855 | Did not authorize; did not receive |
| Streaming | 13.2, 10.4 | 4853, 4837 | Cancelled recurring; unauthorized |
| SaaS | 13.2, 13.1 | 4853, 4855 | Cancelled; service not delivered |
| Software Keys | 13.3, 10.4 | 4853, 4837 | Not as described; unauthorized |
| Adult Content | 10.4 | 4837 | Did not recognize (embarrassment-based) |

Note: Adult content chargebacks are disproportionately driven by "embarrassment disputes" — the cardholder recognizes the charge but claims fraud to avoid discussing the purchase with a bank representative or spouse. This is friendly fraud but coded as authorization dispute.

## Prevention Strategies

**Velocity limits on high-risk product categories:** Limit purchases of high-resale-value digital goods (gift cards, currency, keys) per account per day. Flag or manual-review orders exceeding thresholds.

**Account age requirements:** Require a minimum account age (7–30 days) or prior successful transaction history before allowing purchases above a threshold. New accounts purchasing high-value digital goods immediately are high-risk.

**Real-time fraud scoring:** Deploy a fraud scoring platform that integrates with your checkout. Digital goods specialists include Kount, Signifyd, Forter, and Riskified. These platforms have specific risk models for digital goods categories.

**Velocity cooling-off on failed purchases:** A legitimate customer who enters a card number incorrectly will try once or twice. A fraudster testing stolen cards will try many. Flag sessions with multiple payment failures before a success.

**2FA on account access for high-value assets:** If your platform holds transferable value (game currency, account balance), require 2FA before transfer or withdrawal. This limits the damage from account takeover.

**Delay fulfillment on high-risk scores:** For digital goods, even a 15-minute delay on flagged orders allows fraud to be detected and orders cancelled before delivery. Unlike physical goods, there is no shipping lead time — the window must be built intentionally.

## Summary

Digital goods fraud demands evidence-based dispute management because no physical delivery proof exists. Merchants must invest in comprehensive logging infrastructure — IP, device fingerprint, download events, login records, usage data — before disputes arrive. The merchants who win digital goods chargebacks are those who built their evidence systems at platform launch, not those trying to reconstruct event data after a chargeback is received.
