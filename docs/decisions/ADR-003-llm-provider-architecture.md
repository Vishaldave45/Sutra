# ADR-003: LLM Provider Abstraction and Boundary Isolation

- **Status**: Accepted
- **Date**: 2026-09-09
- **Deciders**: Sutra Architecture Team

---

## Context

Sutra requires language model capabilities for natural language comprehension, reasoning, and response generation. However, coupling the core system directly to a specific vendor's SDK (such as OpenAI, Anthropic, or Google) introduces significant risks:
1. **Vendor Lock-in**: Switching or load-balancing across models or providers would require sweeping changes across route handlers and services.
2. **SDK Type Leakage**: Exposing vendor-specific request/response objects across application layers breaks encapsulation and complicates testing.
3. **Unreliable Testing**: If tests require external network connections or live API keys, test suites become slow, brittle, nondeterministic, and costly.
4. **Uncontrolled Retries & Timeouts**: Vendor SDKs often default to aggressive retries or unbounded timeouts, leading to hanging processes or unexpected rate limits.

---

## Decision

We designed and implemented a **provider-independent LLM abstraction layer** in `packages/agent_core/llm/` adhering to the following rules:

```text
Application / Services / Future Agent Runtime
                      │
                      ▼
            LLMProvider (Interface)
            ├── LLMRequest (Model)
            ├── LLMResponse (Model)
            └── LLMUsage (Model)
                      │
           ┌──────────┴──────────┐
           ▼                     ▼
     OpenAIProvider        MockLLMProvider
           │                     │
           ▼                     ▼
     Official SDK          Offline Deterministic Tests
  (Isolated in Adapter)
```

Key architectural standards:
1. **Abstract Contract**:
   - `LLMProvider` abstract base class defining `generate(request: LLMRequest) -> LLMResponse`.
2. **Provider-Neutral Contracts**:
   - `LLMRequest`: Contains normalized messages (`LLMMessage` with role `user`, `assistant`, `system`), optional model override, temperature, and max tokens. Content is strictly validated against empty and whitespace-only strings.
   - `LLMResponse`: Contains generated text, model used, normalized token usage (`LLMUsage`), provider name, and sanitized provider metadata.
3. **Adapter Isolation**:
   - The official `openai` Python SDK is imported **only** within `packages/agent_core/llm/providers/openai.py`. No OpenAI classes or errors are imported in routes, services, or higher-level abstractions.
4. **Normalized Error Hierarchy**:
   - All vendor exceptions are caught within the adapter and mapped to normalized subclasses of `LLMError`:
     - Non-retryable: `LLMConfigurationError`, `LLMAuthenticationError`, `LLMInvalidRequestError`.
     - Transient / Retryable: `LLMRateLimitError`, `LLMTimeoutError`, `LLMTransientError`.
     - Fallback: `LLMUnexpectedError`.
5. **Bounded Timeout & Selective Retry Policy**:
   - Requests have an explicit configurable timeout (`SUTRA_LLM_TIMEOUT_SECONDS`).
   - Retries are strictly bounded (`SUTRA_LLM_MAX_RETRIES`) and execute with exponential backoff **only** for transient errors (server 5xx, rate limits, network connection drops). Non-retryable errors (authentication, bad requests) fail immediately.
6. **Zero-Network Testability**:
   - `MockLLMProvider` provides deterministic, offline responses, failure injection, and request inspection for test suites.
   - The package can be imported and instantiated without requiring an API key.

---

## Consequences

### Positive
- Future components (such as Phase 5 Agent Runtime) consume a stable, typed Python interface without knowing or caring which vendor serves the completion.
- Full testability: 100% of LLM interaction logic is tested deterministically without network calls or API costs.
- Adding future providers (Anthropic, Gemini, local Ollama) requires only implementing a new adapter class inheriting from `LLMProvider`.
- Credentials and internal vendor error payloads cannot leak through normalized exception boundaries.

### Negative / Tradeoffs
- Advanced vendor-specific proprietary features (e.g., proprietary tool calling formats or vendor-specific caching tokens) must be normalized into generic contracts rather than passed through directly.

---

## Alternatives Considered

1. **Direct OpenAI SDK Usage in Services**:
   - *Rejected*: Direct imports of `openai` in API or conversation services create tight coupling, leak vendor exceptions, and prevent offline automated unit testing.
2. **Adopting LangChain / LlamaIndex / LiteLLM**:
   - *Rejected*: Large third-party frameworks introduce extensive dependency graphs, rapid breaking changes, and high architectural churn. Sutra retains full ownership of its lightweight provider abstraction.

