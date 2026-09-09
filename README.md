# Sutra

Sutra is a WhatsApp-first Personal AI Operating System designed to reduce the
mental and manual work required to run the day.

## Interfaces

- Primary interface: WhatsApp (Planned)
- Secondary interface: Web Control Center (Planned)

## Core Purpose

Sutra is intended to support the loop:

Observe -> Understand -> Remember -> Suggest -> Act -> Learn

These capabilities are PLANNED. They are not implemented in the current
phases.

## Architecture

```text
FastAPI
   │
   ▼
Application / Services
   │
   ▼
Repositories
   │
   ▼
SQLAlchemy (Async)
   │
   ▼
PostgreSQL (16)
```

```text
apps/api/
├── main.py
├── config.py
├── dependencies.py
│
├── api/
│   └── v1/
│       └── routes/
│           └── health.py
│
├── core/
│   ├── errors.py
│   └── logging.py
│
├── db/
│   ├── base.py
│   ├── session.py
│   └── models/
│
└── repositories/

alembic/
├── versions/
├── env.py
└── script.py.mako

tests/
├── api/
└── db/
```

## Implemented Capabilities

- FastAPI application core (`apps/api/main.py`)
- Pydantic Settings environment configuration (`apps/api/config.py`)
- Centralized error handling (`apps/api/core/errors.py`)
- Structured logging (`apps/api/core/logging.py`)
- Application liveness endpoint (`GET /api/v1/health`)
- Database readiness check (`GET /api/v1/health/ready`)
- SQLAlchemy 2.x async engine and session factory (`apps/api/db/session.py`)
- SQLAlchemy Declarative Base (`apps/api/db/base.py`)
- Alembic database migration environment (`alembic/`)
- Repository isolation boundary (`apps/api/repositories/`)
- Local Docker PostgreSQL configuration (`docker-compose.yml`)
- Automated test suites for API & Database (`tests/api/`, `tests/db/`)

## Planned Capabilities (Not Implemented)

- Domain models (User, Message, Conversation, Task, Memory, etc.)
- Business logic & service layer
- Agent runtime & tool execution framework
- LLM integrations & prompt assembly
- WhatsApp webhook/polling integration
- Worker execution engine
- Web Control Center UI

## Local Development

### 1. Start PostgreSQL
```bash
docker compose up -d
```

### 2. Run Database Migrations
```bash
PYTHONPATH=. alembic upgrade head
```

### 3. Run Tests
```bash
PYTHONPATH=. pytest
```

### 4. Run Linter & Formatter
```bash
ruff check .
ruff format --check .
```
