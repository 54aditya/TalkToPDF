"""
Speech-to-Text Service
Transcribes audio files using faster-whisper (CTranslate2-optimized Whisper).
Supports WAV, WebM, MP3, OGG, and other formats supported by pydub.
"""
import os
import tempfile
from faster_whisper import WhisperModel
from app.core.config import settings
from app.core.logging import logger

_MODEL: WhisperModel | None = None


def _get_model() -> WhisperModel:
    global _MODEL
    if _MODEL is None:
        logger.info(f"Loading Whisper model: {settings.STT_MODEL_NAME}")
        _MODEL = WhisperModel(
            settings.STT_MODEL_NAME,
            device="cpu",
            compute_type="int8",
        )
        logger.info("Whisper model loaded successfully.")
    return _MODEL


def transcribe_audio(audio_bytes: bytes, content_type: str = "audio/webm") -> str:
    """
    Transcribes raw audio bytes to text using faster-whisper.

    Writes the bytes to a temporary file (required by the Whisper API),
    runs transcription, then cleans up.

    Args:
        audio_bytes: Raw audio file bytes (WebM, WAV, MP3, etc.).
        content_type: MIME type of the audio for picking the temp file extension.

    Returns:
        The full transcribed text string (stripped of leading/trailing whitespace).

    Raises:
        RuntimeError: If transcription fails.
    """
    ext_map = {
        "audio/webm": ".webm",
        "audio/wav": ".wav",
        "audio/ogg": ".ogg",
        "audio/mpeg": ".mp3",
        "audio/mp4": ".mp4",
    }
    ext = ext_map.get(content_type, ".webm")

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        model = _get_model()
        segments, info = model.transcribe(tmp_path, beam_size=5, language=None)

        transcript = " ".join(segment.text for segment in segments).strip()
        logger.info(
            f"Transcription complete: detected_lang={info.language}, "
            f"chars={len(transcript)}"
        )
        return transcript

    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}", exc_info=True)
        raise RuntimeError(f"Speech-to-text transcription failed: {str(e)}")

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
