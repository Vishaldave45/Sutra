from typing import Any

from packages.agent_core.llm.interface import LLMProvider
from packages.agent_core.llm.models import LLMRequest, LLMResponse, LLMUsage


class MockLLMProvider(LLMProvider):
    """Deterministic mock provider for testing without external network or API keys."""

    def __init__(
        self,
        default_response: str = "Mock generated response",
        default_model: str = "mock-model-v1",
        usage: LLMUsage | None = None,
        should_fail_with: Exception | None = None,
    ) -> None:
        self._default_response = default_response
        self._default_model = default_model
        self._usage = usage or LLMUsage(
            input_tokens=10,
            output_tokens=5,
            total_tokens=15,
        )
        self._should_fail_with = should_fail_with
        self.recorded_requests: list[LLMRequest] = []

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def default_model(self) -> str:
        return self._default_model

    def set_next_response(self, response: str) -> None:
        self._default_response = response

    def set_failure(self, exc: Exception | None) -> None:
        self._should_fail_with = exc

    async def generate(self, request: LLMRequest) -> LLMResponse:
        self.recorded_requests.append(request)

        if self._should_fail_with is not None:
            raise self._should_fail_with

        effective_model = request.model or self._default_model

        metadata: dict[str, Any] = {
            "mock": True,
            "recorded_request_count": len(self.recorded_requests),
        }

        return LLMResponse(
            text=self._default_response,
            model=effective_model,
            usage=self._usage,
            provider=self.provider_name,
            provider_metadata=metadata,
        )
