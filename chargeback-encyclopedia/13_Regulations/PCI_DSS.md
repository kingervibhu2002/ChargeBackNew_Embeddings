---
title: "PCI DSS for Merchants — Compliance Guide"
category: Regulations
doc_type: regulation
audience: merchants
last_updated: 2026-06-01
tags: [PCI DSS, compliance, security, CVV, data storage, SAQ, breach]
---

# PCI DSS for Merchants: What You Must Know

## What Is PCI DSS?

PCI DSS (Payment Card Industry Data Security Standard) is a set of security requirements developed and maintained by the PCI Security Standards Council — a body formed by Visa, Mastercard, American Express, Discover, and JCB to protect cardholder data across the global payment ecosystem. PCI DSS applies to any business that stores, processes, or transmits cardholder data — which means effectively every merchant that accepts card payments.

Compliance with PCI DSS is contractually required by the card networks and enforced through your acquirer. Non-compliance carries fines, increased transaction fees, and — in the event of a data breach — liability for card fraud losses that otherwise would not fall on the merchant.

PCI DSS is currently at version 4.0 (released March 2022), with full enforcement of all version 4.0 requirements by March 2025.

---

## The 12 PCI DSS Requirements

### Requirement 1: Install and Maintain Network Security Controls
Maintain firewall configurations to protect the cardholder data environment. Network segmentation isolating systems that store or transmit cardholder data from the broader corporate network reduces PCI scope significantly and limits breach exposure.

### Requirement 2: Apply Secure Configurations to All System Components
Do not use vendor-supplied default passwords or security parameters on any in-scope system. All point-of-sale terminals, servers, and network devices must be hardened with custom, secure configurations before deployment.

### Requirement 3: Protect Stored Account Data
Cardholder data that is stored must be protected with strong encryption. Critical rule: CVV/CVC values (the 3- or 4-digit security code) must never be stored after authorization is obtained. Storing the CVV — even in encrypted form — is a PCI DSS violation and the most common compliance failure for e-commerce merchants. Primary Account Numbers (PANs) must be rendered unreadable using AES-256 or equivalent encryption if stored.

### Requirement 4: Protect Cardholder Data with Strong Cryptography During Transmission
All cardholder data transmitted across open public networks must be encrypted using TLS 1.2 or higher. This applies to all checkout page traffic, gateway API calls, and any system that transmits card data between environments. Older protocols (TLS 1.0, TLS 1.1, SSL) are explicitly prohibited.

### Requirement 5: Protect All Systems Against Malware
Anti-malware solutions must be deployed on all systems commonly targeted by malicious software. Regular definition updates, periodic scans, and tamper-resistant logging of anti-malware activity are required. Merchants processing card-present transactions must inspect payment terminals regularly for physical tampering or skimmer devices.

### Requirement 6: Develop and Maintain Secure Systems and Software
All software within the cardholder data environment must receive security patches within one month of release for critical vulnerabilities. Web applications that accept card payments must be protected against known web application vulnerabilities (OWASP Top 10) either through a web application firewall (WAF) or through a documented application security review process.

### Requirement 7: Restrict Access to System Components and Cardholder Data by Business Need to Know
Access to cardholder data and systems must be role-based and granted only to personnel with a documented business need. Access rights must be reviewed at least every six months and revoked immediately upon role change or termination.

### Requirement 8: Identify Users and Authenticate Access to System Components
Every user must have a unique credential — shared accounts are prohibited. Multi-factor authentication (MFA) is required for all administrative access to the cardholder data environment and for all remote access to any in-scope system. Password complexity requirements and session timeout policies apply.

### Requirement 9: Restrict Physical Access to Cardholder Data
Facilities containing systems that store or process cardholder data must have physical access controls (badge readers, locked cabinets). Point-of-sale terminals must be inspected regularly for tampering and equipped with serial number records. Visitors must be escorted and badged.

### Requirement 10: Log and Monitor All Access to System Components and Cardholder Data
Comprehensive audit logs of all access to cardholder data environments must be maintained. Logs must be retained for at least 12 months with the most recent 3 months immediately accessible. Automated log analysis, anomaly detection, and alerting for suspicious events are required.

### Requirement 11: Test Security of Systems and Networks Regularly
External and internal vulnerability scans must be conducted quarterly. Annual penetration testing (including application-layer testing) is required. Any significant system change triggers ad-hoc testing. File integrity monitoring must detect unauthorized changes to critical system files.

### Requirement 12: Support Information Security with Organizational Policies and Programs
Maintain a documented information security policy, annual risk assessment, security awareness training, and incident response plan. Third-party vendors with access to cardholder data must be confirmed as PCI compliant. Contracts must define security responsibilities for all service providers.

---

## SAQ Levels: Which Applies to Your Business?

Most merchants complete a Self-Assessment Questionnaire (SAQ) rather than a full Quality Security Assessor (QSA) audit. The applicable SAQ depends on how your business processes card payments.

### SAQ A — Fully Outsourced
For merchants who redirect all card data handling to a PCI-compliant third party. The merchant's website does not receive, store, or process cardholder data. Examples: merchants using hosted payment pages (Stripe Checkout, PayPal Standard) where the entire card form is served by the provider. Approximately 22 requirements.

### SAQ A-EP — E-Commerce Partial Outsource
For e-commerce merchants whose website scripts or iframes could affect the security of the payment page, even if card data itself goes to a third party. Applies to JavaScript-based integrations where the merchant's page controls how the payment form loads. Approximately 191 requirements. Requires annual penetration test.

### SAQ B — Standalone Terminals
For merchants using standalone, dial-out payment terminals not connected to the internet. Card data goes directly from terminal to processor without touching any merchant-controlled software or network. Approximately 41 requirements.

### SAQ C — Payment Application Connected to Internet
For merchants with payment applications connected to the internet that do not store cardholder data. Approximately 140 requirements.

### SAQ D — All Others
For all merchants who store, process, or transmit cardholder data in their own systems and do not qualify for a simpler SAQ. Full 329 requirements. Requires quarterly ASV scans and annual penetration testing.

---

## Scope Reduction Strategies

Reducing PCI scope is the most effective compliance simplification strategy:

- **Hosted payment pages:** Card entry form served entirely from the processor's domain — your server never sees card data.
- **Tokenization:** Replace card numbers with tokens immediately upon receipt. Tokens are valueless outside the processing network.
- **Point-to-Point Encryption (P2PE):** Use a PCI-validated P2PE solution for card-present transactions. Encrypted card data is out of scope.
- **Network segmentation:** Isolate cardholder data systems behind a dedicated firewall segment, reducing the scope of PCI controls to that segment only.

---

## How PCI DSS Relates to Chargebacks

PCI DSS is primarily a data security standard, but it directly intersects with chargeback risk:

**CVV storage and fraud chargebacks:** Merchants who store CVV values in violation of Requirement 3.3 and suffer a breach will face mass fraud chargebacks from compromised card data. Compliant merchants who never store CVV cannot suffer this type of breach-driven chargeback wave.

**Breach liability:** A PCI non-compliant merchant that suffers a breach is liable for forensic investigation costs ($20,000–$100,000+), card brand fines, per-compromised-card assessments ($5–$15 per card), and potentially the fraud losses sustained by issuers on those cards.

**MATCH list placement:** A significant breach tied to PCI non-compliance can result in MATCH list placement, ending the merchant's ability to accept card payments at any acquirer for 5 years.

---

## Annual PCI Compliance Calendar

| Activity | Frequency |
|---|---|
| SAQ completion and submission | Annual |
| External vulnerability scan (Approved Scanning Vendor) | Quarterly |
| Internal vulnerability scan | Quarterly |
| Penetration test | Annual + after significant changes |
| Security awareness training | Annual |
| Incident response plan test | Annual |
| Third-party vendor PCI confirmation | Annual |
