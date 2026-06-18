from __future__ import annotations

from dataclasses import dataclass
from typing import Awaitable, Callable, Any

from .common import ToolResult
import mods.tool_router_mod as router_tools


ToolHandler = Callable[..., Awaitable[ToolResult] | ToolResult]


@dataclass
class MCPTool:
    name: str
    description: str
    parameters: dict[str, Any]
    handler: ToolHandler


_TOOLS: dict[str, MCPTool] = {}


def register_tool(name: str, description: str, parameters: dict[str, Any]):
    def decorator(handler: ToolHandler):
        _TOOLS[name] = MCPTool(
            name=name,
            description=description,
            parameters=parameters,
            handler=handler,
        )
        return handler

    return decorator


@register_tool(
    "ask_ai",
    "Send a user prompt to the configured AI API and return the assistant reply.",
    {"prompt": "string", "user_id": "string", "display_name": "string"},
)
async def _ask_ai(**kwargs) -> ToolResult:
    return await router_tools.handle_tool("ask_ai", **kwargs)


@register_tool(
    "forget",
    "Clear temporary memory for one user.",
    {"user_id": "string"},
)
def _forget(**kwargs) -> ToolResult:
    return router_tools._forget_tool(**kwargs)


@register_tool(
    "status",
    "Show bot provider, model, tool mode, memory mode, and usage mode.",
    {},
)
def _status(**_) -> ToolResult:
    result = router_tools._status_tool()
    result.message = result.message.replace("Tool mode: `router`", "Tool mode: `mcp_like`")
    return result


@register_tool(
    "usage",
    "Show token usage summary from the local usage log.",
    {"user_id": "string | optional"},
)
def _usage(**kwargs) -> ToolResult:
    return router_tools._usage_tool(**kwargs)


@register_tool(
    "privacy",
    "Show a short cloud API privacy notice.",
    {},
)
def _privacy(**_) -> ToolResult:
    return router_tools._privacy_tool()


async def handle_tool(tool_name: str, **kwargs) -> ToolResult:
    """MCP-like tool registry.

    This is not a full MCP server. It demonstrates the idea of registering tools
    with a name, description, parameter schema, and handler function.
    """
    tool = _TOOLS.get(tool_name)
    if tool is None:
        return ToolResult(False, f"Unknown MCP-like tool: {tool_name}")

    result = tool.handler(**kwargs)
    if hasattr(result, "__await__"):
        result = await result  # type: ignore[assignment]
    return result  # type: ignore[return-value]


def list_tools() -> list[dict[str, Any]]:
    return [
        {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters,
        }
        for tool in _TOOLS.values()
    ]
