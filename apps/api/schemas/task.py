from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from apps.api.db.models.task import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: str | None = None
    project_id: UUID | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Task title cannot be empty or whitespace only")
        return v.strip()


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    description: str | None = None
    project_id: UUID | None = None
    priority: TaskPriority | None = None
    due_at: datetime | None = None
    metadata: dict[str, Any] | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Task title cannot be empty or whitespace only")
            return v.strip()
        return v


class TaskRead(BaseModel):
    id: UUID
    project_id: UUID | None
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    due_at: datetime | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        validation_alias="metadata_",
        serialization_alias="metadata",
    )

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
