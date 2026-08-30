"""
load_chargeback_docs.py

Indexes a chargeback knowledge base into the RAG vector store via the MCP server.
Run this once (or whenever you want to refresh the documents):

    python load_chargeback_docs.py

Then use rag_client.py to ask questions against the indexed knowledge.
"""

import asyncio
import hashlib
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from chunking import split_into_chunks


def _doc_id(title: str) -> str:
    """Same MD5[:8]-of-title scheme used by rag_server.py/api_server.py —
    see load_encyclopedia.py's identical helper for why this isn't imported
    from rag_server.py directly (its top-level embedding-model load)."""
    return hashlib.md5(title.encode()).hexdigest()[:8]

# ---------------------------------------------------------------------------
# Chargeback knowledge base
# ---------------------------------------------------------------------------

CHARGEBACK_DOCUMENTS = [

    # -----------------------------------------------------------------------
    # 1. Fundamentals
    # -----------------------------------------------------------------------
    {
        "title": "What Is a Chargeback",
        "content": """
A chargeback is a forced reversal of a payment transaction initiated by the
cardholder's issuing bank. Unlike a refund (which a merchant issues voluntarily),
a chargeback is imposed on the merchant by the card network (Visa, Mastercard,
Amex, Discover) after the cardholder files a dispute.

Key parties involved:
- Cardholder: the customer who disputes the charge.
- Issuing bank (issuer): the bank that gave the cardholder their card. It
  receives the dispute, investigates, and either sides with the cardholder or
  the merchant.
- Acquiring bank (acquirer): the bank that processes payments for the merchant.
  It receives the chargeback from the network and forwards it to the merchant.
- Card network: Visa, Mastercard, Amex, or Discover. Sets the rules and
  reason codes and adjudicates if a case escalates to arbitration.
- Merchant: the business that accepted the original payment. Has a window
  (usually 20–45 days) to respond with evidence.

Process flow:
  Cardholder disputes → Issuer reviews → Issuer files chargeback →
  Network notifies Acquirer → Acquirer notifies Merchant →
  Merchant responds with evidence → Issuer makes final decision →
  (optional) Arbitration by card network
""",
    },

    # -----------------------------------------------------------------------
    # 2. Chargeback lifecycle & timelines
    # -----------------------------------------------------------------------
    {
        "title": "Chargeback Lifecycle and Timelines",
        "content": """
Understanding the timeline is critical because missing a deadline forfeits your
right to dispute.

Stage 1 — Cardholder dispute
  The cardholder contacts their bank within 60–120 days of the transaction
  (120 days is the Visa/Mastercard limit; Amex allows up to 120 days too).
  The issuer provisionally credits the cardholder while investigating.

Stage 2 — Chargeback issued (Day 0)
  The issuer debits the transaction amount plus a chargeback fee ($15–$100)
  from the acquirer. The merchant's account is debited.
  Merchant response window: typically 20–30 days (varies by network and reason code).

Stage 3 — Merchant rebuttal (representment)
  The merchant submits a rebuttal letter plus supporting evidence.
  If compelling, the issuer may reverse the chargeback ("win").

Stage 4 — Pre-arbitration (second chargeback)
  If the issuer rejects the merchant's evidence, it may file a second
  chargeback. The merchant can accept or escalate.

Stage 5 — Arbitration
  Either party escalates to the card network. Fees can reach $500+.
  The losing party pays all arbitration fees. Use only when evidence is very strong.

Key deadlines summary:
  Cardholder to dispute:       60–120 days from transaction date
  Merchant to respond:         20–45 days from chargeback date
  Pre-arbitration response:    10–30 days
  Arbitration filing:          10 days after pre-arb deadline
""",
    },

    # -----------------------------------------------------------------------
    # 3. Visa reason codes
    # -----------------------------------------------------------------------
    {
        "title": "Visa Chargeback Reason Codes",
        "content": """
Visa uses a numerical reason code system under its Visa Claims Resolution (VCR)
framework, grouped into four categories.

FRAUD (10.x)
  10.1  EMV Liability Shift Counterfeit Fraud
        Card-present transaction; chip card used on non-chip terminal.
        Liability shifts to merchant.
  10.2  EMV Liability Shift Non-Counterfeit Fraud
        Lost/stolen card used at non-chip terminal.
  10.3  Other Fraud — Card-Present
        Fraudulent card-present transaction (no EMV dispute).
  10.4  Other Fraud — Card-Absent (CNP)
        Most common online fraud code. Cardholder did not authorise the
        transaction. Merchant must show AVS/CVV match, delivery proof,
        or 3-D Secure authentication.
  10.5  Visa Fraud Monitoring Program
        Merchant flagged by Visa's fraud monitoring; issuer files chargeback.

AUTHORIZATION (11.x)
  11.1  Card Recovery Bulletin
        Card was on the hot-card list; merchant failed to check.
  11.2  Declined Authorization
        Merchant processed transaction after authorization was declined.
  11.3  No Authorization
        Transaction processed without obtaining authorization.

PROCESSING ERRORS (12.x)
  12.1  Late Presentment
        Transaction submitted more than 30 days after the authorization date.
  12.2  Incorrect Transaction Code
        Credit processed as a sale (or vice versa).
  12.3  Incorrect Currency
        Transaction charged in a currency the cardholder did not agree to.
  12.4  Incorrect Account Number
        Wrong account number on the transaction.
  12.5  Incorrect Amount
        Charged amount differs from what the cardholder agreed to pay.
  12.6  Duplicate Processing
        Same transaction submitted twice.
  12.7  Invalid Data
        Missing or incorrect transaction data.

CONSUMER DISPUTES (13.x)
  13.1  Merchandise/Services Not Received
        Cardholder claims goods or services never arrived.
  13.2  Cancelled Recurring Transaction
        Cardholder cancelled a subscription; merchant charged anyway.
  13.3  Not as Described or Defective Merchandise
        Product arrived damaged or significantly different from listing.
  13.4  Counterfeit Merchandise
        Product is fake/counterfeit.
  13.5  Misrepresentation
        Merchant misrepresented the product or terms of sale.
  13.6  Credit Not Processed
        Merchant agreed to refund but did not process the credit.
  13.7  Cancelled Merchandise/Services
        Cardholder cancelled; merchant charged after cancellation.
  13.8  Original Credit Transaction Not Accepted
        Original credit returned to the wrong account.
  13.9  Non-Receipt of Cash or Load Transaction Value
        ATM or load transaction; cardholder did not receive cash.
""",
    },

    # -----------------------------------------------------------------------
    # 4. Mastercard reason codes
    # -----------------------------------------------------------------------
    {
        "title": "Mastercard Chargeback Reason Codes",
        "content": """
Mastercard uses a two-digit reason code system.

FRAUD
  4837  No Cardholder Authorization
        Cardholder denies authorising the transaction. Most common CNP fraud code.
  4840  Fraudulent Processing of Transactions
        Multiple fraudulent transactions on the same card.
  4849  Questionable Merchant Activity
        Merchant flagged by Mastercard's monitoring program (MATCH list).
  4853  Cardholder Dispute (used for fraud when no other code fits)
  4863  Cardholder Does Not Recognize — Potential Fraud
        Cardholder doesn't recognise the transaction; issuer investigates.
  4870  Chip Liability Shift
        Counterfeit fraud at a non-chip terminal.
  4871  Chip and PIN Liability Shift
        Lost/stolen fraud; chip-and-PIN not used.

AUTHORIZATION
  4808  Required Authorization Not Obtained
        Transaction settled without a valid authorisation.
  4812  Account Number Not on File
        Authorisation obtained for a non-existent account.

POINT-OF-INTERACTION ERRORS
  4831  Transaction Amount Differs
        Settled amount does not match the authorised amount.
  4834  Duplicate Processing
        Same transaction submitted more than once.
  4842  Late Presentment
        Transaction submitted after the allowed timeframe.
  4846  Correct Transaction Currency Code Not Provided
        Currency mismatch.

CARDHOLDER DISPUTES
  4853  Cardholder Dispute
        Broad code covering: not as described, defective goods, services not
        rendered, credit not processed, cancelled recurring.
  4855  Goods or Services Not Provided
        Merchandise or service was not delivered.
  4860  Credit Not Processed
        Merchant agreed to a refund but never issued it.
""",
    },

    # -----------------------------------------------------------------------
    # 5. Friendly fraud
    # -----------------------------------------------------------------------
    {
        "title": "Friendly Fraud and First-Party Misuse",
        "content": """
Friendly fraud (also called first-party fraud or chargeback fraud) occurs when
a legitimate cardholder makes a purchase, receives the goods or services, and
then disputes the charge with their bank — falsely claiming fraud or
non-delivery.

Why it happens:
  - "Buyer's remorse": customer regrets the purchase.
  - Convenience: it's easier to call the bank than to deal with the merchant's
    return process.
  - Deliberate abuse: customer intentionally games the system for free goods.
  - Family fraud: a family member (often a child) made the purchase without
    the account holder's awareness.

Scale of the problem:
  Friendly fraud accounts for an estimated 60–80% of all chargebacks. It is
  technically bank fraud (filing a false claim), but issuers rarely prosecute
  individual cardholders.

How to detect friendly fraud:
  - Delivery confirmation matches the cardholder's address.
  - Device fingerprint / IP address is consistent with prior purchases.
  - Customer has successfully received previous orders without dispute.
  - Customer service contacted the merchant but was unsatisfied (check logs).
  - Social media or usage evidence shows the product was received and used.

How to fight friendly fraud in a chargeback rebuttal:
  1. Provide proof of delivery (courier tracking, signature confirmation).
  2. Show the customer's login activity or product usage logs after delivery.
  3. Include customer service chat transcripts or email correspondence.
  4. Provide IP address, device ID, and location data at time of purchase.
  5. If a subscription, show login history during the disputed billing period.
""",
    },

    # -----------------------------------------------------------------------
    # 6. Chargeback prevention
    # -----------------------------------------------------------------------
    {
        "title": "Chargeback Prevention Best Practices",
        "content": """
Preventing chargebacks is far cheaper than fighting them. A chargeback costs
the merchant the transaction amount, a chargeback fee ($15–$100), and the
labour to dispute it. Win rates average only 40–60%.

Authentication tools:
  3-D Secure 2 (3DS2): Adds a layer of cardholder authentication for CNP
  transactions. If the issuer approves a 3DS2-authenticated transaction and the
  cardholder later disputes it as fraud (Visa 10.4 / MC 4837), liability shifts
  to the issuer — not the merchant. Always enable 3DS2 for high-risk orders.

  AVS (Address Verification Service): Checks that the billing address provided
  matches the issuer's records. A full AVS match (street + ZIP) significantly
  reduces fraud chargebacks.

  CVV/CVC verification: Always require the card security code for CNP
  transactions. Storing CVV is prohibited by PCI DSS.

Descriptor clarity:
  Use a recognisable billing descriptor (the name that appears on the
  cardholder's statement). If the descriptor looks unfamiliar, cardholders often
  dispute legitimate charges. Include your website or phone number in the
  descriptor where allowed.

Clear policies:
  - Display your refund, return, and cancellation policies on the checkout page
    and in order confirmation emails.
  - For subscriptions, send a reminder email before each billing cycle.
  - For digital goods, include login instructions immediately after purchase.

Delivery & fulfilment:
  - Use tracked shipping for physical goods; require signature for high-value items.
  - Send shipping confirmation emails with tracking links.
  - For high-risk orders, delay shipment until manual review is complete.

Rapid response to complaints:
  - A cardholder who gets a quick resolution from the merchant will not escalate
    to a chargeback. Offer live chat or a 24-hour email response SLA.
  - Issue proactive refunds for clearly defective or missing orders rather than
    waiting for a chargeback.

Fraud screening tools:
  - Use a fraud scoring service (Kount, Signifyd, Riskified) for CNP orders.
  - Block orders from high-risk countries or IP addresses if not your market.
  - Set velocity rules: flag multiple orders to the same address within 24 hours.

Chargeback alerts:
  Enrol in Visa's Verifi CDRN and Mastercard's Ethoca Alerts. When a cardholder
  contacts their bank, you receive an alert before a formal chargeback is filed,
  giving you time to refund and prevent it.
""",
    },

    # -----------------------------------------------------------------------
    # 7. Writing a winning rebuttal
    # -----------------------------------------------------------------------
    {
        "title": "How to Write a Chargeback Rebuttal Letter",
        "content": """
A rebuttal letter (also called a representment) is your formal response to a
chargeback. Its job is to convince the issuer to reverse the chargeback and
return the funds to the merchant.

Structure of a strong rebuttal letter:

1. Opening summary (2–3 sentences)
   State your position clearly: "We are disputing chargeback [ID] for $[amount]
   dated [date] under reason code [X]. The cardholder received the goods/services
   as ordered. The following evidence demonstrates that this chargeback is invalid."

2. Transaction summary
   - Order date, order ID, transaction amount, card last four digits
   - Product or service description
   - Delivery method and date

3. Address the specific reason code
   Tailor your argument to the exact reason code. Examples:
   - 10.4 / 4837 (fraud): Show AVS/CVV match, 3DS2 authentication result,
     delivery to billing address, IP/device data.
   - 13.1 / 4855 (not received): Show tracking number with delivery confirmation,
     signature if applicable.
   - 13.2 / 4853 (cancelled recurring): Show the cancellation policy displayed
     at sign-up, and that no cancellation request was received before billing.
   - 13.6 / 4860 (credit not processed): Show the refund transaction ID and date,
     or explain why a refund is not warranted under your policy.

4. Evidence checklist
   Include as many of the following as apply:
   - Order confirmation email sent to the cardholder
   - Proof of delivery (courier tracking page, signed POD)
   - AVS and CVV response codes from the authorisation
   - 3DS2 authentication result
   - Customer service logs (emails, chat transcripts)
   - Login / usage logs after the purchase date
   - IP address, device fingerprint, geolocation at time of purchase
   - Photos of the item shipped (for high-value goods)
   - Signed terms and conditions or cancellation policy

5. Closing
   "For the reasons and evidence above, we respectfully request that the
   chargeback be reversed and the funds returned to our account."

Tips:
  - Be concise. Issuers review hundreds of rebuttals; a clear, one-page summary
    outperforms a 20-page document dump.
  - Label every exhibit (Exhibit A: tracking confirmation, Exhibit B: order email).
  - Meet the deadline. A late submission is an automatic loss.
  - Keep a copy of every submission for your records.
""",
    },

    # -----------------------------------------------------------------------
    # 8. Chargeback thresholds & monitoring programs
    # -----------------------------------------------------------------------
    {
        "title": "Chargeback Thresholds and Monitoring Programs",
        "content": """
Card networks set maximum chargeback ratios. Exceeding them triggers monitoring
programs that can result in fines, higher processing fees, or termination of
your merchant account.

Visa Dispute Monitoring Program (VDMP):
  Early Warning:   > 0.65% chargeback ratio OR > 75 chargebacks/month
  Standard:        > 0.9% chargeback ratio OR > 100 chargebacks/month
  Excessive:       > 1.8% chargeback ratio OR > 1,000 chargebacks/month
  Consequence: Monthly fines starting at $50/chargeback; risk of account closure
  after 6 months in the Standard tier.

Visa Fraud Monitoring Program (VFMP):
  Standard:        > 0.9% fraud-to-sales ratio OR > $75,000 fraud/month
  Excessive:       > 1.8% fraud-to-sales ratio OR > $250,000 fraud/month

Mastercard Excessive Chargeback Program (ECP):
  Chargeback Monitored Merchant (CMM): 100–299 chargebacks/month AND > 1.5% ratio
  Excessive Chargeback Merchant (ECM): ≥ 300 chargebacks/month AND > 1.5% ratio
  Consequence: Fines from $1,000/month (CMM) to $100,000/month (ECM); can escalate
  to MATCH list placement (permanent ban from card acceptance).

How chargeback ratio is calculated:
  Chargeback ratio = (chargebacks filed in month) / (transactions processed in month)
  Note: Visa uses the number of chargebacks in the current month divided by
  the number of transactions in the PREVIOUS month. This lag can catch merchants
  off guard if sales volume recently dropped.

MATCH list (Member Alert to Control High-Risk Merchants):
  Formerly the Terminated Merchant File. If a merchant is placed on the MATCH
  list, virtually no acquirer will onboard them for five years. Placement reasons
  include excessive chargebacks, fraud, and PCI violations. Extremely difficult
  to remove even if placed in error.

Practical targets:
  Keep your chargeback ratio below 0.5% as a safe buffer.
  Monitor your ratio monthly, not quarterly.
""",
    },

    # -----------------------------------------------------------------------
    # 9. Chargebacks for digital goods & subscriptions
    # -----------------------------------------------------------------------
    {
        "title": "Chargebacks for Digital Goods and Subscriptions",
        "content": """
Digital goods and subscription businesses face unique chargeback challenges
because there is no physical proof of delivery and cancellations are self-service.

Common dispute reasons for digital goods:
  - "I didn't authorise this" (fraud or family account sharing)
  - "I cancelled but was still charged" (recurring billing dispute)
  - "The product didn't work as described"
  - "I forgot I had this subscription" (recognisability issue)

Prevention strategies for subscriptions:
  1. Send a reminder email 3–7 days before each renewal with a clear cancel link.
  2. Use a recognisable billing descriptor that includes your brand name.
  3. Implement an easy self-service cancellation flow — a difficult cancel process
     drives cardholders straight to their bank.
  4. For free trials, send a "your trial ends in X days" email and get explicit
     consent to bill at sign-up (checkbox, not pre-ticked).
  5. Store proof of the cardholder's agreement to your terms at sign-up
     (timestamp, IP, checkbox confirmation).

Evidence to submit for a cancelled-subscription dispute (Visa 13.2 / MC 4853):
  - Screenshot of the terms shown at sign-up with the billing frequency visible.
  - Timestamp and IP address of the sign-up event.
  - All reminder emails sent with dates.
  - Proof that no cancellation request was received (CRM records).
  - Login history showing the service was accessed during the disputed period.

Evidence to submit for a digital-goods fraud dispute (Visa 10.4):
  - IP address and device fingerprint at time of purchase.
  - Email address used — show it matches previous legitimate purchases.
  - Download logs or login timestamps after the disputed transaction.
  - 3DS2 authentication result (if enrolled).
  - AVS and CVV match on the authorisation.

Refund vs. fight:
  For low-value subscriptions (< $20), issuing an immediate refund when a
  cardholder contacts you is almost always cheaper than a chargeback (which
  adds a $15–$50 fee on top of the refund). Reserve dispute effort for
  higher-value transactions or repeat abusers.
""",
    },

    # -----------------------------------------------------------------------
    # 10. Glossary
    # -----------------------------------------------------------------------
    {
        "title": "Chargeback Glossary of Key Terms",
        "content": """
Acquirer (Acquiring Bank): The financial institution that processes card payments
  on behalf of a merchant and holds the merchant's account.

Authorization: Approval from the card issuer that the card is valid and funds
  are available. Does not guarantee the transaction won't be disputed later.

AVS (Address Verification Service): A fraud-prevention tool that checks whether
  the billing address provided by the cardholder matches the address on file with
  the issuer.

Chargeback: A forced transaction reversal initiated by the cardholder's issuing
  bank. The merchant loses the funds plus a chargeback fee.

Chargeback ratio: Chargebacks received in a month divided by transactions
  processed in the prior month (Visa) or current month (Mastercard).

CVV / CVC / CID: The 3- or 4-digit security code on a card. Verifying this code
  for CNP transactions reduces fraud risk. Merchants may not store CVV after
  authorisation (PCI DSS rule).

Compelling evidence: Documentation submitted by a merchant to prove a
  transaction was legitimate and the cardholder received what they paid for.

CNP (Card-Not-Present): Transactions where the physical card is not used at a
  terminal — e.g., online, phone, or mail-order purchases. Higher fraud risk.

Dispute: The cardholder's formal complaint to their issuing bank claiming a
  transaction is unauthorised or that goods/services were not delivered as agreed.

Friendly fraud: A chargeback filed by a legitimate cardholder who actually
  received the goods or services but disputes the transaction anyway.

Issuer (Issuing Bank): The bank that issued the cardholder's credit or debit
  card. It receives disputes and decides whether to side with the cardholder
  or the merchant.

MATCH list: Mastercard Alert to Control High-Risk Merchants. A blacklist of
  terminated merchants. Being placed on the MATCH list effectively bars a
  merchant from accepting card payments for 5 years.

Pre-arbitration: A second chargeback filed by the issuer if it rejects the
  merchant's first rebuttal. The merchant can accept or escalate to arbitration.

Reason code: A numerical or alphanumeric code assigned by the card network that
  categorises the grounds for the chargeback (e.g., Visa 10.4 = fraud CNP).

Representment: The process of a merchant formally disputing a chargeback by
  re-presenting the transaction to the issuer with supporting evidence.

3-D Secure (3DS2): An authentication protocol for CNP transactions. A successful
  3DS2 authentication shifts fraud-chargeback liability from the merchant to the
  issuer.

Visa Claims Resolution (VCR): Visa's framework that streamlined the dispute
  process into two workflows — Allocation (fraud/authorisation) and Collaboration
  (consumer disputes).

Win rate: The percentage of disputed chargebacks a merchant successfully reverses
  through representment. Industry average is roughly 40–60%.
""",
    },
]


# ---------------------------------------------------------------------------
# Indexing logic
# ---------------------------------------------------------------------------

async def main() -> None:
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["rag_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print(f"Indexing {len(CHARGEBACK_DOCUMENTS)} chargeback documents...\n")

            chunk_total = 0
            for doc in CHARGEBACK_DOCUMENTS:
                result = await session.call_tool(
                    "add_document",
                    {"title": doc["title"], "content": doc["content"]},
                )
                print(f"  {result.content[0].text}")

                # Parallel chunk collection — these 10 docs have no ##
                # markup (confirmed), so split_into_chunks() falls back to
                # its paragraph-grouped splitter automatically.
                document_id = _doc_id(doc["title"])
                chunks = split_into_chunks(doc["content"])
                for chunk in chunks:
                    await session.call_tool(
                        "add_chunk",
                        {
                            "document_title": doc["title"],
                            "document_id":    document_id,
                            "content":        chunk["content"],
                            "chunk_index":    chunk["chunk_index"],
                            "knowledge_type": chunk["knowledge_type"] or "",
                            "actors":         ", ".join(chunk["actors"]),
                            "evidence_tags":  ", ".join(chunk["evidence_tags"]),
                        },
                    )
                chunk_total += len(chunks)

            print(f"\n({chunk_total} chunks indexed)")
            print("Done! Knowledge base is ready.")
            print("Run `python rag_client.py` and ask chargeback questions.")


if __name__ == "__main__":
    asyncio.run(main())
