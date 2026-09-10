from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.config import Settings, settings
from apps.api.db.session import get_db_session
from apps.api.services.conversation import ConversationService
from apps.api.services.project import ProjectService
from apps.api.services.task import TaskService


def get_settings() -> Settings:
    """Dependency provider for application settings."""
    return settings


def get_conversation_service(
    session: AsyncSession = Depends(get_db_session),
) -> ConversationService:
    """Dependency provider for ConversationService."""
    return ConversationService(session)


def get_project_service(
    session: AsyncSession = Depends(get_db_session),
) -> ProjectService:
    """Dependency provider for ProjectService."""
    return ProjectService(session)


def get_task_service(
    session: AsyncSession = Depends(get_db_session),
) -> TaskService:
    """Dependency provider for TaskService."""
    return TaskService(session)
