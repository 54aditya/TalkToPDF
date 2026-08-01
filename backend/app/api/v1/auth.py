"""
Auth API Router
Handles user registration, login, and token-protected /me endpoint.

POST /auth/register — Creates a new user account
POST /auth/login    — Returns a JWT access token
GET  /auth/me       — Returns the current authenticated user's profile
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.exceptions import ValidationException
from app.database.connection import get_mongodb
from app.database.user_repository import UserRepository
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse
from app.services.auth_service import hash_password, verify_password, create_access_token, get_current_user
from app.core.logging import logger


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    payload: UserRegisterRequest,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
):
    """
    Registers a new user account.

    - Rejects duplicate emails
    - Hashes the password with bcrypt
    - Returns a JWT access token immediately (no separate login step needed)
    """
    repo = UserRepository(db)

    existing = await repo.get_by_email(payload.email)
    if existing:
        raise ValidationException("An account with this email address already exists.")

    hashed = hash_password(payload.password)
    user = await repo.create(
        name=payload.name,
        email=payload.email,
        hashed_password=hashed,
    )

    token = create_access_token(user["_id"])
    logger.info(f"New user registered: {payload.email}")
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: UserLoginRequest,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
):
    """
    Authenticates a user and returns a JWT access token.

    Returns 401 with a generic error message for both wrong email and wrong
    password (to prevent email enumeration attacks).
    """
    repo = UserRepository(db)
    user = await repo.get_by_email(payload.email)

    if not user or not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = create_access_token(user["_id"])
    logger.info(f"User logged in: {payload.email}")
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Returns the profile of the currently authenticated user."""
    return current_user
