import asyncio
import logging
from typing import Any

import openai
from openai import AsyncOpenAI

from packages.agent_core.llm.errors import (
    LLMAuthenticationError,
    LLMConfigurationError,
    LLMInvalidRequestError,
    LLMRateLimitError,
    LLMTimeoutError,
    LLMTransientError,
    LLMUnexpectedError,
)
from packages.agent_core.llm.interface import LLMProvider
from packages.agent_core.llm.models import LLMRequest, LLMResponse, LLMUsage

logger = logging.getLogger("sutra.llm.openai")


class OpenAIProvider(LLMProvider):
    """Provider implementation encapsulating the official OpenAI Async SDK."""

    def __init__(
        self,
        api_key: str | None = None,
        default_model: str = "gpt-4o-mini",
        timeout: float = 30.0,
        max_retries: int = 2,
        base_url: str | None = None,
        client: AsyncOpenAI | None = None,
    ) -> None:
        self._default_model = default_model
        self._timeout = timeout
        self._max_retries = max(0, max_retries)

        if client is not None:
            self._client = client
        elif api_key:
            self._client = AsyncOpenAI(
                api_key=api_key,
                timeout=timeout,
                max_retries=0,  # We manage explicit, transparent retries in our layer
                base_url=base_url,
            )
        else:
            self._client = None
            self._api_key = None
            self._base_url = base_url

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def default_model(self) -> str:
        return self._default_model

    def _get_client(self) -> AsyncOpenAI:
        if self._client is not None:
            return self._client
        raise LLMConfigurationError(
            "OpenAI API key is missing. Please set SUTRA_OPENAI_API_KEY."
        )

    def _normalize_error(self, err: Exception) -> Exception:
        if isinstance(err, openai.AuthenticationError):
            return LLMAuthenticationError(
                "OpenAI authentication failed", details=str(err)
            )
        if isinstance(err, openai.BadRequestError):
            return LLMInvalidRequestError(
                "OpenAI rejected request as invalid", details=str(err)
            )
        if isinstance(err, openai.RateLimitError):
            return LLMRateLimitError("OpenAI rate limit exceeded", details=str(err))
        if isinstance(err, (openai.APITimeoutError, asyncio.TimeoutError)):
            return LLMTimeoutError("OpenAI request timed out", details=str(err))
        if isinstance(err, openai.InternalServerError):
            return LLMTransientError(
                "OpenAI transient internal server error", details=str(err)
            )
        if isinstance(err, openai.APIConnectionError):
            return LLMTransientError(
                "OpenAI network/connection error", details=str(err)
            )
        if isinstance(err, openai.APIError):
            return LLMUnexpectedError("OpenAI API error", details=str(err))
        return LLMUnexpectedError(
            f"Unexpected error during OpenAI generation: {type(err).__name__}",
            details=str(err),
        )

    def _is_retryable(self, err: Exception) -> bool:
        # Retry transient server errors, rate limits, timeouts, and network drops
        return isinstance(
            err,
            (
                openai.InternalServerError,
                openai.APIConnectionError,
                openai.RateLimitError,
                openai.APITimeoutError,
                asyncio.TimeoutError,
            ),
        )

    async def generate(self, request: LLMRequest) -> LLMResponse:
        client = self._get_client()
        model_name = request.model or self._default_model

        messages_payload: list[dict[str, str]] = [
            {"role": m.role.value, "content": m.content} for m in request.messages
        ]

        kwargs: dict[str, Any] = {
            "model": model_name,
            "messages": messages_payload,
            "timeout": self._timeout,
        }
        if request.temperature is not None:
            kwargs["temperature"] = request.temperature
        if request.max_tokens is not None:
            kwargs["max_tokens"] = request.max_tokens

        attempts = 0
        while True:
            try:
                raw_response = await client.chat.completions.create(**kwargs)
                break
            except Exception as err:
                attempts += 1
                if attempts <= self._max_retries and self._is_retryable(err):
                    logger.warning(
                        "Transient error contacting OpenAI (attempt %d/%d): %s",
                        attempts,
                        self._max_retries + 1,
                        type(err).__name__,
                    )
                    await asyncio.sleep(0.2 * attempts)
                    continue

                normalized = self._normalize_error(err)
                raise normalized from err

        choice = raw_response.choices[0]
        generated_text = choice.message.content or ""

        usage = LLMUsage()
        if raw_response.usage is not None:
            usage = LLMUsage(
                input_tokens=raw_response.usage.prompt_tokens,
                output_tokens=raw_response.usage.completion_tokens,
                total_tokens=raw_response.usage.total_tokens,
            )

        metadata: dict[str, Any] = {
            "finish_reason": choice.finish_reason,
            "system_fingerprint": getattr(raw_response, "system_fingerprint", None),
        }

        return LLMResponse(
            text=generated_text,
            model=raw_response.model or model_name,
            usage=usage,
            provider=self.provider_name,
            provider_metadata=metadata,
        )
