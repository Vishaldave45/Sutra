from unittest.mock import AsyncMock, MagicMock

import openai
import pytest

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
from packages.agent_core.llm.mock import MockLLMProvider
from packages.agent_core.llm.models import (
    LLMMessage,
    LLMMessageRole,
    LLMRequest,
    LLMResponse,
    LLMUsage,
)
from packages.agent_core.llm.providers.openai import OpenAIProvider

# ---------------------------------------------------------------------------
# 1. Models and Validation Tests
# ---------------------------------------------------------------------------


def test_llm_message_validation() -> None:
    msg = LLMMessage(role=LLMMessageRole.user, content="Hello assistant")
    assert msg.role == LLMMessageRole.user
    assert msg.content == "Hello assistant"

    # Empty content rejected
    with pytest.raises(ValueError, match="cannot be empty"):
        LLMMessage(role=LLMMessageRole.user, content="")

    # Whitespace content rejected
    with pytest.raises(ValueError, match="cannot be empty"):
        LLMMessage(role=LLMMessageRole.user, content="   \t \n ")


def test_llm_request_validation() -> None:
    req = LLMRequest(
        messages=[LLMMessage(role=LLMMessageRole.user, content="Hi")],
        model="custom-model",
        temperature=0.7,
        max_tokens=100,
    )
    assert req.model == "custom-model"
    assert req.temperature == 0.7
    assert req.max_tokens == 100

    # Empty messages list rejected
    with pytest.raises(ValueError, match="at least one message"):
        LLMRequest(messages=[])


def test_llm_response_and_usage() -> None:
    usage = LLMUsage(input_tokens=12, output_tokens=8, total_tokens=20)
    resp = LLMResponse(
        text="Response text",
        model="gpt-4o-mini",
        usage=usage,
        provider="mock",
    )
    assert resp.text == "Response text"
    assert resp.usage.total_tokens == 20
    assert resp.provider == "mock"


# ---------------------------------------------------------------------------
# 2. Mock Provider Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_mock_llm_provider_behavior() -> None:
    mock_provider = MockLLMProvider(
        default_response="Simulated AI response",
        default_model="mock-v1",
    )
    assert isinstance(mock_provider, LLMProvider)
    assert mock_provider.provider_name == "mock"
    assert mock_provider.default_model == "mock-v1"

    req = LLMRequest(messages=[LLMMessage(role=LLMMessageRole.user, content="Hello")])
    res = await mock_provider.generate(req)
    assert res.text == "Simulated AI response"
    assert res.model == "mock-v1"
    assert res.provider == "mock"
    assert len(mock_provider.recorded_requests) == 1

    # Overridden response
    mock_provider.set_next_response("Second response")
    res2 = await mock_provider.generate(req)
    assert res2.text == "Second response"


@pytest.mark.asyncio
async def test_mock_llm_provider_failure_injection() -> None:
    mock_provider = MockLLMProvider()
    mock_provider.set_failure(LLMRateLimitError("Simulated rate limit"))

    req = LLMRequest(messages=[LLMMessage(role=LLMMessageRole.user, content="Test")])
    with pytest.raises(LLMRateLimitError, match="Simulated rate limit"):
        await mock_provider.generate(req)


# ---------------------------------------------------------------------------
# 3. OpenAI Provider Construction & Configuration
# ---------------------------------------------------------------------------


def test_openai_provider_construction_no_key_raises_on_generate() -> None:
    provider = OpenAIProvider(api_key=None, default_model="gpt-4o-mini")
    assert provider.provider_name == "openai"
    assert provider.default_model == "gpt-4o-mini"


@pytest.mark.asyncio
async def test_openai_provider_generate_without_key_raises_configuration_error() -> (
    None
):
    provider = OpenAIProvider(api_key=None)
    req = LLMRequest(messages=[LLMMessage(role=LLMMessageRole.user, content="Hi")])
    with pytest.raises(LLMConfigurationError, match="API key is missing"):
        await provider.generate(req)


# ---------------------------------------------------------------------------
# 4. OpenAI Provider Fakes / Error Normalization / Retries
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_openai_provider_successful_generate() -> None:
    fake_client = AsyncMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "OpenAI response text"
    mock_choice.finish_reason = "stop"

    mock_usage = MagicMock()
    mock_usage.prompt_tokens = 15
    mock_usage.completion_tokens = 25
    mock_usage.total_tokens = 40

    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]
    mock_completion.model = "gpt-4o-mini-2024-07-18"
    mock_completion.usage = mock_usage
    mock_completion.system_fingerprint = "fp_abc123"

    fake_client.chat.completions.create.return_value = mock_completion

    provider = OpenAIProvider(client=fake_client, default_model="gpt-4o-mini")
    req = LLMRequest(
        messages=[LLMMessage(role=LLMMessageRole.user, content="Say hi")],
        temperature=0.5,
        max_tokens=50,
    )
    response = await provider.generate(req)

    assert response.text == "OpenAI response text"
    assert response.model == "gpt-4o-mini-2024-07-18"
    assert response.provider == "openai"
    assert response.usage.input_tokens == 15
    assert response.usage.output_tokens == 25
    assert response.usage.total_tokens == 40
    assert response.provider_metadata["finish_reason"] == "stop"

    # Verify calls passed down to client
    fake_client.chat.completions.create.assert_called_once_with(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say hi"}],
        timeout=30.0,
        temperature=0.5,
        max_tokens=50,
    )


@pytest.mark.asyncio
async def test_openai_provider_authentication_error_normalization() -> None:
    fake_client = AsyncMock()
    fake_client.chat.completions.create.side_effect = openai.AuthenticationError(
        "Incorrect API key provided",
        response=MagicMock(status_code=401),
        body=None,
    )
    provider = OpenAIProvider(client=fake_client, max_retries=2)
    req = LLMRequest(messages=[LLMMessage(role=LLMMessageRole.user, content="Hi")])

    with pytest.raises(LLMAuthenticationError) as exc_info:
        await provider.generate(req)

    assert "authentication failed" in str(exc_info.value).lower()
    # Non-retryable error must not be retried
    assert fake_client.chat.completions.create.call_count == 1


@pytest.mark.asyncio
async def test_openai_provider_invalid_request_error_normalization() -> None:
    fake_client = AsyncMock()
    fake_client.chat.completions.create.side_effect = openai.BadRequestError(
        "Model not found",
        response=MagicMock(status_code=400),
        body=None,
    )
    provider = OpenAIProvider(client=fake_client, max_retries=2)
    req = LLMRequest(messages=[LLMMessage(role=LLMMessageRole.user, content="Hi")])

    with pytest.raises(LLMInvalidRequestError):
        await provider.generate(req)

    # Non-retryable
    assert fake_client.chat.completions.create.call_count == 1


@pytest.mark.asyncio
async def test_openai_provider_transient_retry_and_success() -> None:
    fake_client = AsyncMock()

    mock_choice = MagicMock()
    mock_choice.message.content = "Success after retry"
    mock_choice.finish_reason = "stop"
    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]
    mock_completion.model = "gpt-4o-mini"
    mock_completion.usage = None

    # First call fails with transient InternalServerError, second succeeds
    fake_client.chat.completions.create.side_effect = [
        openai.InternalServerError(
            "Server error", response=MagicMock(status_code=500), body=None
        ),
        mock_completion,
    ]

    provider = OpenAIProvider(client=fake_client, max_retries=2)
    req = LLMRequest(messages=[LLMMessage(role=LLMMessageRole.user, content="Hi")])
    res = await provider.generate(req)

    assert res.text == "Success after retry"
    assert fake_client.chat.completions.create.call_count == 2


@pytest.mark.asyncio
async def test_openai_provider_transient_retry_exhaustion_raises_normalized_error() -> (
    None
):
    fake_client = AsyncMock()
    fake_client.chat.completions.create.side_effect = openai.InternalServerError(
        "500 Internal error",
        response=MagicMock(status_code=500),
        body=None,
    )

    provider = OpenAIProvider(client=fake_client, max_retries=1)
    req = LLMRequest(messages=[LLMMessage(role=LLMMessageRole.user, content="Hi")])

    with pytest.raises(LLMTransientError):
        await provider.generate(req)

    # 1 initial attempt + 1 retry = 2 calls
    assert fake_client.chat.completions.create.call_count == 2


@pytest.mark.asyncio
async def test_openai_provider_timeout_error_normalization() -> None:
    fake_client = AsyncMock()
    fake_client.chat.completions.create.side_effect = openai.APITimeoutError(
        request=MagicMock()
    )

    provider = OpenAIProvider(client=fake_client, max_retries=0)
    req = LLMRequest(messages=[LLMMessage(role=LLMMessageRole.user, content="Hi")])

    with pytest.raises(LLMTimeoutError):
        await provider.generate(req)


@pytest.mark.asyncio
async def test_openai_provider_rate_limit_normalization() -> None:
    fake_client = AsyncMock()
    fake_client.chat.completions.create.side_effect = openai.RateLimitError(
        "Rate limit reached",
        response=MagicMock(status_code=429),
        body=None,
    )

    provider = OpenAIProvider(client=fake_client, max_retries=0)
    req = LLMRequest(messages=[LLMMessage(role=LLMMessageRole.user, content="Hi")])

    with pytest.raises(LLMRateLimitError):
        await provider.generate(req)


@pytest.mark.asyncio
async def test_openai_provider_unexpected_error_normalization() -> None:
    fake_client = AsyncMock()
    fake_client.chat.completions.create.side_effect = RuntimeError("Unknown error")

    provider = OpenAIProvider(client=fake_client, max_retries=0)
    req = LLMRequest(messages=[LLMMessage(role=LLMMessageRole.user, content="Hi")])

    with pytest.raises(LLMUnexpectedError):
        await provider.generate(req)
