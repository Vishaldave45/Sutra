import pytest

from packages.agent_core.tools.errors import DuplicateTool, ToolNotFound
from packages.agent_core.tools.reference import (
    DeterministicFailureTool,
    DeterministicTimeoutTool,
    EchoTool,
)
from packages.agent_core.tools.registry import ToolRegistry


def test_registry_registration_and_get() -> None:
    registry = ToolRegistry()
    echo = EchoTool()
    registry.register(echo)

    assert registry.contains("echo_tool") is True
    assert registry.contains("unknown_tool") is False
    assert len(registry) == 1

    retrieved = registry.get("echo_tool")
    assert retrieved is echo


def test_registry_duplicate_registration_fails() -> None:
    registry = ToolRegistry()
    registry.register(EchoTool())

    with pytest.raises(DuplicateTool, match="already registered"):
        registry.register(EchoTool())


def test_registry_unknown_tool_resolution_fails() -> None:
    registry = ToolRegistry()

    with pytest.raises(ToolNotFound, match="not found in registry"):
        registry.get("non_existent_tool")


def test_registry_unregister() -> None:
    registry = ToolRegistry([EchoTool()])
    assert registry.contains("echo_tool") is True

    registry.unregister("echo_tool")
    assert registry.contains("echo_tool") is False
    assert len(registry) == 0

    with pytest.raises(ToolNotFound, match="Cannot unregister unknown tool"):
        registry.unregister("echo_tool")


def test_registry_listing_deterministic_sort() -> None:
    # Register in non-alphabetical order
    timeout_tool = DeterministicTimeoutTool()
    echo_tool = EchoTool()
    failure_tool = DeterministicFailureTool()

    registry = ToolRegistry([timeout_tool, echo_tool, failure_tool])

    tool_list = registry.list()
    tool_names = [t.name for t in tool_list]

    # Sorted alphabetically
    assert tool_names == ["echo_tool", "failure_tool", "timeout_tool"]
