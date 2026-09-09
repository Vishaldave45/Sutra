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
Application / Service Layer
   │
   ▼
Repository Layer
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
│           ├── conversations.py
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
│       └── conversation.py
│
├── repositories/
│   ├── conversation.py
│   └── message.py
│
├── schemas/
│   └── conversation.py
│
└── services/
    └── conversation.py

alembic/
├── versions/
│   ├── 66fcee048c39_initial_empty_schema.py
│   └── f70c220788dc_create_conversations_and_messages_tables.py
├── env.py
└── script.py.mako

tests/
├── api/
│   ├── test_conversations.py
│   └── test_health.py
└── db/
    └── test_database.py
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
- Conversation domain entities: `Conversation` and `Message` (`apps/api/db/models/conversation.py`)
- Explicit message roles: `user`, `assistant`, `system` (native PostgreSQL Enum)
- Foreign key cascade: deleting a conversation cascades to all its messages
- Clean separation: API -> Service (`ConversationService`) -> Repository (`ConversationRepository`, `MessageRepository`) -> DB
- Conversation API endpoints:
  - `POST /api/v1/conversations`: Create conversation
  - `GET /api/v1/conversations`: List conversations
  - `GET /api/v1/conversations/{id}`: Get conversation
  - `POST /api/v1/conversations/{id}/messages`: Create & persist message
  - `GET /api/v1/conversations/{id}/messages`: List messages in chronological order
- Alembic database migration environment (`alembic/`)
- Local Docker PostgreSQL configuration (`docker-compose.yml`)
- Automated test suites (20 tests passing)

## Planned Capabilities (Not Implemented)

- LLM Provider layer & completions
- Agent runtime, task loops, & agent runs
- Sessions (runtime context separation)
- Memory systems (working, short-term, long-term)
- WhatsApp messaging adapter
- Web Control Center frontend
- Authentication & authorization

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
