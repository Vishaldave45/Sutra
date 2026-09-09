# Sutra

Sutra is a WhatsApp-first Personal AI Operating System designed to reduce the
mental and manual work required to run the day.

## Interfaces

- Primary interface: WhatsApp
- Secondary interface: Web Control Center

## Core Purpose

Sutra is intended to support the loop:

Observe -> Understand -> Remember -> Suggest -> Act -> Learn

These capabilities are planned. They are not implemented in the current
foundation phase.

## High-Level Architecture

The repository is organized into application services under `apps/`, reusable
domain packages under `packages/`, tests under `tests/`, and technical/product
documentation under `docs/`. The architecture will be expanded phase by phase
as decisions are reviewed and locked.

## Development Philosophy

- Implement only the currently locked phase.
- Prefer small, explicit structures over speculative abstractions.
- Keep planned capabilities clearly separate from implemented capabilities.
- Verify each phase before beginning the next one.

## Current Phase

Phase 0 — Project Foundation.

This phase establishes repository structure and engineering governance. No AI,
LLM, database, WhatsApp, memory, agent, tool, API, automation, or frontend
functionality belongs in this phase.
