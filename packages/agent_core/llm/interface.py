from abc import ABC, abstractmethod

from packages.agent_core.llm.models import LLMRequest, LLMResponse


class LLMProvider(ABC):
    """Provider-independent abstract base class for LLM integrations."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider implementation (e.g. 'openai', 'mock')."""
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Default model identifier when not explicitly provided in the request."""
        pass

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a response given a provider-neutral LLMRequest.

        Raises:
            LLMConfigurationError: If provider configuration is invalid or missing.
            LLMAuthenticationError: If authentication with the provider fails.
            LLMInvalidRequestError: If the request is invalid or malformed.
            LLMRateLimitError: If provider rate limits are exceeded.
            LLMTimeoutError: If the request times out.
            LLMTransientError: If a transient server-side error occurs.
            LLMUnexpectedError: For unexpected or unhandled provider errors.
        """
        pass
