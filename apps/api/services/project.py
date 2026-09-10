from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.errors import (
    InvalidProjectTransition,
    ProjectNotFound,
    ValidationError,
)
from apps.api.db.models.project import Project, ProjectStatus, utc_now
from apps.api.repositories.project import ProjectRepository


class ProjectService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = ProjectRepository(session)

    async def create_project(
        self,
        name: str,
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Project:
        if not name or not name.strip():
            raise ValidationError("Project name cannot be empty or whitespace only")

        return await self._repo.create(
            name=name.strip(),
            description=description,
            metadata=metadata,
        )

    async def get_project(self, project_id: UUID) -> Project:
        project = await self._repo.get_by_id(project_id)
        if project is None:
            raise ProjectNotFound(f"Project '{project_id}' not found")
        return project

    async def list_projects(
        self,
        status: ProjectStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Project]:
        safe_limit = max(1, min(limit, 100))
        safe_offset = max(0, offset)
        return await self._repo.list(
            status=status, limit=safe_limit, offset=safe_offset
        )

    async def update_project(
        self,
        project_id: UUID,
        name: str | None = None,
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Project:
        project = await self.get_project(project_id)

        if name is not None:
            if not name or not name.strip():
                raise ValidationError("Project name cannot be empty or whitespace only")
            project.name = name.strip()

        if description is not None:
            project.description = description

        if metadata is not None:
            project.metadata_ = metadata

        return await self._repo.update(project)

    async def complete_project(self, project_id: UUID) -> Project:
        project = await self.get_project(project_id)

        if project.status == ProjectStatus.COMPLETED:
            # Deterministic idempotent completion
            return project

        if project.status == ProjectStatus.ARCHIVED:
            raise InvalidProjectTransition(
                f"Cannot complete project in '{project.status.value}' status"
            )

        project.status = ProjectStatus.COMPLETED
        project.completed_at = utc_now()
        return await self._repo.update(project)

    async def archive_project(self, project_id: UUID) -> Project:
        project = await self.get_project(project_id)

        if project.status == ProjectStatus.ARCHIVED:
            # Deterministic idempotent archive
            return project

        project.status = ProjectStatus.ARCHIVED
        project.completed_at = None
        return await self._repo.update(project)
