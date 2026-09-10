from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.db.models.project import Project, ProjectStatus


class ProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        name: str,
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Project:
        project = Project(
            name=name,
            description=description,
            status=ProjectStatus.ACTIVE,
            metadata_=metadata or {},
        )
        self._session.add(project)
        await self._session.flush()
        await self._session.refresh(project)
        return project

    async def get_by_id(self, project_id: UUID) -> Project | None:
        result = await self._session.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        status: ProjectStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Project]:
        query = select(Project)
        if status is not None:
            query = query.where(Project.status == status)

        query = (
            query.order_by(Project.created_at.desc(), Project.id.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def update(self, project: Project) -> Project:
        await self._session.flush()
        await self._session.refresh(project)
        return project

    async def exists(self, project_id: UUID) -> bool:
        result = await self._session.execute(
            select(func.count()).select_from(Project).where(Project.id == project_id)
        )
        return bool(result.scalar_one() > 0)
