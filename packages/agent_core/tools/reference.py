"""Deterministic reference and test tools."""

import asyncio
from typing import Any

from pydantic import BaseModel, Field

from packages.agent_core.tools.errors import ToolExecutionError
from packages.agent_core.tools.interface import Tool
from packages.agent_core.tools.models import ToolRetryPolicy, ToolRiskLevel

# --- 1. Echo Reference Tool ---


class EchoInput(BaseModel):
    message: str = Field(description="Message string to echo back")


class EchoOutput(BaseModel):
    message: str = Field(description="Echoed message string")


class EchoTool(Tool):
    """Deterministic reference tool that echoes input message."""

    name = "echo_tool"
    description = "Echoes back the provided message payload."
    input_model = EchoInput
    output_model = EchoOutput
    risk_level = ToolRiskLevel.READ
    permission = ["tools.echo"]
    timeout = 5.0
    idempotent = True

    async def execute(self, input_data: EchoInput) -> EchoOutput:
        return EchoOutput(message=input_data.message)


# --- 2. Deterministic Failure Reference Tool ---


class FailureInput(BaseModel):
    error_message: str = Field(default="Deterministic tool execution failure")


class FailureOutput(BaseModel):
    result: str = Field(default="Should not be returned")


class DeterministicFailureTool(Tool):
    """Reference tool that deterministically raises ToolExecutionError."""

    name = "failure_tool"
    description = "Always raises a ToolExecutionError to test failure paths."
    input_model = FailureInput
    output_model = FailureOutput
    risk_level = ToolRiskLevel.LOW
    permission = ["tools.failure"]
    timeout = 5.0
    retry_policy = ToolRetryPolicy(
        max_retries=1, retryable_errors=["ToolExecutionError"]
    )
    idempotent = True

    async def execute(self, input_data: FailureInput) -> FailureOutput:
        raise ToolExecutionError(input_data.error_message)


# --- 3. Deterministic Timeout Reference Tool ---


class TimeoutInput(BaseModel):
    delay_seconds: float = Field(default=2.0, ge=0.0, description="Seconds to sleep")


class TimeoutOutput(BaseModel):
    elapsed: float = Field(description="Elapsed seconds if completed")


class DeterministicTimeoutTool(Tool):
    """Reference tool that sleeps to trigger executor timeout enforcement."""

    name = "timeout_tool"
    description = "Sleeps for a specified duration to trigger executor timeout."
    input_model = TimeoutInput
    output_model = TimeoutOutput
    risk_level = ToolRiskLevel.LOW
    permission = ["tools.timeout"]
    timeout = 0.1  # Short timeout configured so timeout tests are fast
    idempotent = True

    async def execute(self, input_data: TimeoutInput) -> TimeoutOutput:
        await asyncio.sleep(input_data.delay_seconds)
        return TimeoutOutput(elapsed=input_data.delay_seconds)


# --- 4. Invalid Output Reference Tool (For testing output validation failure) ---


class InvalidOutputTool(Tool):
    """Reference tool that deliberately returns invalid output matching no schema."""

    name = "invalid_output_tool"
    description = "Returns an invalid payload to test output validation failure."
    input_model = EchoInput
    output_model = EchoOutput
    risk_level = ToolRiskLevel.LOW
    permission = ["tools.invalid_output"]
    timeout = 5.0

    async def execute(self, input_data: EchoInput) -> Any:
        # Returns wrong structure missing required 'message' field
        return {"wrong_key": 12345}
