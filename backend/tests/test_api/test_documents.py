import io
import pytest
from unittest.mock import patch
from httpx import AsyncClient


@pytest.fixture(autouse=True)
def mock_celery_delay():
    """Mocks Celery task delay trigger globally for documents tests."""
    with patch("app.api.v1.documents.process_document_task.delay") as mock:
        yield mock


@pytest.mark.asyncio
async def test_upload_non_pdf_file(client: AsyncClient):
    """Verifies that the upload endpoint rejects non-PDF file formats."""
    files = {"file": ("test.txt", io.BytesIO(b"dummy text content"), "text/plain")}
    response = await client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 400
    assert "Only PDF documents are supported" in response.json()["message"]



@pytest.mark.asyncio
async def test_upload_valid_pdf_file(client: AsyncClient):
    """Verifies that uploading a PDF returns a 202 Accepted and metadata structure."""
    pdf_content = b"%PDF-1.4 mock pdf structure content"
    files = {"file": ("sample.pdf", io.BytesIO(pdf_content), "application/pdf")}
    
    # Mocking storage dir output paths to avoid pollution
    with patch("os.makedirs"), patch("shutil.copyfileobj"), patch("os.path.getsize", return_value=1234):
        response = await client.post("/api/v1/documents/upload", files=files)
        assert response.status_code == 202
        data = response.json()
        assert "parsing task scheduled" in data["message"]
        assert data["document"]["filename"] == "sample.pdf"
        assert data["document"]["status"] == "pending"
        assert "_id" in data["document"]
