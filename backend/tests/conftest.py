import pytest
from typing import AsyncGenerator
from fastapi import FastAPI
from httpx import AsyncClient
from app.main import app
from app.database.connection import get_mongodb, get_qdrant


# Mock databases for fast unit testing
class MockMongoDatabase:

    async def command(self, cmd: str):
        if cmd == "ping":
            return {"ok": 1}
        raise ValueError(f"Unknown command {cmd}")


class MockQdrantClient:

    async def get_collections(self):
        return []


@pytest.fixture
def test_app() -> FastAPI:
    """Fixture override of DB clients for unit testing."""
    # Override dependencies to inject mock clients
    app.dependency_overrides[get_mongodb] = lambda: MockMongoDatabase()
    app.dependency_overrides[get_qdrant] = lambda: MockQdrantClient()
    return app


@pytest.fixture
async def client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Provides an asynchronous HTTP test client."""
    async with AsyncClient(
        app=test_app, base_url="http://testserver"
    ) as async_client:
        yield async_client
