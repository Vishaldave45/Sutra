# Changelog

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
