# Code Architecture Overview

> Translation note: This document was translated from the Traditional Chinese version with AI assistance.  
> If there is any difference in meaning, the Traditional Chinese version should be treated as the primary reference.

This document briefly explains the main Python files in this project and the overall technical architecture.

The main goal is to demonstrate a lightweight Discord AI Bot with OpenAI-compatible API integration, temporary memory, token usage tracking, and two simple tool-layer designs.

For a more detailed comparison of the tool router and MCP-like simplified architecture, see:

[MODE_OVERVIEW.md](./MODE_OVERVIEW.md)

## File Structure

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

## Python File Descriptions

This section briefly explains the purpose of each file, with a focus on the calling architecture.  
If you have any other questions, feel free to contact me.

### `main.py`

`main.py` is the main entry point of the Discord Bot.

It is responsible for starting the bot, registering commands, receiving user requests, and passing those requests to the corresponding tool modules.

Simply put, `main.py` integrates the files and controls the main flow of the bot.

### `config.py`

`config.py` loads configuration values from `.env`.

This keeps settings such as the Discord token, API key, model name, and tool mode inside `.env` instead of writing them directly into the source code.

### `ai_client.py`

`ai_client.py` handles AI API requests.

It is designed around an OpenAI-compatible API style, so it can be used with OpenRouter, OpenAI, DeepSeek, or other compatible API services.

When the API returns token usage data, `ai_client.py` also passes that data to `usage_tracker.py`.

### `usage_tracker.py`

`usage_tracker.py` records token usage.

If the API provider returns official token usage data, the bot will use the API-provided data first.  
If the API does not return token usage, the bot will fall back to a rough estimate.

This feature is mainly used to observe API usage and roughly compare token consumption across different tool modes or models.

### `views.py`

`views.py` contains simple Discord UI helper components.

It can be used for simple buttons, prompt messages, or small interactive interfaces.

Separating UI-related code helps prevent `main.py` from becoming too large.

### `mods/common.py`

`mods/common.py` contains shared structures or helper functions used by different tool modules.

Its purpose is to let router mode and MCP-like mode use a consistent data format and return logic.

### `mods/tool_router_mod.py`

`tool_router_mod.py` is the traditional decoupled tool router mode.

In this mode, `main.py` sends tool requests to the router, and the router decides which function should be executed.

For more details, see:

[MODE_OVERVIEW.md](./MODE_OVERVIEW.md)

### `mods/mcp_like_mod.py`

`mcp_like_mod.py` is a small MCP-like tool registry demo mode.

It organizes tools by name, description, and handler function as a simplified demonstration of a tool-calling architecture.

This project does not implement the full MCP protocol and is not an official MCP server.  
The MCP-like mode here is only used to demonstrate the concepts of tool registration and tool calling.

For more details, see:

[MODE_OVERVIEW.md](./MODE_OVERVIEW.md)

## Modes

You can switch between two tool architecture modes through `.env`.

```env
TOOL_MODE=router
```

Use the traditional decoupled tool router mode.

```env
TOOL_MODE=mcp_like
```

Use the MCP-like tool registry demo mode.

Both modes provide roughly the same user-facing features, but their internal structures are different.

## Notes

### Managing settings with `.env`

Most important settings are controlled through `.env`.

This includes the API provider, model name, tool mode, memory mode, and token usage tracking mode.

Therefore, by editing `.env`, you can switch between different API providers, models, or tool modes without rewriting the whole program.

### Temporary memory only

This Lite version only uses temporary memory in RAM when memory is enabled.

After the bot restarts, the memory is cleared.

This project does not store long-term user profiles, moderation records, case records, or permanent chat logs.

> This does not include third-party API providers. When using a cloud API, the deployer still needs to check the provider's privacy policy and data retention policy.

### Token usage tracking

The bot can read token usage data when the API returns it.

If the API provider does not return token usage, the bot will use a rough estimate instead.

The estimate may not be accurate and should not be treated as official billing data.

This feature is mainly used to observe token usage and roughly compare the differences between router mode and MCP-like mode.  
Please note that even with the same input, token usage may change depending on the model, API provider, reply content, temporary memory, or generation behavior, so the result should only be used as a reference.

## References

* OpenAI Chat Completions API: https://developers.openai.com/api/reference/chat-completions/
* OpenRouter Chat Completion API: https://openrouter.ai/docs/api/api-reference/chat/send-chat-completion-request
* OpenRouter Quickstart: https://openrouter.ai/docs/quickstart
* DeepSeek API Docs: https://api-docs.deepseek.com/
* Gemini OpenAI Compatibility: https://ai.google.dev/gemini-api/docs/openai

The links above were used as conceptual references for understanding OpenAI-compatible API registration, requests, and actions in this project.  
> Note: When learning or developing with OpenAI-compatible API formats, users still need to check each API provider's model names, pricing, privacy policy, data retention policy, and terms of service.
