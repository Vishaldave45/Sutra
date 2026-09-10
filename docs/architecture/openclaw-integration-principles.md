# Architecture Position: OpenClaw Integration Principles

> **Architectural Evaluation Only**: This document records Sutra's position and integration guidelines regarding OpenClaw. **No code, dependencies, or integrations are implemented in this phase.**

---

## 1. Context

OpenClaw is an open, extensible personal agent automation gateway capable of interfacing with browsers, desktop environments, messaging platforms, and tool ecosystems.

While OpenClaw provides valuable execution capabilities, Sutra must avoid the classic architectural trap of binding its internal core directly to an external, rapidly-evolving framework's internal classes.

---

## 2. Core Integration Principles

If and when OpenClaw capabilities are utilized by Sutra, the integration must strictly obey the following seven principles:

### 1. Protocol / Gateway Boundary over Python Imports
- Sutra must interact with OpenClaw through **well-defined external interfaces** (e.g., HTTP REST, WebSockets, or OpenAPI endpoints exposed by the OpenClaw Gateway).
- **Prohibition**: Sutra application code must **never import internal OpenClaw Python modules** or rely on OpenClaw private classes.

### 2. Sutra Owns the Source of Truth
- Sutra maintains full ownership of its domain models:
  - `Conversation` and `Message` (Database)
  - `AgentRun` (Lifecycle)
  - User preferences, context, and memory
- OpenClaw must never become the authoritative database or persistence layer for Sutra's state.

### 3. Sutra Enforces the Security and Approval Policy
- Security policies, approval prompts, and action risk evaluations (see `docs/security/tool-risk-model.md`) belong to Sutra.
- Sutra will not delegate authorization or permission validation to OpenClaw. OpenClaw operates strictly as an execution worker executing authorized actions.

### 4. OpenClaw Must Remain Replaceable
- The execution interface must sit behind an internal Sutra abstraction (e.g., `ExecutionBackend` or `ToolRunner`).
- Replacing OpenClaw with a native Python sandbox, Docker worker, or alternative execution backend must not require modifying Sutra's core Agent Runtime or Conversation services.

### 5. Independent Failure Domains
- If the OpenClaw gateway is down, unreachable, or restarts, Sutra's core API (`apps/api/`) and conversational storage must remain fully operational.
- OpenClaw connection dropouts must be handled as normalized transient failures.

### 6. No Credential Exposure
- Long-lived credentials and private user keys remain encapsulated within Sutra's secure configuration. OpenClaw instances are granted only scoped, ephemeral execution tokens when necessary.

### 7. Pre-Implementation Feasibility Verification
- Prior to writing any integration code, the specific installed version, API endpoints, and capability specifications of the OpenClaw Gateway must be inspected and validated against Sutra's architecture.

