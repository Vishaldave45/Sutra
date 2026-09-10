"""Agent Runtime models and execution status."""

import enum
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from packages.agent_core.llm.models import LLMUsage


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AgentRunStatus(str, enum.Enum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AgentRun(BaseModel):
    """In-memory execution record for a single agent pass."""

    id: UUID = Field(default_factory=uuid4)
    conversation_id: UUID | None = None
    status: AgentRunStatus = AgentRunStatus.CREATED
    input_prompt: str
    output_text: str | None = None
    system_prompt: str
    model: str
    usage: LLMUsage = Field(default_factory=LLMUsage)
    error: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="ignore")
