# Roadmap

## Phase 0 — Project Foundation (Completed & Committed)

- [x] Establish repository structure and directories.
- [x] Define governance and phase-tracking documentation.
- [x] Initial commit on `main`.

## Phase 1 — Backend Foundation (Completed & Committed)

- [x] Configure Pydantic Settings (`apps/api/config.py`).
- [x] Implement structured logging (`apps/api/core/logging.py`).
- [x] Implement minimal error handling (`apps/api/core/errors.py`).
- [x] Implement health route `GET /api/v1/health`.
- [x] Implement FastAPI application entry point (`apps/api/main.py`).
- [x] Implement dependency provider (`apps/api/dependencies.py`).
- [x] Configure Ruff linter (`ruff.toml`).
- [x] Create test suite with pytest & HTTPX (`tests/api/test_health.py`).

## Phase 2 — Database Architecture (Completed & Committed)

- [x] Configure PostgreSQL in Docker Compose (`docker-compose.yml`).
- [x] Configure database settings (`apps/api/config.py`, `.env.example`).
- [x] Implement SQLAlchemy 2.x Declarative Base (`apps/api/db/base.py`).
- [x] Implement async engine and session factory (`apps/api/db/session.py`).
- [x] Establish repository layer boundary (`apps/api/repositories/`).
- [x] Configure Alembic migrations environment (`alembic/`).
- [x] Generate and execute initial empty migration.
- [x] Implement readiness endpoint `GET /api/v1/health/ready`.
- [x] Implement database test suite (`tests/db/test_database.py`).

## Phase 3 — Conversation System (Completed & Committed)

- [x] Create `Conversation` & `Message` SQLAlchemy models with native Enum roles (`apps/api/db/models/conversation.py`).
- [x] Create migration `f70c220788dc` for conversations and messages.
- [x] Create Pydantic request/response schemas (`apps/api/schemas/conversation.py`).
- [x] Create repositories `ConversationRepository` & `MessageRepository` (`apps/api/repositories/`).
- [x] Create `ConversationService` (`apps/api/services/conversation.py`).
- [x] Create API endpoints on `/api/v1/conversations` (`apps/api/api/v1/routes/conversations.py`).
- [x] Enforce validation, 404 handling, and chronological ordering.
- [x] Create comprehensive domain test suite (`tests/api/test_conversations.py`).

## Phase 4 — LLM Provider Layer (Completed & Committed)

- [x] Define provider-neutral contracts: `LLMRequest`, `LLMResponse`, `LLMUsage` (`packages/agent_core/llm/models.py`).
- [x] Define abstract base class `LLMProvider` (`packages/agent_core/llm/interface.py`).
- [x] Implement deterministic `MockLLMProvider` (`packages/agent_core/llm/mock.py`).
- [x] Implement `OpenAIProvider` with official OpenAI SDK (`packages/agent_core/llm/providers/openai.py`).
- [x] Implement normalized exception hierarchy (`packages/agent_core/llm/errors.py`).
- [x] Implement configurable timeouts and selective retries for transient errors.
- [x] Add LLM settings to configuration (`apps/api/config.py`, `.env.example`).
- [x] Create test suite with mocks/fakes (`tests/test_llm_provider.py`).
- [x] Architectural review & acceptance (Commit `e06151b`).

## Phase 5 — Agent Runtime (Completed & Committed)

- [x] Design Agent Runtime and single-pass execution model.
- [x] Define in-memory execution records (`AgentRun`, `AgentRunStatus`).
- [x] Implement `AgentRuntime` with deterministic message translation and assembly.
- [x] Implement runtime error hierarchy (`AgentInputError`, `AgentConfigurationError`).
- [x] Implement offline test suite with `MockLLMProvider` (`tests/test_agent_runtime.py`).
- [x] Architectural review & acceptance (Commit `9c7019d`).

## Phase 6 — Tool System (Implemented, Pending Acceptance)

- [x] Create strongly typed `ToolDefinition` with Pydantic JSON Schema generation.
- [x] Implement action risk levels (`READ`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) and `permission: list[str]`.
- [x] Implement abstract base class `Tool` (`packages/agent_core/tools/interface.py`).
- [x] Implement isolated, deterministic `ToolRegistry` (`packages/agent_core/tools/registry.py`).
- [x] Implement `ToolExecutor` with input validation, timeout enforcement, output validation, and `ToolResult` normalization.
- [x] Implement dedicated tool error taxonomy with credential scrubbing.
- [x] Implement deterministic reference tools (`EchoTool`, `DeterministicFailureTool`, `DeterministicTimeoutTool`, `InvalidOutputTool`).
- [x] Implement comprehensive unit tests (`tests/test_tool_*.py`).
- [ ] Architectural review & acceptance.

## Later Phases (Planned)

- [ ] Phase 7 — Task & Project Domain
- [ ] Phase 8 — Memory Systems
- [ ] Phase 9 — Context Engine
- [ ] Phase 12 — WhatsApp Integration
- [ ] Phase 14 — Security & Approval Policies
