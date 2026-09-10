# Changelog

## Unreleased

### Added
- Phase 6: Tool System capability layer in `packages/agent_core/tools/`:
  - Strongly typed `ToolDefinition` with Pydantic JSON Schema generation (`input_schema`, `output_schema`).
  - Five-tier action risk classification (`READ`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) and capability scopes (`permission: list[str]`).
  - Declarative retry metadata (`ToolRetryPolicy`) and `idempotent: bool` flag.
  - Abstract base class `Tool` in `packages/agent_core/tools/interface.py`.
  - In-memory, deterministic `ToolRegistry` with unique name enforcement.
  - `ToolExecutor` enforcing pre-execution input validation, centralized execution timeout, output validation, and `ToolResult` normalization.
  - Dedicated tool error hierarchy (`ToolError`, `ToolDefinitionError`, `InvalidToolSchema`, `DuplicateTool`, `ToolNotFound`, `InvalidToolInput`, `ToolExecutionError`, `ToolTimeoutError`) with secret scrubbing.
  - Reference tools in `packages/agent_core/tools/reference.py` (`EchoTool`, `DeterministicFailureTool`, `DeterministicTimeoutTool`, `InvalidOutputTool`).
  - Unit test suites in `tests/test_tool_models.py`, `tests/test_tool_registry.py`, `tests/test_tool_executor.py`.

## 0.5.0 - 2026-09-10 (Phase 5)

### Added
- Phase 5: Native single-pass Agent Runtime in `packages/agent_core/agent/`:
  - `AgentRuntime`: Single-pass execution engine invoking `LLMProvider.generate()`.
  - `AgentRun` and `AgentRunStatus`: In-memory execution record (`CREATED`, `RUNNING`, `COMPLETED`, `FAILED`).
  - `AgentError`, `AgentInputError`, `AgentConfigurationError`: Explicit runtime exceptions.
  - `translate_message_to_llm`: Translation boundary converting conversation messages/schemas to `LLMMessage` with zero database dependencies.
  - Deterministic message assembly (system prompt, chronological history, current user message).
  - Test suite in `tests/test_agent_runtime.py` covering lifecycle, validation, message assembly, translation, failure mapping, and AST-verified provider neutrality.
- Architecture Decision Records:
  - `ADR-001`: Backend Foundation and Layered Architecture (`docs/decisions/ADR-001-backend-architecture.md`).
  - `ADR-002`: Database Architecture and Persistence Boundaries (`docs/decisions/ADR-002-database-architecture.md`).
  - `ADR-003`: LLM Provider Abstraction and Boundary Isolation (`docs/decisions/ADR-003-llm-provider-architecture.md`).
- Domain & Security Architecture Specifications:
  - Conversation Domain Architecture & Model (`docs/architecture/conversation-model.md`).
  - Tool Risk & Action Classification Model (`docs/security/tool-risk-model.md`).
  - OpenClaw Integration Principles (`docs/architecture/openclaw-integration-principles.md`).

## 0.4.0 - 2026-09-09 (Phase 4)

### Added
- Provider-independent LLM abstraction layer in `packages/agent_core/llm/`:
  - `LLMProvider` abstract base interface with `generate(request) -> response`.
  - Request/response/usage contracts (`LLMRequest`, `LLMResponse`, `LLMMessage`, `LLMUsage`).
  - Normalized error hierarchy (`LLMError`, `LLMConfigurationError`, `LLMAuthenticationError`, `LLMInvalidRequestError`, `LLMRateLimitError`, `LLMTimeoutError`, `LLMTransientError`, `LLMUnexpectedError`).
  - `OpenAIProvider` wrapping the official `AsyncOpenAI` client with configurable timeouts, isolated transient retries, and sanitized error mapping.
  - Deterministic `MockLLMProvider` for unit testing and offline simulation.
- Configuration settings for LLM provider, default model, OpenAI API key, timeout, and max retries in `apps/api/config.py` and `.env.example`.
- Automated test suite in `tests/test_llm_provider.py` covering model validation, mock provider, OpenAI client wrapper, timeout, retries, and error normalization.

## 0.3.0 - 2026-09-09 (Phase 3)

### Added
- Domain models `Conversation` and `Message` in `apps/api/db/models/conversation.py`.
- Message role enumeration (`user`, `assistant`, `system`) as native PostgreSQL Enum.
- Alembic migration `f70c220788dc_create_conversations_and_messages_tables.py`.
- `ConversationRepository` and `MessageRepository` in `apps/api/repositories/`.
- `ConversationService` in `apps/api/services/conversation.py`.
- API endpoints registered under `/api/v1/conversations`.
- Integration tests in `tests/api/test_conversations.py`.

## 0.2.0 - 2026-09-09 (Phase 2)

### Added
- Local PostgreSQL 16 service in `docker-compose.yml` on port 5444.
- Database settings in `apps/api/config.py` and `.env.example`.
- SQLAlchemy 2.x Declarative Base in `apps/api/db/base.py`.
- Async engine and session factory in `apps/api/db/session.py`.
- Repository layer boundary in `apps/api/repositories/`.
- Alembic migration environment in `alembic/`.
- Initial schema migration `66fcee048c39_initial_empty_schema.py`.
- Database readiness check at `GET /api/v1/health/ready`.
- Test suite in `tests/db/test_database.py`.

## 0.1.0 - 2026-09-09 (Phase 0 & Phase 1)

### Added
- Bootstrapped the Sutra repository structure.
- FastAPI backend application in `apps/api/main.py`.
- Environment-based configuration using Pydantic Settings in `apps/api/config.py`.
- Health check endpoint at `GET /api/v1/health`.
- Structured logging utility in `apps/api/core/logging.py`.
- Centralized error handling base in `apps/api/core/errors.py`.
- Ruff configuration in `ruff.toml`.
- Pytest test suite in `tests/api/test_health.py`.
