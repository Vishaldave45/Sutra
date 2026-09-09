# Roadmap

## Phase 0 — Project Foundation (Completed & Committed)

- [x] Establish repository structure and directories.
- [x] Define governance and phase-tracking documentation.
- [x] Initial commit on `main`.

## Phase 1 — Backend Foundation (Completed & Committed)

- [x] Configure Pydantic Settings (`apps/api/config.py`).
- [x] Implement structured logging (`apps/api/core/logging.py`).
- [x] Implement minimal error handling (`apps/api/core/errors.py`).
- [x] Implement health route `GET /api/v1/health`.
- [x] Implement FastAPI application entry point (`apps/api/main.py`).
- [x] Implement dependency provider (`apps/api/dependencies.py`).
- [x] Configure Ruff linter (`ruff.toml`).
- [x] Create test suite with pytest & HTTPX (`tests/api/test_health.py`).

## Phase 2 — Database Architecture (Completed & Committed)

- [x] Configure PostgreSQL in Docker Compose (`docker-compose.yml`).
- [x] Configure database settings (`apps/api/config.py`, `.env.example`).
- [x] Implement SQLAlchemy 2.x Declarative Base (`apps/api/db/base.py`).
- [x] Implement async engine and session factory (`apps/api/db/session.py`).
- [x] Establish repository layer boundary (`apps/api/repositories/`).
- [x] Configure Alembic migrations environment (`alembic/`).
- [x] Generate and execute initial empty migration.
- [x] Implement readiness endpoint `GET /api/v1/health/ready`.
- [x] Implement database test suite (`tests/db/test_database.py`).

## Phase 3 — Conversation System (Implemented & Verified)

- [x] Create `Conversation` & `Message` SQLAlchemy models with native Enum roles (`apps/api/db/models/conversation.py`).
- [x] Create migration `f70c220788dc` for conversations and messages.
- [x] Create Pydantic request/response schemas (`apps/api/schemas/conversation.py`).
- [x] Create repositories `ConversationRepository` & `MessageRepository` (`apps/api/repositories/`).
- [x] Create `ConversationService` (`apps/api/services/conversation.py`).
- [x] Create API endpoints on `/api/v1/conversations` (`apps/api/api/v1/routes/conversations.py`).
- [x] Enforce empty & whitespace content validation, 404 handling, and chronological ordering.
- [x] Create comprehensive domain test suite (`tests/api/test_conversations.py`).
- [ ] Architectural review & acceptance.

## Phase 4 — LLM Provider Layer (Locked / Planned)

- [ ] Design LLM client interface & abstraction.
- [ ] Implement provider client integration.
- [ ] Connect conversation context to generation flow.

## Later Phases (Planned)

- [ ] Agent Runtime & Agent Runs
- [ ] Sessions & Execution Context
- [ ] Memory System
- [ ] WhatsApp Integration
- [ ] Web Control Center
