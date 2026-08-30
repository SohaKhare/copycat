"""Load backend/.env and expose only configured provider keys."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_ENV_FILE = _BACKEND_ROOT / ".env"
_ENV_LOADED = False

DEFAULT_GEMINI_MODEL = "gemini/gemini-3.1-flash-lite"
DEFAULT_GEMINI_TEXT_MODEL = "gemini-3.1-flash-lite"
DEFAULT_GEMINI_BROWSER_MODEL = "gemini-3.1-flash-lite"
DEFAULT_ANTHROPIC_MODEL = "anthropic/claude-sonnet-4-5"
DEFAULT_OPENAI_MODEL = "openai/gpt-4o"


def ensure_env_loaded() -> None:
    global _ENV_LOADED
    if not _ENV_LOADED:
        load_dotenv(_ENV_FILE)
        _ENV_LOADED = True


def clean_env(value: str | None) -> str:
    if not value:
        return ""
    return value.strip().strip('"').strip("'")


def get_gemini_api_keys() -> list[str]:
    ensure_env_loaded()
    keys: list[str] = []

    combined = clean_env(os.getenv("GEMINI_API_KEYS"))
    if combined:
        keys.extend(part.strip() for part in combined.split(",") if part.strip())

    for env_name in ("GEMINI_API_KEY", "GEMINI_API_KEY_2", "GEMINI_API_KEY_3"):
        key = clean_env(os.getenv(env_name))
        if key and key not in keys:
            keys.append(key)

    return keys


def get_anthropic_api_key() -> str:
    ensure_env_loaded()
    return clean_env(os.getenv("ANTHROPIC_API_KEY"))


def get_openai_api_key() -> str:
    ensure_env_loaded()
    return clean_env(os.getenv("OPENAI_API_KEY"))


def get_gemini_text_model() -> str:
    """
    Fast model for resolver/planner Gemini calls.
    Override with GEMINI_TEXT_MODEL or RESOLVER_MODEL in .env.
    """

    ensure_env_loaded()
    for env_name in ("GEMINI_TEXT_MODEL", "RESOLVER_MODEL", "PLANNER_MODEL"):
        value = clean_env(os.getenv(env_name))
        if value:
            return value.removeprefix("gemini/")
    return DEFAULT_GEMINI_TEXT_MODEL


def get_gemini_browser_model() -> str:
    """
    Model for the browser ADK agent.
    Override with GEMINI_BROWSER_MODEL in .env.
    """

    ensure_env_loaded()
    configured = clean_env(os.getenv("GEMINI_BROWSER_MODEL"))
    if configured:
        return configured.removeprefix("gemini/")
    return DEFAULT_GEMINI_BROWSER_MODEL


def resolve_browser_model_name() -> str:
    """
    Pick a browser executor model using only providers that have keys in .env.
    Gemini is preferred when GEMINI_API_KEY(s) are set.
    """

    ensure_env_loaded()
    configured = clean_env(os.getenv("MODEL_NAME"))
    gemini_keys = get_gemini_api_keys()
    anthropic_key = get_anthropic_api_key()
    openai_key = get_openai_api_key()

    browser_model = clean_env(os.getenv("GEMINI_BROWSER_MODEL"))
    if browser_model and gemini_keys:
        return f"gemini/{browser_model.removeprefix('gemini/')}"

    if configured.startswith("gemini/"):
        if gemini_keys:
            return configured
        raise ValueError(
            f"MODEL_NAME is {configured} but no GEMINI_API_KEY is configured."
        )

    if configured.startswith("anthropic/"):
        if anthropic_key:
            return configured
        if gemini_keys:
            return DEFAULT_GEMINI_MODEL
        raise ValueError(
            f"MODEL_NAME is {configured} but ANTHROPIC_API_KEY is not configured."
        )

    if configured.startswith("openai/") or configured.startswith("gpt-"):
        if openai_key:
            return configured
        if gemini_keys:
            return DEFAULT_GEMINI_MODEL
        raise ValueError(
            f"MODEL_NAME is {configured} but OPENAI_API_KEY is not configured."
        )

    if configured:
        if gemini_keys:
            return DEFAULT_GEMINI_MODEL
        if anthropic_key:
            return DEFAULT_ANTHROPIC_MODEL
        if openai_key:
            return DEFAULT_OPENAI_MODEL
        raise ValueError(
            f"MODEL_NAME is {configured} but no matching provider API key is set."
        )

    if gemini_keys:
        return f"gemini/{get_gemini_browser_model()}"
    if anthropic_key:
        return DEFAULT_ANTHROPIC_MODEL
    if openai_key:
        return DEFAULT_OPENAI_MODEL

    raise ValueError(
        "No AI provider keys found in backend/.env. "
        "Set GEMINI_API_KEY (recommended), or ANTHROPIC_API_KEY / OPENAI_API_KEY."
    )
