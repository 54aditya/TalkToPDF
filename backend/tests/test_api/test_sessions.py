import pytest
from unittest.mock import patch
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_session(client: AsyncClient):
    """Verifies successful session creation."""
    doc_dict = {
        "_id": "507f1f77bcf86cd799439011",
        "filename": "attention.pdf",
        "status": "processed"
    }
    session_dict = {
        "_id": "507f1f77bcf86cd799439022",
        "title": "attention",
        "document_ids": ["507f1f77bcf86cd799439011"],
        "messages": []
    }
    with patch("app.database.repository.DocumentRepository.get_by_id", return_value=doc_dict), \
         patch("app.database.session_repository.SessionRepository.create", return_value=session_dict):
         
        payload = {
            "document_ids": ["507f1f77bcf86cd799439011"],
            "title": "attention"
        }
        response = await client.post("/api/v1/sessions", json=payload)
        assert response.status_code == 201
        assert response.json()["title"] == "attention"
        assert response.json()["_id"] == "507f1f77bcf86cd799439022"

@pytest.mark.asyncio
async def test_get_session_not_found(client: AsyncClient):
    """Verifies 404 response for missing session ID."""
    with patch("app.database.session_repository.SessionRepository.get_by_id", return_value=None):
        response = await client.get("/api/v1/sessions/507f1f77bcf86cd799439022")
        assert response.status_code == 404
        assert "not found" in response.json()["message"]

@pytest.mark.asyncio
async def test_add_message_success(client: AsyncClient):
    """Verifies adding a message to an existing session."""
    session_dict = {
        "_id": "507f1f77bcf86cd799439022",
        "title": "attention",
        "document_ids": ["507f1f77bcf86cd799439011"]
    }
    with patch("app.database.session_repository.SessionRepository.get_by_id", return_value=session_dict), \
         patch("app.database.session_repository.SessionRepository.add_message", return_value=True):
         
        payload = {
            "role": "user",
            "content": "Explain page 3."
        }
        response = await client.post("/api/v1/sessions/507f1f77bcf86cd799439022/messages", json=payload)
        assert response.status_code == 201
        assert response.json()["message"] == "Message added."
