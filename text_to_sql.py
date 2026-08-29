"""
text_to_sql.py — Natural language to SQL for chargeback queries, scoped by role.

Security model:
  - role and merchant_id are always injected by the server from the authenticated
    session (usermaster table, resolved via auth.py). The LLM never controls
    which merchant's data is returned.
  - role='merchant' is hard-scoped to merchant_id — the merchant filter is
    force-injected into the SQL server-side regardless of what the LLM wrote,
    even if the question asks about another merchant.
  - role in ADMIN_ROLES (bankopsadmin, bankadmin_maker, bankadmin_checker) is
    NOT merchant-scoped — these are Airtel bank staff who can query across all
    merchants, or a specific one if the question names it. No filter is
    force-injected for these roles.
  - Only SELECT statements are allowed. Any attempt to run INSERT/UPDATE/DELETE/DROP
    is blocked before execution, for every role.
  - Results are capped at 100 rows to prevent large dumps.

Usage:
    result = query_chargebacks(
        question    = "show me open chargebacks above 5000",
        role        = "merchant",
        merchant_id = "AIRTEL_M001",
        db_path     = "chargebacks.db",
    )
    print(result["answer"])
"""

import difflib
import re
import sqlite3
from typing import Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

import llm_provider
from merchant_db import get_connection, MERCHANTS, NPCI_REASON_CODES
from usermaster import ADMIN_ROLES

# Known merchant id/name → id, for detecting when a merchant caller's question
# names a DIFFERENT merchant by its real identity (id or business name).
# Case-insensitive; both forms map to the same merchant_id.
_KNOWN_MERCHANTS: dict = {}
_MERCHANT_NAME_BY_ID: dict = {}
for _m in MERCHANTS:
    _KNOWN_MERCHANTS[_m["id"].lower()]   = _m["id"]
    _KNOWN_MERCHANTS[_m["name"].lower()] = _m["id"]
    _MERCHANT_NAME_BY_ID[_m["id"]] = _m["name"]

_ALL_MERCHANT_NAMES: list = [_m["name"] for _m in MERCHANTS]
_MERCHANT_NAMES_LOWER: set = {n.lower() for n in _ALL_MERCHANT_NAMES}


# ---------------------------------------------------------------------------
# Schema description injected into every LLM prompt
# ---------------------------------------------------------------------------

_SCHEMA = """
Table: chargebacks
Columns:
  id                     INTEGER  — auto primary key
  merchant_id            TEXT     — Airtel merchant ID (e.g. AIRTEL_M001)
  merchant_name          TEXT     — merchant display name
  merchant_vpa           TEXT     — UPI VPA of the merchant
  utr                    TEXT     — UPI Transaction Reference Number
  case_id                TEXT     — NPCI dispute case ID
  customer_vpa           TEXT     — customer's UPI ID
  customer_name          TEXT     — customer name
  issuing_bank           TEXT     — customer's bank (SBI, HDFC Bank, etc.)
  transaction_amount     REAL     — original transaction amount in INR
  chargeback_amount      REAL     — disputed amount in INR
  transaction_date       TEXT     — ISO date YYYY-MM-DD
  chargeback_filing_date TEXT     — date NPCI dispute was filed
  response_deadline      TEXT     — last date merchant can respond
  reason_code            TEXT     — NPCI code: U001–U010
  reason_description     TEXT     — human-readable reason
  status                 TEXT     — Open | Pending | Won | Lost | Expired | Accepted
  resolution             TEXT     — Fight | Accept | NULL (if still open)
  resolution_date        TEXT     — date resolved, or NULL
  notes                  TEXT     — free-form notes
  suggested_action       TEXT     — Fight | Accept | NULL — ADVISORY ONLY, refreshed by
                                    suggestion_poller.py (for merchants who have NOT
                                    opted into auto-decision) AND by the live dispute
                                    agent (chargeback_agent.py, via
                                    case_recommendations.py) whenever a live
                                    conversation reaches a real recommendation — either
                                    writer only ever touches this column, never status/
                                    resolution itself; the merchant still decides.
                                    Can be STALE regardless of writer: the poller runs
                                    periodically, and even a live-chat write reflects
                                    only that one conversation's moment in time. ALWAYS
                                    filter status = 'Open' AND resolution IS NULL
                                    alongside suggested_action IS NOT NULL — a
                                    resolved case must never be shown as still
                                    needing action, regardless of what's cached here.
  suggestion_reason      TEXT     — why that action is suggested (cites CBS refund
                                    record or decision_rules.py's reasoning). Does
                                    NOT include a day-count or deadline framing —
                                    that would go stale between poller runs. Compute
                                    urgency live instead: julianday(response_deadline)
                                    - julianday('now') gives days remaining (negative
                                    = overdue), always correct regardless of when the
                                    suggestion itself was last computed.

NPCI Reason Codes:
""" + "\n".join(f"  {k}: {v}" for k, v in NPCI_REASON_CODES.items()) + """

Status values:
  Open      — newly filed, merchant has not yet responded
  Pending   — merchant responded (or was auto-flagged to fight), awaiting bank decision
  Won       — merchant won the dispute
  Lost      — merchant lost the dispute
  Expired   — deadline passed without merchant response (auto-lost)
  Accepted  — merchant chose not to fight (manually, or auto-decided by
              auto_decision_poller.py) and accepted the chargeback

Date format: YYYY-MM-DD  (use SQLite date functions like date('now'), strftime)
"""


# ---------------------------------------------------------------------------
# SQL safety guard
# ---------------------------------------------------------------------------

_ALLOWED_PATTERN = re.compile(r"^\s*SELECT\b", re.IGNORECASE)

_WRITE_PATTERN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|EXEC|EXECUTE|PRAGMA|ATTACH)\b",
    re.IGNORECASE,
)

_UNION_PATTERN = re.compile(r"\bUNION\b", re.IGNORECASE)

_INJECTION_PATTERN = re.compile(
    r"(ignore\s+(previous|prior|all)\s+instructions"
    r"|forget\s+(everything|all)"
    r"|you\s+are\s+now"
    r"|new\s+system\s+prompt"
    r"|where\s+1\s*=\s*1"
    r"|--\s*$"
    r"|;\s*select)",
    re.IGNORECASE,
)

# Privilege-escalation phrasing — only meaningful for role='merchant', where
# asking to see other merchants' data is an escalation attempt. For admin
# roles this is exactly the legitimate use case, so it's checked separately
# (in _is_safe_question) and only applied when role == "merchant".
#
# Vocabulary covers "merchant" plus the synonyms a real user actually types
# ("user", "customer", "account") — confirmed live that "merchant"-only
# vocabulary let "i mean for other users" and similar phrasing slip past
# this check entirely. The underlying data was never at risk (merchant_id
# is force-injected into the SQL regardless — see query_chargebacks()'s
# _enforce_merchant_filter), but without this pattern catching the intent
# up front, the vague follow-up reached SQL generation, the LLM produced
# something that wasn't a clean SELECT, and the caller got a confusing
# "Only SELECT queries are allowed" error instead of a clear, purpose-built
# "you can only see your own data" message.
_MERCHANT_ESCALATION_PATTERN = re.compile(
    r"show\s+all\s+(merchants?|users?|customers?|accounts?)"
    r"|other\s+(merchants?|users?|customers?|accounts?)"
    r"|every\s+(merchant|user|customer|account)",
    re.IGNORECASE,
)

# Queries that are suspicious but not blocked for a MERCHANT caller — allowed
# with a warning note added to the response so the audit trail captures the
# intent. Not applied to admin roles, since "all users/data" is their normal
# job (cross-merchant oversight), not an anomaly.
_SUSPICIOUS_PATTERN = re.compile(
    r"\b(all\s+users|all\s+customers|all\s+data|all\s+records"
    r"|every\s+user|every\s+customer|dump|export\s+all)\b",
    re.IGNORECASE,
)


# Table allowlist — the ONLY table this NL interface is ever allowed to touch.
# chargebacks.db also holds `usermaster` (username/role/merchant_id/
# api_key_hash) — nothing in the SELECT-only / no-write checks above stops a
# generated query from reading it, or from reading sqlite_master (SQLite's
# always-queryable schema catalog). This is a strict allowlist rather than a
# denylist deliberately: enumerating every table/view/catalog that must NEVER
# be reachable is a losing game (new tables added later inherit the leak by
# default); requiring every reference to be pre-approved does not.
_ALLOWED_TABLES = {"chargebacks"}


def _referenced_tables(sql: str) -> set:
    """
    Extract every table name the SQL references via FROM or JOIN, handling
    comma-separated FROM lists ('FROM a, b') and multiple JOINs.
    """
    tables = set()
    from_match = re.search(
        r"\bFROM\s+(.*?)(?=\bWHERE\b|\bGROUP\s+BY\b|\bORDER\s+BY\b|\bLIMIT\b|\bJOIN\b|$)",
        sql, re.IGNORECASE | re.DOTALL,
    )
    if from_match:
        for part in from_match.group(1).split(","):
            m = re.match(r"\s*([a-zA-Z_][a-zA-Z0-9_]*)", part.strip())
            if m:
                tables.add(m.group(1).lower())
    for m in re.finditer(r"\bJOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql, re.IGNORECASE):
        tables.add(m.group(1).lower())
    return tables


def _is_safe_sql(sql: str) -> tuple:
    """
    Validate SQL for safety. Returns (is_safe, reason).

    Checks:
      1. Must be SELECT
      2. No write operations
      3. No UNION (cross-merchant row merge attack)
      4. No stacked statements (semicolon + second query)
      5. No SQL comments (used to cut off merchant filter)
      6. Only references tables in _ALLOWED_TABLES (blocks usermaster,
         sqlite_master, or any future table this interface was never meant
         to expose — checked regardless of what the SELECT/write checks
         above already caught, since none of them look at table names at all)
      7. Must reference a real table at all — a bare SELECT with no FROM
         clause (e.g. SELECT 'Yes' AS answer) means the LLM fabricated a
         literal answer instead of running a real query, typically for a
         meta-question about the conversation itself ("have you shown me
         X?") rather than an actual chargeback data question. Rejecting it
         here surfaces a clear message instead of a confusing execution
         failure further downstream (a WHERE clause with no FROM to supply
         its columns is invalid SQL and always fails at execute() anyway).
    """
    if not _ALLOWED_PATTERN.match(sql):
        return False, "Only SELECT queries are allowed."
    if _WRITE_PATTERN.search(sql):
        return False, "Write operations are not permitted."
    if _UNION_PATTERN.search(sql):
        return False, "UNION queries are not permitted."
    if ";" in sql.rstrip(";"):
        return False, "Stacked queries are not permitted."
    if "--" in sql or "/*" in sql:
        return False, "SQL comments are not permitted."
    referenced = _referenced_tables(sql)
    if not referenced:
        return False, (
            "I can only answer questions by querying your chargeback data — "
            "try asking something specific, like 'show my open chargebacks' "
            "or 'what is my win rate'."
        )
    disallowed = referenced - _ALLOWED_TABLES
    if disallowed:
        return False, "Query references a table that is not permitted."
    return True, ""


_CASE_REF_RE = re.compile(r'\b(?:UTR|NPCI)\d{6,}\w*\b', re.IGNORECASE)

_CONVERSATIONAL_PATTERN = re.compile(
    # "what is/are/does my ..." (e.g. "what is my win rate") is a real data
    # query, not a generic app-capability question — excluded via the
    # negative lookahead so it isn't misrouted into this conversational path.
    r"^\s*(can\s+i|could\s+i|how\s+(do\s+i|can\s+i|to)|is\s+it\s+possible|"
    r"do\s+you\s+(support|have)|what\s+(is|are|does)(?!\s+my\b)|tell\s+me\s+about|"
    r"explain|help\s+me|download|export|print|save|share|send)",
    re.IGNORECASE,
)

# Canned answers for common conversational questions — avoids LLM call
_CONVERSATIONAL_ANSWERS = {
    "download": (
        "Yes — every query result has a **Download CSV** button below the table. "
        "Click it to save the results as a spreadsheet."
    ),
    "export": (
        "Yes — click the **Download CSV** button below any result to export it."
    ),
    "print": (
        "Use your browser's print function (Ctrl+P / Cmd+P) after running a query. "
        "Or click **Download CSV** and open it in Excel to print from there."
    ),
}


def _check_conversational(question: str):
    """
    Return (True, answer) if the question is conversational rather than a data query.
    Return (False, '') if it should proceed as SQL.
    """
    # A specific UTR/case ID reference means this is unambiguously a data
    # lookup, never a generic conversational/capability question — checked
    # first so phrasing like "what is case id of UTR20260518M002010" isn't
    # misrouted just because it happens to start with "what is" (same
    # pattern/reasoning as classifier.py's _CASE_REF_RE: naming an exact case
    # is a stronger signal than any keyword match below could ever be).
    if _CASE_REF_RE.search(question):
        return False, ""

    q = question.strip().lower()
    for keyword, answer in _CONVERSATIONAL_ANSWERS.items():
        if keyword in q:
            return True, answer
    if _CONVERSATIONAL_PATTERN.match(question):
        # Reported live: a general policy/reason-code question ("What is
        # the resolution of U002 cases?") typed into this tab got this
        # dead-end message with no indication of where the real answer
        # lives — the merchant has no way to know this tab only ever
        # queries THEIR OWN records and was never going to answer a
        # conceptual question, in any tab, without being told so
        # explicitly. Named the other tab directly rather than leaving
        # the merchant to rediscover chat.html's tab layout on their own.
        return True, (
            "This tab answers questions about YOUR OWN chargeback records — "
            "it can't answer general questions about how a reason code or "
            "dispute process works. For a question like that, use the "
            "**Dispute Assistant** tab instead.\n\n"
            "Here, try: 'show open cases', 'what is my win rate', "
            "'which cases expire this week'."
        )
    return False, ""


def _mentions_other_merchant(question: str, own_merchant_id: str) -> bool:
    """
    True if the question names a specific merchant (by id or real business
    name) that isn't the caller's own.

    This exists because the server-side filter enforcement in
    query_chargebacks() silently re-scopes any cross-merchant SQL back to the
    caller's own merchant_id — correct for security, but if left undetected
    here the caller gets their OWN data back framed as an answer to a
    question about someone else's, with no indication of the substitution.
    That's worse than a plain rejection: it can be mistaken for genuine
    cross-merchant data. Caught here so query_chargebacks() can reject
    explicitly instead of silently substituting.
    """
    q = question.lower()
    for key, mid in _KNOWN_MERCHANTS.items():
        if key in q and mid != own_merchant_id:
            return True
    return False


def _is_safe_question(question: str, role: str, merchant_id: Optional[str] = None) -> tuple:
    """
    Detect prompt injection attempts in the natural-language question.

    The merchant-escalation checks (generic escalation phrasing, and naming a
    specific other merchant) only apply to role='merchant' — for admin roles
    cross-merchant access is the legitimate use case.
    """
    if _INJECTION_PATTERN.search(question):
        return False, "Query contains disallowed content."
    if role == "merchant":
        if _MERCHANT_ESCALATION_PATTERN.search(question):
            return False, "You can only query your own merchant's chargeback data."
        if merchant_id and _mentions_other_merchant(question, merchant_id):
            return False, "You can only query your own merchant's chargeback data."
    if len(question.strip()) > 500:
        return False, "Question too long (max 500 characters)."
    if len(question.strip()) < 3:
        return False, "Question too short."
    return True, ""


# ---------------------------------------------------------------------------
# Text → SQL
# ---------------------------------------------------------------------------

def _nl_to_sql(
    question: str,
    role: str,
    merchant_id: Optional[str],
    llm: BaseChatModel,
    previous_sql: str = "",
) -> str:
    """
    Ask the LLM to convert a natural-language question to a SQL SELECT.

    previous_sql: the exact SQL executed for the prior turn in this chat
      session, if any. This endpoint is otherwise fully stateless — each call
      only sees the current question — so a follow-up like "give me the
      complete row for this earlier result" has nothing to resolve "this"
      against without it. Passing the previous SQL (not the previous English
      question) is the precise anchor: the LLM can see exactly what filter/
      sort/limit produced the prior result and build the follow-up on top of
      it, rather than falling back to a broad, unscoped query.

    role='merchant': the merchant_id filter is described in the prompt so the
      LLM writes it into the query — and then _enforce_merchant_filter()
      re-injects it server-side anyway to guarantee it's always present,
      regardless of what the LLM actually wrote.
    role in ADMIN_ROLES: no forced filter — admin can see every merchant's
      data, or narrow to one specific merchant_id if the question names it.
      Nothing is re-injected server-side for this role; the LLM's own filter
      (or lack of one) is trusted as-is, same as any other SELECT clause.
    """
    if previous_sql and role not in ADMIN_ROLES and merchant_id:
        # previous_sql is the ALREADY-enforced SQL from the prior turn, which
        # contains a literal '?' bind placeholder from _enforce_merchant_filter
        # — meaningless outside its original params tuple. Rule 11 below tells
        # the LLM to reuse this WHERE clause verbatim; if it echoes the bare
        # '?' back as syntax instead of a real value, _enforce_merchant_filter
        # appends a SECOND '?' on top, leaving two placeholders bound to only
        # one parameter — an intermittent bug, since the LLM doesn't always
        # copy it literally. Substituting back the real value here means
        # even a verbatim echo produces valid, self-contained SQL.
        previous_sql = re.sub(
            r"merchant_id\s*=\s*\?", f"merchant_id = '{merchant_id}'", previous_sql, flags=re.IGNORECASE
        )

    if role in ADMIN_ROLES:
        persona = (
            "You are an analyst supporting Airtel Payments Bank's operations and risk "
            "staff, writing SQLite queries against the chargeback dispute system. The "
            "caller can see chargebacks across every merchant — portfolio-level "
            "oversight is the normal use case, so cross-merchant comparisons, "
            "aggregates, and named-merchant lookups are all expected, not suspicious.\n"
        )
        scope_rules = (
            "  2. This is a BANK ADMIN caller — they can see chargebacks for ALL merchants.\n"
            "     Do NOT add a merchant_id filter unless the question names a specific\n"
            "     merchant (by merchant_id or merchant_name) — in that case filter to it.\n"
            "     Otherwise return rows across every merchant.\n"
        )
    else:
        persona = (
            "You are a self-service data analyst helping one Airtel Payments Bank "
            "merchant understand their own chargeback data, writing SQLite queries "
            "against the dispute system. The caller can only ever see their own "
            "records — frame results as 'your chargebacks', and never write a query "
            "that would surface or imply visibility into any other merchant's data.\n"
        )
        scope_rules = (
            f"  2. Always include: WHERE merchant_id = '{merchant_id}' (or AND merchant_id = ...)\n"
            "     The user can only see their own data — never omit this filter, and never\n"
            "     filter to a different merchant_id even if the question names one.\n"
        )

    response = llm.invoke([
        SystemMessage(content=(
            f"{persona}"
            "Translate the caller's question into the single most precise SELECT that "
            "answers it — never a broader query than what was asked, never a column or "
            "table that isn't in the schema below, and never a guess when the schema "
            "doesn't support what's being asked (see rule 9).\n\n"
            f"{_SCHEMA}\n"
            "RULES:\n"
            "  1. Write a single SQLite SELECT statement only.\n"
            f"{scope_rules}"
            "  3. Use strftime('%Y-%m', transaction_date) for month grouping.\n"
            "  4. Use date('now') for today, date('now', '-7 days') for last week, etc.\n"
            "     SQLite date() modifiers only support days/hours/minutes/seconds/months/years —\n"
            "     there is NO 'weeks' modifier. date('now', '+4 weeks') is not an error, it\n"
            "     silently evaluates to NULL, which makes any BETWEEN/comparison using it match\n"
            "     NOTHING — a query can look correct and still return zero rows every time,\n"
            "     regardless of the actual data. ALWAYS convert weeks to days (N weeks = N*7 days)\n"
            "     before writing the modifier — e.g. 'next 4 weeks' -> date('now', '+28 days').\n"
            "  5. Return ONLY the SQL query — no explanation, no markdown, no backticks.\n"
            "  6. Limit results to 50 rows by default. EXCEPTION: if the user explicitly asks\n"
            "     for EVERY row with no cap (English: 'all', 'every'; Hindi/Hinglish: 'saare',\n"
            "     'sabhi', 'har ek') — e.g. 'saare users ke chargeback de' — do not add a LIMIT\n"
            "     at all; completeness was explicitly requested, so a silent 50-row cutoff would\n"
            "     misrepresent the answer as complete when it isn't. (Execution enforces its own\n"
            "     hard cap of 100 rows regardless, so omitting LIMIT here is always safe.)\n"
            "  7. For 'deadline this week' / 'due in N days/weeks' / 'expiring soon' style questions:\n"
            "     response_deadline BETWEEN date('now') AND date('now', '+N days'), AND also add\n"
            "     status = 'Open'. 'Due'/'expiring' means still awaiting the merchant's response —\n"
            "     a case that's already Won/Lost/Expired/Accepted/Pending is resolved (or already\n"
            "     responded to), so its original deadline is no longer actionable and must not be\n"
            "     included, even though its response_deadline value still falls in the date range.\n"
            "     Only skip the status filter if the user explicitly asks about deadlines\n"
            "     regardless of resolution status (e.g. 'including resolved cases').\n"
            "     If the count of days/weeks itself is an arithmetic expression (e.g. 'next 8\n"
            "     minus 4 weeks', 'next 10-3 days'), evaluate that arithmetic FIRST to get one\n"
            "     number, then treat it as an ordinary single 'next N units' window — i.e.\n"
            "     'next 8 minus 4 weeks' means next (8-4)=4 weeks, the exact same window as\n"
            "     'next 4 weeks': BETWEEN date('now') AND date('now', '+28 days'). Do NOT treat\n"
            "     the two numbers as separate range endpoints (that would mean weeks 4-8 out,\n"
            "     a different and not what 'minus' expresses here).\n"
            "  8. For win rate: use SUM(CASE WHEN status='Won' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)\n"
            "  8b. ALWAYS alias a single aggregate/computed column with AS <plain_words> —\n"
            "      e.g. SELECT COUNT(*) AS total_chargebacks, not bare SELECT COUNT(*). The\n"
            "      formatter turns the column name directly into the label shown to the\n"
            "      merchant; an unaliased 'COUNT(*)' or 'SUM(chargeback_amount)' renders as a\n"
            "      literal, confusing label like 'Count(*): 1' instead of a real answer like\n"
            "      'Total Chargebacks: 1'. Confirmed live — this happened for exactly that query.\n"
            "  9. GENERAL RULE for concepts this schema doesn't have a column for (arbitration/\n"
            "     pre-arbitration stage, delivery/shipping status, evidence submitted, etc.):\n"
            "     NEVER silently drop the criterion and return an unfiltered 'all rows' result —\n"
            "     that looks like a complete answer but actually ignores what was asked, which is\n"
            "     worse than an honest partial answer. Instead:\n"
            "       - If reason_code/reason_description genuinely implies the concept, filter on\n"
            "         that. Example: 'orders that were delivered but customer still disputed' —\n"
            "         U008 ('Goods or services not delivered') is the one code that IS a\n"
            "         non-delivery claim, so filter reason_code != 'U008' (every other code is\n"
            "         orthogonal to delivery, so those disputes happened despite delivery not\n"
            "         being in question).\n"
            "       - If nothing in the schema (reason_code, status, dates) plausibly relates to\n"
            "         the concept at all (e.g. arbitration stage), filter on whatever schema\n"
            "         fields ARE relevant to the rest of the question rather than everything.\n"
            "     Never fabricate a column, value, or WHERE clause that isn't grounded in what\n"
            "     the schema actually contains.\n"
            "  10. For 'top' / 'highest' / 'largest' / 'biggest' phrasing with NO explicit count\n"
            "      (e.g. 'my top chargeback amount', 'highest chargeback'): use LIMIT 1 — the\n"
            "      user wants the single highest value, not a full sorted list. Only use a\n"
            "      larger LIMIT when they give an explicit count ('top 5', 'top 10 chargebacks').\n"
            "      EXCEPTION — never use LIMIT 1 when the question asks for the highest value\n"
            "      PER GROUP (signalled by 'each'/'every'/'per' + a group noun: 'highest\n"
            "      chargeback of EACH bank', 'top amount per merchant', 'highest for every\n"
            "      customer'). That phrasing wants one row per group via GROUP BY — LIMIT 1\n"
            "      would wrongly discard every group but one. Omit LIMIT entirely in that case\n"
            "      (GROUP BY result sets are already one row per group, not per raw record).\n"
            "  12. This schema has THREE distinct dates — do not conflate them:\n"
            "        transaction_date        — when the original purchase/payment happened\n"
            "        chargeback_filing_date  — when the DISPUTE/chargeback was filed/raised\n"
            "        response_deadline       — when the merchant must respond by\n"
            "      'chargeback raised/filed/disputed on X' means chargeback_filing_date = X, NOT\n"
            "      transaction_date — those are different dates for the same case (a purchase on\n"
            "      one date can be disputed weeks later). 'purchased/bought/paid on X' means\n"
            "      transaction_date. Using the wrong one can silently return zero rows even when\n"
            "      a matching case exists, because the two dates rarely coincide.\n"
            "      'outstanding'/'do I owe'/'currently have' + a time period, with NO explicit verb\n"
            "      naming the transaction itself (contrast: 'purchased this month' IS explicit —\n"
            "      that still means transaction_date) — ALWAYS means chargeback_filing_date, never\n"
            "      transaction_date. This overrides rule 3's general 'transaction_date for month\n"
            "      grouping' default for this specific phrasing: an outstanding-amount question is\n"
            "      asking about the CHARGEBACK's own timeline (when the dispute entered the system),\n"
            "      not the original purchase's timeline — confirmed live this ambiguity was real, not\n"
            "      hypothetical: the identical question 'how much is outstanding this month?', asked\n"
            "      unchanged across separate calls, non-deterministically produced transaction_date\n"
            "      in some runs and chargeback_filing_date in others, giving genuinely different\n"
            "      rupee totals for the exact same question.\n"
            "      'outstanding'/'owe'/'due' (amount) ALSO always means status = 'Open' ONLY — never\n"
            "      'Open','Pending' or any other combination. This is the same definition of an open/\n"
            "      outstanding case used everywhere else in this application (merchant_db.py's\n"
            "      list_open_chargebacks(), the Dispute Assistant's own case-listing feature) — a\n"
            "      case in any other status (Pending, Won, Lost, Expired, Accepted) is either already\n"
            "      resolved or in a different workflow stage, not part of what the merchant currently\n"
            "      owes. Confirmed live this was ALSO drifting independently of the date-column issue\n"
            "      above — some runs included Pending cases in the sum, some didn't, for the same\n"
            "      unchanged question.\n"
            "      DO NOT apply that same status='Open' filter to a plain COUNT question with no\n"
            "      financial-liability framing and no explicit status word — 'how many chargebacks\n"
            "      do I currently have', 'how many chargebacks do I have', 'how many chargebacks have\n"
            "      I had this year' all mean the TOTAL count across every status, exactly like asking\n"
            "      'how many chargebacks have ever been filed against me' would. 'Currently have' here\n"
            "      describes the account's current chargeback history, not a filter on the case's own\n"
            "      current STATUS being literally 'Open' — that reading silently undercounts to just\n"
            "      the Open-status rows and was confirmed live to do exactly that (returned 1 instead\n"
            "      of the real total of 18). Only filter by status when the question explicitly names\n"
            "      one ('open', 'pending', 'still unresolved', 'closed', 'won', 'lost', etc.) or is\n"
            "      unambiguously about financial exposure ('outstanding', 'owe', 'at risk').\n"
            "  13. For questions about suggested_action/suggestion_reason: ALWAYS also filter\n"
            "      status = 'Open' AND resolution IS NULL — a suggestion may be stale relative to\n"
            "      a case resolved since it was last computed, and a resolved case must never be\n"
            "      shown as still needing action. If the question also asks about urgency/deadline\n"
            "      (e.g. 'how many days left', 'is this urgent'), compute it live — never assume\n"
            "      suggestion_reason contains a day-count (it deliberately doesn't, since that\n"
            "      would go stale between poller runs): use\n"
            "      CAST(julianday(response_deadline) - julianday('now') AS INTEGER) AS days_left\n"
            "      (negative means the deadline has already passed).\n"
            "  14. For 'why is my chargeback/case <status>?' style questions (e.g. 'why is my\n"
            "      chargeback pending', 'why was this rejected'): SELECT enough columns for the\n"
            "      answer to stand on its own — at minimum case_id, reason_description, status,\n"
            "      response_deadline — never a single bare column like just reason_description.\n"
            "      'Why' is asking for the explanation IN CONTEXT of a specific real case, not\n"
            "      an isolated text fragment with no case reference attached. Also do NOT add\n"
            "      LIMIT 1 unless the question or an earlier rule explicitly calls for exactly\n"
            "      one row (rule 10) — if more than one case matches, the merchant needs to see\n"
            "      all of them, not silently just the first. Confirmed live: 'why my chargeback\n"
            "      is pending' for a merchant with 2 matching Pending cases returned only\n"
            "      'Reason Description: Merchant not providing refund' with no case_id, no\n"
            "      indication a second matching case existed, and no deadline — technically not\n"
            "      wrong, but useless for actually acting on.\n"
            + (
                "  11. A previous query from THIS SAME conversation is given below. Treat the\n"
                "      current question as a CONTINUATION of it by default, not a fresh\n"
                "      independent request — this applies whether or not the question uses\n"
                "      explicit backward-reference words ('this earlier result', 'that record').\n"
                "      A bare follow-up instruction with no filter of its own (e.g. 'show me all\n"
                "      columns', 'show me all columns buddy', 'sort by amount instead', 'now as a\n"
                "      list') means: keep the previous query's WHERE clause exactly, and change\n"
                "      ONLY what this new question explicitly asks for (columns, sort order, etc).\n"
                "      Do NOT drop the previous filter just because this question doesn't restate\n"
                "      it — silently reverting to an unscoped 'all rows' query is wrong far more\n"
                "      often than continuing the prior filter is. Only drop it when the new\n"
                "      question clearly asks for something broader or unrelated (e.g. 'now show\n"
                "      me all my chargebacks', 'forget that, show everything', 'actually I meant\n"
                "      Kotak transactions' naming a completely different scope).\n\n"
                f"      Previous SQL:\n      {previous_sql}\n"
                if previous_sql else ""
            )
        )),
        HumanMessage(content=question),
    ])
    return response.content.strip()


def _enforce_merchant_filter(sql: str, merchant_id: str) -> tuple:
    """
    Inject a parameterized merchant_id filter directly into the SQL.

    Appends AND merchant_id = ? before ORDER BY / GROUP BY / LIMIT,
    or at the end. Never uses a subquery wrapper (which breaks when the
    inner SELECT omits merchant_id from its column list).

    The merchant_id value is passed as a parameter — never interpolated
    as a string — so it cannot be used for SQL injection.
    """
    sql = sql.rstrip("; \t\n")

    # Find the earliest clause that must come AFTER WHERE conditions
    tail_match = re.search(
        r"\b(order\s+by|group\s+by|limit|having)\b",
        sql,
        re.IGNORECASE,
    )

    has_where     = bool(re.search(r"\bWHERE\b", sql, re.IGNORECASE))
    connector     = "AND" if has_where else "WHERE"
    filter_clause = f"{connector} merchant_id = ?"

    if tail_match:
        pos      = tail_match.start()
        before   = sql[:pos].rstrip()
        after    = sql[pos:]
        enforced = f"{before} {filter_clause} {after}"
    else:
        enforced = f"{sql} {filter_clause}"

    return enforced, (merchant_id,)


_SUGGESTION_COL_RE = re.compile(r"\bsuggested_action\b|\bsuggestion_reason\b", re.IGNORECASE)


def _enforce_suggestion_status_guard(sql: str) -> str:
    """
    Force-inject `AND status = 'Open' AND resolution IS NULL` whenever the
    query references suggested_action/suggestion_reason, regardless of
    whether the LLM remembered to write that filter itself.

    suggested_action is written by suggestion_poller.py, a periodically-run
    script, not a live computation — a case can be resolved by the merchant
    (or auto-poller) at any point after a suggestion was last computed for
    it, and nothing clears the stale value until the next poller run. Without
    this guard, a resolved case could still surface as "needs action" purely
    because the prompt-level instruction to filter on status got dropped —
    the same defense-in-depth pattern used for merchant scoping: don't trust
    a single correctness guarantee, enforce it again independent of the LLM.

    Applied unconditionally (both merchant and admin roles) — staleness is a
    property of the data, not the caller's scope.
    """
    if not _SUGGESTION_COL_RE.search(sql):
        return sql

    sql = sql.rstrip("; \t\n")
    tail_match = re.search(r"\b(order\s+by|group\s+by|limit|having)\b", sql, re.IGNORECASE)
    has_where  = bool(re.search(r"\bWHERE\b", sql, re.IGNORECASE))
    connector  = "AND" if has_where else "WHERE"
    guard      = f"{connector} status = 'Open' AND resolution IS NULL"

    if tail_match:
        pos = tail_match.start()
        return f"{sql[:pos].rstrip()} {guard} {sql[pos:]}"
    return f"{sql} {guard}"


_COL_EQ_RE_TEMPLATE = r"{col}\s*=\s*'([^']*)'"
_COL_IN_RE_TEMPLATE = r"{col}\s+IN\s*\(([^)]*)\)"


def _extract_column_literals(sql: str, column: str) -> list:
    """
    Return every quoted string literal filtered against `column`, whether
    written as `column = '...'` or `column IN ('...', '...')`.

    Both forms are common LLM output for "give me X for merchant A and
    merchant B" — an earlier version of this check only matched the `=` form
    and silently missed IN (...) lists entirely, which would have let a
    merchant-role caller reference another merchant via IN() undetected.
    """
    literals = list(re.findall(_COL_EQ_RE_TEMPLATE.format(col=column), sql, re.IGNORECASE))
    for m in re.finditer(_COL_IN_RE_TEMPLATE.format(col=column), sql, re.IGNORECASE):
        literals += re.findall(r"'([^']*)'", m.group(1))
    return literals


def _sql_references_other_merchant(sql: str, own_merchant_id: str) -> bool:
    """
    True if the LLM-generated SQL filters on a merchant_id or merchant_name
    literal that isn't the caller's own.

    This is deliberately checked against the generated SQL itself, not the
    natural-language question: a question-side keyword/name check (like
    _mentions_other_merchant) only catches merchants it already knows the
    real name/id of, so a typo, a retired display name, or any other variant
    phrase sails straight through — the LLM still writes a merchant_name
    filter for whatever string the user typed, that filter still returns
    zero rows once force-scoped to the caller's own merchant_id, and the
    caller just sees an unexplained "no results" instead of a clear denial.
    Checking the SQL catches every such case, because it only cares whether
    a DIFFERENT identity was filtered on at all, not what string it was.
    """
    own_name = _MERCHANT_NAME_BY_ID.get(own_merchant_id, "").lower()
    for lit in _extract_column_literals(sql, "merchant_id"):
        if lit != own_merchant_id:
            return True
    for lit in _extract_column_literals(sql, "merchant_name"):
        if lit.strip().lower() != own_name:
            return True
    return False


def _correct_merchant_name_typos(sql: str) -> tuple:
    """
    Fuzzy-correct merchant_name literals that don't exactly match any real
    merchant name (e.g. 'Airtel Boroadband Solutions' -> 'Airtel Broadband
    Solutions'), in both `= '...'` and `IN (...)` forms.

    Without this, a single-letter typo in an admin's question silently drops
    that merchant from the result — the misspelled literal matches zero rows,
    with no error and no indication anything was wrong. Admin queries are
    exactly where this bites hardest, since admins are the ones deliberately
    naming multiple merchants in one question.

    Returns (corrected_sql, corrections) — corrections is a list of
    (typed, corrected) pairs for any fix actually applied, so the caller can
    tell the user their spelling was corrected rather than silently rewriting
    their query underneath them.
    """
    corrections = []

    def _closest(typed: str) -> Optional[str]:
        if typed.lower() in _MERCHANT_NAMES_LOWER:
            return None  # already an exact match, nothing to correct
        match = difflib.get_close_matches(typed, _ALL_MERCHANT_NAMES, n=1, cutoff=0.75)
        return match[0] if match else None

    def _fix_eq(m):
        typed = m.group(1)
        fixed = _closest(typed)
        if fixed:
            corrections.append((typed, fixed))
            return f"merchant_name = '{fixed}'"
        return m.group(0)

    def _fix_in(m):
        items = re.findall(r"'([^']*)'", m.group(1))
        fixed_items = []
        for typed in items:
            fixed = _closest(typed)
            if fixed:
                corrections.append((typed, fixed))
                fixed_items.append(fixed)
            else:
                fixed_items.append(typed)
        return "merchant_name IN (" + ", ".join(f"'{v}'" for v in fixed_items) + ")"

    sql = re.sub(_COL_EQ_RE_TEMPLATE.format(col="merchant_name"), _fix_eq, sql, flags=re.IGNORECASE)
    sql = re.sub(_COL_IN_RE_TEMPLATE.format(col="merchant_name"), _fix_in, sql, flags=re.IGNORECASE)
    return sql, corrections


# ---------------------------------------------------------------------------
# Column-level PII policy
# ---------------------------------------------------------------------------

# Columns suppressed for a MERCHANT caller by default — internal IDs / their
# own identity, which they already know and which could aid enumeration
# attacks. Admin callers keep merchant_id/merchant_name/merchant_vpa visible —
# a cross-merchant result set is meaningless without knowing whose row is whose.
_HIDDEN_COLS_MERCHANT = {"id", "merchant_id", "merchant_name", "merchant_vpa"}
_HIDDEN_COLS_ADMIN    = {"id"}
_MERCHANT_IDENTITY_COLS = {"merchant_id", "merchant_name", "merchant_vpa"}

# Question phrasing that explicitly asks for the caller's own merchant
# identity back — e.g. "...along with my merchant name". Without this, a
# merchant explicitly requesting their own merchant name would still have it
# silently stripped by the default hidden-column suppression above, even
# though the LLM correctly included it in the SELECT — the display layer
# would be discarding something the caller asked for by name.
_MERCHANT_IDENTITY_KEYWORDS = (
    "merchant name", "merchant id", "merchant_id", "merchant vpa",
    "which merchant", "my merchant",
)

# Columns that contain customer PII — partially masked before display, for every role.
_PII_COLS = {"customer_vpa", "customer_name"}


def _hidden_cols(role: str, question: str = "") -> set:
    if role in ADMIN_ROLES:
        return _HIDDEN_COLS_ADMIN
    if any(kw in question.lower() for kw in _MERCHANT_IDENTITY_KEYWORDS):
        return _HIDDEN_COLS_MERCHANT - _MERCHANT_IDENTITY_COLS
    return _HIDDEN_COLS_MERCHANT


def _mask_value(col: str, val) -> str:
    """
    Partially mask PII column values.

    customer_vpa  customer7899@upi  → cust[---]@upi
    customer_name Customer 7899     → Customer [---]
    """
    if val is None:
        return ""
    s = str(val)
    if col == "customer_vpa" and "@" in s:
        local, domain = s.split("@", 1)
        return local[:4] + "[---]@" + domain
    if col == "customer_name":
        parts = s.split(" ", 1)
        return parts[0] + " [---]"
    return s


# ---------------------------------------------------------------------------
# Result formatter
# ---------------------------------------------------------------------------

def _rows_to_dicts(rows, role: str, question: str = "") -> list:
    """
    Convert sqlite3.Row results to plain dicts with PII masking applied.
    Hidden columns are excluded (role- and question-dependent). Used for CSV
    export on the client side.
    """
    result = []
    if not rows:
        return result
    hidden = _hidden_cols(role, question)
    for row in rows:
        d = {}
        for col in row.keys():
            if col in hidden:
                continue
            val = row[col]
            if col in _PII_COLS:
                val = _mask_value(col, val)
            d[col] = val if val is not None else ""
        result.append(d)
    return result


def _format_rows(rows, question: str, role: str) -> str:
    """Convert raw DB rows into a human-readable response with PII masking."""
    if not rows:
        return "No chargebacks found matching your query."

    cols   = rows[0].keys()
    hidden = _hidden_cols(role, question)

    # Single-value summary (COUNT, SUM, AVG, win_rate, etc.)
    if len(rows) == 1 and len(cols) == 1:
        col   = cols[0]
        value = rows[0][col]
        if isinstance(value, float):
            value = f"{value:,.2f}%"  if "rate" in col.lower() else f"₹{value:,.2f}" if "amount" in col.lower() else f"{value:,.2f}"
        return f"{col.replace('_', ' ').title()}: **{value}**"

    # Table format with PII masking and column filtering
    lines = []
    for i, row in enumerate(rows, 1):
        parts = []
        for col in cols:
            if col in hidden:
                continue                        # suppress internal/redundant columns
            val = row[col]
            if val is None:
                continue
            label = col.replace("_", " ").title()
            if col in _PII_COLS:
                val = _mask_value(col, val)     # partial mask for customer data
            elif col in ("transaction_amount", "chargeback_amount") and isinstance(val, (int, float)):
                val = f"₹{val:,.2f}"
            parts.append(f"{label}: {val}")
        lines.append(f"**{i}.** " + "  |  ".join(parts))

    pii_note = "\n\n*Customer identifiers are partially masked for privacy.*"
    header   = f"Found **{len(rows)}** record(s):\n\n"
    return header + "\n".join(lines) + pii_note


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def query_chargebacks(
    question:     str,
    role:         str,
    merchant_id:  Optional[str] = None,
    db_path:      str = "chargebacks.db",
    groq_api_key: Optional[str] = None,
    previous_sql: str = "",
) -> dict:
    """
    Convert a natural-language question to SQL, execute it, and return results.

    Security pipeline:
      1. Question injection check  — reject prompt injection (and, for role=
         'merchant', cross-merchant escalation phrasing) in the question
      2. LLM generates SQL, prompted according to role's scope (+ previous_sql
         as context for follow-up references, if provided)
      3. SQL safety check          — SELECT only, no UNION, no comments, no writes
      4. Merchant filter enforce   — only for role='merchant': parameterized
         wrap, merchant_id never interpolated, always the caller's own id.
         Admin roles skip this step entirely — they're allowed cross-merchant.
      5. Execute (read-only conn)
      6. Cap results at 100 rows
      7. Format for display (role determines which columns are hidden)

    Args:
        question     (str): Caller's natural-language question.
        role         (str): 'merchant' or one of usermaster.ADMIN_ROLES —
                             resolved server-side from the authenticated session.
        merchant_id  (str): Required when role='merchant'; ignored for admin roles.
        db_path      (str): Path to SQLite DB.
        groq_api_key (str): Explicit Groq API key override — bypasses
                             llm_provider.py's LLM_PROVIDER setting and
                             always uses Groq. Leave unset to use whichever
                             provider LLM_PROVIDER configures (default groq).
        previous_sql (str): The SQL executed for the prior turn in this chat
                             session, if any — lets the LLM resolve follow-up
                             references ("this earlier result", "that record").
                             This endpoint is otherwise stateless per-call; the
                             caller (chat.html) is responsible for remembering
                             and re-sending it. Note this only ever informs the
                             PROMPT — the SQL actually executed is still freshly
                             generated and passes through the full safety
                             pipeline below regardless of what previous_sql says.

    Returns:
        dict: sql, answer, rows, error, and (only set True on the Step 0
        conversational bail-out below) conversational — callers must check
        this before treating `answer` as a real, data-derived answer.
    """
    is_admin = role in ADMIN_ROLES
    if not is_admin and role != "merchant":
        return {"sql": "", "answer": "", "rows": 0, "error": f"Unknown role: {role}"}
    if not is_admin and not merchant_id:
        return {"sql": "", "answer": "", "rows": 0, "error": "merchant_id is required for role='merchant'."}

    # groq_api_key is a Groq-specific override, kept for backward
    # compatibility (nothing in this codebase currently passes it — grep-
    # verified — but an external caller might supply it directly). The
    # default path is provider-aware via llm_provider.py
    # (LLM_PROVIDER=groq|openai), shared with chargeback_agent.py so the
    # two callers can't drift on model names or error messages the way this
    # project's Groq model choice already did once (see llm_provider.py).
    try:
        if groq_api_key:
            from langchain_groq import ChatGroq
            llm = ChatGroq(model="openai/gpt-oss-120b", api_key=groq_api_key, temperature=0)
        else:
            llm = llm_provider.make_llm()
    except ValueError as e:
        return {"sql": "", "answer": "", "rows": 0, "error": str(e)}

    # Step 0 — conversational questions (download, how-to, etc.) → text answer
    is_conv, conv_answer = _check_conversational(question)
    if is_conv:
        # "conversational": True is the only thing that distinguishes this
        # from a real, SQL-derived answer — same shape otherwise (error="",
        # answer=<text>). Reported live: chargeback_agent.py calls this
        # function directly (code reuse, not an HTTP hop) from several
        # spots when it detects a data-lookup intent, and blindly trusted
        # result["answer"] as if it always meant "here's the merchant's
        # data" — surfacing THIS tab's own "I can't answer that here, try
        # the other tab" bail-out as the Dispute Assistant's own answer,
        # nonsensically telling the merchant to go to the tab they were
        # already in. Callers must check this flag before treating
        # `answer` as real content.
        return {"sql": "", "answer": conv_answer, "rows": 0, "error": "",
                "suspicious": False, "rows_data": [], "conversational": True}

    # Step 1 — question injection guard + suspicious intent flag
    safe_q, reason_q = _is_safe_question(question, role, merchant_id)
    if not safe_q:
        return {"sql": "", "answer": "", "rows": 0, "error": reason_q,
                "suspicious": True, "rows_data": []}
    # Broad-language flag only matters for a merchant caller — for admin
    # roles, cross-merchant breadth is the normal use case, not an anomaly.
    suspicious = (not is_admin) and bool(_SUSPICIOUS_PATTERN.search(question))

    # Step 2 — generate SQL
    try:
        sql = _nl_to_sql(question, role, merchant_id, llm, previous_sql[:1000])
    except Exception:
        # Deliberately not str(e) here — for a provider-side failure (e.g.
        # a Groq rate-limit 429) that's the raw API exception body: org ID,
        # billing links, internal error codes. Confirmed live this was
        # reaching the merchant verbatim as the chat answer via
        # chargeback_agent.py's `result.get("error")` fallback. A generic,
        # merchant-safe message here, same tone as guardrails.py's
        # CostCircuitBreaker ("Daily limit reached"), not a diagnostic.
        return {"sql": "", "answer": "", "rows": 0,
                "error": "Unable to look up that right now — please try again in a few minutes."}

    # Step 2b — fuzzy-correct merchant_name typos before anything downstream
    # relies on exact string matches (safety checks, execution, formatting).
    sql, name_corrections = _correct_merchant_name_typos(sql)

    # Step 3 — SQL safety check
    safe_sql, reason_sql = _is_safe_sql(sql)
    if not safe_sql:
        return {"sql": sql, "answer": "", "rows": 0, "error": reason_sql}

    # Step 3b — for a merchant caller, reject outright if the generated SQL
    # filters on any merchant_id/merchant_name other than their own — catches
    # every phrasing (typos, retired names, made-up names), not just the
    # handful of real merchant names _is_safe_question already knows about.
    # Without this, such a query would still execute (force-scoped to the
    # caller's own merchant_id), return zero rows because the mismatched
    # name/id never matches, and surface as an unexplained "no results"
    # instead of a clear denial.
    if not is_admin and _sql_references_other_merchant(sql, merchant_id):
        return {"sql": sql, "answer": "", "rows": 0,
                "error": "You can only query your own merchant's chargeback data.",
                "suspicious": True, "rows_data": []}

    # Step 4 — enforce merchant filter with parameterized binding.
    # Admin roles are NOT scoped to a single merchant, so nothing is forced —
    # the LLM's own SQL (validated as SELECT-only above) is executed as-is.
    if is_admin:
        wrapped_sql, params = sql, ()
    else:
        wrapped_sql, params = _enforce_merchant_filter(sql, merchant_id)

    # Step 4b — force a fresh status check on any query touching suggestion
    # columns, for both roles — see _enforce_suggestion_status_guard() for why.
    wrapped_sql = _enforce_suggestion_status_guard(wrapped_sql)

    # Step 5 — execute read-only
    # conn.close() lives in `finally`, not right after execute() in the try
    # body — a bare try/except left the connection open (and its lock held)
    # on every query that failed at execute(), not just ones that failed to
    # even connect. In a long-running server process, every such failure
    # accumulated one more unclosed connection, which is exactly the kind of
    # thing that eventually causes unrelated writers (like a schema
    # migration or auto_decision_poller.py) to hit "database is locked".
    conn = None
    try:
        conn = get_connection(db_path)
        rows = conn.execute(wrapped_sql, params).fetchmany(100)
    except sqlite3.Error as e:
        # Never expose raw DB error to client — may leak schema details
        return {"sql": wrapped_sql, "answer": "", "rows": 0,
                "error": "Query could not be executed. Please rephrase your question."}
    finally:
        if conn is not None:
            conn.close()

    # Step 6 — format display text + collect raw data for CSV export
    answer    = _format_rows(rows, question, role)
    rows_data = _rows_to_dicts(rows, role, question)

    if suspicious:
        answer += (
            "\n\n⚠️ *Your query used broad language ('all users/data'). "
            "Only your own chargeback records are shown. "
            "Customer identifiers are partially masked.*"
        )

    if name_corrections:
        fixes = "; ".join(f"'{typed}' → '{fixed}'" for typed, fixed in name_corrections)
        answer += f"\n\n*Note: corrected merchant name spelling — {fixes}.*"

    return {
        "sql":        wrapped_sql,
        "answer":     answer,
        "rows":       len(rows),
        "error":      "",
        "suspicious": suspicious,
        "rows_data":  rows_data,   # raw dicts for client-side CSV download
    }
