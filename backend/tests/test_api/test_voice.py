import pytest
from unittest.mock import patch
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_transcribe_empty_file(client: AsyncClient):
    """Verifies that empty files are rejected."""
    files = {"audio": ("empty.webm", b"", "audio/webm")}
    response = await client.post("/api/v1/voice/transcribe", files=files)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"]

@pytest.mark.asyncio
async def test_transcribe_success(client: AsyncClient):
    """Verifies transcription returns parsed text."""
    with patch("app.api.v1.voice.transcribe_audio", return_value="hello world"):
        files = {"audio": ("sample.webm", b"mock audio content", "audio/webm")}
        response = await client.post("/api/v1/voice/transcribe", files=files)
        assert response.status_code == 200
        assert response.json()["transcript"] == "hello world"

@pytest.mark.asyncio
async def test_synthesize_empty_text(client: AsyncClient):
    """Verifies that empty text payloads are rejected."""
    payload = {"text": "  "}
    response = await client.post("/api/v1/voice/synthesize", json=payload)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"]

@pytest.mark.asyncio
async def test_synthesize_success(client: AsyncClient):
    """Verifies synthesis returns raw audio bytes."""
    with patch("app.api.v1.voice.synthesize_speech", return_value=(b"fake wav bytes", "audio/wav")):
        payload = {"text": "Hello, how can I assist you?"}
        response = await client.post("/api/v1/voice/synthesize", json=payload)
        assert response.status_code == 200
        assert response.content == b"fake wav bytes"
        assert response.headers["content-type"] == "audio/wav"
