---
title: "Login Logs and Product Usage Evidence"
section: "09_Evidence"
category: "Evidence Library"
document_type: "Evidence Reference"
keywords: ["login logs", "usage logs", "product usage evidence", "SaaS evidence", "streaming evidence", "gaming evidence", "friendly fraud defense", "digital goods", "data retention"]
difficulty: "Intermediate"
---

# Login Logs and Product Usage Evidence

## Why Usage Logs Are Decisive Evidence

For digital products, subscription services, SaaS platforms, streaming services, and gaming applications, login and usage logs are the most powerful form of chargeback evidence available. No other evidence type as directly refutes a cardholder's claim of non-receipt or non-authorization.

Consider the logical structure of a "I never authorized this" chargeback:
- Cardholder claim: "I did not make this purchase and did not use this service."
- Usage log evidence: "Your account logged in [7 times] from [cardholder's device] in the [30 days] after this purchase, accessing [specific features/content]."

These two facts cannot both be true. If the cardholder's account was actively used after the transaction date — from the cardholder's own device and IP address — then the cardholder's claim of non-authorization is almost certainly false.

Usage logs are also valuable in non-receipt disputes for digital goods and in quality disputes where the cardholder claims the product did not work — if they used it extensively, it clearly worked.

## What to Log: Core Event Types

### Login Events
Every login event should be logged with:
- **Timestamp:** Date, time, and timezone (preferably UTC with local time noted).
- **User account identifier:** User ID, email address, or account number.
- **IP address:** The IP address from which the login request originated.
- **Device identifier:** Device fingerprint, device ID, or device type/OS/browser string.
- **Login method:** Password, OAuth (Google, Facebook), SSO, magic link, etc.
- **Login outcome:** Success, failed (wrong password), MFA required, MFA passed, MFA failed.
- **Geographic location (enriched):** City, country, ISP derived from IP geolocation.

### Session Events
After a successful login, track session-level events:
- Session start and end timestamps.
- Session duration.
- Actions taken during the session (feature access, content viewed, data modified).

### Product Usage Events
Specific to your platform type:

**SaaS / Business Software:**
- Feature-level access: which modules, reports, or tools were used.
- Data operations: records created, modified, or exported.
- API calls: timestamp, endpoint, result.
- Document or project access.

**Streaming / Media:**
- Content title, episode, or media item accessed.
- Playback start and end time.
- Playback duration (proves consumption, not just access).
- Device used for playback.
- Whether content was downloaded (offline viewing).

**Gaming:**
- Game session start and end.
- Character activity (quests completed, items acquired, matches played).
- In-game purchases (additional to the disputed transaction).
- Login and logout timestamps.
- Game events that demonstrate active play.

**E-Learning / Course Platforms:**
- Lesson or module accessed.
- Time spent on each module.
- Quiz or assessment submissions.
- Certificate downloads.

**Cloud Storage / File Services:**
- File upload and download events.
- Files shared or accessed.
- Storage used (increasing storage use post-purchase proves access).

## How to Present Usage Logs in Dispute Response

Raw log files are not submission-ready. A 10,000-line server log dump is not evidence — it is noise. The analyst cannot find the relevant lines, and a wall of unformatted text creates a negative impression.

**Formatting for dispute submission:**

Extract and present a targeted summary of relevant events:

```
Account Usage Log Summary — [Account ID / Email] (Exhibit C)

Account: customer@email.com (Account ID: 84729)
Disputed Transaction Date: 2024-03-15 (Order #48291)

Login Events After Disputed Transaction Date:

Date/Time (UTC)    IP Address       Device                     Action
---------------------------------------------------------------------------
2024-03-15 16:42  203.0.113.42     iPhone 15, iOS 17.2        Login (Success)
2024-03-15 16:44  203.0.113.42     iPhone 15, iOS 17.2        Accessed Premium Content
2024-03-16 09:12  203.0.113.42     MacBook Pro, macOS 14.3    Login (Success)
2024-03-16 09:15  203.0.113.42     MacBook Pro, macOS 14.3    Downloaded content (3 items)
2024-03-20 18:30  203.0.113.47     iPhone 15, iOS 17.2        Login (Success)
[...continued through dispute date...]

Total post-purchase login events: 14
Total content access events: 27
Account remains active as of [date].

Note: IP 203.0.113.42 and 203.0.113.47 both resolve to Comcast Cable,
Chicago, IL — consistent with cardholder billing address.
```

This format is immediately readable and makes the key argument without requiring the analyst to interpret raw data. The final note links the IP addresses back to the cardholder's home location.

**Annotate the rebuttal letter:**
In your rebuttal letter, reference the usage log exhibit explicitly: "As shown in Exhibit C, the cardholder's account was accessed [14 times] in the [30 days] following the disputed purchase, including [content accessed/features used]. This usage pattern is inconsistent with the cardholder's claim that they did not authorize this transaction."

## Particularly Valuable for SaaS, Streaming, and Gaming

### SaaS Platforms
For B2B SaaS disputes, usage logs are especially powerful because:
- Business software is purchased for a specific use case; accidental purchase is implausible.
- Usage of specific features (ran a report, exported data, sent an email campaign) proves deliberate, purposeful engagement with the product.
- API call logs are machine-generated and not easily fabricated — they carry high credibility.

If the cardholder generated API calls, exported reports, or integrated your service with their other tools after the disputed purchase date, this evidence is extremely compelling.

### Streaming Services
Play history is decisive. A cardholder who streams 30 hours of content in the month after a subscription charge cannot credibly claim they did not authorize the subscription. Present a clear play history:
- Titles watched, duration, dates.
- Any content favorited or saved to watchlist (proves engagement).
- Any profile customization (proves account ownership).

### Gaming
In-game event logs are uniquely detailed and granular. A dispute claiming unauthorized purchase followed by extensive gameplay (quests completed, items earned, levels advanced, matches played) is easily refuted with gaming event logs.

For in-game purchase disputes specifically: show that the disputed in-game currency was spent (what items were purchased with it, what achievements require the items). This proves the cardholder or someone with account access actively used the purchased content.

## Digital Goods Activation Records

For one-time digital goods (software keys, licenses, e-books):

**Software license activation:**
- Activation timestamp.
- Machine fingerprint (hardware ID of the activating machine).
- IP address at activation.
- Number of activation attempts (one attempt = likely the buyer; many attempts = possibly sold to others).
- Whether the license is currently active or has been revoked.

**Key activation:**
- When the key was redeemed.
- From what IP and platform.
- What account the key was redeemed to (if applicable).

**E-book download:**
- Download timestamp.
- File delivery format confirmed (e.g., PDF delivered to email, EPUB sent to device).
- Email delivery confirmation (open/click events if tracked).

## Strongest Evidence for Friendly Fraud Defense

Usage logs are the strongest friendly fraud defense available because:

1. **They are objective:** Server-generated logs are not subject to merchant manipulation claims in the same way as narrative rebuttal letters.

2. **They are specific:** Unlike "delivery confirmed" (which a cardholder can argue was stolen from their mailbox), usage logs showing specific content access or feature use require the cardholder to claim either their account was hacked or a family member used it — explanations that require them to acknowledge the service was actually received.

3. **They refute the core claim directly:** A chargeback claiming "I never authorized this transaction" is most powerfully refuted not by proving you collected payment correctly, but by proving the cardholder used what they bought.

4. **They satisfy Visa CE3.0 requirements:** Prior transaction login and device data from usage logs can be used to establish CE3.0 qualifying prior transactions, triggering liability shift back to the issuer.

## Data Retention Requirements

Chargeback disputes can arrive up to 120 days after a transaction (and occasionally later for Amex). Your logging infrastructure must retain data for at least 180 days to ensure availability for any dispute response. For CE3.0 purposes (which requires prior transaction data up to 365 days old), one year of retention is preferable.

**Practical retention guidance:**
- Transaction-level logs (purchase, refund, subscription event): Retain indefinitely or 7 years for financial compliance.
- Login and session logs: Minimum 180 days; 365 days preferred.
- Feature usage event logs: Minimum 180 days; 365 days preferred.
- IP address logs: Subject to privacy regulations (GDPR, CCPA) — retain within compliance framework with appropriate legal basis.

Ensure your data retention policies are documented and that log data is not purged on schedules shorter than your dispute response needs.

## Summary

Login and usage logs are the most direct and powerful evidence available for digital goods and subscription service chargebacks. They directly refute "never authorized" claims by demonstrating that the cardholder's account was actively used after the disputed transaction date. Build your logging infrastructure to capture login events (timestamp, IP, device), session events, and platform-specific usage events. Retain data for at least 180 days. When submitting as evidence, extract and format the relevant events into a readable summary — never submit raw log files. Usage logs, combined with device fingerprint and IP geolocation, create an evidence package that issuers consistently find compelling for friendly fraud rebuttal.
