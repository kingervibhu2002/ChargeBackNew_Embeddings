"""
llm_provider.py — Provider-agnostic LLM factory, toggled by LLM_PROVIDER.

Both chargeback_agent.py's DisputeAgent and text_to_sql.py's
query_chargebacks() need an LLM client, and each used to construct ChatGroq
directly. Factored out here for the same reason network_detection.py and
chunking.py exist as their own modules: two call sites need identical
provider-selection logic (env var name, model names, error messages), and
this is the only way they can't silently diverge — e.g. one of them getting
updated after a model retirement and the other not, which already happened
once with Groq's Llama-3 line (see the matching comments this module's
model table replaces).

Note on naming: Groq's models here ("openai/gpt-oss-120b") are the
open-source gpt-oss models *hosted on Groq's infrastructure* — not a call to
OpenAI's own API. That's a real, separate provider from "openai" below
(real gpt-4o via OpenAI's API), not a typo.

Usage:
    export LLM_PROVIDER=groq        # default if unset — existing deployments
    export GROQ_API_KEY=...         # (GROQ_API_KEY set, LLM_PROVIDER unset)
                                     # behave identically to before this file existed
    # or
    export LLM_PROVIDER=openai
    export OPENAI_API_KEY=...
"""

import os
from typing import Tuple

_PROVIDERS = {
    "groq": {
        "primary":  "openai/gpt-oss-120b",
        "fallback": "openai/gpt-oss-20b",
        "env_key":  "GROQ_API_KEY",
        "signup":   "https://console.groq.com",
    },
    "openai": {
        "primary":  "gpt-4o",
        "fallback": "gpt-4o-mini",
        "env_key":  "OPENAI_API_KEY",
        "signup":   "https://platform.openai.com/api-keys",
    },
}


def get_provider_name() -> str:
    """
    Which provider is configured, via the LLM_PROVIDER env var.

    Defaults to "groq" — the only provider this project originally
    supported — so an existing deployment with GROQ_API_KEY set and
    LLM_PROVIDER unset keeps behaving exactly as it did before this module
    existed.

    Raises:
        ValueError: If LLM_PROVIDER is set to something not in _PROVIDERS.
    """
    name = os.environ.get("LLM_PROVIDER", "groq").strip().lower()
    if name not in _PROVIDERS:
        raise ValueError(
            f"Unknown LLM_PROVIDER '{name}' — must be one of: {', '.join(_PROVIDERS)}"
        )
    return name


def _resolve_key(provider: str) -> str:
    cfg = _PROVIDERS[provider]
    key = os.environ.get(cfg["env_key"])
    if not key:
        raise ValueError(
            f"{cfg['env_key']} is not set (required for LLM_PROVIDER={provider}). "
            f"Get a key at {cfg['signup']} and run:\n"
            f"  export {cfg['env_key']}=your_key_here"
        )
    return key


def get_env_key_name() -> str:
    """The env var name (e.g. "GROQ_API_KEY") the configured provider reads
    its API key from — for callers building a user-facing message about
    which key is missing, without reaching into _PROVIDERS directly."""
    return _PROVIDERS[get_provider_name()]["env_key"]


def is_configured() -> bool:
    """
    True if the configured provider's API key is actually set — used at
    server startup to decide whether to build the dispute agent at all
    (mirrors api_server.py's pre-existing GROQ_API_KEY gate, now provider-
    aware instead of hardcoded to one provider).
    """
    try:
        _resolve_key(get_provider_name())
        return True
    except ValueError:
        return False


def make_llms(temperature: float = 0) -> Tuple[object, object]:
    """
    Create (primary, fallback) chat model instances for the configured
    provider. Both providers follow the same primary/fallback pattern —
    a higher-quality model for normal use, a faster/cheaper one as a
    fallback if the primary call fails (see chargeback_agent.py's
    DisputeAgent._invoke()).

    Returns:
        (primary_llm, fallback_llm)

    Raises:
        ValueError: If LLM_PROVIDER names an unknown provider, or if that
                   provider's API key env var is not set.
    """
    provider = get_provider_name()
    key = _resolve_key(provider)
    cfg = _PROVIDERS[provider]

    if provider == "groq":
        from langchain_groq import ChatGroq
        return (
            ChatGroq(model=cfg["primary"], temperature=temperature, api_key=key),
            ChatGroq(model=cfg["fallback"], temperature=temperature, api_key=key),
        )
    else:  # openai
        from langchain_openai import ChatOpenAI
        return (
            ChatOpenAI(model=cfg["primary"], temperature=temperature, api_key=key),
            ChatOpenAI(model=cfg["fallback"], temperature=temperature, api_key=key),
        )


def make_llm(temperature: float = 0) -> object:
    """
    Single-model variant for callers (text_to_sql.py) that only need one
    LLM, not a primary+fallback pair. Returns just the primary model.
    """
    primary, _ = make_llms(temperature=temperature)
    return primary
