from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from apps.api.api.v1.routes.conversations import router as conversations_router
from apps.api.api.v1.routes.health import router as health_router
from apps.api.config import settings
from apps.api.core.errors import register_error_handlers
from apps.api.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging(log_level=settings.log_level)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Sutra API",
        version="0.1.0",
        debug=settings.debug,
        lifespan=lifespan,
    )

    register_error_handlers(app)

    # API v1 routes
    app.include_router(health_router, prefix=settings.api_v1_prefix)
    app.include_router(conversations_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
