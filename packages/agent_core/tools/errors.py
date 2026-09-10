"""Tool system error hierarchy."""

import re
from typing import Any

_SENSITIVE_PATTERNS = [
    re.compile(r"(?i)(bearer\s+)[A-Za-z0-9_\-\.]{8,}"),
    re.compile(r"(?i)(api[_-]?key\s*[:=]\s*['\"]?)[A-Za-z0-9_\-\.]{8,}['\"]?"),
    re.compile(r"(?i)(sk-[A-Za-z0-9_\-]{16,})"),
    re.compile(r"(?i)(authorization\s*[:=]\s*(?:basic\s+|bearer\s+)?)[^\s'\"]+"),
]


def sanitize_error_message(message: str) -> str:
    """Scrub sensitive credentials/tokens from error messages."""
    sanitized = message
    for pattern in _SENSITIVE_PATTERNS:
        sanitized = pattern.sub(r"\1[REDACTED]", sanitized)
    return sanitized


class ToolError(Exception):
    """Base exception for all tool system errors."""

    def __init__(self, message: str, details: Any = None) -> None:
        safe_message = sanitize_error_message(message)
        super().__init__(safe_message)
        self.message = safe_message
        self.details = details


class ToolDefinitionError(ToolError):
    """Raised when a tool definition or schema contract is invalid."""

    pass


class InvalidToolSchema(ToolDefinitionError):
    """Raised when an input or output schema definition is invalid."""

    pass


class DuplicateTool(ToolDefinitionError):
    """Raised when a tool with the same name is registered multiple times."""

    pass


class ToolNotFound(ToolError):
    """Raised when resolving an unregistered or unknown tool name."""

    pass


class InvalidToolInput(ToolError):
    """Raised when provided input fails validation against the tool's input schema."""

    pass


class ToolExecutionError(ToolError):
    """Raised when tool execution fails or produces invalid output."""

    pass


class ToolTimeoutError(ToolExecutionError):
    """Raised when tool execution exceeds the configured timeout."""

    pass
