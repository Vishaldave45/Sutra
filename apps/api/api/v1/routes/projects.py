from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from apps.api.db.models.project import ProjectStatus
from apps.api.dependencies import get_project_service
from apps.api.schemas.project import (
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
)
from apps.api.services.project import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post(
    "",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create project",
)
async def create_project(
    payload: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
) -> ProjectRead:
    project = await service.create_project(
        name=payload.name,
        description=payload.description,
        metadata=payload.metadata,
    )
    return ProjectRead.model_validate(project)


@router.get(
    "",
    response_model=list[ProjectRead],
    summary="List projects",
)
async def list_projects(
    status: ProjectStatus | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: ProjectService = Depends(get_project_service),
) -> list[ProjectRead]:
    projects = await service.list_projects(
        status=status,
        limit=limit,
        offset=offset,
    )
    return [ProjectRead.model_validate(p) for p in projects]


@router.get(
    "/{project_id}",
    response_model=ProjectRead,
    summary="Get project by ID",
)
async def get_project(
    project_id: UUID,
    service: ProjectService = Depends(get_project_service),
) -> ProjectRead:
    project = await service.get_project(project_id)
    return ProjectRead.model_validate(project)


@router.patch(
    "/{project_id}",
    response_model=ProjectRead,
    summary="Update project",
)
async def update_project(
    project_id: UUID,
    payload: ProjectUpdate,
    service: ProjectService = Depends(get_project_service),
) -> ProjectRead:
    project = await service.update_project(
        project_id=project_id,
        name=payload.name,
        description=payload.description,
        metadata=payload.metadata,
    )
    return ProjectRead.model_validate(project)


@router.post(
    "/{project_id}/complete",
    response_model=ProjectRead,
    summary="Complete project",
)
async def complete_project(
    project_id: UUID,
    service: ProjectService = Depends(get_project_service),
) -> ProjectRead:
    project = await service.complete_project(project_id)
    return ProjectRead.model_validate(project)


@router.post(
    "/{project_id}/archive",
    response_model=ProjectRead,
    summary="Archive project",
)
async def archive_project(
    project_id: UUID,
    service: ProjectService = Depends(get_project_service),
) -> ProjectRead:
    project = await service.archive_project(project_id)
    return ProjectRead.model_validate(project)
