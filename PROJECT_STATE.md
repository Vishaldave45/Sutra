# Project State

## Project

Sutra — WhatsApp-first Personal AI Operating System.

## Vision

Reduce the mental and manual work required to run the day through the loop:
Observe -> Understand -> Remember -> Suggest -> Act -> Learn.

## Current Phase

Phase 6 — Tool System.

STATUS: 🟡 IMPLEMENTATION COMPLETE (Pending architectural review & acceptance)

## Current Objective

Complete architectural review and verification for Phase 6 (Tool System).

## Completed Work

### Phase 0 — Project Foundation
- Established directory skeleton and governance documentation.
- Tracked placeholder configuration.

### Phase 1 — Backend Foundation
- Implemented environment-based configuration via `pydantic-settings` (`apps/api/config.py`).
- Implemented application entry point and lifespan logging (`apps/api/main.py`).
- Implemented dependency injection skeleton (`apps/api/dependencies.py`).
- Implemented centralized error handler (`apps/api/core/errors.py`).
- Implemented structured logging setup (`apps/api/core/logging.py`).
- Implemented health check endpoint `GET /api/v1/health`.
- Configured Ruff linter and code style rules (`ruff.toml`).

### Phase 2 — Database Architecture
- Configured Docker Compose for PostgreSQL 16 on port 5444 (`docker-compose.yml`).
- Created SQLAlchemy 2.x Declarative Base (`apps/api/db/base.py`).
- Created async engine and session factory with connection management (`apps/api/db/session.py`).
- Established repository layer boundary (`apps/api/repositories/`).
- Initialized Alembic migrations and applied initial schema (`alembic/`).
- Extended health system with readiness check `GET /api/v1/health/ready`.

### Phase 3 — Conversation System
- Implemented domain models `Conversation` and `Message` in `apps/api/db/models/conversation.py`.
- Message roles strictly constrained to `user`, `assistant`, `system` via Enum.
- Implemented migration `f70c220788dc_create_conversations_and_messages_tables.py` and upgraded to `head`.
- Created Pydantic schemas in `apps/api/schemas/conversation.py`.
- Created `ConversationRepository` and `MessageRepository` in `apps/api/repositories/`.
- Created `ConversationService` in `apps/api/services/conversation.py`.
- Created conversation API routes in `apps/api/api/v1/routes/conversations.py`.

### Phase 4 — LLM Provider Layer
- Defined provider-neutral models `LLMMessage`, `LLMRequest`, `LLMResponse`, `LLMUsage` in `packages/agent_core/llm/models.py`.
- Defined abstract base class `LLMProvider` in `packages/agent_core/llm/interface.py`.
- Created normalized error hierarchy in `packages/agent_core/llm/errors.py`.
- Implemented deterministic `MockLLMProvider` in `packages/agent_core/llm/mock.py`.
- Implemented official OpenAI SDK client wrapper `OpenAIProvider` in `packages/agent_core/llm/providers/openai.py` with isolated dependencies, configurable timeout, transparent transient retries, and sanitized error mapping.
- Added LLM configuration settings (`apps/api/config.py`, `.env.example`).
- Created test suite in `tests/test_llm_provider.py`.
- Formally accepted and committed at `e06151b`.

### Phase 5 — Agent Runtime
- Implemented native single-pass Agent Runtime in `packages/agent_core/agent/runtime.py`.
- Implemented in-memory `AgentRun` model and `AgentRunStatus` enum (`packages/agent_core/agent/models.py`).
- Verified provider-neutral and database-free dependency boundary (zero `openai`, zero `apps.api.db`, zero `sqlalchemy` imports in `packages/agent_core/agent/`).
- Formally accepted and committed at `9c7019d`.

### Phase 6 — Tool System (Implementation Complete)
- Implemented strongly typed tool definition contracts and models in `packages/agent_core/tools/models.py`:
  - `ToolDefinition` with Pydantic JSON Schema generation (`input_schema`, `output_schema`).
  - Action risk classification using Sutra's five-tier model (`READ`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
  - Capability scope declaration via `permission: list[str]`.
  - Declarative retry metadata (`ToolRetryPolicy`) and semantic `idempotent: bool` flag.
  - Normalized `ToolResult` model.
- Implemented abstract base class `Tool` in `packages/agent_core/tools/interface.py`.
- Implemented deterministic, isolated `ToolRegistry` in `packages/agent_core/tools/registry.py`.
- Implemented `ToolExecutor` in `packages/agent_core/tools/executor.py` enforcing input validation, centralized execution timeout, output validation, and normalized results.
- Implemented error taxonomy in `packages/agent_core/tools/errors.py` with credential scrubbing.
- Implemented deterministic reference tools in `packages/agent_core/tools/reference.py` (`EchoTool`, `DeterministicFailureTool`, `DeterministicTimeoutTool`, `InvalidOutputTool`).
- Added test suites in `tests/test_tool_models.py`, `tests/test_tool_registry.py`, `tests/test_tool_executor.py`.
- Verified Phase 5 `AgentRuntime` remains strictly single-pass (no tool execution loop).

## Implemented vs Planned

### IMPLEMENTED
- Domain models: `Conversation`, `Message`, `MessageRole`
- API endpoints: `/api/v1/conversations`, `/api/v1/health`
- LLM Provider abstraction: `LLMProvider`, `OpenAIProvider`, `MockLLMProvider`
- Native single-pass Agent Runtime: `AgentRuntime`, `AgentRun`, `AgentRunStatus`
- Tool System infrastructure: `Tool`, `ToolDefinition`, `ToolRegistry`, `ToolExecutor`, `ToolResult`
- Automated test suites (69 tests passing across all suites)

### PLANNED (Not Implemented)
- Agent Tool Calling / ReAct Loop
- Task & Project domain (Phase 7)
- Memory systems (Phase 8)
- Context Engine (Phase 9)
- WhatsApp integration (Phase 12)
- Security & Approval policy implementation (Phase 14)
- OpenClaw execution backend (future optional adapter)

## Current Work

Awaiting architectural review and acceptance of Phase 6.

## Next Work

Phase 7 — Task & Project Domain.

## Important Decisions

- The tool system is pure capability infrastructure; no ReAct loop, planner, or autonomous execution loop is implemented.
- `ToolExecutor` centrally owns execution timeout; individual tools never implement their own timeout.
- `ToolRegistry` is strictly in-memory and isolated with zero database dependency.
- `AgentRuntime` remains strictly single-pass; it is not wired to `ToolExecutor`.
- The tool system has zero dependency on `apps.api`, `fastapi`, `sqlalchemy`, `openai`, or `openclaw`.

## Testing Status

- Pytest: 69 tests passing across all suites (`tests/api/`, `tests/db/`, `tests/test_llm_provider.py`, `tests/test_agent_runtime.py`, `tests/test_tool_*.py`).
- Ruff: Checks and formatting passed cleanly across all files.

## Environment Status

- Python 3.12 virtual environment (`.venv/`) configured.
- PostgreSQL 16 container `sutra_postgres` running on port 5444.
