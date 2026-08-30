"""
Groq (OpenAI-compatible) client for text + Whisper STT.

Used when Gemini is overloaded. Set GROQ_API_KEY in backend/.env.
Optional GROQ_MODEL (default llama-3.3-70b-versatile).
"""

from __future__ import annotations

from dataclasses import dataclass

import httpx

from backend.env_config import get_groq_api_key, get_groq_chat_model
from backend.logging_setup import log

_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
_STT_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
_STT_MODEL = "whisper-large-v3"


@dataclass
class GroqTextResponse:
    text: str


def _flatten_text_contents(contents) -> str | None:
    """Return plain text if this call has no images/audio parts."""

    if isinstance(contents, str):
        return contents

    if not isinstance(contents, list):
        return None

    parts: list[str] = []
    for item in contents:
        if isinstance(item, str):
            parts.append(item)
            continue
        text = getattr(item, "text", None)
        if isinstance(text, str) and text:
            parts.append(text)
            continue
        return None
    return "\n".join(parts) if parts else None


def call_groq_text(contents, *, model: str | None = None) -> GroqTextResponse:
    prompt = _flatten_text_contents(contents)
    if prompt is None:
        raise ValueError("Groq text fallback cannot handle image or audio parts.")

    api_key = get_groq_api_key()
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set.")

    model_name = model or get_groq_chat_model()
    log.info("Groq chat model=%s", model_name)

    response = httpx.post(
        _CHAT_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        },
        timeout=60.0,
    )
    response.raise_for_status()
    payload = response.json()
    text = (
        payload.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
    )
    return GroqTextResponse(text=text or "")


def transcribe_with_groq(audio: bytes, mime_type: str) -> str:
    api_key = get_groq_api_key()
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set.")

    extension = "wav"
    if "webm" in mime_type:
        extension = "webm"
    elif "mpeg" in mime_type or "mp3" in mime_type:
        extension = "mp3"

    log.info("Groq STT model=%s", _STT_MODEL)
    response = httpx.post(
        _STT_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        data={"model": _STT_MODEL, "response_format": "text"},
        files={"file": (f"audio.{extension}", audio, mime_type or "audio/wav")},
        timeout=60.0,
    )
    response.raise_for_status()
    return response.text.strip()
