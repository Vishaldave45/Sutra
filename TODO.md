# Roadmap

## Phase 0 — Project Foundation (Completed & Committed)

- [x] Establish repository structure and directories.
- [x] Define governance and phase-tracking documentation.
- [x] Initial commit on `main`.

## Phase 1 — Backend Foundation (Implemented & Verified)

- [x] Configure Pydantic Settings (`apps/api/config.py`).
- [x] Implement structured logging (`apps/api/core/logging.py`).
- [x] Implement minimal error handling (`apps/api/core/errors.py`).
- [x] Implement health route `GET /api/v1/health` (`apps/api/api/v1/routes/health.py`).
- [x] Implement FastAPI application entry point (`apps/api/main.py`).
- [x] Implement dependency provider (`apps/api/dependencies.py`).
- [x] Configure Ruff linter (`ruff.toml`).
- [x] Create test suite with pytest & HTTPX (`tests/api/test_health.py`).
- [x] Verify startup without external services.
- [ ] Architectural review & acceptance.

## Phase 2 — Database Architecture (Locked / Planned)

- [ ] Design PostgreSQL schema & data models.
- [ ] Configure database connections and migrations.
- [ ] Implement repository interfaces.

## Later Phases (Planned)

- [ ] Core Agent Engine
- [ ] Memory System
- [ ] WhatsApp Integration
- [ ] Web Control Center
