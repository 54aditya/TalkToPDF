"""
Text-to-Speech Service
Converts text to speech audio bytes.

Supports two providers (controlled by TTS_PROVIDER setting):
  - 'elevenlabs': Cloud-based, high-quality voice via ElevenLabs API
  - 'piper':      Local synthesis using pyttsx3 as a lightweight fallback

The service always returns raw WAV or MP3 bytes + the MIME type string.
"""
import io
from typing import Tuple
from app.core.config import settings
from app.core.logging import logger


def synthesize_speech(text: str) -> Tuple[bytes, str]:
    """
    Converts text to audio bytes using the configured TTS provider.

    Args:
        text: The text string to synthesize.

    Returns:
        A tuple of (audio_bytes, mime_type).
        mime_type is 'audio/mpeg' for ElevenLabs MP3 or 'audio/wav' for local.

    Raises:
        RuntimeError: If synthesis fails with the primary provider.
    """
    provider = settings.TTS_PROVIDER.lower()

    if provider == "elevenlabs" and settings.ELEVENLABS_API_KEY:
        return _synthesize_elevenlabs(text)
    else:
        return _synthesize_local(text)


def _synthesize_elevenlabs(text: str) -> Tuple[bytes, str]:
    """Calls the ElevenLabs streaming TTS API."""
    try:
        import httpx
        headers = {
            "xi-api-key": settings.ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }
        payload = {
            "text": text,
            "model_id": "eleven_turbo_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{settings.ELEVENLABS_VOICE_ID}"
        response = httpx.post(url, json=payload, headers=headers, timeout=30.0)
        response.raise_for_status()
        logger.info(f"ElevenLabs TTS: synthesized {len(text)} chars")
        return response.content, "audio/mpeg"
    except Exception as e:
        logger.error(f"ElevenLabs TTS failed: {str(e)}; falling back to local TTS")
        return _synthesize_local(text)


def _synthesize_local(text: str) -> Tuple[bytes, str]:
    """
    Local TTS using pyttsx3 (offline, no API key needed).
    Writes to an in-memory WAV buffer via a temporary file.
    """
    try:
        import pyttsx3
        import tempfile
        import os

        engine = pyttsx3.init()
        engine.setProperty("rate", 165)
        engine.setProperty("volume", 0.95)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        engine.save_to_file(text, tmp_path)
        engine.runAndWait()

        with open(tmp_path, "rb") as f:
            audio_bytes = f.read()

        os.remove(tmp_path)
        logger.info(f"Local TTS: synthesized {len(text)} chars → {len(audio_bytes)} bytes WAV")
        return audio_bytes, "audio/wav"

    except Exception as e:
        logger.error(f"Local TTS failed: {str(e)}", exc_info=True)
        raise RuntimeError(f"Text-to-speech synthesis failed: {str(e)}")
