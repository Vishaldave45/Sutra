"""Tool system data models, contracts, and schema definitions."""

import enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from packages.agent_core.tools.errors import InvalidToolSchema


class ToolRiskLevel(str, enum.Enum):
    READ = "READ"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ToolRetryPolicy(BaseModel):
    """Declarative retry policy metadata (no runtime orchestration in Phase 6)."""

    max_retries: int = Field(default=0, ge=0)
    initial_interval_seconds: float = Field(default=1.0, ge=0.0)
    backoff_factor: float = Field(default=2.0, ge=1.0)
    retryable_errors: list[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")


class ToolDefinition(BaseModel):
    """Strongly typed tool definition contract."""

    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    risk_level: ToolRiskLevel = ToolRiskLevel.READ
    permission: list[str] = Field(default_factory=list)
    timeout: float = Field(default=30.0, gt=0.0)
    retry_policy: ToolRetryPolicy = Field(default_factory=ToolRetryPolicy)
    idempotent: bool = False

    model_config = ConfigDict(extra="forbid")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Tool name cannot be empty or whitespace only")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Tool description cannot be empty or whitespace only")
        return v.strip()

    @field_validator("input_schema", "output_schema")
    @classmethod
    def validate_schema(cls, v: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(v, dict):
            raise InvalidToolSchema(
                "Tool schema must be a valid JSON Schema dictionary"
            )
        return v


class ToolResult(BaseModel):
    """Normalized tool execution result."""

    success: bool
    tool_name: str
    output: Any | None = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="ignore")
