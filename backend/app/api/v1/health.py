from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from qdrant_client import AsyncQdrantClient
from app.database.connection import get_mongodb, get_qdrant
from app.core.logging import logger

router = APIRouter()


@router.get("/health", tags=["System"])
async def health_check(
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    qdrant: AsyncQdrantClient = Depends(get_qdrant),
):
    """Liveness/Readiness probe verifying API, MongoDB, and Qdrant statuses."""
    mongodb_ok = False
    qdrant_ok = False

    try:
        await db.command("ping")
        mongodb_ok = True
    except Exception as e:
        logger.error(f"Healthcheck: MongoDB connection failed: {e}")

    try:
        await qdrant.get_collections()
        qdrant_ok = True
    except Exception as e:
        logger.error(f"Healthcheck: Qdrant connection failed: {e}")

    status = "healthy" if mongodb_ok and qdrant_ok else "unhealthy"

    return {
        "status": status,
        "services": {
            "api": "healthy",
            "mongodb": "healthy" if mongodb_ok else "unhealthy",
            "qdrant": "healthy" if qdrant_ok else "unhealthy",
        },
    }
