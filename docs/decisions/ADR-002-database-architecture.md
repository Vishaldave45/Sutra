# ADR-002: Database Architecture and Persistence Boundaries

- **Status**: Accepted
- **Date**: 2026-09-09
- **Deciders**: Sutra Architecture Team

---

## Context

Sutra requires durable persistence for user interactions, configurations, and eventual agent actions. To maintain reliability across asynchronous operations, the persistence architecture must:
1. Support native asynchronous concurrency compatible with FastAPI and async LLM provider calls.
2. Provide predictable, version-controlled schema evolution.
3. Prevent business services from directly managing database connections, commits, or transaction boundaries.
4. Support flexible metadata without schema sprawl (e.g., heterogeneous payloads from WhatsApp, API channels, or LLM tokens).
5. Avoid premature schema commitment for domain concepts that have not yet undergone architecture locking.

---

## Decision

We selected **PostgreSQL 16** managed via **SQLAlchemy 2.x (Async)**, **psycopg 3**, and **Alembic**, under the following architectural rules:

1. **Async Engine & Session Lifecycle**:
   - `create_async_engine` with `async_sessionmaker` configured in `apps/api/db/session.py`.
   - Dependency injection (`get_db_session`) yields isolated sessions with automatic rollback on unhandled exceptions and explicit commits on successful completion.
2. **Declarative Base**:
   - Centralized `Base(DeclarativeBase)` in `apps/api/db/base.py`.
3. **Repository Pattern Boundary**:
   - Persistence operations are encapsulated in `apps/api/repositories/`. Business services call repository methods and never assemble SQL strings or manipulate raw sessions.
4. **Migration System**:
   - Alembic manages schema migrations (`alembic/`), configured to resolve connection settings dynamically from application environment variables without hardcoded credentials.
   - Initial migration established the base migration path before any domain models were introduced.
5. **JSONB for Flexible Extensibility**:
   - Domain models utilize PostgreSQL `JSONB` for `metadata` fields to store non-relational context without necessitating frequent schema migrations.
6. **Local Development Containerization**:
   - PostgreSQL 16 Alpine container managed via `docker-compose.yml` with healthchecks and persistent named volume.
7. **Readiness vs. Liveness Isolation**:
   - Liveness check (`GET /api/v1/health`) remains completely independent of database connectivity.
   - Readiness check (`GET /api/v1/health/ready`) performs an active `SELECT 1` ping against PostgreSQL, returning HTTP 503 if unavailable without leaking connection parameters.

---

## Consequences

### Positive
- Zero blocking I/O across the database interaction layer.
- Explicit transaction boundaries prevent partial or corrupted database writes.
- Migration history is strictly version-controlled and reproducible across environments.
- Business services remain decoupled from database vendor specifics.

### Negative / Tradeoffs
- Asynchronous SQLAlchemy requires adherence to greenlet-safe patterns and careful relationship loading strategies (e.g., explicit joined/selectin loading) to avoid missing greenlet errors.
- Alembic requires synchronous driver access (`postgresql+psycopg://`) during offline/online migration runs.

---

## Alternatives Considered

1. **Synchronous SQLAlchemy / psycopg2**:
   - *Rejected*: Blocks the Python event loop during queries, degrading concurrency in an async FastAPI application.
2. **Tortoise ORM / Peewee**:
   - *Rejected*: Smaller ecosystems, fewer migration management capabilities compared to Alembic, and limited support for complex enterprise patterns.
3. **MongoDB / Document Store**:
   - *Rejected*: Relational integrity, foreign key constraints (e.g., `conversations` -> `messages`), and strict transactional safety are critical for Sutra's core data model.
4. **Premature Domain Tables & pgvector in Phase 2**:
   - *Rejected*: Creating `users`, `memories`, `tasks`, or vector indexes before their functional domain requirements are locked leads to brittle, poorly-specified database schemas.

