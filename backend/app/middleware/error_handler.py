from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.exceptions import BaseAppException
from app.core.logging import logger


def register_error_handlers(app: FastAPI) -> None:
    """Registers exception handlers for FastAPI app to catch and format custom domain exceptions."""

    @app.exception_handler(BaseAppException)
    async def app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
        logger.error(f"Application error occurred: {exc.message} - Detail: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.__class__.__name__,
                "message": exc.message,
                "detail": exc.detail,
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.critical(f"Unhandled system error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred. Please contact the administrator.",
            },
        )
