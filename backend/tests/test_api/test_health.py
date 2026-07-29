import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_endpoint(client: AsyncClient):
    """Verifies that the /api/v1/health endpoint returns 200 OK and expected payloads."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["services"]["api"] == "healthy"
    assert data["services"]["mongodb"] == "healthy"
    assert data["services"]["qdrant"] == "healthy"


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Verifies that the root / endpoint responds successfully."""
    response = await client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]
