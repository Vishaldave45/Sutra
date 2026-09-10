"""Native single-pass Agent Runtime."""

import re
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from packages.agent_core.agent.errors import AgentConfigurationError, AgentInputError
from packages.agent_core.agent.models import AgentRun, AgentRunStatus
from packages.agent_core.llm.errors import LLMError
from packages.agent_core.llm.interface import LLMProvider
from packages.agent_core.llm.models import (
    LLMMessage,
    LLMMessageRole,
    LLMRequest,
    LLMUsage,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


DEFAULT_SYSTEM_PROMPT = "You are Sutra, an AI assistant."

# Patterns for sensitive tokens (API keys, Authorization headers, Bearer tokens)
_SENSITIVE_PATTERNS = [
    re.compile(r"(?i)(bearer\s+)[A-Za-z0-9_\-\.]{8,}"),
    re.compile(r"(?i)(api[_-]?key\s*[:=]\s*['\"]?)[A-Za-z0-9_\-\.]{8,}['\"]?"),
    re.compile(r"(?i)(sk-[A-Za-z0-9_\-]{16,})"),
    re.compile(r"(?i)(authorization\s*[:=]\s*['\"]?)[^\s'\"]+"),
]


def sanitize_runtime_error(exc: Exception) -> str:
    """Sanitize execution errors for recording on AgentRun.

    Contract:
    - If the error is an LLMError (normalized by Phase 4 LLM providers),
      its message is already categorized and provider-normalized.
    - If it is an arbitrary or unexpected exception, scrub potential secrets
      (API keys, Bearer tokens, Authorization headers) and provide a clean,
      safe representation without exposing raw transport payloads.
    - Operates completely provider-neutral without importing provider SDKs.
    """
    if isinstance(exc, LLMError):
        raw = exc.message or f"LLM error: {type(exc).__name__}"
    else:
        raw = f"{type(exc).__name__}: {exc}"

    sanitized = raw
    for pattern in _SENSITIVE_PATTERNS:
        sanitized = pattern.sub(r"\1[REDACTED]", sanitized)

    return sanitized


def translate_message_to_llm(message: Any) -> LLMMessage:
    """Translate a message representation to a provider-neutral LLMMessage.

    Accepts:
    - LLMMessage instances
    - Generic objects/schemas exposing 'role' and 'content' attributes
    - Dictionaries containing 'role' and 'content' keys

    Supported roles (case-insensitive string or LLMMessageRole):
    - user
    - assistant
    - system

    Has zero dependency on database models or SQLAlchemy enums.
    """
    if isinstance(message, LLMMessage):
        return message

    if isinstance(message, dict):
        role_raw = message.get("role")
        content = message.get("content")
    else:
        role_raw = getattr(message, "role", None)
        content = getattr(message, "content", None)

    if content is None:
        raise AgentInputError("Message content is missing")

    # Normalize role to string
    if isinstance(role_raw, LLMMessageRole):
        role_str = role_raw.value
    elif isinstance(role_raw, str):
        role_str = role_raw.lower().strip()
    elif hasattr(role_raw, "value") and isinstance(role_raw.value, str):
        role_str = role_raw.value.lower().strip()
    else:
        raise AgentInputError(f"Unsupported message role type: {type(role_raw)}")

    if role_str == LLMMessageRole.user.value:
        llm_role = LLMMessageRole.user
    elif role_str == LLMMessageRole.assistant.value:
        llm_role = LLMMessageRole.assistant
    elif role_str == LLMMessageRole.system.value:
        llm_role = LLMMessageRole.system
    else:
        raise AgentInputError(f"Unsupported message role: '{role_str}'")

    try:
        return LLMMessage(role=llm_role, content=content)
    except ValueError as exc:
        raise AgentInputError(f"Invalid message content: {exc}") from exc


class AgentRuntime:
    """Single-pass native Agent Runtime.

    Executes one finite reasoning pass over input and history via an LLMProvider.
    """

    def __init__(
        self,
        llm_provider: LLMProvider,
        default_system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        default_model: str | None = None,
    ) -> None:
        if llm_provider is None or not isinstance(llm_provider, LLMProvider):
            raise AgentConfigurationError("A valid LLMProvider instance is required")

        self._provider = llm_provider
        self._default_system_prompt = default_system_prompt
        self._default_model = default_model

    @property
    def provider(self) -> LLMProvider:
        return self._provider

    @property
    def default_system_prompt(self) -> str:
        return self._default_system_prompt

    async def execute(
        self,
        input_text: str,
        history: list[Any] | None = None,
        system_prompt: str | None = None,
        conversation_id: UUID | None = None,
        model: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AgentRun:
        """Execute a single pass of the agent runtime.

        Lifecycle:
            AgentRun(CREATED) -> RUNNING -> COMPLETED (on success)
            AgentRun(CREATED) -> RUNNING -> FAILED (on provider/execution error)

        Pre-execution input errors raise AgentInputError before run creation.
        """
        if (
            input_text is None
            or not isinstance(input_text, str)
            or not input_text.strip()
        ):
            raise AgentInputError("Input text cannot be empty or whitespace only")

        effective_system_prompt = (
            system_prompt if system_prompt is not None else self._default_system_prompt
        )
        if not effective_system_prompt or not effective_system_prompt.strip():
            raise AgentInputError("System prompt cannot be empty or whitespace only")

        effective_model = model or self._default_model or self._provider.default_model

        # Pre-validate and translate history before run initialization
        translated_history: list[LLMMessage] = []
        if history:
            for item in history:
                translated_history.append(translate_message_to_llm(item))

        current_user_message = LLMMessage(
            role=LLMMessageRole.user,
            content=input_text,
        )

        messages = [
            LLMMessage(role=LLMMessageRole.system, content=effective_system_prompt),
            *translated_history,
            current_user_message,
        ]

        # Explicit lifecycle transition: CREATED -> RUNNING
        run = AgentRun(
            conversation_id=conversation_id,
            status=AgentRunStatus.CREATED,
            input_prompt=input_text,
            system_prompt=effective_system_prompt,
            model=effective_model,
            metadata=dict(metadata or {}),
        )
        run.status = AgentRunStatus.RUNNING

        request = LLMRequest(
            messages=messages,
            model=effective_model,
        )

        try:
            response = await self._provider.generate(request)
            # Explicit transition: RUNNING -> COMPLETED
            run.status = AgentRunStatus.COMPLETED
            run.output_text = response.text
            run.model = response.model
            run.usage = response.usage
            run.completed_at = utc_now()
            return run
        except Exception as exc:
            # Explicit transition: RUNNING -> FAILED
            run.status = AgentRunStatus.FAILED
            run.error = sanitize_runtime_error(exc)
            run.usage = LLMUsage()
            run.completed_at = utc_now()
            return run
