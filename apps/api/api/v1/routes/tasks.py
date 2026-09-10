from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from apps.api.db.models.task import TaskPriority, TaskStatus
from apps.api.dependencies import get_task_service
from apps.api.schemas.task import (
    TaskCreate,
    TaskRead,
    TaskUpdate,
)
from apps.api.services.task import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post(
    "",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create task",
)
async def create_task(
    payload: TaskCreate,
    service: TaskService = Depends(get_task_service),
) -> TaskRead:
    task = await service.create_task(
        title=payload.title,
        description=payload.description,
        project_id=payload.project_id,
        priority=payload.priority,
        due_at=payload.due_at,
        metadata=payload.metadata,
    )
    return TaskRead.model_validate(task)


@router.get(
    "",
    response_model=list[TaskRead],
    summary="List tasks",
)
async def list_tasks(
    project_id: UUID | None = Query(None),
    status: TaskStatus | None = Query(None),
    priority: TaskPriority | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: TaskService = Depends(get_task_service),
) -> list[TaskRead]:
    tasks = await service.list_tasks(
        project_id=project_id,
        status=status,
        priority=priority,
        limit=limit,
        offset=offset,
    )
    return [TaskRead.model_validate(t) for t in tasks]


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    summary="Get task by ID",
)
async def get_task(
    task_id: UUID,
    service: TaskService = Depends(get_task_service),
) -> TaskRead:
    task = await service.get_task(task_id)
    return TaskRead.model_validate(task)


@router.patch(
    "/{task_id}",
    response_model=TaskRead,
    summary="Update task attributes",
)
async def update_task(
    task_id: UUID,
    payload: TaskUpdate,
    service: TaskService = Depends(get_task_service),
) -> TaskRead:
    # Explicitly unpack fields to ensure status cannot be modified here
    update_data = payload.model_dump(exclude_unset=True)
    clear_project = "project_id" in update_data and update_data["project_id"] is None
    clear_due = "due_at" in update_data and update_data["due_at"] is None
    clear_desc = "description" in update_data and update_data["description"] is None

    task = await service.update_task(
        task_id=task_id,
        title=payload.title,
        description=payload.description,
        project_id=payload.project_id,
        priority=payload.priority,
        due_at=payload.due_at,
        metadata=payload.metadata,
        clear_project_id=clear_project,
        clear_due_at=clear_due,
        clear_description=clear_desc,
    )
    return TaskRead.model_validate(task)


@router.post(
    "/{task_id}/start",
    response_model=TaskRead,
    summary="Start task (transition to IN_PROGRESS)",
)
async def start_task(
    task_id: UUID,
    service: TaskService = Depends(get_task_service),
) -> TaskRead:
    task = await service.start_task(task_id)
    return TaskRead.model_validate(task)


@router.post(
    "/{task_id}/complete",
    response_model=TaskRead,
    summary="Complete task (transition to DONE)",
)
async def complete_task(
    task_id: UUID,
    service: TaskService = Depends(get_task_service),
) -> TaskRead:
    task = await service.complete_task(task_id)
    return TaskRead.model_validate(task)


@router.post(
    "/{task_id}/cancel",
    response_model=TaskRead,
    summary="Cancel task (transition to CANCELLED)",
)
async def cancel_task(
    task_id: UUID,
    service: TaskService = Depends(get_task_service),
) -> TaskRead:
    task = await service.cancel_task(task_id)
    return TaskRead.model_validate(task)
