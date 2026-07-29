import contextlib
from typing import AsyncIterator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.database.connection import db_manager
from app.middleware.error_handler import register_error_handlers
from app.api.router import api_router


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manages application startup and shutdown lifespans."""
    # Startup tasks
    setup_logging()
    logger.info("Initializing application startup sequence...")
    try:
        await db_manager.connect()
    except Exception as e:
        logger.error(f"Startup sequence failed during database connection: {e}")
        # In production, we might want to shut down or raise. Let's raise.
        raise e

    logger.info("Startup sequence complete. Server is ready.")
    yield

    # Shutdown tasks
    logger.info("Initializing application shutdown sequence...")
    await db_manager.disconnect()
    logger.info("Shutdown sequence complete.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production to point to the frontend host
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Custom Error handlers
register_error_handlers(app)

# Include main API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "message": f"Welcome to the {settings.PROJECT_NAME} API. For documentation, visit /docs"
    }
