# 模式说明：Router 与 MCP-like 工具架构

> 翻译说明：本文件由繁体中文版本经 AI 辅助翻译而来。  
> 如果其他语言版本与繁体中文版本在语义上有所差异，请以繁体中文版本为准。

这份文件说明本项目中的两种工具调用模式，并详细说明各模式的指令流程、工具注册原理，以及本项目为了支持这个架构所做的程序拆分。

本项目支持两种模式：

```env
TOOL_MODE=router
```

使用传统解耦工具路由。

```env
TOOL_MODE=mcp_like
```

使用 MCP-like 工具注册展示模式。

两种模式提供的 Discord 指令大致相同，但内部的工具组织方式不同。

## 目录

* [前言](#前言)
* [Discord 指令流程](#discord-指令流程)
* [Discord 指令与工具名称对应](#discord-指令与工具名称对应)
* [Router 模式的基本概念](#router-模式的基本概念)
* [Router 模式如何调用工具](#router-模式如何调用工具)
* [Router 模式的优点与限制](#router-模式的优点与限制)
* [MCP-like 模式的基本概念](#mcp-like-模式的基本概念)
* [MCP-like 工具注册原理](#mcp-like-工具注册原理)
* [`register_tool()` 做了什么](#register_tool-做了什么)
* [MCP-like 模式如何调用工具](#mcp-like-模式如何调用工具)
* [为什么 MCP-like 模式仍共用 router 的功能逻辑](#为什么-mcp-like-模式仍共用-router-的功能逻辑)
* [总结](#总结)
* [小语](#小语)
* [参考资料](#参考资料)

## 前言

简单来说，可以把两种模式想成两种不同的工具整理方式。

`router` 模式比较像一把多功能瑞士刀。  
它简单、直接、资源开销较小，适合小型项目快速分派功能；但当工具越来越多时，内部条件判断可能会逐渐变得臃肿，后续就需要更好的分类与整理方式。

`mcp_like` 模式比较像一个整理好的工具箱。  
每个工具都有自己的名称、描述与处理函数，结构比较清楚，也比较接近 tool-calling 的概念；但如果未来真的将大量工具描述或参数 schema 提供给 AI 使用，就可能增加 prompt 或 token 使用量。

> 注意：本项目中的 `mcp_like` 是高度简化的展示版本，并没有实现完整 MCP protocol，也没有让 AI 自主选择工具。

---

## Discord 指令流程

使用者在 Discord 中输入 slash command，例如：

```text
/ai
/status
/usage
/privacy
/forget
```

这些指令会先由 `main.py` 接收。

`main.py` 本身不直接处理所有功能，而是把请求交给目前选定的工具模块。

在 `main.py` 中，会根据 `.env` 的设置决定要使用哪个工具模块：

```python
if config.TOOL_MODE == "mcp_like":
    from mods.mcp_like_mod import handle_tool
else:
    from mods.tool_router_mod import handle_tool
```

因此，不管目前使用的是 `router` 模式还是 `mcp_like` 模式，`main.py` 都只需要调用同一个函数：

```python
result = await handle_tool(...)
```

这样可以让 `main.py` 保持干净，专注在 Discord Bot 的启动、指令注册与交互回复。

---

## Discord 指令与工具名称对应

本项目中的 slash commands 会对应到内部工具名称。

| Discord 指令 | 内部工具名称 | 功能 |
| ---------- | --------- | ------------------- |
| `/ai` | `ask_ai` | 将使用者输入传给 AI API 并回复 |
| `/forget` | `forget` | 清除使用者的临时记忆 |
| `/status` | `status` | 显示 Bot 目前设置与架构模式 |
| `/usage` | `usage` | 显示 token 使用量统计 |
| `/privacy` | `privacy` | 显示云端 API 隐私提醒 |

例如 `/ai` 指令会调用：

```python
handle_tool(
    "ask_ai",
    prompt=prompt,
    user_id=str(interaction.user.id),
    display_name=interaction.user.display_name,
)
```

`main.py` 不需要知道 `ask_ai` 里面实际怎么调用 API，只要把请求交给工具层处理即可。

---

## Router 模式的基本概念

`tool_router_mod.py` 是传统的解耦工具路由模式。

它的做法是：  
`main.py` 把工具名称传进 `handle_tool()`，然后 router 用条件判断决定要执行哪个功能。

简化概念如下：

```python
async def handle_tool(tool_name: str, **kwargs):
    if tool_name == "ask_ai":
        return await _ask_ai_tool(**kwargs)
    if tool_name == "forget":
        return _forget_tool(**kwargs)
    if tool_name == "status":
        return _status_tool()
```

这种方式很直观，也很适合小型项目。

它的优点是容易理解、容易修改。  
缺点是当工具越来越多时，router 里可能会累积很多 `if` 判断，后续需要更好的分类方式。

---

## Router 模式如何调用工具

在 `router` 模式中，所有工具请求都会先进入 `tool_router_mod.py` 的 `handle_tool()`。

`main.py` 只需要把工具名称与需要的参数传进去：

```python
result = await handle_tool(
    "ask_ai",
    prompt=prompt,
    user_id=str(interaction.user.id),
    display_name=interaction.user.display_name,
)
```

接着 `tool_router_mod.py` 会根据 `tool_name` 判断要执行哪个功能。

简化流程如下：

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

也就是说，router 模式比较像一个「功能分派中心」。

它不会把每个工具整理成独立的注册项目，而是用条件判断的方式，把不同工具名称导向不同处理函数。

这些工具最后都会返回统一的 `ToolResult`。

## Router 模式的优点与限制

Router 模式的优点是简单、直观，也很适合小型项目。

它的流程大致是：

```text
Discord command
↓
main.py
↓
handle_tool(tool_name, ...)
↓
if tool_name == ...
↓
对应工具函数
↓
ToolResult
↓
Discord response
```

这种方式很容易理解，也不需要额外的工具注册表或 schema 设计。

不过，当工具数量增加时，`handle_tool()` 里面的条件判断可能会越来越多，router 本身就可能变得比较臃肿。

因此 router 模式适合：

* 小型项目
* 工具数量不多的情况
* 想快速完成工具分派的情况
* 想让程序流程简单易懂的情况

如果未来工具变多，或希望每个工具都有更清楚的名称、描述与参数格式，就可以考虑改成 MCP-like 工具注册架构。

## MCP-like 模式的基本概念

`mcp_like_mod.py` 展示的是一个小型 MCP-like 工具注册架构。

这里的 MCP-like 并不是正式 MCP server，也没有完整实现 MCP protocol。

本项目只是用简单的方式展示以下概念：

* 工具可以被注册
* 工具可以有名称
* 工具可以有描述
* 工具可以有参数说明
* 工具可以通过统一格式被调用

也就是说，工具不只是单纯写在 `if` 判断里，而是被整理成一个一个「工具项目」。

---

## MCP-like 工具注册原理

在 `mcp_like_mod.py` 中，每个工具会被包装成 `MCPTool`。

```python
@dataclass
class MCPTool:
    name: str
    description: str
    parameters: dict[str, Any]
    handler: ToolHandler
```

每个工具包含：

| 字段 | 作用 |
| ------------- | ---------------- |
| `name` | 工具名称，例如 `ask_ai` |
| `description` | 工具用途描述 |
| `parameters` | 工具需要的参数说明 |
| `handler` | 实际执行功能的函数 |

工具会被存放在 `_TOOLS` 字典中：

```python
_TOOLS: dict[str, MCPTool] = {}
```

这个 `_TOOLS` 可以理解成一个简单的工具注册表。

---

## `register_tool()` 做了什么

`register_tool()` 是一个 decorator，用来注册工具。

简化概念如下：

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

使用方式如下：

```python
@register_tool(
    "ask_ai",
    "Send a user prompt to the configured AI API and return the assistant reply.",
    {"prompt": "string", "user_id": "string", "display_name": "string"},
)
async def _ask_ai(**kwargs):
    return await router_tools.handle_tool("ask_ai", **kwargs)
```

这段的意思是：

1. 建立一个名称为 `ask_ai` 的工具
2. 加上工具描述
3. 加上参数格式说明
4. 指定 `_ask_ai()` 作为实际执行的 handler
5. 将这个工具放进 `_TOOLS` 注册表

之后只要调用：

```python
handle_tool("ask_ai", ...)
```

程序就会到 `_TOOLS` 里找到 `ask_ai`，再执行它对应的 handler function。

---

## MCP-like 模式如何调用工具

`mcp_like_mod.py` 中的 `handle_tool()` 会做三件事：

1. 根据工具名称查找工具
2. 执行该工具的 handler
3. 如果 handler 是 async，就等待它完成

简化流程如下：

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

因此 MCP-like 模式的概念流程是：

```text
Discord command
↓
main.py
↓
mcp_like_mod.py
↓
_TOOLS 工具注册表
↓
registered tool handler
↓
ai_client.py / usage_tracker.py / memory
↓
Discord response
```

## 为什么 MCP-like 模式仍然共用底层功能逻辑

简答：因为两种模式的核心功能目标相同，差别主要在于“工具如何被组织与调用”。

在本项目中，`router` 模式与 `mcp_like` 模式提供的用户功能基本一致，例如 AI 回复、状态查询、usage 统计、隐私说明与临时记忆管理。

也就是说，两种模式要完成的事情是相同的。
真正不同的地方在于工具处理结构：

```text
router 模式：
使用传统集中式路由判断工具名称，并分派到对应功能。

mcp_like 模式：
把工具整理成名称、描述、参数信息与 handler function 的注册表，再通过统一入口调用工具。
```

因此，`mcp_like_mod.py` 并没有重新写一整套 AI、usage、memory 或其他功能处理逻辑，而是共用已经整理好的底层功能。

这样做不只是为了简化。
它也能让比较焦点更清楚：

* 两种模式使用相同的底层工具能力
* 两种模式的用户功能结果尽量保持一致
* 比较时能专注在“路由方式”与“工具注册方式”的差异
* 避免因为重复实现造成两边功能行为不一致
* 让 `mcp_like_mod.py` 专注展示工具注册层，而不是重新实现整个 bot

换句话说，本项目想比较的不是“两套不同功能的 bot”，而是：

```text
同一组工具能力
在不同工具组织方式下
程序结构会有什么差异
```

所以这个版本的 `mcp_like` 更像是加在工具层上的“注册展示层”。
它让工具可以被整理成类似 MCP / tool-calling 思路中的结构，但仍然共用相同的底层功能处理逻辑。

本项目的 `mcp_like` 模式没有实现：

* MCP client/server 通信
* MCP protocol message format
* 外部工具 discovery
* 完整 schema 验证
* 真正由 AI 自主选择工具
* AI 自主生成工具参数
* 权限管理或工具执行沙盒

因此，它更准确地说是：

```text
MCP-like tool registry demo
```

而不是：

```text
Full MCP implementation
```

这样设计可以让项目保持小型、易读，同时更容易观察传统 router 与 MCP-like tool registry 在程序结构上的差异。

---

## 总结

本项目的 MCP-like 模式主要展示了「工具注册」与「工具调用」的概念。

它通过 `MCPTool`、`register_tool()`、`_TOOLS` 与 `handle_tool()`，让工具可以被整理成一个个具有名称、描述、参数与处理函数的项目。

虽然它不是完整 MCP protocol，但它能够展示 tool-calling 架构的基本雏形。

这让项目在保持轻量的同时，也能说明：

* Discord 指令如何进入工具层
* 工具如何被注册
* 工具如何被调用
* API、usage、memory 如何被拆成独立模块
* 传统 router 与 MCP-like 架构的差异

## 小语

MCP-style 架构的优点是清楚、规整，而且每个工具都能被明确描述；但如果工具描述、参数 schema 与上下文全部交给 AI 使用，也可能带来较高的 token 与资源消耗。

Router 架构则比较简单直接，对小型项目来说更轻量，也比较容易快速实现。不过当工具越来越多时，router 内部也可能变得臃肿，需要进一步整理。

因此这两种方式不一定是谁取代谁，而是适合不同规模与不同需求的项目。  
对这个 Lite Bot 来说，重点不是做出完整 MCP 系统，而是用小型范例理解「传统解耦」与「工具注册」两种思路的差别。

> 感谢一路看到这里的你 :D

## 参考资料

以下链接是本项目在理解 MCP-like 工具注册、tool-calling、router 与解耦架构时参考的概念资料。  
本项目的 `mcp_like` 模式只是简化展示，并不是完整 MCP protocol 实作。

### MCP / Tool-calling

* Model Context Protocol Introduction: https://modelcontextprotocol.io/docs/getting-started/intro
* MCP Tools Specification: https://modelcontextprotocol.io/specification/2025-06-18/server/tools
* OpenAI Function Calling Guide: https://developers.openai.com/api/docs/guides/function-calling

### Router / 解耦架构

* Command Pattern: https://refactoring.guru/design-patterns/command
* Chain of Responsibility Pattern: https://refactoring.guru/design-patterns/chain-of-responsibility
* Strategy Pattern: https://refactoring.guru/design-patterns/strategy
* Refactoring: https://refactoring.com/

以上链接仅作为学习与开发参考。  
实际使用 MCP、tool-calling、云端 API 或自动化工具时，仍需要自行确认相关文件、服务条款、安全限制与资料处理方式。
