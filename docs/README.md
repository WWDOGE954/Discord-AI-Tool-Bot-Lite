# Documentation

This folder contains supplementary documents for **Discord AI Tool Bot Lite**.

Some documents were translated with AI assistance.
If a translated document differs in meaning from the Traditional Chinese source document, please treat the Traditional Chinese version as the primary reference.

## Document Structure

```text
docs/
  README.md
  TRANSLATION_NOTE.md

  OVERVIEW-EN/
    CODE_OVERVIEW.md
    MODE_OVERVIEW.md

  OVERVIEW-TW-CN/
    CODE_OVERVIEW-TW-CN.md
    MODE_OVERVIEW-TW-CN.md

  OVERVIEW-ZH-CN/
    CODE_OVERVIEW-ZH-CN.md
    MODE_OVERVIEW-ZH-CN.md

  OVERVIEW-JP/
    CODE_OVERVIEW-JP.md
    MODE_OVERVIEW-JP.md

  OVERVIEW-KR/
    CODE_OVERVIEW-KR.md
    MODE_OVERVIEW-KR.md
```

## Code Overview

These documents explain the main Python files and the overall code structure.

* [English](./OVERVIEW-EN/CODE_OVERVIEW.md)
* [繁體中文](./OVERVIEW-TW-CN/CODE_OVERVIEW-TW-CN.md)
* [简体中文](./OVERVIEW-ZH-CN/CODE_OVERVIEW-ZH-CN.md)
* [日本語](./OVERVIEW-JP/CODE_OVERVIEW-JP.md)
* [한국어](./OVERVIEW-KR/CODE_OVERVIEW-KR.md)

## Mode Overview

These documents explain the difference between the traditional `router` mode and the `mcp_like` tool registry demo mode.

* [English](./OVERVIEW-EN/MODE_OVERVIEW.md)
* [繁體中文](./OVERVIEW-TW-CN/MODE_OVERVIEW-TW-CN.md)
* [简体中文](./OVERVIEW-ZH-CN/MODE_OVERVIEW-ZH-CN.md)
* [日本語](./OVERVIEW-JP/MODE_OVERVIEW-JP.md)
* [한국어](./OVERVIEW-KR/MODE_OVERVIEW-KR.md)

## Translation Note

* [Translation Note](./TRANSLATION_NOTE.md)

## Notes

This project is mainly focused on tool architecture experiments.

The AI chat feature is intentionally simple.
The main purpose of the project is to demonstrate:

* Discord slash command handling
* separation of Discord logic from tool logic
* traditional router-based tool dispatch
* MCP-like tool registry structure
* basic comparison between `router` and `mcp_like` modes

The `mcp_like` mode is only a lightweight tool registry demo.
It is not a full MCP protocol implementation and is not a real MCP server.
