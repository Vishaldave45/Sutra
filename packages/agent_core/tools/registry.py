"""Tool registry for isolated, deterministic tool storage and resolution."""

from collections.abc import Iterable

from packages.agent_core.tools.errors import DuplicateTool, ToolNotFound
from packages.agent_core.tools.interface import Tool


class ToolRegistry:
    """In-memory tool registry.

    Owns registration and resolution. Does NOT execute tools, perform authorization,
    or depend on global state or database persistence.
    """

    def __init__(self, tools: Iterable[Tool] | None = None) -> None:
        self._tools: dict[str, Tool] = {}
        if tools:
            for tool in tools:
                self.register(tool)

    def register(self, tool: Tool) -> None:
        """Register a tool. Fails deterministically if name already registered."""
        name = tool.name
        if name in self._tools:
            raise DuplicateTool(f"Tool with name '{name}' is already registered")
        self._tools[name] = tool

    def unregister(self, name: str) -> None:
        """Unregister a tool by name. Raises ToolNotFound if missing."""
        if name not in self._tools:
            raise ToolNotFound(f"Cannot unregister unknown tool '{name}'")
        del self._tools[name]

    def get(self, name: str) -> Tool:
        """Retrieve a tool by name. Raises ToolNotFound if not found."""
        if name not in self._tools:
            raise ToolNotFound(f"Tool '{name}' not found in registry")
        return self._tools[name]

    def contains(self, name: str) -> bool:
        """Check if a tool is registered."""
        return name in self._tools

    def list(self) -> list[Tool]:
        """Return all registered tools sorted deterministically by tool name."""
        return [self._tools[k] for k in sorted(self._tools.keys())]

    def __len__(self) -> int:
        return len(self._tools)
