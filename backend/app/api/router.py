from fastapi import APIRouter
from app.api.v1 import health, documents, chat, voice, auth, sessions

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(documents.router)
api_router.include_router(chat.router)
api_router.include_router(voice.router)
api_router.include_router(sessions.router)
