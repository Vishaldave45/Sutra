# ADR-001: Backend Foundation and Layered Architecture

- **Status**: Accepted
- **Date**: 2026-09-09
- **Deciders**: Sutra Architecture Team

---

## Context

Sutra is designed as a WhatsApp-first Personal AI Operating System whose core purpose is to reduce the mental and manual friction of daily life across a continuous cognitive loop:
`Observe -> Understand -> Remember -> Suggest -> Act -> Learn`.

To fulfill this mission, Sutra requires a backend web framework and architecture that is:
1. **Asynchronous & High-Throughput**: Designed for concurrency to support long-polling webhooks (WhatsApp), concurrent LLM generations, and asynchronous background tasks.
2. **Cleanly Separated**: Guarded against business logic leaking into HTTP controllers or raw database queries.
3. **Strictly Typed & Self-Validating**: Ensuring runtime safety, schema validation, and automatic API documentation.
4. **Lightweight & Foundation-First**: Avoidant of bloated, heavy-handed web frameworks that mandate premature ORMs or monolithic structures.

---

## Decision

We chose **Python 3.12+** with **FastAPI** organized under a **strict layered architecture**:

```text
HTTP / Webhook Interface (FastAPI Router)
                │
                ▼
      Application Service Layer
                │
                ▼
        Repository Layer
                │
                ▼
      Database (SQLAlchemy)
```

Key architectural standards established:
- **Web Framework**: FastAPI for high-performance async request handling, dependency injection, and native OpenAPI generation.
- **Validation & Serialization**: Pydantic 2.x and `pydantic-settings` for environment-driven configuration and request/response contracts.
- **Layered Boundary**:
  - `apps/api/api/v1/routes/`: Responsible only for HTTP status codes, request parsing, and delegating to services.
  - `apps/api/services/`: Pure business and application orchestration logic.
  - `apps/api/repositories/`: Encapsulation of database queries and persistence mechanics.
  - `apps/api/core/`: Centralized structured logging and normalized exception handling (`SutraAppError`).
- **Code Quality & Testing**: Ruff for fast linting/formatting and `pytest` + `httpx` for test execution.
- **Explicit Lifecycle**: Clear separation of liveness (`GET /api/v1/health`) from external dependencies to guarantee zero-dependency application bootstrapping.

---

## Consequences

### Positive
- API endpoints remain declarative, readable, and decoupled from persistence details.
- High testability: services and repositories can be tested independently using mocks or isolated sessions without bootstrapping the HTTP server.
- Consistent configuration through validated environment variables (`SUTRA_` prefix).
- Predictable and normalized API error responses.

### Negative / Tradeoffs
- Requires boilerplate classes (routers, services, repositories, and schemas) compared to active-record or monolithic approaches.
- Requires team discipline to avoid bypassing service boundaries from route handlers.

---

## Alternatives Considered

1. **Django / Django Ninja**:
   - *Rejected*: Django brings substantial monolithic baggage (built-in auth, admin, synchronous ORM roots) that conflicts with our phase-locked micro-architecture and asynchronous LLM orchestration goals.
2. **Flask**:
   - *Rejected*: Lacks native asynchronous concurrency and modern typed request validation without assembling multiple disparate third-party extensions.
3. **Direct Database Access in FastAPI Routes**:
   - *Rejected*: Tightly couples HTTP route handlers to database session mechanics, making future transport additions (e.g., CLI, message queues, WhatsApp event handlers) difficult to refactor.

