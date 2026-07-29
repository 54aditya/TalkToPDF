from fastapi import APIRouter
from app.api.v1 import health, documents

api_router = APIRouter()

# Register sub-routers
api_router.include_router(health.router)
api_router.include_router(documents.router)
