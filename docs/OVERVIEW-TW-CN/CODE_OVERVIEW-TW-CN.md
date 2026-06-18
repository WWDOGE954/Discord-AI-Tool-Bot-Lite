# 程式架構說明

這份文件用來簡單說明本專案的主要 Python 檔案，以及整體技術架構。

主要目標是展示一個輕量化的 Discord AI Bot，包含 OpenAI-compatible API 串接、暫時記憶、token 使用量紀錄，以及兩種簡單的工具層設計。

如果想查看工具路由與 MCP-like（簡化版）架構的更詳細比較，可參考：

[MODE_OVERVIEW-CN.md](./MODE_OVERVIEW-CN.md)

## 檔案結構

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

## Python 檔案說明

這裡主要簡單說明各檔案的用途，並著重在調用架構。
如果有其他問題，歡迎聯絡我。

### `main.py`

`main.py` 是 Discord Bot 的主要進入點。

它主要負責啟動機器人、註冊指令、接收使用者請求，並將請求交給對應的工具模組處理。

簡單來說，`main.py` 負責整合各檔案，並控制 Bot 的主要流程。

### `config.py`

`config.py` 用來從 `.env` 載入設定值。

這樣可以讓 Discord token、API key、模型名稱、工具模式等設定保留在 `.env` 中，而不是直接寫進原始碼。

### `ai_client.py`

`ai_client.py` 負責處理 AI API 請求。

它是以 OpenAI-compatible API 為基礎設計，因此可以用於 OpenRouter、OpenAI、DeepSeek，或其他相容的 API 服務。

當 API 回傳 token usage 資料時，`ai_client.py` 也會將相關資料傳給 `usage_tracker.py`。

### `usage_tracker.py`

`usage_tracker.py` 負責記錄 token 使用量。

如果 API provider 有回傳官方 token usage 資料，Bot 會優先使用 API 回傳的數據。
如果 API 沒有回傳 token 使用量，Bot 會改用粗略估算。

這個功能主要用來觀察 API 使用量，以及簡單比較不同工具模式或不同模型的大致 token 消耗。

### `views.py`

`views.py` 包含簡單的 Discord UI 輔助元件。

它可以用來放置簡單按鈕、提示訊息，或小型互動介面。

將 UI 相關程式碼獨立出來，可以避免 `main.py` 變得太大。

### `mods/common.py`

`mods/common.py` 包含不同工具模組共用的結構或輔助函式。

它的用途是讓 router 模式與 MCP-like 模式可以使用一致的資料格式與回傳邏輯。

### `mods/tool_router_mod.py`

`tool_router_mod.py` 是傳統的解耦工具路由模式。

在這個模式下，`main.py` 會把工具請求交給 router，再由 router 判斷應該執行哪個功能。

詳細說明可參考：

[MODE_OVERVIEW-CN.md](./MODE_OVERVIEW-CN.md)

### `mods/mcp_like_mod.py`

`mcp_like_mod.py` 是小型 MCP-like 工具註冊展示模式。

它會將工具以名稱、描述與處理函式的方式整理，作為 tool-calling 架構的簡化展示。

本專案沒有實作完整 MCP protocol，也不是正式 MCP server。
這裡的 MCP-like 模式只是用來展示工具註冊與工具呼叫概念。

詳細說明可參考：

[MODE_OVERVIEW-CN.md](./MODE_OVERVIEW-CN.md)

## 模式

可以透過 `.env` 切換兩種工具架構模式。

```env
TOOL_MODE=router
```

使用傳統的解耦工具路由模式。

```env
TOOL_MODE=mcp_like
```

使用 MCP-like 工具註冊展示模式。

兩種模式提供的使用者功能大致相同，但內部結構不同。

## 注意事項

### 以 `.env` 管理設定

大部分重要設定都透過 `.env` 控制。

包含 API provider、模型名稱、工具模式、記憶模式與 token 使用量紀錄模式。

因此只要修改 `.env`，就可以切換不同 API provider、模型或工具模式，而不需要重寫整個程式。

### 僅使用暫時記憶

這個 Lite 版本只在啟用記憶功能時使用 RAM 來暫時記憶。

Bot 重啟後，記憶會被清除。

本專案不會保存長期使用者 profile、管理紀錄、案件紀錄或永久聊天紀錄。

> 這並不包含第三方 API provider。使用雲端 API 時，部署者仍需要自行確認 API 服務的隱私政策與資料保存方式。

### Token 使用量紀錄

Bot 可以在 API 回傳 token usage 資料時讀取該資料。

如果 API provider 沒有回傳 token usage，Bot 會改用粗略估算。

估算結果不一定精準，不應被視為正式計費資料。

這個功能主要是用來觀察 token 使用量，以及簡單比較 router 模式與 MCP-like 模式的大致差異。
需要注意的是，即使輸入同一句話，也可能因模型、API provider、回覆內容、暫時記憶或生成狀況不同，而產生不同的 token 使用量，因此結果只能作為參考。

## 參考資料

* OpenAI Chat Completions API: https://developers.openai.com/api/reference/chat-completions/
* OpenRouter Chat Completion API: https://openrouter.ai/docs/api/api-reference/chat/send-chat-completion-request
* OpenRouter Quickstart: https://openrouter.ai/docs/quickstart
* DeepSeek API Docs: https://api-docs.deepseek.com/
* Gemini OpenAI Compatibility: https://ai.google.dev/gemini-api/docs/openai

以上連結是本專案在理解 OpenAI-compatible API 註冊、請求與動作時的參考資料。
 > 注意:實際應用OpenAI-compatible API 格式的學習與開發參考。使用不同 API provider 時，仍需要自行確認該服務的模型名稱、價格、隱私政策、資料保存方式與服務條款。
