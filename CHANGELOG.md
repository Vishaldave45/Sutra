# Changelog

## Unreleased - Phase 4

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
