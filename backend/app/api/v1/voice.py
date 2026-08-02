"""
Voice API Router
Provides Speech-to-Text (STT) and Text-to-Speech (TTS) endpoints.

POST /voice/transcribe  — Accepts audio file, returns transcript JSON
POST /voice/synthesize  — Accepts JSON text, returns audio bytes stream
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from app.services.stt_service import transcribe_audio
from app.services.tts_service import synthesize_speech
from app.core.logging import logger


router = APIRouter(prefix="/voice", tags=["Voice"])

_MAX_AUDIO_SIZE_BYTES = 25 * 1024 * 1024

SUPPORTED_AUDIO_TYPES = {
    "audio/webm",
    "audio/wav",
    "audio/mpeg",
    "audio/ogg",
    "audio/mp4",
    "audio/x-m4a",
}


class SynthesizeRequest(BaseModel):
    text: str


@router.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    """
    Transcribes an uploaded audio file to text using faster-whisper.

    Accepts: WebM, WAV, MP3, OGG, MP4 audio files (max 25 MB).

    Returns:
        { "transcript": "..." }
    """
    content_type = audio.content_type or "audio/webm"

    audio_bytes = await audio.read()
    await audio.close()

    if len(audio_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded audio file is empty.")

    if len(audio_bytes) > _MAX_AUDIO_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="Audio file exceeds the 25 MB size limit.")

    logger.info(f"STT request: {len(audio_bytes)} bytes, type={content_type}")

    try:
        transcript = transcribe_audio(audio_bytes, content_type=content_type)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"transcript": transcript}


@router.post("/synthesize")
def synthesize(request: SynthesizeRequest):
    """
    Converts text to speech and returns an audio byte stream.

    Uses ElevenLabs if configured, otherwise falls back to local pyttsx3.

    Returns: Audio bytes with appropriate Content-Type (audio/mpeg or audio/wav).
    """
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text field must not be empty.")

    if len(text) > 5000:
        raise HTTPException(status_code=400, detail="Text exceeds the 5000 character limit for TTS.")

    logger.info(f"TTS request: {len(text)} chars")

    try:
        audio_bytes, mime_type = synthesize_speech(text)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return Response(
        content=audio_bytes,
        media_type=mime_type,
        headers={
            "Content-Disposition": "inline; filename=\"response.wav\"",
            "Content-Length": str(len(audio_bytes)),
        },
    )
