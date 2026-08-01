import pytest
from unittest.mock import patch
from httpx import AsyncClient
from app.services.auth_service import hash_password

@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Verifies that registration fails if the email already exists."""
    with patch("app.database.user_repository.UserRepository.get_by_email") as mock_get:
        mock_get.return_value = {"_id": "507f1f77bcf86cd799439011", "email": "test@example.com"}
        
        payload = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "securepassword123"
        }
        response = await client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 400
        assert "already exists" in response.json()["message"]

@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """Verifies successful user registration."""
    with patch("app.database.user_repository.UserRepository.get_by_email", return_value=None), \
         patch("app.database.user_repository.UserRepository.create") as mock_create:
         
        mock_create.return_value = {
            "_id": "507f1f77bcf86cd799439011",
            "name": "Test User",
            "email": "test@example.com",
            "hashed_password": "hashed"
        }
        
        payload = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "securepassword123"
        }
        response = await client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Verifies login fails with invalid credentials."""
    with patch("app.database.user_repository.UserRepository.get_by_email", return_value=None):
        payload = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        response = await client.post("/api/v1/auth/login", json=payload)
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Verifies login succeeds with correct credentials."""
    hashed = hash_password("securepassword123")
    user_dict = {
        "_id": "507f1f77bcf86cd799439011",
        "name": "Test User",
        "email": "test@example.com",
        "hashed_password": hashed
    }
    with patch("app.database.user_repository.UserRepository.get_by_email", return_value=user_dict):
        payload = {
            "email": "test@example.com",
            "password": "securepassword123"
        }
        response = await client.post("/api/v1/auth/login", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
