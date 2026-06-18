# Mode Overview: Router and MCP-like Tool Architecture

> Translation note: This document was translated from the Traditional Chinese version with AI assistance.  
> If there is any difference in meaning, the Traditional Chinese version should be treated as the primary reference.

This document explains the two tool-calling modes in this project. It also describes each mode's command flow, tool registration concept, and how the code was split to support this architecture.

This project supports two modes:

```env
TOOL_MODE=router
```

Use the traditional decoupled tool router.

```env
TOOL_MODE=mcp_like
```

Use the MCP-like tool registry demo mode.

Both modes provide roughly the same Discord commands, but their internal tool organization is different.

## Table of Contents

* [Introduction](#introduction)
* [Discord Command Flow](#discord-command-flow)
* [Discord Commands and Internal Tool Names](#discord-commands-and-internal-tool-names)
* [Basic Concept of Router Mode](#basic-concept-of-router-mode)
* [How Router Mode Calls Tools](#how-router-mode-calls-tools)
* [Advantages and Limitations of Router Mode](#advantages-and-limitations-of-router-mode)
* [Basic Concept of MCP-like Mode](#basic-concept-of-mcp-like-mode)
* [MCP-like Tool Registration Concept](#mcp-like-tool-registration-concept)
* [What `register_tool()` Does](#what-register_tool-does)
* [How MCP-like Mode Calls Tools](#how-mcp-like-mode-calls-tools)
* [Why MCP-like Mode Still Reuses Router Logic](#why-mcp-like-mode-still-reuses-router-logic)
* [Summary](#summary)
* [Closing Note](#closing-note)
* [References](#references)

## Introduction

Simply put, the two modes can be understood as two different ways of organizing tools.

`router` mode is like a multi-purpose Swiss army knife.  
It is simple, direct, and has relatively low overhead, making it suitable for quickly dispatching features in small projects. However, when the number of tools increases, the internal condition checks can gradually become bulky, and better classification or organization may be needed later.

`mcp_like` mode is more like a well-organized toolbox.  
Each tool has its own name, description, and handler function. The structure is clearer and closer to the idea of tool-calling. However, if a large number of tool descriptions or parameter schemas are provided to the AI in the future, the prompt or token usage may increase.

> Note: The `mcp_like` mode in this project is a highly simplified demo version. It does not implement the full MCP protocol and does not let the AI autonomously choose tools.

---

## Discord Command Flow

Users enter slash commands in Discord, such as:

```text
/ai
/status
/usage
/privacy
/forget
```

These commands are first received by `main.py`.

`main.py` does not directly handle all features. Instead, it passes the request to the currently selected tool module.

In `main.py`, the tool module is selected based on the `.env` setting:

```python
if config.TOOL_MODE == "mcp_like":
    from mods.mcp_like_mod import handle_tool
else:
    from mods.tool_router_mod import handle_tool
```

Therefore, whether the current mode is `router` or `mcp_like`, `main.py` only needs to call the same function:

```python
result = await handle_tool(...)
```

This keeps `main.py` clean and focused on starting the Discord Bot, registering commands, and responding to interactions.

---

## Discord Commands and Internal Tool Names

The slash commands in this project correspond to internal tool names.

| Discord command | Internal tool name | Function |
| ---------- | --------- | ------------------- |
| `/ai` | `ask_ai` | Send user input to the AI API and return a reply |
| `/forget` | `forget` | Clear the user's temporary memory |
| `/status` | `status` | Show the bot's current settings and architecture mode |
| `/usage` | `usage` | Show token usage statistics |
| `/privacy` | `privacy` | Show a cloud API privacy notice |

For example, the `/ai` command calls:

```python
handle_tool(
    "ask_ai",
    prompt=prompt,
    user_id=str(interaction.user.id),
    display_name=interaction.user.display_name,
)
```

`main.py` does not need to know how `ask_ai` actually calls the API. It only needs to pass the request to the tool layer.

---

## Basic Concept of Router Mode

`tool_router_mod.py` is the traditional decoupled tool router mode.

Its approach is:  
`main.py` passes the tool name into `handle_tool()`, and the router uses conditional checks to decide which function to execute.

A simplified example:

```python
async def handle_tool(tool_name: str, **kwargs):
    if tool_name == "ask_ai":
        return await _ask_ai_tool(**kwargs)
    if tool_name == "forget":
        return _forget_tool(**kwargs)
    if tool_name == "status":
        return _status_tool()
```

This approach is intuitive and suitable for small projects.

Its advantages are that it is easy to understand and easy to modify.  
Its limitation is that when the number of tools increases, the router may accumulate many `if` checks, so better classification may be needed later.

---

## How Router Mode Calls Tools

In `router` mode, all tool requests first enter `handle_tool()` in `tool_router_mod.py`.

`main.py` only needs to pass in the tool name and the required parameters:

```python
result = await handle_tool(
    "ask_ai",
    prompt=prompt,
    user_id=str(interaction.user.id),
    display_name=interaction.user.display_name,
)
```

Then `tool_router_mod.py` decides what to execute based on `tool_name`.

Simplified flow:

```python
async def handle_tool(tool_name: str, **kwargs):
    if tool_name == "ask_ai":
        return await _ask_ai_tool(**kwargs)

    if tool_name == "forget":
        return _forget_tool(**kwargs)

    if tool_name == "status":
        return _status_tool()

    if tool_name == "usage":
        return _usage_tool()

    if tool_name == "privacy":
        return _privacy_tool()

    return ToolResult(False, f"Unknown tool: {tool_name}")
```

In other words, router mode acts like a feature dispatch center.

It does not organize every tool as an independent registered item. Instead, it uses conditional checks to direct different tool names to different handler functions.

These tools eventually return a unified `ToolResult`.

## Advantages and Limitations of Router Mode

The advantage of router mode is that it is simple, intuitive, and suitable for small projects.

Its flow is roughly:

```text
Discord command
↓
main.py
↓
handle_tool(tool_name, ...)
↓
if tool_name == ...
↓
corresponding tool function
↓
ToolResult
↓
Discord response
```

This approach is easy to understand and does not require an additional tool registry or schema design.

However, as the number of tools increases, the conditional checks inside `handle_tool()` may also increase, and the router itself may become bulky.

Therefore, router mode is suitable for:

* Small projects
* Cases with only a small number of tools
* Situations where fast feature dispatch is needed
* Projects that prioritize simple and readable control flow

If the number of tools grows, or if each tool needs a clearer name, description, and parameter format, then an MCP-like tool registry architecture can be considered.

## Basic Concept of MCP-like Mode

`mcp_like_mod.py` demonstrates a small MCP-like tool registry architecture.

The MCP-like mode here is not an official MCP server and does not implement the full MCP protocol.

This project only uses a simple approach to demonstrate these concepts:

* Tools can be registered
* Tools can have names
* Tools can have descriptions
* Tools can have parameter descriptions
* Tools can be called through a unified format

In other words, tools are not only written inside `if` statements. They are organized as individual "tool items."

---

## MCP-like Tool Registration Concept

In `mcp_like_mod.py`, each tool is wrapped as an `MCPTool`.

```python
@dataclass
class MCPTool:
    name: str
    description: str
    parameters: dict[str, Any]
    handler: ToolHandler
```

Each tool contains:

| Field | Purpose |
| ------------- | ---------------- |
| `name` | Tool name, such as `ask_ai` |
| `description` | Description of what the tool does |
| `parameters` | Description of the parameters needed by the tool |
| `handler` | The function that actually executes the feature |

Tools are stored in the `_TOOLS` dictionary:

```python
_TOOLS: dict[str, MCPTool] = {}
```

This `_TOOLS` dictionary can be understood as a simple tool registry.

---

## What `register_tool()` Does

`register_tool()` is a decorator used to register tools.

Simplified concept:

```python
def register_tool(name, description, parameters):
    def decorator(handler):
        _TOOLS[name] = MCPTool(
            name=name,
            description=description,
            parameters=parameters,
            handler=handler,
        )
        return handler

    return decorator
```

Usage example:

```python
@register_tool(
    "ask_ai",
    "Send a user prompt to the configured AI API and return the assistant reply.",
    {"prompt": "string", "user_id": "string", "display_name": "string"},
)
async def _ask_ai(**kwargs):
    return await router_tools.handle_tool("ask_ai", **kwargs)
```

This means:

1. Create a tool named `ask_ai`
2. Add a tool description
3. Add a parameter format description
4. Use `_ask_ai()` as the actual handler
5. Put this tool into the `_TOOLS` registry

After that, when calling:

```python
handle_tool("ask_ai", ...)
```

The program will find `ask_ai` inside `_TOOLS` and execute its corresponding handler function.

---

## How MCP-like Mode Calls Tools

In `mcp_like_mod.py`, `handle_tool()` does three things:

1. Find the tool by tool name
2. Execute the tool's handler
3. If the handler is async, wait for it to finish

Simplified flow:

```python
async def handle_tool(tool_name: str, **kwargs):
    tool = _TOOLS.get(tool_name)

    if tool is None:
        return ToolResult(False, f"Unknown MCP-like tool: {tool_name}")

    result = tool.handler(**kwargs)

    if hasattr(result, "__await__"):
        result = await result

    return result
```

So the concept flow of MCP-like mode is:

```text
Discord command
↓
main.py
↓
mcp_like_mod.py
↓
_TOOLS tool registry
↓
registered tool handler
↓
ai_client.py / usage_tracker.py / memory
↓
Discord response
```

## Why MCP-like Mode Still Reuses Router Logic

> Short answer: to keep the project lightweight and focused on the core concept.

In this project, `mcp_like_mod.py` is mainly used to demonstrate the concepts of tool registration and tool calling.

To keep the project lightweight, `mcp_like` mode does not rewrite a full set of AI, usage, and memory handling logic. Instead, it reuses the already organized functionality from router mode as much as possible.

The benefits are:

* Avoiding duplicate implementation of the same features
* Keeping the user-facing features consistent between the two modes
* Letting `mcp_like_mod.py` focus on demonstrating the tool registry architecture
* Keeping the project small, readable, and easy to compare

In other words, this version of `mcp_like` is more like a registration demo layer added on top of the tool layer, not a standalone MCP system that fully replaces all lower-level functionality.

It does not implement:

* MCP client/server communication
* MCP protocol message format
* External tool discovery
* Full schema validation
* True AI-driven autonomous tool selection

Currently, it only demonstrates the idea of a "tool registry" in a lightweight way.

That means it is closer to:

```text
MCP-like tool registry demo
```

rather than:

```text
Full MCP implementation
```

The reason for this design is that the main goal of this project is to stay simple, readable, and easy to demonstrate, rather than implementing a full MCP system.

---

## Summary

The MCP-like mode in this project mainly demonstrates the concepts of tool registration and tool calling.

Through `MCPTool`, `register_tool()`, `_TOOLS`, and `handle_tool()`, tools can be organized into items with names, descriptions, parameters, and handler functions.

Although it is not a full MCP protocol implementation, it can demonstrate the basic shape of a tool-calling architecture.

This allows the project to remain lightweight while explaining:

* How Discord commands enter the tool layer
* How tools are registered
* How tools are called
* How API, usage, and memory are split into independent modules
* The differences between traditional router architecture and MCP-like architecture

## Closing Note

MCP-style architecture has the advantage of being clear and structured, and each tool can be explicitly described. However, if all tool descriptions, parameter schemas, and context are provided to the AI, it may also result in higher token and resource consumption.

Router architecture is simpler and more direct. For small projects, it is lighter and easier to implement quickly. However, when the number of tools grows, the router itself may also become bulky and require further organization.

Therefore, these two approaches do not necessarily replace each other. They are suitable for projects of different sizes and needs.  
For this Lite Bot, the goal is not to build a full MCP system, but to use a small example to understand the difference between "traditional decoupling" and "tool registration."

> Thanks for reading this far :D

## References

The following links were used as conceptual references for understanding MCP-like tool registration, tool-calling, router logic, and decoupled architecture in this project.  
The `mcp_like` mode in this project is only a simplified demo and is not a full MCP protocol implementation.

### MCP / Tool-calling

* Model Context Protocol Introduction: https://modelcontextprotocol.io/docs/getting-started/intro
* MCP Tools Specification: https://modelcontextprotocol.io/specification/2025-06-18/server/tools
* OpenAI Function Calling Guide: https://developers.openai.com/api/docs/guides/function-calling

### Router / Decoupled architecture

* Command Pattern: https://refactoring.guru/design-patterns/command
* Chain of Responsibility Pattern: https://refactoring.guru/design-patterns/chain-of-responsibility
* Strategy Pattern: https://refactoring.guru/design-patterns/strategy
* Refactoring: https://refactoring.com/

These links are for learning and development reference only.  
When actually using MCP, tool-calling, cloud APIs, or automation tools, users still need to check the relevant documentation, terms of service, safety restrictions, and data handling policies.
