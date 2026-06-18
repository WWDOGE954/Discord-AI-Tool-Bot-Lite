# コードアーキテクチャ概要

> 翻訳について：この文書は繁体字中国語版をもとに、AI の補助を受けて翻訳されています。  
> 意味に差異がある場合は、繁体字中国語版を主な基準としてください。

この文書では、本プロジェクトの主な Python ファイルと、全体的な技術構成を簡単に説明します。

主な目的は、OpenAI-compatible API 連携、一時メモリ、token 使用量の記録、そして 2 種類の簡単なツール層設計を含む、軽量な Discord AI Bot を示すことです。

ツールルーターと MCP-like（簡易版）アーキテクチャのより詳しい比較は、次を参照してください：

[MODE_OVERVIEW-JP.md](./MODE_OVERVIEW-JP.md)

## ファイル構成

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

## Python ファイルの説明

ここでは各ファイルの用途を簡単に説明し、特に呼び出し構造に注目します。  
他に質問がある場合は、気軽に連絡してください。

### `main.py`

`main.py` は Discord Bot の主なエントリーポイントです。

Bot の起動、コマンド登録、ユーザーリクエストの受信、そして対応するツールモジュールへの受け渡しを担当します。

簡単に言うと、`main.py` は各ファイルを統合し、Bot の主な処理の流れを制御します。

### `config.py`

`config.py` は `.env` から設定値を読み込みます。

これにより、Discord token、API key、モデル名、ツールモードなどの設定をソースコードに直接書かず、`.env` に保持できます。

### `ai_client.py`

`ai_client.py` は AI API リクエストを処理します。

OpenAI-compatible API を基準に設計されているため、OpenRouter、OpenAI、DeepSeek、またはその他の互換 API サービスで使用できます。

API が token usage データを返した場合、`ai_client.py` はその関連データを `usage_tracker.py` に渡します。

### `usage_tracker.py`

`usage_tracker.py` は token 使用量を記録します。

API provider が公式の token usage データを返す場合、Bot はその API 返却データを優先して使用します。  
API が token 使用量を返さない場合、Bot は大まかな推定値を使用します。

この機能は主に API 使用量を観察し、異なるツールモードやモデル間のおおよその token 消費量を比較するためのものです。

### `views.py`

`views.py` には簡単な Discord UI 補助コンポーネントが含まれます。

簡単なボタン、通知メッセージ、小さなインタラクティブ UI などに使用できます。

UI 関連のコードを分離することで、`main.py` が大きくなりすぎるのを防げます。

### `mods/common.py`

`mods/common.py` には、異なるツールモジュールで共有される構造や補助関数が含まれます。

router モードと MCP-like モードが同じデータ形式と戻り値のロジックを使えるようにするためのものです。

### `mods/tool_router_mod.py`

`tool_router_mod.py` は従来型の分離されたツールルーターモードです。

このモードでは、`main.py` がツールリクエストを router に渡し、router がどの機能を実行するか判断します。

詳細は次を参照してください：

[MODE_OVERVIEW-JP.md](./MODE_OVERVIEW-JP.md)

### `mods/mcp_like_mod.py`

`mcp_like_mod.py` は小型の MCP-like ツール登録デモモードです。

ツールを名前、説明、処理関数として整理し、tool-calling アーキテクチャの簡易デモとして示します。

本プロジェクトは完全な MCP protocol を実装しておらず、正式な MCP server でもありません。  
ここでの MCP-like モードは、ツール登録とツール呼び出しの概念を示すためのものです。

詳細は次を参照してください：

[MODE_OVERVIEW-JP.md](./MODE_OVERVIEW-JP.md)

## モード

`.env` を通して 2 種類のツールアーキテクチャモードを切り替えられます。

```env
TOOL_MODE=router
```

従来型の分離されたツールルーターモードを使用します。

```env
TOOL_MODE=mcp_like
```

MCP-like ツール登録デモモードを使用します。

2 つのモードはユーザー向けの機能としてはおおむね同じですが、内部構造が異なります。

## 注意事項

### `.env` で設定を管理する

重要な設定の多くは `.env` で制御されます。

API provider、モデル名、ツールモード、メモリモード、token 使用量記録モードなどが含まれます。

そのため `.env` を変更するだけで、プログラム全体を書き換えずに API provider、モデル、ツールモードを切り替えられます。

### 一時メモリのみを使用

この Lite 版は、メモリ機能を有効にした場合のみ RAM 上の一時メモリを使用します。

Bot を再起動すると、メモリは消去されます。

本プロジェクトは、長期的な user profile、モデレーション記録、case 記録、永続的なチャットログを保存しません。

> ただし、これは第三者 API provider には適用されません。クラウド API を使用する場合、デプロイする人は API サービスのプライバシーポリシーとデータ保存方法を自分で確認する必要があります。

### Token 使用量の記録

Bot は API が token usage データを返した場合、そのデータを読み取れます。

API provider が token usage を返さない場合、Bot は大まかな推定値を使用します。

推定結果は必ずしも正確ではなく、正式な課金データとして扱うべきではありません。

この機能は主に token 使用量を観察し、router モードと MCP-like モードのおおよその差を比較するためのものです。  
同じ入力であっても、モデル、API provider、返信内容、一時メモリ、生成状況によって token 使用量が変わる場合があるため、結果は参考程度にしてください。

## 参考資料

* OpenAI Chat Completions API: https://developers.openai.com/api/reference/chat-completions/
* OpenRouter Chat Completion API: https://openrouter.ai/docs/api/api-reference/chat/send-chat-completion-request
* OpenRouter Quickstart: https://openrouter.ai/docs/quickstart
* DeepSeek API Docs: https://api-docs.deepseek.com/
* Gemini OpenAI Compatibility: https://ai.google.dev/gemini-api/docs/openai

上記のリンクは、本プロジェクトで OpenAI-compatible API の登録、リクエスト、動作を理解するために参照した資料です。  
> 注意：OpenAI-compatible API 形式を学習・開発に利用する場合でも、使用する API provider ごとにモデル名、価格、プライバシーポリシー、データ保存方式、利用規約を確認する必要があります。
