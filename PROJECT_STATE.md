# Project State

## Project

Sutra — WhatsApp-first Personal AI Operating System.

## Vision

Reduce the mental and manual work required to run the day through the loop:
Observe -> Understand -> Remember -> Suggest -> Act -> Learn.

## Current Phase

Phase 3 — Conversation System.

STATUS: 🔒 LOCKED (Implemented, awaiting architectural review)

## Current Objective

Implement Sutra's persistent conversation and message domain with strict separation:
`Conversation` / `Message` distinct from `Session` and `AgentRun`.

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
- Explicit database indices created for conversation timestamps and message chronological retrieval (`conversation_id`, `created_at`, `id`).
- Implemented migration `f70c220788dc_create_conversations_and_messages_tables.py` and upgraded to `head`.
- Created Pydantic schemas in `apps/api/schemas/conversation.py` with validation rejecting empty/whitespace messages.
- Created `ConversationRepository` and `MessageRepository` in `apps/api/repositories/`.
- Created `ConversationService` in `apps/api/services/conversation.py` enforcing domain rules, 404 on missing conversations, and 422 on invalid content.
- Created conversation API routes in `apps/api/api/v1/routes/conversations.py` registered on `/api/v1/conversations`.
- Created comprehensive test suite in `tests/api/test_conversations.py`.
- All 20 tests pass, Ruff check & format clean.

## Implemented vs Planned

### IMPLEMENTED
- Domain models: `Conversation`, `Message`, `MessageRole`
- API endpoints:
  - `POST /api/v1/conversations`
  - `GET /api/v1/conversations`
  - `GET /api/v1/conversations/{id}`
  - `POST /api/v1/conversations/{id}/messages`
  - `GET /api/v1/conversations/{id}/messages`
- Foreign key cascade: deleting conversation deletes all related messages
- Chronological message ordering by `(created_at, id)`
- Error handling: NotFoundError (404), ValidationError (422)
- Unit and integration tests (20 tests passing)

### PLANNED (Not Implemented)
- Sessions (runtime context separation)
- Agent runs & task loops
- LLM connectivity & prompt generation
- WhatsApp webhook/polling integration
- Memory systems (working, short-term, long-term)
- Worker execution engine
- Web Control Center UI
- Authentication & authorization

## Current Work

Phase 3 implementation complete. Ready for architectural review.

## Next Work

Phase 4 — LLM Provider Layer.
Awaiting Phase 3 review and acceptance before unlocking.

## Important Decisions

- `Conversation` != `Session` != `AgentRun`: Session and AgentRun concepts are intentionally not implemented in Phase 3.
- `ondelete="CASCADE"` chosen for `Message.conversation_id`: deleting a conversation deletes its messages to prevent orphaned message records.
- Chronological ordering enforced at DB level using `ORDER BY created_at ASC, id ASC` with composite index `ix_messages_conversation_created_at`.
- No LLM integration or automated responses exist in Phase 3; message endpoint is purely persistence.
- No git commits created without explicit instruction.

## Testing Status

- Pytest: 20 tests passing across `tests/api/test_conversations.py`, `tests/api/test_health.py`, and `tests/db/test_database.py`.
- Ruff: Checks and formatting passed cleanly across all 36 files.

## Environment Status

- Python 3.12 virtual environment (`.venv/`) configured.
- PostgreSQL 16 container `sutra_postgres` running and healthy on port 5444.
