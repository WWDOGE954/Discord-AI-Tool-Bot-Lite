# 模式說明：Router 與 MCP-like 工具架構

這份文件說明本專案中的兩種工具調用模式，並詳細說明各模式的指令流程、工具註冊原理，以及本專案為了支援這個架構所做的程式拆分。

本專案支援兩種模式：

```env
TOOL_MODE=router
```

使用傳統解耦工具路由。

```env
TOOL_MODE=mcp_like
```

使用 MCP-like 工具註冊展示模式。

兩種模式提供的 Discord 指令大致相同，但內部的工具組織方式不同。

## 目錄

* [前言](#前言)
* [Discord 指令流程](#discord-指令流程)
* [Discord 指令與工具名稱對應](#discord-指令與工具名稱對應)
* [Router 模式的基本概念](#router-模式的基本概念)
* [Router 模式如何呼叫工具](#router-模式如何呼叫工具)
* [Router 模式的優點與限制](#router-模式的優點與限制)
* [MCP-like 模式的基本概念](#mcp-like-模式的基本概念)
* [MCP-like 工具註冊原理](#mcp-like-工具註冊原理)
* [`register_tool()` 做了什麼](#register_tool-做了什麼)
* [MCP-like 模式如何呼叫工具](#mcp-like-模式如何呼叫工具)
* [為什麼 MCP-like 模式仍共用 router 的功能邏輯](#為什麼-mcp-like-模式仍共用-router-的功能邏輯)
* [總結](#總結)
* [小語](#小語)


## 前言

簡單來說，可以把兩種模式想成兩種不同的工具整理方式。

`router` 模式比較像一把多功能瑞士刀。
它簡單、直接、資源開銷較小，適合小型專案快速分派功能；但當工具越來越多時，內部條件判斷可能會逐漸變得臃腫，後續就需要更好的分類與整理方式。

`mcp_like` 模式比較像一個整理好的工具箱。
每個工具都有自己的名稱、描述與處理函式，結構比較清楚，也比較接近 tool-calling 的概念；但如果未來真的將大量工具描述或參數 schema 提供給 AI 使用，就可能增加 prompt 或 token 使用量。

> 注意：本專案中的 `mcp_like` 是非常非常高度簡化的展示版本，並沒有實作完整 MCP protocol，也沒有讓 AI 自主選擇工具。

---

## Discord 指令流程

使用者在 Discord 中輸入 slash command，例如：

```text
/ai
/status
/usage
/privacy
/forget
```

這些指令會先由 `main.py` 接收。

`main.py` 本身不直接處理所有功能，而是把請求交給目前選定的工具模組。

在 `main.py` 中，會根據 `.env` 的設定決定要使用哪個工具模組：

```python
if config.TOOL_MODE == "mcp_like":
    from mods.mcp_like_mod import handle_tool
else:
    from mods.tool_router_mod import handle_tool
```

因此，不管目前使用的是 `router` 模式還是 `mcp_like` 模式，`main.py` 都只需要呼叫同一個函式：

```python
result = await handle_tool(...)
```

這樣可以讓 `main.py` 保持乾淨，專注在 Discord Bot 的啟動、指令註冊與互動回覆。

---

## Discord 指令與工具名稱對應

本專案中的 slash commands 會對應到內部工具名稱。

| Discord 指令 | 內部工具名稱    | 功能                  |
| ---------- | --------- | ------------------- |
| `/ai`      | `ask_ai`  | 將使用者輸入傳給 AI API 並回覆 |
| `/forget`  | `forget`  | 清除使用者的暫時記憶          |
| `/status`  | `status`  | 顯示 Bot 目前設定與架構模式    |
| `/usage`   | `usage`   | 顯示 token 使用量統計      |
| `/privacy` | `privacy` | 顯示雲端 API 隱私提醒       |

例如 `/ai` 指令會呼叫：

```python
handle_tool(
    "ask_ai",
    prompt=prompt,
    user_id=str(interaction.user.id),
    display_name=interaction.user.display_name,
)
```

`main.py` 不需要知道 `ask_ai` 裡面實際怎麼呼叫 API，只要把請求交給工具層處理即可。

---

## Router 模式的基本概念

`tool_router_mod.py` 是傳統的解耦工具路由模式。

它的做法是：
`main.py` 把工具名稱傳進 `handle_tool()`，然後 router 用條件判斷決定要執行哪個功能。

簡化概念如下：

```python
async def handle_tool(tool_name: str, **kwargs):
    if tool_name == "ask_ai":
        return await _ask_ai_tool(**kwargs)
    if tool_name == "forget":
        return _forget_tool(**kwargs)
    if tool_name == "status":
        return _status_tool()
```

這種方式很直覺，也很適合小型專案。

它的優點是容易理解、容易修改。
缺點是當工具越來越多時，router 裡可能會累積很多 `if` 判斷，後續需要更好的分類方式。

---

## Router 模式如何呼叫工具

在 `router` 模式中，所有工具請求都會先進入 `tool_router_mod.py` 的 `handle_tool()`。

`main.py` 只需要把工具名稱與需要的參數傳進去：

```python
result = await handle_tool(
    "ask_ai",
    prompt=prompt,
    user_id=str(interaction.user.id),
    display_name=interaction.user.display_name,
)
```

接著 `tool_router_mod.py` 會根據 `tool_name` 判斷要執行哪個功能。

簡化流程如下：

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

也就是說，router 模式比較像一個「功能分派中心」。

它不會把每個工具整理成獨立的註冊項目，而是用條件判斷的方式，把不同工具名稱導向不同處理函式。

這些工具最後都會回傳統一的 `ToolResult`。


## Router 模式的優點與限制

Router 模式的優點是簡單、直覺，也很適合小型專案。

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
對應工具函式
↓
ToolResult
↓
Discord response
```

這種方式很容易理解，也不需要額外的工具註冊表或 schema 設計。

不過，當工具數量增加時，`handle_tool()` 裡面的條件判斷可能會越來越多，router 本身就可能變得比較臃腫。

因此 router 模式適合：

* 小型專案
* 工具數量不多的情況
* 想快速完成工具分派的情況
* 想讓程式流程簡單易懂的情況

如果未來工具變多，或希望每個工具都有更清楚的名稱、描述與參數格式，就可以考慮改成 MCP-like 工具註冊架構。


## MCP-like 模式的基本概念

`mcp_like_mod.py` 展示的是一個小型 MCP-like 工具註冊架構。

這裡的 MCP-like 並不是正式 MCP server，也沒有完整實作 MCP protocol。

本專案只是用簡單的方式展示以下概念：

* 工具可以被註冊
* 工具可以有名稱
* 工具可以有描述
* 工具可以有參數說明
* 工具可以透過統一格式被呼叫

也就是說，工具不只是單純寫在 `if` 判斷裡，而是被整理成一個一個「工具項目」。

---



## MCP-like 工具註冊原理

在 `mcp_like_mod.py` 中，每個工具會被包裝成 `MCPTool`。

```python
@dataclass
class MCPTool:
    name: str
    description: str
    parameters: dict[str, Any]
    handler: ToolHandler
```

每個工具包含：

| 欄位            | 作用               |
| ------------- | ---------------- |
| `name`        | 工具名稱，例如 `ask_ai` |
| `description` | 工具用途描述           |
| `parameters`  | 工具需要的參數說明        |
| `handler`     | 實際執行功能的函式        |

工具會被存放在 `_TOOLS` 字典中：

```python
_TOOLS: dict[str, MCPTool] = {}
```

這個 `_TOOLS` 可以理解成一個簡單的工具註冊表。

---

## `register_tool()` 做了什麼

`register_tool()` 是一個 decorator，用來註冊工具。

簡化概念如下：

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

這段的意思是：

1. 建立一個名稱為 `ask_ai` 的工具
2. 加上工具描述
3. 加上參數格式說明
4. 指定 `_ask_ai()` 作為實際執行的 handler
5. 將這個工具放進 `_TOOLS` 註冊表

之後只要呼叫：

```python
handle_tool("ask_ai", ...)
```

程式就會到 `_TOOLS` 裡找到 `ask_ai`，再執行它對應的 handler function。

---

## MCP-like 模式如何呼叫工具

`mcp_like_mod.py` 中的 `handle_tool()` 會做三件事：

1. 根據工具名稱查找工具
2. 執行該工具的 handler
3. 如果 handler 是 async，就等待它完成

簡化流程如下：

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
_TOOLS 工具註冊表
↓
registered tool handler
↓
ai_client.py / usage_tracker.py / memory
↓
Discord response
```
## 為什麼 MCP-like 模式仍共用底層功能邏輯

簡答：因為兩種模式的核心功能目標相同，差別主要在「工具如何被組織與呼叫」。

在本專案中，`router` 模式與 `mcp_like` 模式提供的使用者功能基本一致，例如 AI 回覆、狀態查詢、usage 統計、隱私說明與暫時記憶管理。

也就是說，兩種模式要完成的事情是相同的。
真正不同的地方在於：

```text
router 模式：
用傳統集中式路由判斷工具名稱，並分派到對應功能。

mcp_like 模式：
把工具整理成名稱、描述、參數資訊與 handler function 的註冊表，再透過統一入口呼叫工具。
```

因此，`mcp_like_mod.py` 並沒有重新寫一整套 AI、usage、memory 或其他功能處理邏輯，而是共用已經整理好的底層功能。
這樣做不是單純為了省事，而是為了讓比較焦點更清楚：

* 兩種模式使用相同的底層功能
* 使用者得到的功能結果盡量一致
* 比較時能專注在「路由方式」與「工具註冊方式」的差異
* 避免因為重複實作造成兩邊功能行為不一致
* 讓 `mcp_like_mod.py` 專注展示工具註冊層，而不是重新實作整個 bot

換句話說，本專案想比較的不是「兩套不同功能的 bot」，而是：

```text
同一組工具能力
在不同工具組織方式下
程式結構會有什麼差異
```

所以這個版本的 `mcp_like` 比較像是加在工具層上的「註冊展示層」。
它讓工具可以被整理成類似 MCP / tool-calling 思路中的結構，但仍共用相同的底層功能處理邏輯。

本專案的 `mcp_like` 模式沒有實作：

* MCP client/server 通訊
* MCP protocol message format
* 外部工具 discovery
* 完整 schema 驗證
* 真正由 AI 自主選擇工具
* AI 自主產生工具參數
* 權限管理或工具執行沙盒

因此，它比較準確地說是：

```text
MCP-like tool registry demo
```

而不是：

```text
Full MCP implementation
```

這樣設計的原因是，本專案的重點不是重做兩套功能，而是在相同功能基礎上，展示傳統 router 與 MCP-like tool registry 在程式結構上的差異。

---

## 總結

本專案的 MCP-like 模式主要展示了「工具註冊」與「工具呼叫」的概念。

它透過 `MCPTool`、`register_tool()`、`_TOOLS` 與 `handle_tool()`，讓工具可以被整理成一個個具有名稱、描述、參數與處理函式的項目。

雖然它不是完整 MCP protocol，但它能夠展示 tool-calling 架構的基本雛形。

這讓專案在保持輕量的同時，也能說明：

* Discord 指令如何進入工具層
* 工具如何被註冊
* 工具如何被呼叫
* API、usage、memory 如何被拆成獨立模組
* 傳統 router 與 MCP-like 架構的差異

## 小語

MCP-style 架構的優點是清楚、規整，而且每個工具都能被明確描述；但如果工具描述、參數 schema 與上下文全部交給 AI 使用，也可能帶來較高的 token 與資源消耗。

Router 架構則比較簡單直接，對小型專案來說更輕量，也比較容易快速實作。不過當工具越來越多時，router 內部也可能變得臃腫，需要進一步整理。

因此這兩種方式不一定是誰取代誰，而是適合不同規模與不同需求的專案。
對這個 Lite Bot 來說，重點不是做出完整 MCP 系統，而是用小型範例理解「傳統解耦」與「工具註冊」兩種思路的差別。 
  > 感謝一路看到這裡的你/:D

## 參考資料

以下連結是本專案在理解 MCP-like 工具註冊、tool-calling、router 與解耦架構時參考的概念資料。
 > 本專案的 `mcp_like` 模式只是簡化展示，並不是完整 MCP protocol 實作。

### MCP / Tool-calling

* Model Context Protocol Introduction: https://modelcontextprotocol.io/docs/getting-started/intro
* MCP Tools Specification: https://modelcontextprotocol.io/specification/2025-06-18/server/tools
* OpenAI Function Calling Guide: https://developers.openai.com/api/docs/guides/function-calling

### Router / 解耦架構

* Command Pattern: https://refactoring.guru/design-patterns/command
* Chain of Responsibility Pattern: https://refactoring.guru/design-patterns/chain-of-responsibility
* Strategy Pattern: https://refactoring.guru/design-patterns/strategy
* Refactoring: https://refactoring.com/

 > 實際使用 MCP、tool-calling、雲端 API 或自動化工具時，仍需要自行確認相關文件、服務條款、安全限制與資料處理方式。
