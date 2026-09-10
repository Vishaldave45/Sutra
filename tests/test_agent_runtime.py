import ast
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pytest

from packages.agent_core.agent.errors import AgentConfigurationError, AgentInputError
from packages.agent_core.agent.models import AgentRun, AgentRunStatus
from packages.agent_core.agent.runtime import (
    AgentRuntime,
    sanitize_runtime_error,
    translate_message_to_llm,
)
from packages.agent_core.llm.errors import (
    LLMAuthenticationError,
    LLMRateLimitError,
    LLMTimeoutError,
    LLMTransientError,
)
from packages.agent_core.llm.interface import LLMProvider
from packages.agent_core.llm.mock import MockLLMProvider
from packages.agent_core.llm.models import (
    LLMMessage,
    LLMMessageRole,
    LLMUsage,
)


def test_agent_run_model_defaults() -> None:
    run = AgentRun(
        input_prompt="Hello",
        system_prompt="System instructions",
        model="mock-model",
    )
    assert run.status == AgentRunStatus.CREATED
    assert run.input_prompt == "Hello"
    assert run.output_text is None
    assert run.error is None
    assert run.completed_at is None
    assert isinstance(run.created_at, datetime)
    assert isinstance(run.usage, LLMUsage)


def test_runtime_configuration_validation() -> None:
    with pytest.raises(
        AgentConfigurationError, match="valid LLMProvider instance is required"
    ):
        AgentRuntime(llm_provider=None)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_successful_execution_and_lifecycle() -> None:
    # 1. Successful execution & 2. CREATED -> RUNNING -> COMPLETED lifecycle
    mock_provider = MockLLMProvider(
        default_response="Greetings from Sutra agent!",
        default_model="mock-model-v1",
        usage=LLMUsage(input_tokens=15, output_tokens=10, total_tokens=25),
    )
    runtime = AgentRuntime(
        llm_provider=mock_provider,
        default_system_prompt="Base prompt",
    )

    cid = uuid4()
    run = await runtime.execute(
        input_text="Help me plan my day",
        conversation_id=cid,
    )

    # Output, Model, Usage, Conversation ID mappings
    assert run.status == AgentRunStatus.COMPLETED
    assert run.conversation_id == cid
    assert run.input_prompt == "Help me plan my day"
    assert run.output_text == "Greetings from Sutra agent!"
    assert run.model == "mock-model-v1"
    assert run.usage.input_tokens == 15
    assert run.usage.output_tokens == 10
    assert run.usage.total_tokens == 25
    assert run.error is None
    # completed_at set on success
    assert run.completed_at is not None
    assert run.completed_at >= run.created_at

    # Provider request verification - called exactly once
    assert len(mock_provider.recorded_requests) == 1
    req = mock_provider.recorded_requests[0]
    assert len(req.messages) == 2
    assert req.messages[0].role == LLMMessageRole.system
    assert req.messages[0].content == "Base prompt"
    assert req.messages[1].role == LLMMessageRole.user
    assert req.messages[1].content == "Help me plan my day"


@pytest.mark.asyncio
async def test_failed_provider_execution_lifecycle() -> None:
    # 3. Failed provider execution & 4. CREATED -> RUNNING -> FAILED lifecycle
    mock_provider = MockLLMProvider()
    mock_provider.set_failure(LLMTransientError("Provider connection failed"))

    runtime = AgentRuntime(llm_provider=mock_provider)

    cid = uuid4()
    run = await runtime.execute(
        input_text="Will fail",
        conversation_id=cid,
    )

    assert run.status == AgentRunStatus.FAILED
    assert run.conversation_id == cid
    assert run.input_prompt == "Will fail"
    assert run.output_text is None
    assert "Provider connection failed" in (run.error or "")
    # completed_at set on failure
    assert run.completed_at is not None
    assert run.completed_at >= run.created_at
    # Exactly one provider call
    assert len(mock_provider.recorded_requests) == 1


@pytest.mark.asyncio
async def test_empty_and_whitespace_input_rejected() -> None:
    # 5. Empty input rejected & 6. Whitespace input rejected
    # & 17. No provider call on invalid input
    mock_provider = MockLLMProvider()
    runtime = AgentRuntime(llm_provider=mock_provider)

    with pytest.raises(AgentInputError, match="cannot be empty or whitespace only"):
        await runtime.execute(input_text="")

    with pytest.raises(AgentInputError, match="cannot be empty or whitespace only"):
        await runtime.execute(input_text="   \n\t  ")

    # Verify no provider call made
    assert len(mock_provider.recorded_requests) == 0


@pytest.mark.asyncio
async def test_empty_system_prompt_rejected() -> None:
    mock_provider = MockLLMProvider()
    runtime = AgentRuntime(llm_provider=mock_provider)

    with pytest.raises(
        AgentInputError, match="System prompt cannot be empty or whitespace only"
    ):
        await runtime.execute(input_text="Hello", system_prompt="   ")

    assert len(mock_provider.recorded_requests) == 0


@pytest.mark.asyncio
async def test_message_assembly_ordering_and_system_placement() -> None:
    # 7. System prompt placement & 8. History ordering & 9. Current user message
    mock_provider = MockLLMProvider(default_response="Acknowledged")
    runtime = AgentRuntime(
        llm_provider=mock_provider,
        default_system_prompt="Default system prompt",
    )

    history = [
        {"role": "user", "content": "Prior message 1"},
        {"role": "assistant", "content": "Prior answer 1"},
        {"role": "user", "content": "Prior message 2"},
    ]

    custom_system_prompt = "Custom system instructions"
    run = await runtime.execute(
        input_text="Current prompt",
        history=history,
        system_prompt=custom_system_prompt,
    )

    assert run.status == AgentRunStatus.COMPLETED
    assert len(mock_provider.recorded_requests) == 1
    req = mock_provider.recorded_requests[0]

    # Verify message count: 1 (system) + 3 (history) + 1 (current) = 5
    assert len(req.messages) == 5

    # 1. System message first
    assert req.messages[0].role == LLMMessageRole.system
    assert req.messages[0].content == custom_system_prompt

    # 2. History preserving order
    assert req.messages[1].role == LLMMessageRole.user
    assert req.messages[1].content == "Prior message 1"
    assert req.messages[2].role == LLMMessageRole.assistant
    assert req.messages[2].content == "Prior answer 1"
    assert req.messages[3].role == LLMMessageRole.user
    assert req.messages[3].content == "Prior message 2"

    # 3. Current user message last
    assert req.messages[4].role == LLMMessageRole.user
    assert req.messages[4].content == "Current prompt"


@pytest.mark.asyncio
async def test_message_translation_boundary_with_generic_objects() -> None:
    mock_provider = MockLLMProvider()
    runtime = AgentRuntime(llm_provider=mock_provider)

    # Generic object exposing role and content without database models
    class GenericMessageStub:
        def __init__(self, role: str, content: str) -> None:
            self.role = role
            self.content = content

    stub = GenericMessageStub(role="user", content="Generic stub message")

    run = await runtime.execute(
        input_text="Next question",
        history=[stub],
    )

    assert run.status == AgentRunStatus.COMPLETED
    req = mock_provider.recorded_requests[0]
    assert len(req.messages) == 3
    assert req.messages[1].role == LLMMessageRole.user
    assert req.messages[1].content == "Generic stub message"


def test_translate_message_supported_roles() -> None:
    # String roles
    m_user = translate_message_to_llm({"role": "user", "content": "hello"})
    assert m_user.role == LLMMessageRole.user

    m_asst = translate_message_to_llm({"role": "assistant", "content": "hi"})
    assert m_asst.role == LLMMessageRole.assistant

    m_sys = translate_message_to_llm({"role": "system", "content": "rules"})
    assert m_sys.role == LLMMessageRole.system

    # LLMMessageRole enums
    m_enum = translate_message_to_llm(
        {"role": LLMMessageRole.user, "content": "enum message"}
    )
    assert m_enum.role == LLMMessageRole.user

    # Pass-through LLMMessage
    existing_llm_msg = LLMMessage(role=LLMMessageRole.assistant, content="direct pass")
    assert translate_message_to_llm(existing_llm_msg) is existing_llm_msg


def test_translate_message_unsupported_role_fails_explicitly() -> None:
    # Unsupported roles fail explicitly
    with pytest.raises(AgentInputError, match="Unsupported message role"):
        translate_message_to_llm({"role": "tool", "content": "tool output"})

    with pytest.raises(AgentInputError, match="Unsupported message role"):
        translate_message_to_llm({"role": "unknown_role", "content": "content"})


def test_translate_message_missing_or_empty_content_fails() -> None:
    with pytest.raises(AgentInputError, match="Message content is missing"):
        translate_message_to_llm({"role": "user"})

    with pytest.raises(AgentInputError, match="Invalid message content"):
        translate_message_to_llm({"role": "user", "content": "   "})


def test_sanitize_runtime_error_contract() -> None:
    # 1. Normalized LLM errors preserve safe categorized message
    err_auth = LLMAuthenticationError("OpenAI authentication failed")
    assert sanitize_runtime_error(err_auth) == "OpenAI authentication failed"

    err_rate = LLMRateLimitError("OpenAI rate limit exceeded")
    assert sanitize_runtime_error(err_rate) == "OpenAI rate limit exceeded"

    err_timeout = LLMTimeoutError("OpenAI request timed out")
    assert sanitize_runtime_error(err_timeout) == "OpenAI request timed out"

    # 2. Arbitrary unexpected errors with potential secrets are sanitized
    raw_leak = ValueError(
        "Request failed with Authorization: Bearer sk-1234567890abcdef123456"
    )
    sanitized = sanitize_runtime_error(raw_leak)
    assert "sk-1234567890abcdef123456" not in sanitized
    assert "Bearer [REDACTED]" in sanitized or "[REDACTED]" in sanitized

    raw_key = RuntimeError("Failed api_key=secret_key_12345678")
    sanitized_key = sanitize_runtime_error(raw_key)
    assert "secret_key_12345678" not in sanitized_key


@pytest.mark.asyncio
async def test_custom_model_override() -> None:
    # 13. Model mapping
    mock_provider = MockLLMProvider(default_model="base-mock")
    runtime = AgentRuntime(llm_provider=mock_provider, default_model="runtime-default")

    # Inherits runtime default
    run1 = await runtime.execute(input_text="Prompt 1")
    assert run1.model == "runtime-default"

    # Overridden per execution
    run2 = await runtime.execute(input_text="Prompt 2", model="override-model")
    assert run2.model == "override-model"


def test_provider_neutral_dependency_boundary() -> None:
    # Provider-neutral dependency boundary: zero openai or db imports
    from packages.agent_core.agent import runtime as runtime_mod

    assert hasattr(runtime_mod, "LLMProvider")
    assert issubclass(runtime_mod.LLMProvider, LLMProvider)
    assert "openai" not in runtime_mod.__dict__
    assert "apps" not in runtime_mod.__dict__
    assert "sqlalchemy" not in runtime_mod.__dict__

    agent_modules = [
        m
        for name, m in sys.modules.items()
        if name.startswith("packages.agent_core.agent")
    ]
    for mod in agent_modules:
        assert "openai" not in mod.__dict__
        assert "sqlalchemy" not in mod.__dict__
        assert "apps" not in mod.__dict__


def test_ast_verify_no_prohibited_imports_in_agent_core() -> None:
    agent_dir = Path("packages/agent_core/agent")
    forbidden_roots = ["openai", "apps.api.db", "sqlalchemy"]
    for py_file in agent_dir.glob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    for forbidden in forbidden_roots:
                        msg = f"Forbidden 'import {alias.name}' in {py_file}"
                        assert not alias.name.startswith(forbidden), msg
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for forbidden in forbidden_roots:
                        msg = f"Forbidden 'from {node.module} import ...' in {py_file}"
                        assert not node.module.startswith(forbidden), msg
