import ast
import sys
from pathlib import Path

import pytest

from packages.agent_core.tools.errors import ToolError, sanitize_error_message
from packages.agent_core.tools.executor import ToolExecutor
from packages.agent_core.tools.reference import (
    DeterministicFailureTool,
    DeterministicTimeoutTool,
    EchoInput,
    EchoTool,
    InvalidOutputTool,
)


@pytest.mark.asyncio
async def test_executor_successful_execution() -> None:
    executor = ToolExecutor()
    echo = EchoTool()

    # With dict input
    result = await executor.execute(echo, {"message": "Hello World"})
    assert result.success is True
    assert result.tool_name == "echo_tool"
    assert result.output == {"message": "Hello World"}
    assert result.error is None

    # With Pydantic input model
    result_model = await executor.execute(echo, EchoInput(message="Direct model"))
    assert result_model.success is True
    assert result_model.output == {"message": "Direct model"}


@pytest.mark.asyncio
async def test_executor_input_validation_failure_prevents_execution() -> None:
    executor = ToolExecutor()

    # Tracking execution call on a spy tool subclass
    class SpyEchoTool(EchoTool):
        def __init__(self) -> None:
            super().__init__()
            self.execute_called = False

        async def execute(self, input_data: EchoInput) -> EchoInput:
            self.execute_called = True
            return await super().execute(input_data)

    spy_tool = SpyEchoTool()

    # Missing required field 'message'
    result = await executor.execute(spy_tool, {})
    assert result.success is False
    assert result.tool_name == "echo_tool"
    assert result.output is None
    assert result.metadata.get("error_type") == "InvalidToolInput"
    assert result.metadata.get("validation_phase") == "input"
    assert "Input validation failed" in (result.error or "")
    # Invariant: Invalid input must NEVER reach tool.execute()
    assert spy_tool.execute_called is False

    # Wrong type for 'message' (dict instead of string)
    result_type = await executor.execute(spy_tool, {"message": {"nested": 123}})
    assert result_type.success is False
    assert result_type.metadata.get("error_type") == "InvalidToolInput"
    assert "Input validation failed" in (result_type.error or "")
    assert spy_tool.execute_called is False


@pytest.mark.asyncio
async def test_executor_output_validation_failure() -> None:
    executor = ToolExecutor()
    invalid_tool = InvalidOutputTool()

    result = await executor.execute(invalid_tool, {"message": "Hi"})
    assert result.success is False
    assert result.tool_name == "invalid_output_tool"
    assert result.output is None
    assert result.metadata.get("error_type") == "ToolExecutionError"
    assert result.metadata.get("validation_phase") == "output"
    assert "Output validation failed" in (result.error or "")


@pytest.mark.asyncio
async def test_executor_deterministic_runtime_failure() -> None:
    executor = ToolExecutor()
    fail_tool = DeterministicFailureTool()

    result = await executor.execute(
        fail_tool, {"error_message": "Deliberate test failure"}
    )
    assert result.success is False
    assert result.tool_name == "failure_tool"
    assert result.output is None
    assert "Deliberate test failure" in (result.error or "")
    assert result.metadata.get("error_type") == "ToolExecutionError"


@pytest.mark.asyncio
async def test_executor_centralized_timeout_enforcement() -> None:
    executor = ToolExecutor()
    # Tool has timeout = 0.1s; we ask for 0.4s delay
    timeout_tool = DeterministicTimeoutTool()

    result = await executor.execute(timeout_tool, {"delay_seconds": 0.4})
    assert result.success is False
    assert result.tool_name == "timeout_tool"
    assert result.output is None
    assert result.metadata.get("error_type") == "ToolTimeoutError"
    assert result.metadata.get("timeout_seconds") == 0.1
    assert "timed out after" in (result.error or "")


def test_sanitize_error_message_scrubbing() -> None:
    msg_bearer = "Error contacting API with Bearer sk-proj-1234567890abcdef"
    sanitized = sanitize_error_message(msg_bearer)
    assert "sk-proj-1234567890abcdef" not in sanitized
    assert "[REDACTED]" in sanitized

    msg_key = "Connection failed api_key=secret_value_12345678"
    sanitized_key = sanitize_error_message(msg_key)
    assert "secret_value_12345678" not in sanitized_key

    # Custom tool error sanitization
    err = ToolError("Failed with Authorization: Basic dXNlcjpwYXNz")
    assert "dXNlcjpwYXNz" not in str(err)


def test_dependency_boundary_verification() -> None:
    forbidden_modules = [
        "apps.api",
        "fastapi",
        "sqlalchemy",
        "openai",
        "openclaw",
    ]
    tools_modules = [
        m
        for name, m in sys.modules.items()
        if name.startswith("packages.agent_core.tools")
    ]
    for mod in tools_modules:
        for forbidden in forbidden_modules:
            msg = f"Forbidden module {forbidden} found in {mod}"
            assert forbidden not in mod.__dict__, msg


def test_ast_verify_no_forbidden_imports_in_tools() -> None:
    tools_dir = Path("packages/agent_core/tools")
    forbidden_roots = [
        "apps.api",
        "fastapi",
        "sqlalchemy",
        "openai",
        "openclaw",
    ]
    for py_file in tools_dir.glob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    for forbidden in forbidden_roots:
                        assert not alias.name.startswith(forbidden), (
                            f"Forbidden 'import {alias.name}' in {py_file}"
                        )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for forbidden in forbidden_roots:
                        assert not node.module.startswith(forbidden), (
                            f"Forbidden 'from {node.module} import ...' in {py_file}"
                        )
