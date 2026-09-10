"""API v1 route handlers."""

from apps.api.api.v1.routes.conversations import router as conversations_router
from apps.api.api.v1.routes.health import router as health_router
from apps.api.api.v1.routes.projects import router as projects_router
from apps.api.api.v1.routes.tasks import router as tasks_router

__all__ = [
    "conversations_router",
    "health_router",
    "projects_router",
    "tasks_router",
]
