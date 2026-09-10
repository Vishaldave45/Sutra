from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.db.models.task import Task, TaskPriority, TaskStatus


class TaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        title: str,
        description: str | None = None,
        project_id: UUID | None = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        due_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Task:
        task = Task(
            title=title,
            description=description,
            project_id=project_id,
            status=TaskStatus.TODO,
            priority=priority,
            due_at=due_at,
            metadata_=metadata or {},
        )
        self._session.add(task)
        await self._session.flush()
        await self._session.refresh(task)
        return task

    async def get_by_id(self, task_id: UUID) -> Task | None:
        result = await self._session.execute(select(Task).where(Task.id == task_id))
        return result.scalar_one_or_none()

    async def list(
        self,
        project_id: UUID | None = None,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Task]:
        query = select(Task)
        if project_id is not None:
            query = query.where(Task.project_id == project_id)
        if status is not None:
            query = query.where(Task.status == status)
        if priority is not None:
            query = query.where(Task.priority == priority)

        # Deterministic default sorting:
        # due_at ascending (nulls last), then created_at desc, then id desc
        query = (
            query.order_by(
                Task.due_at.asc().nulls_last(),
                Task.created_at.desc(),
                Task.id.desc(),
            )
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def update(self, task: Task) -> Task:
        await self._session.flush()
        await self._session.refresh(task)
        return task

    async def count_by_project(self, project_id: UUID) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(Task).where(Task.project_id == project_id)
        )
        return int(result.scalar_one())
