from typing import Any, Dict, Optional


class BaseAppException(Exception):
    """Base exception class for all custom domain errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        detail: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.detail = detail


class NotFoundException(BaseAppException):
    def __init__(self, message: str, detail: Optional[Any] = None) -> None:
        super().__init__(message, status_code=404, detail=detail)


class UnauthorizedException(BaseAppException):
    def __init__(self, message: str = "Unauthorized access", detail: Optional[Any] = None) -> None:
        super().__init__(message, status_code=401, detail=detail)


class ForbiddenException(BaseAppException):
    def __init__(self, message: str = "Action forbidden", detail: Optional[Any] = None) -> None:
        super().__init__(message, status_code=403, detail=detail)


class ValidationException(BaseAppException):
    def __init__(self, message: str, detail: Optional[Any] = None) -> None:
        super().__init__(message, status_code=400, detail=detail)


class DatabaseException(BaseAppException):
    def __init__(self, message: str, detail: Optional[Any] = None) -> None:
        super().__init__(message, status_code=500, detail=detail)


class ExternalAPIException(BaseAppException):
    def __init__(self, message: str, detail: Optional[Any] = None) -> None:
        super().__init__(message, status_code=502, detail=detail)
