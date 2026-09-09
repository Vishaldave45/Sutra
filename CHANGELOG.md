# Changelog

## Unreleased - Phase 2

### Added
- Local PostgreSQL 16 service in `docker-compose.yml` on port 5444.
- Database settings in `apps/api/config.py` and `.env.example`.
- SQLAlchemy 2.x Declarative Base in `apps/api/db/base.py`.
- Async engine and session factory in `apps/api/db/session.py`.
- Repository layer boundary in `apps/api/repositories/`.
- Alembic migration environment in `alembic/` configured to use application settings dynamically.
- Initial schema migration `66fcee048c39_initial_empty_schema.py`.
- Database readiness check at `GET /api/v1/health/ready`.
- Test suite in `tests/db/test_database.py` covering database connection, session lifecycle, readiness, Alembic configuration, and liveness isolation.

## Unreleased - Phase 1

### Added
- FastAPI backend application in `apps/api/main.py`.
- Environment-based configuration using Pydantic Settings in `apps/api/config.py`.
- Health check endpoint at `GET /api/v1/health` returning `{"status": "ok", "service": "sutra-api"}`.
- Structured logging utility in `apps/api/core/logging.py`.
- Centralized error handling base in `apps/api/core/errors.py`.
- Dependency injection placeholder in `apps/api/dependencies.py`.
- Ruff configuration in `ruff.toml`.
- Pytest test suite in `tests/api/test_health.py`.
- Updated `.env.example` with application environment variables.

## 0.1.0 - 2026-09-09

### Added
- Bootstrapped the Sutra repository structure.
- Added project governance and phase-tracking documentation.
- Added placeholder environment and Docker Compose configuration.
