from typing import Any


class LLMError(Exception):
    """Base exception for all normalized LLM provider errors."""

    def __init__(self, message: str, details: Any = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class LLMConfigurationError(LLMError):
    """Raised when provider configuration or credentials are missing or invalid."""

    pass


class LLMAuthenticationError(LLMError):
    """Raised when authentication fails with the provider (e.g. invalid API key)."""

    pass


class LLMInvalidRequestError(LLMError):
    """Raised when request is malformed or rejected as invalid (non-retryable)."""

    pass


class LLMRateLimitError(LLMError):
    """Raised when provider rate limits are exceeded (transient)."""

    pass


class LLMTimeoutError(LLMError):
    """Raised when an LLM call exceeds the configured timeout."""

    pass


class LLMTransientError(LLMError):
    """Raised when a transient provider-side failure occurs (5xx, server error)."""

    pass


class LLMUnexpectedError(LLMError):
    """Raised when an unhandled or unexpected provider failure occurs."""

    pass
