---
title: "IP Address and Geolocation Evidence"
section: "09_Evidence"
category: "Evidence Library"
document_type: "Evidence Reference"
keywords: ["IP address", "geolocation", "IP evidence", "VPN detection", "proxy detection", "chargeback evidence", "IP geolocation", "cardholder location"]
difficulty: "Beginner"
---

# IP Address and Geolocation Evidence

## What Is IP Address Evidence?

Every device connected to the internet communicates through an IP (Internet Protocol) address — a numeric identifier that routes data packets between the device and the web servers it communicates with. When a customer places an order on your website, their device's IP address is transmitted with every HTTP request.

Capturing and logging the IP address at the time of a transaction provides a geographic and network-level data point that links the transaction to a specific location and internet service provider. In a chargeback rebuttal, this data is presented as evidence that the transaction originated from a location consistent with — or inconsistent with — the cardholder's claimed circumstances.

IP address evidence is most powerful when used in combination with other signals (device fingerprint, billing address, prior transaction patterns) rather than as standalone evidence. Alone, it can always be explained away. Combined with other consistent signals, it becomes compelling.

## Capturing IP at Transaction

IP address capture must happen at the exact moment of checkout — when the customer submits the payment form, not when they browsed the site. Many merchants capture IPs at session start or at form render, but the most relevant IP for a payment dispute is the IP from which the payment submission was made.

**What to capture:**
- The full IP address (IPv4: e.g., 203.0.113.42 or IPv6: e.g., 2001:db8::1).
- The timestamp of the transaction (same second as payment submission, in UTC with timezone noted).
- The HTTP headers that may include `X-Forwarded-For` (which reveals original IP behind proxies and load balancers).

**Where to capture it:**
- Server-side: The most reliable capture point. Your web server or application framework records the IP from the incoming HTTP request.
- Payment gateway: Some payment gateways capture and log the cardholder's IP on behalf of the merchant. Check your gateway's data exports for IP fields.

**Important:** `X-Forwarded-For` headers can be spoofed by sophisticated clients. For high-risk transactions, combine server-side IP capture with a client-side JavaScript call to an IP detection API (which captures from the browser directly) to cross-reference both values.

## IP Geolocation

Geolocation is the process of mapping an IP address to a physical location. This is not an exact science — IP addresses are associated with geographic regions, not precise addresses — but the output is generally:

- **Country:** Accurate to 95%+ for most IP addresses.
- **Region/State:** Accurate to 75–85%.
- **City:** Accurate to 50–70%. A city-level hit may be within 25–50 miles.
- **Postal code:** Accurate to 30–50%. Less reliable.

Geolocation accuracy is highest for fixed broadband connections (where ISP assigns IPs to geographic regions) and lowest for mobile networks (where IP pools cover large geographic areas) and for VPN or proxy traffic.

**Geolocation services:** MaxMind GeoIP2, IP2Location, ipstack, and ipinfo.io provide programmatic geolocation. Most fraud platforms include geolocation as a built-in feature.

## Linking IP to Cardholder's Billing Address Region

In your chargeback rebuttal, the IP-to-location argument follows this structure:

**Step 1: State the IP address.**
"The transaction was placed from IP address [203.0.113.42] at [timestamp]."

**Step 2: State the geolocation result.**
"Geolocation of this IP address resolves to [Chicago, Illinois, United States] / [ISP: Comcast / AS7922]."

**Step 3: Link to cardholder's known location.**
"The cardholder's billing address on file is [Chicago, IL 60601], consistent with the geolocation of the transaction IP address."

**Step 4: Add supporting context.**
"Prior transactions from this same cardholder account were placed from IP addresses resolving to the same ISP and metropolitan area, consistent with a single household's internet connection."

This chain of reasoning — IP → ISP → location → matches cardholder's billing address — is straightforward for an issuer analyst to evaluate and is compelling when all steps align.

## VPN and Proxy Detection

One of the most important IP enrichments is detecting whether the IP is associated with a VPN service, proxy network, or Tor exit node.

**Why VPN/proxy detection matters:**
- A legitimate cardholder in their home city would not typically route through a VPN based in another country for a routine online purchase.
- A fraudster who has stolen card data will often use a VPN or proxy to appear to be in the cardholder's home region, attempting to evade geo-mismatch detection.
- Detecting a VPN/proxy at time of transaction is a fraud risk signal.
- Detecting a VPN/proxy that the cardholder's account has never used before is an especially strong anomaly signal.

**VPN/proxy detection services:** IPQualityScore, MaxMind minFraud, ipinfo.io, and most commercial fraud platforms include VPN/proxy/Tor detection as part of their IP intelligence.

**Presenting VPN detection in evidence:**
"The IP address used for the disputed transaction ([IP]) was identified as a VPN/proxy endpoint [source: MaxMind / IPQualityScore], rather than a residential or business ISP connection. The cardholder's prior transactions were placed from residential IP addresses, suggesting this transaction may have originated from a different user routing through an anonymizing service."

Alternatively, if the disputed transaction's IP is NOT a VPN and matches the cardholder's normal ISP pattern: present this as a positive indicator that the transaction came from the cardholder's regular connection.

## How to Present IP Evidence in Dispute Response

**Formatting for issuers:**

IP evidence is best presented in a structured format with clear annotations:

```
Disputed Transaction IP Evidence (Exhibit B):

Transaction IP:       203.0.113.42
Transaction Timestamp: 2024-03-15 14:32:07 UTC
Geolocation:          Chicago, IL, United States
ISP/Organization:     Comcast Cable (AS7922)
VPN/Proxy Detected:   No
Tor Exit Node:        No

Cardholder Billing Address: 452 N. Michigan Ave, Chicago, IL 60611

Match Assessment: The transaction IP geolocates to the same city and
ISP as the cardholder's billing address, consistent with a purchase
made from the cardholder's home internet connection.

Prior Transaction IPs (Exhibit B-2): [List of prior transaction IPs
from same account, all resolving to Chicago, IL / Comcast AS7922]
```

This format is immediately readable for a dispute analyst and makes the connection between IP, location, and cardholder geography explicit without requiring the analyst to draw inferences from raw data.

## Limitations of IP Address Evidence

**Mobile network IPs:** Carrier network IP addresses (AT&T, Verizon, T-Mobile) cover large geographic areas. A mobile IP geolocating to "New York Metropolitan Area" does not precisely identify location — it might cover all five boroughs and parts of New Jersey. Combine with device fingerprint for stronger location attribution on mobile transactions.

**Shared IPs (NAT):** Many households and businesses share a single public IP address through Network Address Translation (NAT). Multiple users behind the same router share the same public IP. An IP match to a cardholder's ISP does not exclude the possibility of a different person on the same network.

**Dynamic IP assignment:** Most ISPs assign IPs dynamically — they change periodically (daily, weekly, or on each connection). An IP address used for the disputed transaction may no longer be assigned to the same household when the dispute arrives weeks later. This is fine for historical evidence (capture the IP at transaction time and present it with the contemporaneous geolocation), but do not check the geolocation weeks later and assume it is the same household.

**VPN use by legitimate customers:** Privacy-conscious legitimate customers may use VPNs. A VPN-using customer placing a legitimate purchase should not be automatically treated as a fraudster. Evaluate VPN detection as one signal among many, not a standalone disqualifier.

**IPv6 geolocation accuracy:** IPv6 geolocation is generally less accurate than IPv4 geolocation because IPv6 address blocks are newer and geolocation databases have less historical accuracy data. If your platform logs IPv6 addresses, ensure your geolocation database is current.

## Combining IP with Device Fingerprint

The combination of IP address and device fingerprint is considerably more powerful than either alone:

- IP alone: "A device in Chicago placed this order." (Could be many people.)
- Device fingerprint alone: "This specific device placed this order." (Location unknown from fingerprint.)
- IP + Device fingerprint: "This specific device, which has previously placed orders from Chicago-based Comcast IPs associated with this cardholder's account, placed this order from a Chicago-based Comcast IP." 

This combination directly links the specific device to the specific geographic footprint of the cardholder's known internet usage — a very strong combined argument for friendly fraud defense.

## Summary

IP address evidence provides geographic and network-level context for a transaction, linking the checkout session to a physical location consistent with (or inconsistent with) the cardholder's known geographic footprint. Capture IP at transaction submission time, enrich with geolocation and VPN/proxy detection, and present in a structured format that makes the IP-location-cardholder chain of inference explicit. IP evidence is most powerful when combined with device fingerprinting (which identifies the specific device) and prior transaction history (which establishes the cardholder's normal access patterns). Limitations — mobile IP imprecision, VPN use, shared NAT — should be acknowledged and addressed in your rebuttal where applicable.
