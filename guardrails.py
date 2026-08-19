"""
guardrails.py — Safety and operational guardrails for the chargeback RAG system.

Provides six standalone utilities used across api_server.py and
chargeback_agent.py. Each utility is independent — import only what you need.

  mask_pii()            — redact card numbers, CVV, and SSN from text
  detect_prompt_injection() — detect LLM hijack attempts
  check_length()        — enforce min/max query length
  RateLimiter           — per-user sliding-window rate limiter with abuse blocking
  AuditLogger           — append-only JSONL compliance log (PII-safe)
  CostCircuitBreaker    — daily LLM call counter that trips on threshold
"""

import json
import re
import time
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Optional


def _parse_json_safe(text: str, fallback: dict) -> dict:
    """
    Robustly extract a JSON object from an LLM response string.

    Tries three strategies before returning the fallback dict:
      1. Direct json.loads() — works when response is pure JSON.
      2. Extract from ```json ... ``` markdown code block.
      3. Extract the first { ... } substring found anywhere in text.

    Args:
        text     (str):  Raw LLM response text.
        fallback (dict): Returned if all strategies fail.

    Returns:
        dict: Parsed JSON object, or fallback on failure.
    """
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return fallback


# ---------------------------------------------------------------------------
# PII Masking
# ---------------------------------------------------------------------------

# Card numbers: 13-19 digits, optionally separated by spaces or hyphens
_CARD_RE = re.compile(r'\b(?:\d[ -]?){13,19}\b')
# CVV/CVC: 3-4 digits near relevant keyword
_CVV_RE  = re.compile(r'(?:cvv|cvc|security\s+code)[:\s]*\d{3,4}', re.IGNORECASE)
# US Social Security Numbers: 9 digits with optional separators
_SSN_RE  = re.compile(r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b')


def mask_pii(text: str) -> str:
    """
    Replace PII patterns in text with safe redaction placeholders.

    Covers payment card numbers, CVV/CVC codes, and US Social Security
    Numbers. Applied to all user queries before they are written to logs,
    ensuring PII never enters the audit trail.

    Args:
        text (str): Raw input text that may contain PII.

    Returns:
        str: Text with sensitive values replaced by [REDACTED] markers.
    """
    text = _CARD_RE.sub('[CARD-REDACTED]', text)
    text = _CVV_RE.sub('[CVV-REDACTED]', text)
    text = _SSN_RE.sub('[SSN-REDACTED]', text)
    return text


# ---------------------------------------------------------------------------
# Prompt Injection Detection
# ---------------------------------------------------------------------------

_INJECTION_PATTERNS = [
    r'ignore\s+(previous|prior|all)\s+instructions',
    r'you\s+are\s+now\s+(a\s+)?different',
    r'pretend\s+you\s+(have\s+no|are)',
    r'act\s+as\s+if\s+you',
    r'disregard\s+(your|all)',
    r'new\s+system\s+prompt',
    r'jailbreak',
    r'\bDAN\b',
    r'override\s+(your|all)',
    r'forget\s+(everything|all\s+previous)',
    r'you\s+have\s+no\s+restrictions',
]
_INJECTION_RE = re.compile('|'.join(_INJECTION_PATTERNS), re.IGNORECASE)


def detect_prompt_injection(text: str) -> bool:
    """
    Detect whether text contains known prompt injection patterns.

    Checks for common techniques used to override LLM system instructions.
    Applied to queries before any LLM call so the injected instructions
    never reach the model.

    Args:
        text (str): User input text to inspect.

    Returns:
        bool: True if an injection pattern is detected.
    """
    return bool(_INJECTION_RE.search(text))


# ---------------------------------------------------------------------------
# Length Validation
# ---------------------------------------------------------------------------

def check_length(text: str, min_len: int = 10, max_len: int = 2000) -> Optional[str]:
    """
    Validate that a query is within acceptable length bounds.

    Short inputs (< 10 chars) are usually not genuine disputes.
    Long inputs (> 2000 chars) risk hitting LLM context limits and
    increasing per-query cost.

    Args:
        text    (str): The user's raw input.
        min_len (int): Minimum acceptable character count. Default 10.
        max_len (int): Maximum acceptable character count. Default 2000.

    Returns:
        Optional[str]: An error message if validation fails, None if OK.
    """
    stripped = text.strip()
    if len(stripped) < min_len:
        return "Query too short. Please describe your dispute in more detail."
    if len(stripped) > max_len:
        return f"Query too long. Please summarise your dispute in under {max_len} characters."
    return None


# ---------------------------------------------------------------------------
# Rate Limiter
# ---------------------------------------------------------------------------

class RateLimiter:
    """
    In-memory sliding-window rate limiter with abuse detection.

    Tracks request timestamps per user identifier (typically the client IP).
    Enforces a per-hour request cap and temporarily blocks users who
    repeatedly submit abusive or invalid inputs.

    Usage:
        limiter = RateLimiter(max_requests=20, window_seconds=3600)

        error = limiter.check("192.168.1.1")
        if error:
            return 429 response

        # When a query is rejected as abusive:
        limiter.record_abuse("192.168.1.1")
    """

    def __init__(
        self,
        max_requests:    int = 20,
        window_seconds:  int = 3600,
        abuse_threshold: int = 5,
        block_seconds:   int = 1800,
    ):
        """
        Args:
            max_requests    (int): Max requests allowed per window. Default 20/hour.
            window_seconds  (int): Sliding window duration in seconds. Default 3600.
            abuse_threshold (int): Abusive inputs before a temporary block. Default 5.
            block_seconds   (int): Duration of the abuse block in seconds. Default 1800 (30 min).
        """
        self._max_requests    = max_requests
        self._window          = window_seconds
        self._abuse_threshold = abuse_threshold
        self._block_seconds   = block_seconds
        self._history         = defaultdict(list)   # user_id → [timestamp, ...]
        self._blocked         = {}                  # user_id → unblock_at timestamp
        self._abuse_count     = defaultdict(int)    # user_id → abuse event count

    def check(self, user_id: str) -> Optional[str]:
        """
        Check whether a user is allowed to make a request right now.

        Prunes old timestamps, checks block status, and enforces the
        sliding-window cap in one pass.

        Args:
            user_id (str): Unique user identifier (e.g. client IP address).

        Returns:
            Optional[str]: Error message if blocked or rate-limited, None if allowed.
        """
        now = time.time()

        # Check temporary abuse block
        if user_id in self._blocked:
            if now < self._blocked[user_id]:
                remaining = int(self._blocked[user_id] - now)
                mins = remaining // 60 + 1
                return f"Too many invalid requests. Try again in {mins} minute(s)."
            del self._blocked[user_id]
            self._abuse_count[user_id] = 0

        # Prune timestamps outside the sliding window
        self._history[user_id] = [
            t for t in self._history[user_id] if now - t < self._window
        ]

        if len(self._history[user_id]) >= self._max_requests:
            return (
                f"Rate limit reached ({self._max_requests} requests/hour). "
                "Try again later."
            )

        self._history[user_id].append(now)
        return None

    def record_abuse(self, user_id: str) -> None:
        """
        Record one abusive or invalid input event for a user.

        After abuse_threshold events the user is blocked for block_seconds.

        Args:
            user_id (str): Unique user identifier.
        """
        self._abuse_count[user_id] += 1
        if self._abuse_count[user_id] >= self._abuse_threshold:
            self._blocked[user_id] = time.time() + self._block_seconds


# ---------------------------------------------------------------------------
# Audit Logger
# ---------------------------------------------------------------------------

class AuditLogger:
    """
    Append-only JSONL audit logger for all chargeback API activity.

    Each line is a self-contained JSON object with timestamp, user,
    PII-safe query, result summary, and latency. Required for financial
    services compliance and post-incident investigation.

    Usage:
        logger = AuditLogger("audit.log")
        logger.log(
            user_id="127.0.0.1",
            endpoint="/dispute",
            query="I got a Visa chargeback...",
            result={"decision": "fight", "reason_code": "Visa 13.1"},
            latency_ms=1840,
        )
    """

    def __init__(self, path: str = "audit.log"):
        """
        Args:
            path (str): Path to the JSONL log file. Created if absent.
                        Always appended to, never truncated.
        """
        self._path = Path(path)

    def log(
        self,
        user_id:    str,
        endpoint:   str,
        query:      str,
        result:     dict,
        latency_ms: int,
    ) -> None:
        """
        Append one audit record to the log file.

        PII is masked before writing — raw card numbers or SSNs are never
        stored even if present in the original query.

        Args:
            user_id    (str):  User identifier (e.g. client IP).
            endpoint   (str):  API path called (e.g. "/dispute", "/search").
            query      (str):  The user's query (PII-masked before logging).
            result     (dict): Response summary fields.
            latency_ms (int):  Request duration in milliseconds.
        """
        record = {
            "ts":          datetime.utcnow().isoformat() + "Z",
            "user_id":     user_id,
            "endpoint":    endpoint,
            "query":       mask_pii(query),
            "decision":    result.get("decision", ""),
            "reason_code": result.get("reason_code", ""),
            "valid":       result.get("is_valid_query", True),
            "latency_ms":  latency_ms,
        }
        with self._path.open("a") as f:
            f.write(json.dumps(record) + "\n")


# ---------------------------------------------------------------------------
# Cost Circuit Breaker
# ---------------------------------------------------------------------------

class CostCircuitBreaker:
    """
    Daily LLM call counter that opens (blocks requests) when a limit is hit.

    Prevents runaway cost from bugs, abusive traffic, or misconfiguration.
    Resets automatically at midnight UTC. When open, the /dispute endpoint
    returns 503 instead of calling the LLM.

    Usage:
        breaker = CostCircuitBreaker(max_daily_calls=500)

        if breaker.is_open():
            raise HTTPException(503, "Daily limit reached")

        breaker.record_calls(n=7)   # each dispute run uses ~7 LLM calls
    """

    def __init__(self, max_daily_calls: int = 500):
        """
        Args:
            max_daily_calls (int): Maximum LLM calls allowed per calendar day.
                                   Each dispute request makes ~7 calls (one per node).
                                   Default 500 ≈ ~70 full dispute runs/day.
        """
        self._max   = max_daily_calls
        self._count = 0
        self._day   = date.today()

    def _reset_if_new_day(self) -> None:
        today = date.today()
        if today != self._day:
            self._count = 0
            self._day   = today

    def is_open(self) -> bool:
        """
        True if the circuit is open and requests should be rejected.

        Returns:
            bool: True when the daily call limit has been reached.
        """
        self._reset_if_new_day()
        return self._count >= self._max

    def record_calls(self, n: int = 1) -> None:
        """
        Record that n LLM calls were made.

        Args:
            n (int): Number of calls to add to today's count. Default 1.
        """
        self._reset_if_new_day()
        self._count += n

    @property
    def daily_count(self) -> int:
        """Number of LLM calls made so far today."""
        self._reset_if_new_day()
        return self._count

    @property
    def daily_limit(self) -> int:
        """The configured daily limit."""
        return self._max
