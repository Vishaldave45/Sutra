# Project State

## Project

Sutra — WhatsApp-first Personal AI Operating System.

## Vision

Reduce the mental and manual work required to run the day through the loop:
Observe -> Understand -> Remember -> Suggest -> Act -> Learn.

## Current Phase

Phase 4 — LLM Provider Layer.

STATUS: 🔒 LOCKED (Implemented, awaiting architectural review)

## Current Objective

Create a provider-independent LLM abstraction that future Sutra services and the future Agent Runtime can use, without introducing an agent framework or coupling LLM calls to conversation routes.

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
- Created test suite in `tests/test_llm_provider.py` covering models, mock provider, OpenAI construction, error normalization, retry exhaustion, timeout, rate limits, and token usage tracking.
- All 35 tests pass, Ruff check & format clean.

## Implemented vs Planned

### IMPLEMENTED
- Domain models: `Conversation`, `Message`, `MessageRole`
- API endpoints: `/api/v1/conversations`, `/api/v1/health`
- LLM Provider abstraction: `LLMProvider`, `OpenAIProvider`, `MockLLMProvider`
- Provider contracts: `LLMRequest`, `LLMResponse`, `LLMUsage`
- Error normalization & retry policy for transient LLM failures
- Automated test suites (35 tests passing)

### PLANNED (Not Implemented)
> The LLM provider layer exists, but Sutra's Agent Runtime has not yet been implemented.
- Agent Runtime & reasoning loop
- Agent execution runs (`AgentRun`)
- Sessions (runtime context separation)
- Automated AI responses on message creation
- Tool calling & function execution
- Memory systems (working, short-term, long-term)
- WhatsApp webhook/polling integration
- Worker execution engine
- Web Control Center UI
- Authentication & authorization

## Current Work

Phase 4 implementation complete. Ready for architectural review.

## Next Work

Phase 5 — Agent Runtime (reasoning loop, execution boundaries, prompt composition).
Awaiting Phase 4 review and acceptance before unlocking.

## Important Decisions

- The LLM provider layer is strictly decoupled from API routes and `POST /api/v1/conversations/{id}/messages`. No automated LLM response is triggered on message persistence.
- Official OpenAI SDK dependency is strictly confined to `packages/agent_core/llm/providers/openai.py`.
- Raw vendor SDK exceptions never cross the abstraction boundary; all are normalized to `LLMError` subclasses.
- Retries are restricted exclusively to transient errors (server 5xx, timeouts, connection drops, rate limits). Non-retryable errors (authentication, bad requests) fail immediately without retries.
- No git commits created without explicit instruction.

## Testing Status

- Pytest: 35 tests passing across all suites (`tests/api/`, `tests/db/`, `tests/test_llm_provider.py`).
- Ruff: Checks and formatting passed cleanly across all 45 files.
- Real network calls avoided: all provider tests use isolated mocks and fakes.

## Environment Status

- Python 3.12 virtual environment (`.venv/`) configured with `openai` and existing dependencies.
- PostgreSQL 16 container `sutra_postgres` running on port 5444.
