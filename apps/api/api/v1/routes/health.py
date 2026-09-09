import logging

from fastapi import APIRouter, Response, status
from pydantic import BaseModel
from sqlalchemy import text

from apps.api.db.session import async_session_factory

logger = logging.getLogger("sutra.health")

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    service: str


class ReadinessResponse(BaseModel):
    status: str
    service: str
    database: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Liveness check: returns 200 OK without requiring external services."""
    return HealthResponse(status="ok", service="sutra-api")


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ReadinessResponse,
            "description": "Database is unavailable",
        }
    },
)
async def readiness_check(response: Response) -> ReadinessResponse:
    """Readiness check: verifies database connectivity without leaking credentials."""
    db_status = "unavailable"
    try:
        async with async_session_factory() as session:
            result = await session.execute(text("SELECT 1"))
            if result.scalar() == 1:
                db_status = "ok"
    except Exception as exc:
        logger.warning("Database readiness check failed: %s", type(exc).__name__)
        db_status = "unavailable"

    if db_status != "ok":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return ReadinessResponse(
            status="degraded",
            service="sutra-api",
            database="unavailable",
        )

    return ReadinessResponse(
        status="ok",
        service="sutra-api",
        database="ok",
    )
