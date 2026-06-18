# Discord AI Tool Bot Lite

> 注意：本项目部分文件可能由 AI 辅助翻译。
> 如果其他语言版本与繁体中文版本在语义上有所差异，请以繁体中文版本为主要参考。

一个以工具架构实验为主的轻量化 Discord AI Bot 项目。

本项目使用 Discord Bot 作为小型展示环境，用来比较两种工具处理方式：

* 传统 `router` 模式
* `mcp_like` 工具注册展示模式

AI 聊天功能本身刻意保持简单。
本项目的主要目的不是制作完整聊天机器人，而是展示 Discord 指令如何进入内部工具层、如何将工具逻辑从 `main.py` 拆分出来，以及如何用轻量方式展示 MCP-like 工具注册架构。

本项目主要用于学习记录、课堂展示、API 测试与架构比较。

## 项目说明

本项目是由我的高中学习作品整理与重构而来。

它主要作为学习记录、课堂展示与小型架构实验保存。
因此本项目未来不一定会持续维护或定期更新。

我已经尽力确认代码、文档、安全提醒与项目结构。
如果你发现错误、说明不清楚、安全疑虑，或有更好的实现方式，欢迎提出 issue 或开启 discussion 讨论。

## MCP-like 范围说明

本项目中的 `mcp_like` 模式并不是完整 MCP protocol 实现。

在真正的 MCP-style 架构中，MCP server 会向外提供工具列表，每个工具通常包含名称、描述与输入参数 schema。
Host、client 或 model 可以根据这些工具信息，决定是否调用某个工具，以及用什么参数调用该工具。

本项目没有实现完整流程。

本项目只展示工具注册层：

* 如何整理工具名称
* 如何为工具加入描述
* 如何记录简单的参数信息
* 如何把工具名称对应到实际 handler function
* 如何通过统一的 `handle_tool()` 入口调用已注册工具

因此，本项目的 `mcp_like` 模式更准确地说是 MCP-like tool registry demo，而不是完整 MCP server。

本项目没有实现 MCP client/server 通信、MCP protocol message format、tool discovery、完整 schema 验证、AI 自主选择工具，或 AI 自主生成工具参数。


## 目录

* [功能](#功能)
* [项目结构](#项目结构)
* [文档](#文档)
* [安装与启动](#安装与启动)
* [环境设置](#环境设置)
* [指令](#指令)
* [架构模式](#架构模式)
* [Token 使用量](#token-使用量)
* [隐私与安全](#隐私与安全)
* [参考资料](#参考资料)
* [授权](#授权)

## 功能

* `/ai` AI 聊天指令
* `/status` 显示 Bot 状态
* `/usage` 显示 token 使用量摘要
* `/privacy` 显示云端 API 隐私提醒
* `/forget` 清除临时记忆
* 可选的 mention 回复模式
* 支持 OpenAI-compatible API
* 通过 `.env` 设置 API、模型、记忆模式与工具模式
* 传统 router 模式
* MCP-like 工具注册展示模式
* API 有返回 usage 时读取 token 使用量
* API 没有返回 usage 时可使用粗略估算

## 项目结构

```text
Discord-AI-BOT-Lite/
  main.py
  config.py
  ai_client.py
  usage_tracker.py
  views.py
  .env.example
  requirements.txt
  .gitignore
  LICENSE
  README.md
  README-CN.md
  README-ZH-CN.md

  docs/
    TRANSLATION_NOTE.md
    OVERVIEW-EN/
    OVERVIEW-TW-CN/
    OVERVIEW-ZH-CN/
    OVERVIEW-JP/
    OVERVIEW-KR/

  mods/
    __init__.py
    common.py
    tool_router_mod.py
    mcp_like_mod.py
```

这个档案是执行时产生的本机纪录档，不应上传到 GitHub 或其他公开平台。

```text
.env
__pycache__/
*.pyc
usage_logs.jsonl
*.log
logs/
data/
```

再次申明任何情况下真正的 .env 档案应保持私人，不应上传到任何公开场所。

## 文档

程序架构与技术说明：

* [Code Overview - English](./docs/OVERVIEW-EN/CODE_OVERVIEW.md)
* [Code Overview - 繁體中文](./docs/OVERVIEW-TW-CN/CODE_OVERVIEW-TW-CN.md)
* [Code Overview - 简体中文](./docs/OVERVIEW-ZH-CN/CODE_OVERVIEW-ZH-CN.md)
* [Code Overview - 日本語](./docs/OVERVIEW-JP/CODE_OVERVIEW-JP.md)
* [Code Overview - 한국어](./docs/OVERVIEW-KR/CODE_OVERVIEW-KR.md)

Router 与 MCP-like 模式说明：

* [Mode Overview - English](./docs/OVERVIEW-EN/MODE_OVERVIEW.md)
* [Mode Overview - 繁體中文](./docs/OVERVIEW-TW-CN/MODE_OVERVIEW-TW-CN.md)
* [Mode Overview - 简体中文](./docs/OVERVIEW-ZH-CN/MODE_OVERVIEW-ZH-CN.md)
* [Mode Overview - 日本語](./docs/OVERVIEW-JP/MODE_OVERVIEW-JP.md)
* [Mode Overview - 한국어](./docs/OVERVIEW-KR/MODE_OVERVIEW-KR.md)

翻译说明：

* [Translation Note](./docs/TRANSLATION_NOTE.md)



## 安装与启动

安装依赖：

```bash
pip install -r requirements.txt
```

复制环境设置范例：

```bash
copy .env.example .env
```

macOS 或 Linux 可使用：

```bash
cp .env.example .env
```

在 `.env` 中填入 Discord token 与 AI API 设置：

```env
DISCORD_TOKEN=
AI_API_BASE_URL=
AI_API_KEY=
AI_MODEL=
```

启动 Bot：

```bash
python main.py
```

## 环境设置

OpenAI-compatible API 设置范例：

```env
AI_PROVIDER=openai_compatible
AI_API_BASE_URL=https://openrouter.ai/api/v1
AI_API_KEY=
AI_MODEL=openrouter/free
```

其他范例：

```env
AI_API_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4o-mini
```

```env
AI_API_BASE_URL=https://api.deepseek.com/v1
AI_MODEL=deepseek-chat
```

本项目会将 chat completion 请求发送到：

```text
<AI_API_BASE_URL>/chat/completions
```

## 指令

| 指令         | 说明                      |
| ---------- | ----------------------- |
| `/ai`      | 将 prompt 发送给设置好的 AI API |
| `/status`  | 显示 Bot 状态、模型、记忆模式与工具模式  |
| `/usage`   | 显示 token 使用量摘要          |
| `/privacy` | 显示云端 API 隐私提醒           |
| `/forget`  | 清除当前用户的临时记忆             |

## 架构模式

在 `.env` 中设置工具模式。

```env
TOOL_MODE=router
```

### `router` 模式

传统解耦工具路由：

```text
Discord command
↓
main.py
↓
tool_router_mod.py
↓
ai_client.py / usage_tracker.py / memory
↓
Discord response
```

这个模式简单直接。`main.py` 负责 Discord 事件与指令，`tool_router_mod.py` 则负责将 `ask_ai`、`status`、`usage`、`privacy` 等内部工具名称分派到对应的处理函数。

```env
TOOL_MODE=mcp_like
```

### `mcp_like` 模式

MCP-like 工具注册展示模式：

```text
Discord command
↓
main.py
↓
mcp_like_mod.py
↓
registered tool
↓
handler
↓
Discord response
```

每个工具都有名称、描述、参数信息与处理函数。

本项目没有实现完整 MCP protocol，也不是正式 MCP server。`mcp_like` 模式只是用来轻量展示工具注册与 tool-calling 架构概念。

## Token 使用量

当 API provider 有返回 token usage 数据时，Bot 会读取 API 返回数据。

如果 API 没有返回 token usage，Bot 可以使用粗略估算：

```env
USAGE_MODE=api_or_estimate
```

使用量数据会写入：

```env
USAGE_LOG_FILE=usage_logs.jsonl
```

>注意:这个档案是执行时产生的本机纪录档，不应上传到 GitHub 或其他公开平台。

token 使用量结果只适合用于观察与调试，不应被视为正式计费数据。

## 隐私与安全

云端 API 模式可能会将 prompts、临时用户上下文与生成回复发送到设置的第三方 API provider。

请不要将私人 token、密码、个人资料、敏感管理记录或服务器机密信息放进 prompt。

这个 Lite 版本默认只使用 RAM 来临时记忆，不包含长期 moderation cases、user profiling、music playback、PC monitoring 或永久用户记录。

但是第三方 API provider 可能会依照其服务条款与政策处理或保存数据。使用云端 API 前，请自行确认该服务的价格、隐私政策、数据保存政策与服务条款。

如果是隐私敏感的服务器、学校环境，或包含未成年人的社区，可能更适合使用本地 AI 部署。

### 安全提醒

本项目需要 Discord bot token、AI API key 等私人凭证才能运行。

请不要公开：

* `.env` 文件
* Discord bot token
* API key
* Webhook URL
* 密码
* runtime logs
* usage logs
* 用户记录
* 私人设置文件

如果不小心公开 Discord token 或 API key，请立刻撤销或重新生成。

作者不负责因设置错误、部署错误、修改错误或公开上传私人文件而造成的 token 泄露、API key 泄露、非预期 API 费用、账号问题、数据丢失、隐私问题、服务滥用或其他误用。

## 参考资料

以下链接是本项目在理解 OpenAI-compatible API、MCP-like 工具注册、tool-calling、router 设计与解耦架构时参考的概念资料。

> 本项目只实现轻量化的 MCP-like 工具注册展示，并不是完整 MCP protocol 实现。

### OpenAI-compatible API

* OpenAI Chat Completions API: https://developers.openai.com/api/reference/chat-completions/
* OpenRouter Chat Completion API: https://openrouter.ai/docs/api/api-reference/chat/send-chat-completion-request
* OpenRouter Quickstart: https://openrouter.ai/docs/quickstart
* DeepSeek API Docs: https://api-docs.deepseek.com/
* Gemini OpenAI Compatibility: https://ai.google.dev/gemini-api/docs/openai

### MCP / Tool-calling

* Model Context Protocol Introduction: https://modelcontextprotocol.io/docs/getting-started/intro
* MCP Tools Specification: https://modelcontextprotocol.io/specification/2025-06-18/server/tools
* OpenAI Function Calling Guide: https://developers.openai.com/api/docs/guides/function-calling

### Router / 解耦架构

* Command Pattern: https://refactoring.guru/design-patterns/command
* Chain of Responsibility Pattern: https://refactoring.guru/design-patterns/chain-of-responsibility
* Strategy Pattern: https://refactoring.guru/design-patterns/strategy
* Refactoring: https://refactoring.com/

实际在项目中使用 MCP、tool-calling、云端 API 或自动化工具前，仍需要自行确认官方文件、服务条款、价格、隐私政策、数据保存方式与安全限制。

## 授权

完整授权条款与免责声明请参考 [LICENSE](../../LICENSE)。

README 中的安全提醒主要是实际使用上的提醒；`LICENSE` 文件才是主要授权与免责声明文件。

