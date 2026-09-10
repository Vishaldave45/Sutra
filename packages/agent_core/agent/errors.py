"""Agent Runtime error hierarchy."""

from typing import Any


class AgentError(Exception):
    """Base exception for agent runtime errors."""

    def __init__(self, message: str, details: Any = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class AgentInputError(AgentError):
    """Raised when input validation fails prior to execution."""

    pass


class AgentConfigurationError(AgentError):
    """Raised when runtime configuration is invalid prior to execution."""

    pass
