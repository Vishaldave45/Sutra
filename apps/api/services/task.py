from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.errors import (
    InvalidTaskTransition,
    ProjectNotFoundForTask,
    TaskNotFound,
    ValidationError,
)
from apps.api.db.models.task import Task, TaskPriority, TaskStatus, utc_now
from apps.api.repositories.project import ProjectRepository
from apps.api.repositories.task import TaskRepository


class TaskService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = TaskRepository(session)
        self._project_repo = ProjectRepository(session)

    async def create_task(
        self,
        title: str,
        description: str | None = None,
        project_id: UUID | None = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        due_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Task:
        if not title or not title.strip():
            raise ValidationError("Task title cannot be empty or whitespace only")

        if project_id is not None:
            project_exists = await self._project_repo.exists(project_id)
            if not project_exists:
                raise ProjectNotFoundForTask(
                    f"Referenced project '{project_id}' does not exist"
                )

        return await self._repo.create(
            title=title.strip(),
            description=description,
            project_id=project_id,
            priority=priority,
            due_at=due_at,
            metadata=metadata,
        )

    async def get_task(self, task_id: UUID) -> Task:
        task = await self._repo.get_by_id(task_id)
        if task is None:
            raise TaskNotFound(f"Task '{task_id}' not found")
        return task

    async def list_tasks(
        self,
        project_id: UUID | None = None,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Task]:
        safe_limit = max(1, min(limit, 100))
        safe_offset = max(0, offset)
        return await self._repo.list(
            project_id=project_id,
            status=status,
            priority=priority,
            limit=safe_limit,
            offset=safe_offset,
        )

    async def update_task(
        self,
        task_id: UUID,
        title: str | None = None,
        description: str | None = None,
        project_id: UUID | None = None,
        priority: TaskPriority | None = None,
        due_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
        clear_project_id: bool = False,
        clear_due_at: bool = False,
        clear_description: bool = False,
    ) -> Task:
        task = await self.get_task(task_id)

        if title is not None:
            if not title or not title.strip():
                raise ValidationError("Task title cannot be empty or whitespace only")
            task.title = title.strip()

        if clear_description:
            task.description = None
        elif description is not None:
            task.description = description

        if clear_project_id:
            task.project_id = None
        elif project_id is not None:
            project_exists = await self._project_repo.exists(project_id)
            if not project_exists:
                raise ProjectNotFoundForTask(
                    f"Referenced project '{project_id}' does not exist"
                )
            task.project_id = project_id

        if priority is not None:
            task.priority = priority

        if clear_due_at:
            task.due_at = None
        elif due_at is not None:
            task.due_at = due_at

        if metadata is not None:
            task.metadata_ = metadata

        return await self._repo.update(task)

    async def start_task(self, task_id: UUID) -> Task:
        task = await self.get_task(task_id)

        if task.status == TaskStatus.IN_PROGRESS:
            # Deterministic idempotent call
            return task

        if task.status in (TaskStatus.DONE, TaskStatus.CANCELLED):
            raise InvalidTaskTransition(
                f"Cannot start task in terminal state '{task.status.value}'"
            )

        if task.status != TaskStatus.TODO:
            raise InvalidTaskTransition(
                f"Invalid transition from '{task.status.value}' "
                f"to '{TaskStatus.IN_PROGRESS.value}'"
            )

        task.status = TaskStatus.IN_PROGRESS
        task.completed_at = None
        return await self._repo.update(task)

    async def complete_task(self, task_id: UUID) -> Task:
        task = await self.get_task(task_id)

        if task.status == TaskStatus.DONE:
            # Deterministic idempotent completion
            return task

        if task.status == TaskStatus.CANCELLED:
            raise InvalidTaskTransition(
                f"Cannot complete task in terminal state '{TaskStatus.CANCELLED.value}'"
            )

        if task.status not in (TaskStatus.TODO, TaskStatus.IN_PROGRESS):
            raise InvalidTaskTransition(
                f"Invalid transition from '{task.status.value}' "
                f"to '{TaskStatus.DONE.value}'"
            )

        task.status = TaskStatus.DONE
        task.completed_at = utc_now()
        return await self._repo.update(task)

    async def cancel_task(self, task_id: UUID) -> Task:
        task = await self.get_task(task_id)

        if task.status == TaskStatus.CANCELLED:
            # Deterministic idempotent cancellation
            return task

        if task.status == TaskStatus.DONE:
            raise InvalidTaskTransition(
                f"Cannot cancel task in terminal state '{TaskStatus.DONE.value}'"
            )

        if task.status not in (TaskStatus.TODO, TaskStatus.IN_PROGRESS):
            raise InvalidTaskTransition(
                f"Invalid transition from '{task.status.value}' "
                f"to '{TaskStatus.CANCELLED.value}'"
            )

        task.status = TaskStatus.CANCELLED
        task.completed_at = None
        return await self._repo.update(task)
