import pytest
from pydantic import BaseModel, Field

from packages.agent_core.tools.errors import InvalidToolSchema
from packages.agent_core.tools.models import (
    ToolDefinition,
    ToolResult,
    ToolRetryPolicy,
    ToolRiskLevel,
)


class SampleInput(BaseModel):
    query: str = Field(description="Search query")
    limit: int = Field(default=10, ge=1, le=100)


class SampleOutput(BaseModel):
    results: list[str]


def test_tool_definition_valid_construction() -> None:
    input_schema = SampleInput.model_json_schema()
    output_schema = SampleOutput.model_json_schema()

    definition = ToolDefinition(
        name="sample_tool",
        description="A sample tool for testing definitions",
        input_schema=input_schema,
        output_schema=output_schema,
        risk_level=ToolRiskLevel.LOW,
        permission=["tools.search"],
        timeout=15.0,
        retry_policy=ToolRetryPolicy(max_retries=2, retryable_errors=["NetworkError"]),
        idempotent=True,
    )

    assert definition.name == "sample_tool"
    assert definition.description == "A sample tool for testing definitions"
    assert definition.risk_level == ToolRiskLevel.LOW
    assert definition.permission == ["tools.search"]
    assert definition.timeout == 15.0
    assert definition.retry_policy.max_retries == 2
    assert definition.retry_policy.retryable_errors == ["NetworkError"]
    assert definition.idempotent is True
    assert isinstance(definition.input_schema, dict)
    assert definition.input_schema["properties"]["query"]["type"] == "string"
    assert definition.input_schema["properties"]["limit"]["type"] == "integer"


def test_tool_definition_invalid_name_or_description() -> None:
    schema = {"type": "object"}

    with pytest.raises(ValueError, match="Tool name cannot be empty"):
        ToolDefinition(
            name="",
            description="Valid desc",
            input_schema=schema,
            output_schema=schema,
        )

    with pytest.raises(ValueError, match="Tool name cannot be empty"):
        ToolDefinition(
            name="   ",
            description="Valid desc",
            input_schema=schema,
            output_schema=schema,
        )

    with pytest.raises(ValueError, match="Tool description cannot be empty"):
        ToolDefinition(
            name="valid_tool",
            description="   ",
            input_schema=schema,
            output_schema=schema,
        )


def test_tool_definition_invalid_schema() -> None:
    with pytest.raises((ValueError, InvalidToolSchema)):
        ToolDefinition(
            name="tool",
            description="desc",
            input_schema="not-a-dict",  # type: ignore[arg-type]
            output_schema={"type": "object"},
        )


def test_tool_risk_level_values() -> None:
    expected_tiers = {"READ", "LOW", "MEDIUM", "HIGH", "CRITICAL"}
    actual_tiers = {tier.value for tier in ToolRiskLevel}
    assert actual_tiers == expected_tiers


def test_tool_result_construction() -> None:
    res_success = ToolResult(
        success=True,
        tool_name="echo_tool",
        output={"msg": "ok"},
    )
    assert res_success.success is True
    assert res_success.tool_name == "echo_tool"
    assert res_success.output == {"msg": "ok"}
    assert res_success.error is None

    res_fail = ToolResult(
        success=False,
        tool_name="failure_tool",
        error="Execution failed",
        metadata={"phase": "execution"},
    )
    assert res_fail.success is False
    assert res_fail.error == "Execution failed"
    assert res_fail.metadata["phase"] == "execution"
