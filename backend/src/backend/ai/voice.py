"""
Gemini voice I/O for the web command path.

Three discrete, stateless calls (no Gemini Live / websockets here - that's the
desktop experiment in voice/live_agent.py):

  transcribe_command  - mic audio  -> the user's command text
  summarize_for_speech - full result message -> one short spoken sentence
  synthesize_speech   - text -> WAV bytes (Gemini TTS returns raw PCM; we wrap it)

Model ids are env-overridable so a wrong default is a one-line .env fix rather
than a code change.
"""

import io
import os
import wave

from dotenv import load_dotenv
from google.genai import types

from backend.ai.gemini_client import call_gemini
from backend.ai.groq_client import transcribe_with_groq
from backend.env_config import get_groq_api_key
from backend.logging_setup import log

load_dotenv()

STT_MODEL = os.getenv("STT_MODEL", "gemini-flash-latest")
TTS_MODEL = os.getenv("TTS_MODEL", "gemini-2.5-flash-preview-tts")
TTS_VOICE = os.getenv("TTS_VOICE", "Kore")
SPEAKABLE_MODEL = os.getenv("SPEAKABLE_MODEL", "gemini-3.1-flash-lite")

# Gemini TTS output is raw signed 16-bit little-endian PCM, mono, 24 kHz.
_TTS_SAMPLE_RATE = 24000


def transcribe_command(audio: bytes, mime_type: str) -> str:
    """Transcribe a spoken command. Returns the words spoken, nothing else."""

    if get_groq_api_key():
        try:
            return transcribe_with_groq(audio, mime_type)
        except Exception:
            log.exception("Groq STT failed; falling back to Gemini")

    response = call_gemini(
        model=STT_MODEL,
        contents=[
            (
                "Transcribe this voice command exactly. Return only the words "
                "spoken - no preamble, no quotes, no notes about punctuation."
            ),
            types.Part.from_bytes(data=audio, mime_type=mime_type),
        ],
    )

    return (response.text or "").strip()


def summarize_for_speech(text: str) -> str:
    """Compress a result message into one sentence a voice assistant would say."""

    response = call_gemini(
        model=SPEAKABLE_MODEL,
        contents=(
            "Rewrite this assistant result as ONE short, natural sentence to be "
            "read aloud by a voice assistant. No markdown, no lists, no emoji.\n\n"
            + text
        ),
    )

    return (response.text or text).strip()


def synthesize_speech(text: str) -> tuple[bytes, str]:
    """Text -> (wav_bytes, "audio/wav")."""

    response = call_gemini(
        model=TTS_MODEL,
        contents=text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=TTS_VOICE
                    )
                )
            ),
        ),
    )

    pcm = response.candidates[0].content.parts[0].inline_data.data

    return _pcm_to_wav(pcm), "audio/wav"


def _pcm_to_wav(pcm: bytes) -> bytes:
    buffer = io.BytesIO()

    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(_TTS_SAMPLE_RATE)
        wav_file.writeframes(pcm)

    return buffer.getvalue()
