"""Tool abstraction and base class."""

from abc import ABC, abstractmethod

from pydantic import BaseModel

from packages.agent_core.tools.errors import ToolDefinitionError
from packages.agent_core.tools.models import (
    ToolDefinition,
    ToolRetryPolicy,
    ToolRiskLevel,
)


class Tool(ABC):
    """Abstract base class for all tools."""

    name: str = ""
    description: str = ""
    input_model: type[BaseModel]
    output_model: type[BaseModel]
    risk_level: ToolRiskLevel = ToolRiskLevel.READ
    permission: list[str] = []
    timeout: float = 30.0
    retry_policy: ToolRetryPolicy | None = None
    idempotent: bool = False

    def __init__(self) -> None:
        self._validate_contract()

    def _validate_contract(self) -> None:
        if not self.name or not self.name.strip():
            msg = f"Tool {type(self).__name__} must define a non-empty 'name'"
            raise ToolDefinitionError(msg)
        if not self.description or not self.description.strip():
            msg = f"Tool {self.name} must define a non-empty 'description'"
            raise ToolDefinitionError(msg)

        input_cls = getattr(self, "input_model", None)
        output_cls = getattr(self, "output_model", None)

        if input_cls is None or not (
            isinstance(input_cls, type) and issubclass(input_cls, BaseModel)
        ):
            msg = f"Tool {self.name} must specify a Pydantic 'input_model'"
            raise ToolDefinitionError(msg)

        if output_cls is None or not (
            isinstance(output_cls, type) and issubclass(output_cls, BaseModel)
        ):
            msg = f"Tool {self.name} must specify a Pydantic 'output_model'"
            raise ToolDefinitionError(msg)

    @property
    def definition(self) -> ToolDefinition:
        """Generate canonical strongly typed ToolDefinition with JSON Schema."""
        return ToolDefinition(
            name=self.name,
            description=self.description,
            input_schema=self.input_model.model_json_schema(),
            output_schema=self.output_model.model_json_schema(),
            risk_level=self.risk_level,
            permission=list(self.permission),
            timeout=self.timeout,
            retry_policy=self.retry_policy or ToolRetryPolicy(),
            idempotent=self.idempotent,
        )

    @abstractmethod
    async def execute(self, input_data: BaseModel) -> BaseModel:
        """Execute tool-specific logic.

        Must NOT implement timeout handling; timeout is enforced centrally
        by ToolExecutor.
        """
        pass
