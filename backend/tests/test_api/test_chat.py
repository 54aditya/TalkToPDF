import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_chat_query_missing_documents(client: AsyncClient):
    """Verifies that query rejects empty document_ids list."""
    payload = {
        "query": "What is the primary topic of the paper?",
        "document_ids": []
    }
    response = await client.post("/api/v1/chat/query", json=payload)
    assert response.status_code == 400
    assert "At least one document_id must be provided" in response.json()["detail"]

@pytest.mark.asyncio
async def test_chat_query_unprocessed_document(client: AsyncClient):
    """Verifies that query rejects documents that are not processed yet."""
    doc_dict = {
        "_id": "507f1f77bcf86cd799439011",
        "filename": "sample.pdf",
        "status": "pending"
    }
    with patch("app.database.repository.DocumentRepository.get_by_id", return_value=doc_dict):
        payload = {
            "query": "What is self-attention?",
            "document_ids": ["507f1f77bcf86cd799439011"]
        }
        response = await client.post("/api/v1/chat/query", json=payload)
        assert response.status_code == 422
        assert "is not yet processed" in response.json()["detail"]

@pytest.mark.asyncio
async def test_chat_query_success_stream(client: AsyncClient):
    """Verifies successful chat query streaming and citation headers."""
    doc_dict = {
        "_id": "507f1f77bcf86cd799439011",
        "filename": "sample.pdf",
        "status": "processed"
    }
    
    mock_chunks = [
        {
            "score": 0.85,
            "text": "Self-attention is a sequence-to-sequence operation.",
            "page": 3,
            "doc_id": "507f1f77bcf86cd799439011"
        }
    ]
    
    async def mock_stream(*args, **kwargs):
        yield '{"type": "token", "content": "Self-attention is an mechanism."}'
        yield '{"type": "done"}'

    with patch("app.database.repository.DocumentRepository.get_by_id", return_value=doc_dict), \
         patch("app.api.v1.chat.embed_query", return_value=[0.1]*768), \
         patch("app.api.v1.chat.search_similar_chunks", return_value=mock_chunks), \
         patch("app.api.v1.chat.stream_rag_answer", return_value=mock_stream()):
         
        payload = {
            "query": "Explain self-attention",
            "document_ids": ["507f1f77bcf86cd799439011"]
        }
        response = await client.post("/api/v1/chat/query", json=payload)
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        
        body = response.text
        assert "citations" in body
        assert "Self-attention is an mechanism" in body
