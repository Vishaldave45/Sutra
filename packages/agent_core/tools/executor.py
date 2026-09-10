"""Centralized Tool Executor enforcing validation, execution, and timeout boundaries."""

import asyncio
from typing import Any

from pydantic import BaseModel, ValidationError

from packages.agent_core.tools.errors import (
    InvalidToolInput,
    ToolExecutionError,
    ToolTimeoutError,
    sanitize_error_message,
)
from packages.agent_core.tools.interface import Tool
from packages.agent_core.tools.models import ToolResult


class ToolExecutor:
    """Central execution boundary for tools.

    Enforces:
    1. Input validation before execution (using tool.input_model)
       Canonical semantic error mapping: ValidationError -> InvalidToolInput
    2. Centralized execution timeout (using tool.definition.timeout)
       Canonical semantic error mapping: asyncio.TimeoutError -> ToolTimeoutError
    3. Tool invocation
    4. Output validation (using tool.output_model)
    5. Result normalization into ToolResult

    Does NOT select tools, call LLMs, run loops, or perform authorization.
    """

    def __init__(self, default_timeout: float | None = None) -> None:
        self._default_timeout = default_timeout

    async def execute(
        self,
        tool: Tool,
        raw_input: Any,
        timeout_override: float | None = None,
    ) -> ToolResult:
        """Execute a tool with validation, timeout, and output normalization."""
        tool_name = tool.name
        effective_timeout = (
            timeout_override
            if timeout_override is not None
            else (self._default_timeout or tool.definition.timeout)
        )

        # 1. Input validation before execution
        # Mapping: ValidationError -> InvalidToolInput -> ToolResult
        try:
            if isinstance(raw_input, tool.input_model):
                validated_input = raw_input
            elif isinstance(raw_input, dict):
                validated_input = tool.input_model.model_validate(raw_input)
            elif isinstance(raw_input, BaseModel):
                validated_input = tool.input_model.model_validate(
                    raw_input.model_dump()
                )
            else:
                validated_input = tool.input_model.model_validate(raw_input)
        except ValidationError as err:
            canonical_err = InvalidToolInput(
                f"Input validation failed for tool '{tool_name}': {err}"
            )
            return ToolResult(
                success=False,
                tool_name=tool_name,
                output=None,
                error=canonical_err.message,
                metadata={
                    "error_type": "InvalidToolInput",
                    "validation_phase": "input",
                },
            )
        except Exception as exc:
            canonical_err = InvalidToolInput(
                f"Unexpected input error for tool '{tool_name}': {exc}"
            )
            return ToolResult(
                success=False,
                tool_name=tool_name,
                output=None,
                error=canonical_err.message,
                metadata={
                    "error_type": "InvalidToolInput",
                    "validation_phase": "input",
                },
            )

        # 2. Centralized timeout enforcement and tool execution
        # Mapping: asyncio.TimeoutError -> ToolTimeoutError -> ToolResult
        try:
            raw_output = await asyncio.wait_for(
                tool.execute(validated_input),
                timeout=effective_timeout,
            )
        except asyncio.TimeoutError:
            canonical_err = ToolTimeoutError(
                f"Tool '{tool_name}' timed out after {effective_timeout:.2f} seconds"
            )
            return ToolResult(
                success=False,
                tool_name=tool_name,
                output=None,
                error=canonical_err.message,
                metadata={
                    "error_type": "ToolTimeoutError",
                    "timeout_seconds": effective_timeout,
                },
            )
        except ToolExecutionError as exc:
            safe_msg = sanitize_error_message(str(exc))
            return ToolResult(
                success=False,
                tool_name=tool_name,
                output=None,
                error=safe_msg,
                metadata={"error_type": type(exc).__name__},
            )
        except Exception as exc:
            canonical_err = ToolExecutionError(
                f"Tool execution failed: {type(exc).__name__}: {exc}"
            )
            return ToolResult(
                success=False,
                tool_name=tool_name,
                output=None,
                error=canonical_err.message,
                metadata={"error_type": "ToolExecutionError"},
            )

        # 3. Output validation against tool.output_model
        try:
            if isinstance(raw_output, tool.output_model):
                validated_output = raw_output
            elif isinstance(raw_output, dict):
                validated_output = tool.output_model.model_validate(raw_output)
            elif isinstance(raw_output, BaseModel):
                validated_output = tool.output_model.model_validate(
                    raw_output.model_dump()
                )
            else:
                validated_output = tool.output_model.model_validate(raw_output)
        except ValidationError as err:
            canonical_err = ToolExecutionError(
                f"Output validation failed for tool '{tool_name}': {err}"
            )
            return ToolResult(
                success=False,
                tool_name=tool_name,
                output=None,
                error=canonical_err.message,
                metadata={
                    "error_type": "ToolExecutionError",
                    "validation_phase": "output",
                },
            )
        except Exception as exc:
            canonical_err = ToolExecutionError(
                f"Unexpected output error for tool '{tool_name}': {exc}"
            )
            return ToolResult(
                success=False,
                tool_name=tool_name,
                output=None,
                error=canonical_err.message,
                metadata={
                    "error_type": "ToolExecutionError",
                    "validation_phase": "output",
                },
            )

        # 4. Normalized successful ToolResult
        if isinstance(validated_output, BaseModel):
            output_payload = validated_output.model_dump()
        else:
            output_payload = validated_output

        return ToolResult(
            success=True,
            tool_name=tool_name,
            output=output_payload,
            error=None,
            metadata={},
        )
