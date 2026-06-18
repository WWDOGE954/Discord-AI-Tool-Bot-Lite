## 專案說明

本專案是由我的高中學習作品整理與重構而來。

它主要作為學習紀錄、課堂展示與小型架構實驗保存。
因此本專案未來不一定會持續維護或定期更新。

我已經盡力確認程式碼、文件、安全提醒與專案結構。
如果你發現錯誤、說明不清楚、安全疑慮，或有更好的實作方式，歡迎提出 issue 或開啟 discussion 討論。

# Discord AI Tool Bot Lite

一個以工具架構實驗為主的輕量化 Discord AI Bot 專案。

本專案使用 Discord Bot 作為小型展示環境，用來比較兩種工具處理方式：

* 傳統 `router` 模式
* `mcp_like` 工具註冊展示模式

AI 聊天功能本身刻意保持簡單。
本專案的主要目的不是製作完整聊天機器人，而是展示 Discord 指令如何進入內部工具層、如何將工具邏輯從 `main.py` 拆分出來，以及如何用輕量方式展示 MCP-like 工具註冊架構。

本專案主要用於學習紀錄、課堂展示、API 測試與架構比較。

## MCP-like 範圍說明

本專案中的 `mcp_like` 模式並不是完整 MCP protocol 實作。

真正的 MCP-style 架構中，MCP server 會向外提供工具清單，每個工具通常包含名稱、描述與輸入參數 schema。
Host、client 或 model 可以根據這些工具資訊，決定是否呼叫某個工具，以及用什麼參數呼叫該工具。

本專案沒有實作完整流程。

本專案只展示工具註冊層：

* 如何整理工具名稱
* 如何替工具加入描述
* 如何記錄簡單的參數資訊
* 如何把工具名稱對應到實際 handler function
* 如何透過統一的 `handle_tool()` 入口呼叫已註冊工具

因此，本專案的 `mcp_like` 模式比較準確地說是 MCP-like tool registry demo，而不是完整 MCP server。

本專案沒有實作 MCP client/server 通訊、MCP protocol message format、tool discovery、完整 schema 驗證、AI 自主選擇工具，或 AI 自主產生工具參數。

## 目錄

- [功能](#功能)
- [專案結構](#專案結構)
- [文件](#文件)
- [安裝與啟動](#安裝與啟動)
- [環境設定](#環境設定)
- [指令](#指令)
- [架構模式](#架構模式)
- [Token 使用量](#token-使用量)
- [隱私與安全](#隱私與安全)
- [參考資料](#參考資料)
- [授權](#授權)

## 功能

- `/ai` AI 聊天指令
- `/status` 顯示 Bot 狀態
- `/usage` 顯示 token 使用量摘要
- `/privacy` 顯示雲端 API 隱私提醒
- `/forget` 清除暫時記憶
- 可選的 mention 回覆模式
- 支援 OpenAI-compatible API
- 透過 `.env` 設定 API、模型、記憶模式與工具模式
- 傳統 router 模式
- MCP-like 工具註冊展示模式
- API 有回傳 usage 時讀取 token 使用量
- API 沒有回傳 usage 時可使用粗略估算

## 專案結構

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

在公開或分享本專案前，請確認 runtime 檔案與私人設定檔沒有被包含進去。

.env

```text
.env
__pycache__/
*.pyc
usage_logs.jsonl
*.log
logs/
data/
```

再次申明任何情況下真正的 .env 檔案應保持私人，不應上傳到任何公開場所。

## 文件

程式架構與技術說明：

- [Code Overview - English](./docs/OVERVIEW-EN/CODE_OVERVIEW.md)
- [Code Overview - 繁體中文](./docs/OVERVIEW-TW-CN/CODE_OVERVIEW-TW-CN.md)
- [Code Overview - 简体中文](./docs/OVERVIEW-ZH-CN/CODE_OVERVIEW-ZH-CN.md)
- [Code Overview - 日本語](./docs/OVERVIEW-JP/CODE_OVERVIEW-JP.md)
- [Code Overview - 한국어](./docs/OVERVIEW-KR/CODE_OVERVIEW-KR.md)

Router 與 MCP-like 模式說明：

- [Mode Overview - English](./docs/OVERVIEW-EN/MODE_OVERVIEW.md)
- [Mode Overview - 繁體中文](./docs/OVERVIEW-TW-CN/MODE_OVERVIEW-TW-CN.md)
- [Mode Overview - 简体中文](./docs/OVERVIEW-ZH-CN/MODE_OVERVIEW-ZH-CN.md)
- [Mode Overview - 日本語](./docs/OVERVIEW-JP/MODE_OVERVIEW-JP.md)
- [Mode Overview - 한국어](./docs/OVERVIEW-KR/MODE_OVERVIEW-KR.md)

翻譯說明：

- [Translation Note](./docs/TRANSLATION_NOTE.md)

如果之後修改資料夾名稱，請記得同步更新 README 內的連結。

## 安裝與啟動

安裝套件：

```bash
pip install -r requirements.txt
```

複製環境設定範例：

```bash
copy .env.example .env
```

macOS 或 Linux 可使用：

```bash
cp .env.example .env
```

在 `.env` 中填入 Discord token 與 AI API 設定：

```env
DISCORD_TOKEN=
AI_API_BASE_URL=
AI_API_KEY=
AI_MODEL=
```

啟動 Bot：

```bash
python main.py
```

## 環境設定

OpenAI-compatible API 設定範例：

```env
AI_PROVIDER=openai_compatible
AI_API_BASE_URL=https://openrouter.ai/api/v1
AI_API_KEY=
AI_MODEL=openrouter/free
```

其他範例：

```env
AI_API_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4o-mini
```

```env
AI_API_BASE_URL=https://api.deepseek.com/v1
AI_MODEL=deepseek-chat
```

本專案會將 chat completion 請求送到：

```text
<AI_API_BASE_URL>/chat/completions
```

## 指令

| 指令 | 說明 |
|---|---|
| `/ai` | 將 prompt 傳給設定好的 AI API |
| `/status` | 顯示 Bot 狀態、模型、記憶模式與工具模式 |
| `/usage` | 顯示 token 使用量摘要 |
| `/privacy` | 顯示雲端 API 隱私提醒 |
| `/forget` | 清除目前使用者的暫時記憶 |

## 架構模式

在 `.env` 中設定工具模式。

```env
TOOL_MODE=router
```

### `router` 模式

傳統解耦工具路由：

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

這個模式簡單直接。`main.py` 負責 Discord 事件與指令，`tool_router_mod.py` 則負責將 `ask_ai`、`status`、`usage`、`privacy` 等內部工具名稱分派到對應的處理函式。

```env
TOOL_MODE=mcp_like
```

### `mcp_like` 模式

MCP-like 工具註冊展示模式：

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

每個工具都有名稱、描述、參數資訊與處理函式。

本專案沒有實作完整 MCP protocol，也不是正式 MCP server。`mcp_like` 模式只是用來輕量展示工具註冊與 tool-calling 架構概念。

## Token 使用量

當 API provider 有回傳 token usage 資料時，Bot 會讀取 API 回傳資料。

如果 API 沒有回傳 token usage，Bot 可以使用粗略估算：

```env
USAGE_MODE=api_or_estimate
```

使用量資料會寫入：

```env
USAGE_LOG_FILE=usage_logs.jsonl
```

> 注意:這個檔案是執行時產生的本機紀錄檔，不應上傳到 GitHub 或其他公開平台。

token 使用量結果只適合用於觀察與除錯，不應被視為正式計費資料。

## 隱私與安全

雲端 API 模式可能會將 prompts、暫時使用者上下文與生成回覆傳送到設定的第三方 API provider。

請不要將私人 token、密碼、個人資料、敏感管理紀錄或伺服器機密資訊放進 prompt。

這個 Lite 版本預設只使用 RAM 來暫時記憶，不包含長期 moderation cases、user profiling、music playback、PC monitoring 或永久使用者紀錄。

但是第三方 API provider 可能會依照其服務條款與政策處理或保存資料。使用雲端 API 前，請自行確認該服務的價格、隱私政策、資料保存政策與服務條款。

如果是隱私敏感的伺服器、學校環境，或包含未成年人的社群，可能更適合使用本地 AI 部署。

### 安全提醒

本專案需要 Discord bot token、AI API key 等私人憑證才能運作。

請不要公開：

- `.env` 檔案
- Discord bot token
- API key
- Webhook URL
- 密碼
- runtime logs
- usage logs
- 使用者紀錄
- 私人設定檔

如果不小心公開 Discord token 或 API key，請立刻撤銷或重新產生。

作者不負責因設定錯誤、部署錯誤、修改錯誤或公開上傳私人檔案而造成的 token 外洩、API key 外洩、非預期 API 費用、帳號問題、資料遺失、隱私問題、服務濫用或其他誤用。

## 參考資料

以下連結是本專案在理解 OpenAI-compatible API、MCP-like 工具註冊、tool-calling、router 設計與解耦架構時參考的概念資料。

> 本專案只實作輕量化的 MCP-like 工具註冊展示，並不是完整 MCP protocol 實作。

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

### Router / 解耦架構

* Command Pattern: https://refactoring.guru/design-patterns/command
* Chain of Responsibility Pattern: https://refactoring.guru/design-patterns/chain-of-responsibility
* Strategy Pattern: https://refactoring.guru/design-patterns/strategy
* Refactoring: https://refactoring.com/

實際在專案中使用 MCP、tool-calling、雲端 API 或自動化工具前，仍需要自行確認官方文件、服務條款、價格、隱私政策、資料保存方式與安全限制。


## 授權

完整授權條款與免責聲明請參考 [LICENSE](./LICENSE)。

README 中的安全提醒主要是實際使用上的提醒；`LICENSE` 檔案才是主要授權與免責聲明文件。
