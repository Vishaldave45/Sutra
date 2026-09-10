# Project State

## Project

Sutra — WhatsApp-first Personal AI Operating System.

## Vision

Reduce the mental and manual work required to run the day through the loop:
Observe -> Understand -> Remember -> Suggest -> Act -> Learn.

## Current Phase

Phase 5 — Agent Runtime.

STATUS: 🟡 IMPLEMENTATION COMPLETE (Pending architectural review & acceptance)

## Current Objective

Complete architectural review and verification for Phase 5 (Native Single-Pass Agent Runtime).

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

### Phase 5 — Agent Runtime (Implementation Complete)
- Implemented native single-pass Agent Runtime in `packages/agent_core/agent/runtime.py`:
  - Finite single-pass execution via `LLMProvider.generate()`.
  - Deterministic message assembly (System prompt -> Ordered history -> Current user message).
  - Explicit message translation boundary (`translate_message_to_llm`) converting generic objects/dicts/schemas to `LLMMessage` with ZERO database imports.
  - Runtime error sanitization helper (`sanitize_runtime_error`) scrubbing potential secret leaks and preserving normalized LLM provider errors.
- Implemented in-memory `AgentRun` model and `AgentRunStatus` enum (`packages/agent_core/agent/models.py`):
  - Strict statuses: `CREATED`, `RUNNING`, `COMPLETED`, `FAILED`.
  - Explicit lifecycle transitions (`CREATED -> RUNNING -> COMPLETED` / `CREATED -> RUNNING -> FAILED`).
  - Zero database persistence; completely decoupled from PostgreSQL.
- Implemented runtime error hierarchy in `packages/agent_core/agent/errors.py` (`AgentError`, `AgentInputError`, `AgentConfigurationError`).
- Added deterministic offline test suite in `tests/test_agent_runtime.py` covering all requirements with `MockLLMProvider`.
- Verified provider-neutral and database-free dependency boundary (zero `openai`, zero `apps.api.db`, zero `sqlalchemy` imports in `packages/agent_core/agent/`).

### Architecture Documentation Backfill
- ADR-001: Backend Foundation and Layered Architecture (`docs/decisions/ADR-001-backend-architecture.md`).
- ADR-002: Database Architecture and Persistence Boundaries (`docs/decisions/ADR-002-database-architecture.md`).
- ADR-003: LLM Provider Abstraction and Boundary Isolation (`docs/decisions/ADR-003-llm-provider-architecture.md`).
- Conversation Architecture & Model specification (`docs/architecture/conversation-model.md`).
- Tool Risk & Action Classification Model (`docs/security/tool-risk-model.md`).
- OpenClaw Integration Principles (`docs/architecture/openclaw-integration-principles.md`).
- Git Development & Operational Integrity policy (`docs/operations/git-development.md`).

## Implemented vs Planned

### IMPLEMENTED
- Domain models: `Conversation`, `Message`, `MessageRole`
- API endpoints: `/api/v1/conversations`, `/api/v1/health`
- LLM Provider abstraction: `LLMProvider`, `OpenAIProvider`, `MockLLMProvider`
- Provider contracts: `LLMRequest`, `LLMResponse`, `LLMUsage`
- Native single-pass Agent Runtime: `AgentRuntime`, `AgentRun`, `AgentRunStatus`
- In-memory execution record: `AgentRun`
- Deterministic message translation and prompt assembly
- Automated test suites (50 tests passing across all suites)

### PLANNED (Not Implemented)
- Tool System & execution sandboxes (Phase 6)
- Task & Project domain (Phase 7)
- Memory systems (Phase 8)
- Context Engine (Phase 9)
- WhatsApp integration (Phase 12)
- Security & Approval policy implementation (Phase 14)
- OpenClaw execution backend (future optional adapter)

## Current Work

Awaiting architectural review and acceptance of Phase 5.

## Next Work

Phase 6 — Tool Calling & Function Execution.

## Important Decisions

- The runtime is strictly single-pass: no ReAct loop, no autonomous loop, no planning loop, no background worker.
- `AgentRun` is an in-memory execution model and has no database table, no SQLAlchemy model, and no Alembic migration.
- `AgentRuntime` has zero database dependency, imports neither `apps.api.db` nor `sqlalchemy`, and does not automatically wire into `POST /api/v1/conversations/{id}/messages`.
- OpenClaw is not integrated into Phase 5; it remains an optional future adapter.
- The `AgentRuntime` depends only on generic `LLMProvider` abstractions and has zero dependency on provider SDKs.

## Testing Status

- Pytest: 50 tests passing across all suites (`tests/api/`, `tests/db/`, `tests/test_llm_provider.py`, `tests/test_agent_runtime.py`).
- Ruff: Checks and formatting passed cleanly across all files.

## Environment Status

- Python 3.12 virtual environment (`.venv/`) configured.
- PostgreSQL 16 container `sutra_postgres` running on port 5444.
