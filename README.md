# Discord AI Bot Lite

> Note: Some documents in this project were translated with AI assistance.  
> If a translated document differs in meaning from the Traditional Chinese source document, please treat the Traditional Chinese version as the primary reference.

A lightweight Discord AI bot for learning, classroom demonstration, and quick API testing.

This project is intentionally small. It focuses on simple AI chat, simple tools, token usage tracking, temporary memory, and two tool architecture modes: a traditional router mode and an MCP-like tool registry demo.

## Project Note

This project was organized and refactored from one of my high school learning projects.

It is mainly kept as a learning record, classroom demonstration, and small architecture experiment.
Because of this, the project may not be actively maintained or regularly updated.

I have tried my best to check the code, documentation, security notes, and project structure.
If you find any mistakes, unclear explanations, security concerns, or better implementation ideas, feel free to open an issue or start a discussion.


## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Setup](#setup)
- [Environment Settings](#environment-settings)
- [Commands](#commands)
- [Architecture Modes](#architecture-modes)
- [Token Usage](#token-usage)
- [Privacy and Safety](#privacy-and-safety)
- [References](#references)
- [License](#license)

## Features

- `/ai` chat command
- `/status` bot status
- `/usage` token usage summary
- `/privacy` cloud API privacy notice
- `/forget` clear temporary memory
- Optional mention reply mode
- OpenAI-compatible API support
- `.env` based API, model, memory, and tool mode settings
- Traditional router mode
- MCP-like tool registry demo mode
- Token usage tracking from API responses when available
- Rough token usage estimation fallback when the API does not return usage data

## Project Structure

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

Before uploading to GitHub, make sure runtime files are removed:

```text
.env
__pycache__/
*.pyc
usage_logs.jsonl
*.log
logs/
data/
```

Only upload `.env.example`, not your real `.env` file.

## Documentation

Code structure and technical overview:

- [Code Overview - English](./docs/OVERVIEW-EN/CODE_OVERVIEW.md)
- [Code Overview - Traditional Chinese](./docs/OVERVIEW-TW-CN/CODE_OVERVIEW-TW-CN.md)
- [Code Overview - Simplified Chinese](./docs/OVERVIEW-ZH-CN/CODE_OVERVIEW-ZH-CN.md)
- [Code Overview - Japanese](./docs/OVERVIEW-JP/CODE_OVERVIEW-JP.md)
- [Code Overview - Korean](./docs/OVERVIEW-KR/CODE_OVERVIEW-KR.md)

Router and MCP-like mode explanation:

- [Mode Overview - English](./docs/OVERVIEW-EN/MODE_OVERVIEW.md)
- [Mode Overview - Traditional Chinese](./docs/OVERVIEW-TW-CN/MODE_OVERVIEW-TW-CN.md)
- [Mode Overview - Simplified Chinese](./docs/OVERVIEW-ZH-CN/MODE_OVERVIEW-ZH-CN.md)
- [Mode Overview - Japanese](./docs/OVERVIEW-JP/MODE_OVERVIEW-JP.md)
- [Mode Overview - Korean](./docs/OVERVIEW-KR/MODE_OVERVIEW-KR.md)

Translation note:

- [Translation Note](./docs/TRANSLATION_NOTE.md)

If you rename the documentation folders, remember to update these links.

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy the environment example:

```bash
copy .env.example .env
```

On macOS or Linux:

```bash
cp .env.example .env
```

Fill in your Discord token and AI API settings in `.env`:

```env
DISCORD_TOKEN=
AI_API_BASE_URL=
AI_API_KEY=
AI_MODEL=
```

Run the bot:

```bash
python main.py
```

## Environment Settings

Example OpenAI-compatible API settings:

```env
AI_PROVIDER=openai_compatible
AI_API_BASE_URL=https://openrouter.ai/api/v1
AI_API_KEY=
AI_MODEL=openrouter/free
```

Other examples:

```env
AI_API_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4o-mini
```

```env
AI_API_BASE_URL=https://api.deepseek.com/v1
AI_MODEL=deepseek-chat
```

The project sends chat completion requests to:

```text
<AI_API_BASE_URL>/chat/completions
```

## Commands

| Command | Description |
|---|---|
| `/ai` | Send a prompt to the configured AI API |
| `/status` | Show bot status, model, memory mode, and tool mode |
| `/usage` | Show token usage summary |
| `/privacy` | Show a cloud API privacy reminder |
| `/forget` | Clear temporary memory for the current user |

## Architecture Modes

Set the tool mode in `.env`.

```env
TOOL_MODE=router
```

### `router` mode

Traditional decoupled tool router:

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

This mode is simple and direct. `main.py` handles Discord events and commands, while `tool_router_mod.py` routes internal tool names such as `ask_ai`, `status`, `usage`, and `privacy` to the correct handler.

```env
TOOL_MODE=mcp_like
```

### `mcp_like` mode

MCP-like tool registry demo:

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

Each tool has a name, description, parameter information, and handler function.

This project does not implement the full MCP protocol and is not a real MCP server. The `mcp_like` mode is only a lightweight demonstration of tool registration and tool-calling structure.

## Token Usage

The bot reads token usage from the API response when the provider returns usage data.

If the provider does not return token usage data, the bot can use a rough estimate:

```env
USAGE_MODE=api_or_estimate
```

Usage data is written to:

```env
USAGE_LOG_FILE=usage_logs.jsonl
```

This file should be ignored by Git.

Token usage results are only for observation and debugging. They should not be treated as official billing data.

## Privacy and Safety

Cloud API mode may send prompts, temporary user context, and generated replies to the configured third-party API provider.

Do not put private tokens, passwords, personal data, sensitive moderation records, or confidential server information into prompts.

This Lite version only uses temporary RAM memory by default. It does not include long-term moderation cases, user profiling, music playback, PC monitoring, or persistent user records.

However, third-party API providers may process or retain data according to their own terms and policies. Before using a cloud API, check the provider's pricing, privacy policy, data retention policy, and terms of service.

For privacy-sensitive servers, school environments, or communities involving minors, local AI deployment may be more appropriate.

### Security Notice

This project requires private credentials such as a Discord bot token and an AI API key.

Do not publish:

- `.env` files
- Discord bot tokens
- API keys
- Webhook URLs
- Passwords
- Runtime logs
- Usage logs
- User records
- Private configuration files

If you accidentally expose a Discord token or API key, revoke or regenerate it immediately.

The author is not responsible for leaked tokens, leaked API keys, unexpected API charges, account issues, data loss, privacy problems, service abuse, or misuse caused by improper setup, deployment, modification, or public upload of private files.

## References

The following links were used as conceptual references while understanding OpenAI-compatible APIs, MCP-like tool registration, tool-calling, router design, and decoupled architecture.

These links are for learning and development reference only.
This project only implements a lightweight MCP-like tool registry demo. It is not a full MCP protocol implementation.

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

### Router / Decoupled Architecture

* Command Pattern: https://refactoring.guru/design-patterns/command
* Chain of Responsibility Pattern: https://refactoring.guru/design-patterns/chain-of-responsibility
* Strategy Pattern: https://refactoring.guru/design-patterns/strategy
* Refactoring: https://refactoring.com/

Before using MCP, tool-calling, cloud APIs, or automation tools in a real project, please check the official documentation, service terms, pricing, privacy policy, data retention policy, and security requirements by yourself.


## License

See [LICENSE](./LICENSE) for the full license terms and disclaimer.

The README safety notes are practical usage reminders. The `LICENSE` file is the main license and disclaimer document.
