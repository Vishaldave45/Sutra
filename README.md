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
backend foundation.

## High-Level Architecture

The repository is organized into application services under `apps/`, reusable
domain packages under `packages/`, tests under `tests/`, and technical/product
documentation under `docs/`.

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
└── core/
    ├── errors.py
    └── logging.py

tests/
└── api/
    └── test_health.py
```

## Implemented Capabilities

- FastAPI application core (`apps/api/main.py`)
- Pydantic Settings environment-based configuration (`apps/api/config.py`)
- Centralized error-handling baseline (`apps/api/core/errors.py`)
- Structured logging configuration (`apps/api/core/logging.py`)
- Liveness health endpoint (`GET /api/v1/health`)
- Automated tests using pytest and HTTPX

## Planned Capabilities (Not Implemented)

- Database persistence & migrations (PostgreSQL / SQLAlchemy)
- Agent runtime & tool execution framework
- LLM integrations & context assembly
- Memory systems (working, short-term, long-term)
- WhatsApp messaging adapter
- Web Control Center frontend

## Current Phase

Phase 1 — Backend Foundation.

This phase establishes the runnable FastAPI backend boundary. No database,
LLM, agent, tool, or messaging integration is present.
