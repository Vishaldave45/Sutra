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


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(SutraAppError)
    async def sutra_app_error_handler(
        request: Request, exc: SutraAppError
    ) -> JSONResponse:
        logger.error(
            "Application error on %s %s: %s",
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
