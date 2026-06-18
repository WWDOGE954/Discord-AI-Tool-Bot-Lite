# Discord AI Tool Bot Lite

> Note: Some documents in this project were translated with AI assistance.
> If a translated document differs in meaning from the Traditional Chinese source document, please treat the Traditional Chinese version as the primary reference.

A lightweight Discord AI bot project focused on tool architecture experiments.

This project uses a Discord bot as a small demonstration environment to compare two tool-handling approaches:

* a traditional `router` mode
* an `mcp_like` tool registry demo mode

The AI chat feature is intentionally simple.
The main purpose of this project is to show how Discord commands can be routed into internal tools, how tool logic can be separated from `main.py`, and how a lightweight MCP-like registry can be structured without implementing the full MCP protocol.

This project is mainly for learning, classroom demonstration, API testing, and architecture comparison.

## Project Note

This repository was organized and refactored from one of my high school learning projects.

It was prepared as part of my personal portfolio and learning record. Since this is one of my first repositories uploaded to GitHub, there may still be issues in the repository structure, documentation, wording, or setup instructions.

Unless there is a special reason, this bot will probably not receive major updates in the future. The repository is mainly kept for documentation, learning, educational reference, and portfolio purposes.

If you find any problems or have suggestions, feel free to contact me, open an issue, or use the discussion area.

## MCP-like Scope Clarification

The `mcp_like` mode in this project is not a full MCP protocol implementation.

In a real MCP-style architecture, an MCP server exposes a list of tools. Each tool usually includes a name, description, and input parameter schema.
A host, client, or model can inspect those tool definitions and decide whether to call a tool and what arguments should be passed to it.

This project does not implement that full flow.

This project only demonstrates the earlier tool registration concept:

* how to organize tool names
* how to attach descriptions to tools
* how to store simple parameter information
* how to map tool names to handler functions
* how to call registered tools through a unified `handle_tool()` entry point

Therefore, the `mcp_like` mode in this project is more accurately described as:

```text
MCP-like tool registry demo
```

rather than:

```text
Full MCP server
```

This project does not implement:

* MCP client / server communication
* MCP protocol message format
* tools/list or tool discovery
* full input schema validation
* AI-driven tool selection
* AI-generated tool arguments
* permission management or tool execution sandboxing

In other words, this Lite version uses a Discord bot as a small example to show how tool registration could be structured in an MCP-like style.
The focus is on understanding the difference between a traditional router and a tool registry, not on implementing the full MCP system.


## What This Project Demonstrates

* Discord slash command handling
* OpenAI-compatible API integration
* Temporary RAM-based user memory
* Token usage tracking and rough estimation
* Separation of Discord logic from tool logic
* Traditional router-based tool dispatch
* MCP-like tool registry structure
* Basic comparison between router and MCP-like architecture

## Features

* `/ai` chat command
* `/status` bot status
* `/usage` token usage summary
* `/privacy` cloud API privacy notice
* `/forget` clear temporary memory
* Optional mention reply mode
* `.env` based API, model, memory, and tool mode settings

## Documentation

See [`docs/README.md`](./docs/README.md) for documentation, command guides, architecture notes, translation notes, and supplementary multilingual documents.

## Requirements

* Python 3.10+
* Discord bot token
* AI API key from an OpenAI-compatible API provider
* `discord.py`
* `python-dotenv`
* `requests`
* `aiohttp`

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Configuration

Copy the public template:

```bash
cp .env.example .env
```

On Windows, you can also use:

```bash
copy .env.example .env
```

Then fill in your private values:

```env
DISCORD_TOKEN=
AI_API_BASE_URL=
AI_API_KEY=
AI_MODEL=
```

Example OpenAI-compatible API settings:

```env
AI_PROVIDER=openai_compatible
AI_API_BASE_URL=https://openrouter.ai/api/v1
AI_API_KEY=
AI_MODEL=openrouter/free
```

The project sends chat completion requests to:

```text
<AI_API_BASE_URL>/chat/completions
```

## Running the Bot

```bash
python main.py
```

For faster slash command sync during testing, set `GUILD_ID` in `.env` if the project supports guild-specific command sync.

## Commands

| Command    | Description                                        |
| ---------- | -------------------------------------------------- |
| `/ai`      | Send a prompt to the configured AI API             |
| `/status`  | Show bot status, model, memory mode, and tool mode |
| `/usage`   | Show token usage summary                           |
| `/privacy` | Show a cloud API privacy reminder                  |
| `/forget`  | Clear temporary memory for the current user        |

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

## AI Provider and Privacy Notice

This project uses an OpenAI-compatible API style.

Cloud API mode may send prompts, temporary user context, and generated replies to the configured third-party API provider.

Do not put private tokens, passwords, personal data, sensitive moderation records, or confidential server information into prompts.

This Lite version only uses temporary RAM memory by default. It does not include long-term moderation cases, user profiling, music playback, PC monitoring, or persistent user records.

However, third-party API providers may process or retain data according to their own terms and policies. Before using a cloud API, check the provider's pricing, privacy policy, data retention policy, and terms of service.

For privacy-sensitive servers, school environments, or communities involving minors, local AI deployment may be more appropriate.

## Safety Notice

Never commit the following files or data:

* `.env`
* Discord bot tokens
* Webhook URLs
* API keys or passwords
* Runtime logs
* Usage logs
* User records
* Private configuration files

Use `.env.example` as a safe public template. Copy it to `.env` locally and fill in your private values.

If a Discord token, webhook URL, API key, or password is ever exposed, revoke or regenerate it immediately.

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
