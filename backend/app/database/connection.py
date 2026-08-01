from motor.motor_asyncio import AsyncIOMotorClient
from qdrant_client import AsyncQdrantClient
from app.core.config import settings
from app.core.logging import logger


class DatabaseManager:
    """Manages lifecycle of database connections (MongoDB and Qdrant)."""

    def __init__(self) -> None:
        self.mongo_client: AsyncIOMotorClient = None
        self.mongo_db = None
        self.qdrant_client: AsyncQdrantClient = None

    async def connect(self) -> None:
        """Initializes database connection clients."""
        logger.info("Connecting to MongoDB...")
        try:
            self.mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
            self.mongo_db = self.mongo_client[settings.MONGODB_DB_NAME]
            await self.mongo_client.admin.command("ping")
            logger.info("Successfully connected to MongoDB.")
        except Exception as e:
            logger.critical(f"Failed to connect to MongoDB: {e}")
            raise e

        logger.info("Connecting to Qdrant...")
        try:
            self.qdrant_client = AsyncQdrantClient(url=settings.QDRANT_URL)
            logger.info("Successfully connected to Qdrant.")
        except Exception as e:
            logger.critical(f"Failed to connect to Qdrant: {e}")
            raise e

    async def disconnect(self) -> None:
        """Closes all active database clients."""
        if self.mongo_client:
            logger.info("Closing MongoDB connection...")
            self.mongo_client.close()
            logger.info("MongoDB connection closed.")
        if self.qdrant_client:
            logger.info("Closing Qdrant connection...")
            await self.qdrant_client.close()
            logger.info("Qdrant connection closed.")


db_manager = DatabaseManager()


async def get_mongodb():
    """Dependency to retrieve MongoDB database object."""
    if db_manager.mongo_db is None:
        raise RuntimeError("Database connection not initialized.")
    return db_manager.mongo_db


async def get_qdrant():
    """Dependency to retrieve Qdrant client."""
    if db_manager.qdrant_client is None:
        raise RuntimeError("Qdrant connection not initialized.")
    return db_manager.qdrant_client
