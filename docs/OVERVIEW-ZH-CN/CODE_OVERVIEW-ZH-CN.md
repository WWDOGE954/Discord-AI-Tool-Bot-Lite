# 程序架构说明

> 翻译说明：本文件由繁体中文版本经 AI 辅助翻译而来。  
> 如果其他语言版本与繁体中文版本在语义上有所差异，请以繁体中文版本为准。

这份文件用来简单说明本项目的主要 Python 文件，以及整体技术架构。

主要目标是展示一个轻量化的 Discord AI Bot，包含 OpenAI-compatible API 连接、临时记忆、token 使用量记录，以及两种简单的工具层设计。

如果想查看工具路由与 MCP-like（简化版）架构的更详细比较，可参考：

[MODE_OVERVIEW-ZH-CN.md](./MODE_OVERVIEW-ZH-CN.md)

## 文件结构

```text
Discord-AI-BOT-Lite/
  main.py
  config.py
  ai_client.py
  usage_tracker.py
  views.py
  .env.example
  requirements.txt
  README.md
  LICENSE
  CODE.md
  MODE_OVERVIEW-CN.md

  mods/
    __init__.py
    common.py
    tool_router_mod.py
    mcp_like_mod.py
```

## Python 文件说明

这里主要简单说明各文件的用途，并着重在调用架构。  
如果有其他问题，欢迎联系我。

### `main.py`

`main.py` 是 Discord Bot 的主要入口点。

它主要负责启动机器人、注册指令、接收使用者请求，并将请求交给对应的工具模块处理。

简单来说，`main.py` 负责整合各文件，并控制 Bot 的主要流程。

### `config.py`

`config.py` 用来从 `.env` 载入设置值。

这样可以让 Discord token、API key、模型名称、工具模式等设置保留在 `.env` 中，而不是直接写进源代码。

### `ai_client.py`

`ai_client.py` 负责处理 AI API 请求。

它是以 OpenAI-compatible API 为基础设计，因此可以用于 OpenRouter、OpenAI、DeepSeek，或其他兼容的 API 服务。

当 API 返回 token usage 数据时，`ai_client.py` 也会将相关数据传给 `usage_tracker.py`。

### `usage_tracker.py`

`usage_tracker.py` 负责记录 token 使用量。

如果 API provider 有返回官方 token usage 数据，Bot 会优先使用 API 返回的数据。  
如果 API 没有返回 token 使用量，Bot 会改用粗略估算。

这个功能主要用来观察 API 使用量，以及简单比较不同工具模式或不同模型的大致 token 消耗。

### `views.py`

`views.py` 包含简单的 Discord UI 辅助组件。

它可以用来放置简单按钮、提示消息，或小型交互界面。

将 UI 相关代码独立出来，可以避免 `main.py` 变得太大。

### `mods/common.py`

`mods/common.py` 包含不同工具模块共用的结构或辅助函数。

它的用途是让 router 模式与 MCP-like 模式可以使用一致的数据格式与返回逻辑。

### `mods/tool_router_mod.py`

`tool_router_mod.py` 是传统的解耦工具路由模式。

在这个模式下，`main.py` 会把工具请求交给 router，再由 router 判断应该执行哪个功能。

详细说明可参考：

[MODE_OVERVIEW-ZH-CN.md](./MODE_OVERVIEW-ZH-CN.md)

### `mods/mcp_like_mod.py`

`mcp_like_mod.py` 是小型 MCP-like 工具注册展示模式。

它会将工具以名称、描述与处理函数的方式整理，作为 tool-calling 架构的简化展示。

本项目没有实现完整 MCP protocol，也不是正式 MCP server。  
这里的 MCP-like 模式只是用来展示工具注册与工具调用概念。

详细说明可参考：

[MODE_OVERVIEW-ZH-CN.md](./MODE_OVERVIEW-ZH-CN.md)

## 模式

可以通过 `.env` 切换两种工具架构模式。

```env
TOOL_MODE=router
```

使用传统的解耦工具路由模式。

```env
TOOL_MODE=mcp_like
```

使用 MCP-like 工具注册展示模式。

两种模式提供的使用者功能大致相同，但内部结构不同。

## 注意事项

### 以 `.env` 管理设置

大部分重要设置都通过 `.env` 控制。

包含 API provider、模型名称、工具模式、记忆模式与 token 使用量记录模式。

因此只要修改 `.env`，就可以切换不同 API provider、模型或工具模式，而不需要重写整个程序。

### 仅使用临时记忆

这个 Lite 版本只在启用记忆功能时，使用 RAM 中的临时记忆。

Bot 重启后，记忆会被清除。

本项目不会保存长期使用者 profile、管理记录、案件记录或永久聊天记录。

> 这并不包含第三方 API provider。使用云端 API 时，部署者仍需要自行确认 API 服务的隐私政策与数据保存方式。

### Token 使用量记录

Bot 可以在 API 返回 token usage 数据时读取该数据。

如果 API provider 没有返回 token usage，Bot 会改用粗略估算。

估算结果不一定精准，不应被视为正式计费数据。

这个功能主要是用来观察 token 使用量，以及简单比较 router 模式与 MCP-like 模式的大致差异。  
需要注意的是，即使输入同一句话，也可能因模型、API provider、回复内容、临时记忆或生成状况不同，而产生不同的 token 使用量，因此结果只能作为参考。

## 参考资料

* OpenAI Chat Completions API: https://developers.openai.com/api/reference/chat-completions/
* OpenRouter Chat Completion API: https://openrouter.ai/docs/api/api-reference/chat/send-chat-completion-request
* OpenRouter Quickstart: https://openrouter.ai/docs/quickstart
* DeepSeek API Docs: https://api-docs.deepseek.com/
* Gemini OpenAI Compatibility: https://ai.google.dev/gemini-api/docs/openai

以上链接是本项目在理解 OpenAI-compatible API 注册、请求与动作时的参考资料。  
> 注意：实际应用 OpenAI-compatible API 格式进行学习与开发时，使用不同 API provider 仍需要自行确认该服务的模型名称、价格、隐私政策、数据保存方式与服务条款。
