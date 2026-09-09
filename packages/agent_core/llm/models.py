import enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LLMMessageRole(str, enum.Enum):
    system = "system"
    user = "user"
    assistant = "assistant"


class LLMMessage(BaseModel):
    role: LLMMessageRole
    content: str

    @field_validator("content")
    @classmethod
    def validate_content_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Message content cannot be empty or whitespace only")
        return v


class LLMRequest(BaseModel):
    messages: list[LLMMessage]
    model: str | None = None
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, gt=0)

    model_config = ConfigDict(extra="ignore")

    @field_validator("messages")
    @classmethod
    def validate_messages(cls, v: list[LLMMessage]) -> list[LLMMessage]:
        if not v:
            raise ValueError("LLMRequest must contain at least one message")
        return v


class LLMUsage(BaseModel):
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None


class LLMResponse(BaseModel):
    text: str
    model: str
    usage: LLMUsage = Field(default_factory=LLMUsage)
    provider: str
    provider_metadata: dict[str, Any] = Field(default_factory=dict)
