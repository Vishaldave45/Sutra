import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("sutra.errors")


class SutraAppError(Exception):
    """Base exception for application-level errors in Sutra."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        details: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


class NotFoundError(SutraAppError):
    """Resource not found error."""

    def __init__(
        self, message: str = "Resource not found", details: Any = None
    ) -> None:
        super().__init__(message=message, status_code=404, details=details)


class ValidationError(SutraAppError):
    """Input validation error."""

    def __init__(self, message: str = "Validation error", details: Any = None) -> None:
        super().__init__(message=message, status_code=422, details=details)


# Domain-specific errors for Phase 7
class ProjectNotFound(NotFoundError):
    """Project not found."""

    def __init__(self, message: str = "Project not found", details: Any = None) -> None:
        super().__init__(message=message, details=details)


class TaskNotFound(NotFoundError):
    """Task not found."""

    def __init__(self, message: str = "Task not found", details: Any = None) -> None:
        super().__init__(message=message, details=details)


class ProjectNotFoundForTask(NotFoundError):
    """Referenced project does not exist when creating/updating task."""

    def __init__(
        self, message: str = "Referenced project not found", details: Any = None
    ) -> None:
        super().__init__(message=message, details=details)


class InvalidTaskTransition(SutraAppError):
    """Invalid task state transition."""

    def __init__(
        self, message: str = "Invalid task state transition", details: Any = None
    ) -> None:
        super().__init__(message=message, status_code=409, details=details)


class InvalidProjectTransition(SutraAppError):
    """Invalid project state transition."""

    def __init__(
        self, message: str = "Invalid project state transition", details: Any = None
    ) -> None:
        super().__init__(message=message, status_code=409, details=details)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(SutraAppError)
    async def sutra_app_error_handler(
        request: Request, exc: SutraAppError
    ) -> JSONResponse:
        logger.warning(
            "Application error [%s] on %s %s: %s",
            exc.status_code,
            request.method,
            request.url.path,
            exc.message,
        )
        content: dict[str, Any] = {"error": exc.message}
        if exc.details is not None:
            content["details"] = exc.details
        return JSONResponse(
            status_code=exc.status_code,
            content=content,
        )
