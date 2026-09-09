# Changelog

## Unreleased - Phase 3

### Added
- Domain models `Conversation` and `Message` in `apps/api/db/models/conversation.py`.
- Message role enumeration (`user`, `assistant`, `system`) as native PostgreSQL Enum.
- Alembic migration `f70c220788dc_create_conversations_and_messages_tables.py` establishing `conversations` and `messages` tables with indices and foreign key cascade.
- `ConversationRepository` and `MessageRepository` in `apps/api/repositories/` encapsulating database queries.
- `ConversationService` in `apps/api/services/conversation.py` providing application-level logic, non-empty validation, and error management.
- Pydantic models `ConversationCreate`, `ConversationRead`, `MessageCreate`, and `MessageRead` in `apps/api/schemas/conversation.py`.
- API endpoints registered under `/api/v1/conversations`:
  - `POST /api/v1/conversations`
  - `GET /api/v1/conversations`
  - `GET /api/v1/conversations/{id}`
  - `POST /api/v1/conversations/{id}/messages`
  - `GET /api/v1/conversations/{id}/messages`
- Integration tests in `tests/api/test_conversations.py` validating conversation/message CRUD, role validation, whitespace rejection, chronological ordering, and cascade deletion.

## 0.2.0 - 2026-09-09 (Phase 2)

### Added
- Local PostgreSQL 16 service in `docker-compose.yml` on port 5444.
- Database settings in `apps/api/config.py` and `.env.example`.
- SQLAlchemy 2.x Declarative Base in `apps/api/db/base.py`.
- Async engine and session factory in `apps/api/db/session.py`.
- Repository layer boundary in `apps/api/repositories/`.
- Alembic migration environment in `alembic/` configured to use application settings dynamically.
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
