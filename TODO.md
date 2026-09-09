# Roadmap

## Phase 0 — Project Foundation (Completed & Committed)

- [x] Establish repository structure and directories.
- [x] Define governance and phase-tracking documentation.
- [x] Initial commit on `main`.

## Phase 1 — Backend Foundation (Implemented & Verified)

- [x] Configure Pydantic Settings (`apps/api/config.py`).
- [x] Implement structured logging (`apps/api/core/logging.py`).
- [x] Implement minimal error handling (`apps/api/core/errors.py`).
- [x] Implement health route `GET /api/v1/health`.
- [x] Implement FastAPI application entry point (`apps/api/main.py`).
- [x] Implement dependency provider (`apps/api/dependencies.py`).
- [x] Configure Ruff linter (`ruff.toml`).
- [x] Create test suite with pytest & HTTPX (`tests/api/test_health.py`).

## Phase 2 — Database Architecture (Implemented & Verified)

- [x] Configure PostgreSQL in Docker Compose (`docker-compose.yml`).
- [x] Configure database settings (`apps/api/config.py`, `.env.example`).
- [x] Implement SQLAlchemy 2.x Declarative Base (`apps/api/db/base.py`).
- [x] Implement async engine and session factory (`apps/api/db/session.py`).
- [x] Establish repository layer boundary (`apps/api/repositories/`).
- [x] Configure Alembic migrations environment (`alembic/`).
- [x] Generate and execute initial empty migration.
- [x] Implement readiness endpoint `GET /api/v1/health/ready`.
- [x] Implement database test suite (`tests/db/test_database.py`).
- [ ] Architectural review & acceptance.

## Phase 3 — Conversation System (Locked / Planned)

- [ ] Design Conversation & Message schemas and models.
- [ ] Implement Conversation & Message repositories.
- [ ] Implement conversation service layer.

## Later Phases (Planned)

- [ ] Core Agent Engine
- [ ] Memory System
- [ ] WhatsApp Integration
- [ ] Web Control Center
