# モード概要：Router と MCP-like ツールアーキテクチャ

> 翻訳について：この文書は繁体字中国語版をもとに、AI の補助を受けて翻訳されています。  
> 意味に差異がある場合は、繁体字中国語版を主な基準としてください。

この文書では、本プロジェクトにおける 2 種類のツール呼び出しモードを説明します。また、各モードのコマンドフロー、ツール登録の仕組み、そしてこの構成を支えるために行ったコード分割についても説明します。

本プロジェクトは次の 2 つのモードをサポートします：

```env
TOOL_MODE=router
```

従来型の分離されたツールルーターを使用します。

```env
TOOL_MODE=mcp_like
```

MCP-like ツール登録デモモードを使用します。

2 つのモードは Discord コマンドとしてはおおむね同じ機能を提供しますが、内部でのツールの整理方法が異なります。

## 目次

* [はじめに](#はじめに)
* [Discord コマンドの流れ](#discord-コマンドの流れ)
* [Discord コマンドと内部ツール名の対応](#discord-コマンドと内部ツール名の対応)
* [Router モードの基本概念](#router-モードの基本概念)
* [Router モードがツールを呼び出す方法](#router-モードがツールを呼び出す方法)
* [Router モードの利点と制限](#router-モードの利点と制限)
* [MCP-like モードの基本概念](#mcp-like-モードの基本概念)
* [MCP-like ツール登録の仕組み](#mcp-like-ツール登録の仕組み)
* [`register_tool()` が行うこと](#register_tool-が行うこと)
* [MCP-like モードがツールを呼び出す方法](#mcp-like-モードがツールを呼び出す方法)
* [なぜ MCP-like モードは router の機能ロジックを共用するのか](#なぜ-mcp-like-モードは-router-の機能ロジックを共用するのか)
* [まとめ](#まとめ)
* [あとがき](#あとがき)
* [参考資料](#参考資料)

## はじめに

簡単に言うと、2 つのモードはツールの整理方法が異なるものとして考えられます。

`router` モードは、多機能なスイスアーミーナイフのようなものです。  
シンプルで直接的、リソース消費も比較的小さく、小規模プロジェクトで素早く機能を振り分けるのに適しています。ただし、ツールが増えると内部の条件分岐が徐々に肥大化する可能性があり、後からより良い分類や整理が必要になります。

`mcp_like` モードは、整理された工具箱のようなものです。  
各ツールに名前、説明、処理関数があり、構造がより明確で、tool-calling の考え方に近くなります。ただし、将来的に大量のツール説明やパラメータ schema を AI に渡す場合、prompt や token 使用量が増える可能性があります。

> 注意：本プロジェクトの `mcp_like` は高度に簡略化されたデモ版です。完全な MCP protocol は実装しておらず、AI が自律的にツールを選択する仕組みもありません。

---

## Discord コマンドの流れ

ユーザーは Discord で次のような slash command を入力します：

```text
/ai
/status
/usage
/privacy
/forget
```

これらのコマンドはまず `main.py` に受け取られます。

`main.py` 自体はすべての機能を直接処理しません。代わりに、現在選択されているツールモジュールへリクエストを渡します。

`main.py` では、`.env` の設定に基づいて使用するツールモジュールを決定します：

```python
if config.TOOL_MODE == "mcp_like":
    from mods.mcp_like_mod import handle_tool
else:
    from mods.tool_router_mod import handle_tool
```

そのため、現在のモードが `router` でも `mcp_like` でも、`main.py` は同じ関数を呼び出すだけで済みます：

```python
result = await handle_tool(...)
```

これにより `main.py` は整理された状態を保ち、Discord Bot の起動、コマンド登録、インタラクションへの返信に集中できます。

---

## Discord コマンドと内部ツール名の対応

本プロジェクトの slash commands は、内部ツール名に対応しています。

| Discord コマンド | 内部ツール名 | 機能 |
| ---------- | --------- | ------------------- |
| `/ai` | `ask_ai` | ユーザー入力を AI API に送り、返信を返す |
| `/forget` | `forget` | ユーザーの一時メモリを消去する |
| `/status` | `status` | Bot の現在の設定とアーキテクチャモードを表示する |
| `/usage` | `usage` | token 使用量の統計を表示する |
| `/privacy` | `privacy` | クラウド API に関するプライバシー注意を表示する |

例えば `/ai` コマンドは次のように呼び出します：

```python
handle_tool(
    "ask_ai",
    prompt=prompt,
    user_id=str(interaction.user.id),
    display_name=interaction.user.display_name,
)
```

`main.py` は `ask_ai` の内部で実際に API をどう呼ぶかを知る必要はありません。リクエストをツール層に渡すだけです。

---

## Router モードの基本概念

`tool_router_mod.py` は従来型の分離されたツールルーターモードです。

考え方は次の通りです：  
`main.py` がツール名を `handle_tool()` に渡し、router が条件分岐によって実行すべき機能を判断します。

簡略化した例：

```python
async def handle_tool(tool_name: str, **kwargs):
    if tool_name == "ask_ai":
        return await _ask_ai_tool(**kwargs)
    if tool_name == "forget":
        return _forget_tool(**kwargs)
    if tool_name == "status":
        return _status_tool()
```

この方法は直感的で、小規模プロジェクトに適しています。

利点は理解しやすく、変更もしやすいことです。  
一方で、ツール数が増えると router 内に多くの `if` 分岐が蓄積される可能性があり、後からより良い分類が必要になる場合があります。

---

## Router モードがツールを呼び出す方法

`router` モードでは、すべてのツールリクエストがまず `tool_router_mod.py` の `handle_tool()` に入ります。

`main.py` はツール名と必要なパラメータを渡すだけです：

```python
result = await handle_tool(
    "ask_ai",
    prompt=prompt,
    user_id=str(interaction.user.id),
    display_name=interaction.user.display_name,
)
```

その後、`tool_router_mod.py` は `tool_name` に基づいて実行する機能を判断します。

簡略化した流れ：

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

つまり router モードは「機能の振り分けセンター」のようなものです。

各ツールを独立した登録項目として整理するのではなく、条件分岐によって異なるツール名を異なる処理関数へ導きます。

これらのツールは最終的に統一された `ToolResult` を返します。

## Router モードの利点と制限

Router モードの利点は、シンプルで直感的であり、小規模プロジェクトに適していることです。

流れはおおよそ次の通りです：

```text
Discord command
↓
main.py
↓
handle_tool(tool_name, ...)
↓
if tool_name == ...
↓
対応するツール関数
↓
ToolResult
↓
Discord response
```

この方法は理解しやすく、追加のツール登録表や schema 設計も必要ありません。

ただし、ツール数が増えると `handle_tool()` 内の条件分岐も増え、router 自体が肥大化する可能性があります。

そのため router モードは次のような場合に向いています：

* 小規模プロジェクト
* ツール数が少ない場合
* 素早く機能を振り分けたい場合
* プログラムの流れをシンプルで読みやすく保ちたい場合

将来的にツールが増えたり、各ツールにより明確な名前、説明、パラメータ形式が必要になった場合は、MCP-like ツール登録アーキテクチャを検討できます。

## MCP-like モードの基本概念

`mcp_like_mod.py` は小型の MCP-like ツール登録アーキテクチャを示します。

ここでの MCP-like は正式な MCP server ではなく、完全な MCP protocol も実装していません。

本プロジェクトは、次の概念をシンプルに示すだけです：

* ツールを登録できる
* ツールには名前を付けられる
* ツールには説明を付けられる
* ツールにはパラメータ説明を持たせられる
* ツールを統一された形式で呼び出せる

つまり、ツールは単に `if` 分岐の中に書かれるだけでなく、1 つ 1 つの「ツール項目」として整理されます。

---

## MCP-like ツール登録の仕組み

`mcp_like_mod.py` では、各ツールが `MCPTool` としてラップされます。

```python
@dataclass
class MCPTool:
    name: str
    description: str
    parameters: dict[str, Any]
    handler: ToolHandler
```

各ツールには次の要素があります：

| 項目 | 役割 |
| ------------- | ---------------- |
| `name` | ツール名。例：`ask_ai` |
| `description` | ツールの用途説明 |
| `parameters` | ツールに必要なパラメータの説明 |
| `handler` | 実際に機能を実行する関数 |

ツールは `_TOOLS` 辞書に保存されます：

```python
_TOOLS: dict[str, MCPTool] = {}
```

この `_TOOLS` は、簡単なツール登録表として理解できます。

---

## `register_tool()` が行うこと

`register_tool()` はツールを登録するための decorator です。

簡略化した概念：

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

使用例：

```python
@register_tool(
    "ask_ai",
    "Send a user prompt to the configured AI API and return the assistant reply.",
    {"prompt": "string", "user_id": "string", "display_name": "string"},
)
async def _ask_ai(**kwargs):
    return await router_tools.handle_tool("ask_ai", **kwargs)
```

このコードは次の意味です：

1. `ask_ai` という名前のツールを作成する
2. ツール説明を追加する
3. パラメータ形式の説明を追加する
4. `_ask_ai()` を実際の handler として指定する
5. このツールを `_TOOLS` 登録表に入れる

その後、次のように呼び出すと：

```python
handle_tool("ask_ai", ...)
```

プログラムは `_TOOLS` から `ask_ai` を見つけ、その対応する handler function を実行します。

---

## MCP-like モードがツールを呼び出す方法

`mcp_like_mod.py` の `handle_tool()` は 3 つのことを行います：

1. ツール名でツールを探す
2. そのツールの handler を実行する
3. handler が async の場合は完了を待つ

簡略化した流れ：

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

したがって、MCP-like モードの概念的な流れは次の通りです：

```text
Discord command
↓
main.py
↓
mcp_like_mod.py
↓
_TOOLS ツール登録表
↓
registered tool handler
↓
ai_client.py / usage_tracker.py / memory
↓
Discord response
```

## なぜ MCP-like モードは router の機能ロジックを共用するのか

> 簡単に言うと：軽量化と核心概念への集中のためです。

本プロジェクトでは、`mcp_like_mod.py` は主に「ツール登録」と「ツール呼び出し」の概念を示すために使われます。

プロジェクトを軽量に保つため、`mcp_like` モードでは AI、usage、memory の処理ロジックを一式書き直していません。代わりに、router モードで既に整理された機能をできるだけ共用します。

利点は次の通りです：

* 同じ機能の重複実装を避けられる
* 2 つのモードでユーザー向け機能を一致させられる
* `mcp_like_mod.py` がツール登録アーキテクチャの説明に集中できる
* プロジェクトを小さく、読みやすく、比較しやすく保てる

つまり、この `mcp_like` はツール層の上に追加された「登録デモ層」に近く、下層機能をすべて置き換える独立した MCP システムではありません。

実装していないもの：

* MCP client/server 通信
* MCP protocol message format
* 外部ツール discovery
* 完全な schema 検証
* AI による真の自律的ツール選択

現在は「ツール登録表」の概念を軽量に示しているだけです。

つまり、これは次に近いものです：

```text
MCP-like tool registry demo
```

次のようなものではありません：

```text
Full MCP implementation
```

このような設計にしている理由は、本プロジェクトの主な目的が、完全な MCP システムの実装ではなく、シンプルで読みやすく、説明しやすい状態を保つことだからです。

---

## まとめ

本プロジェクトの MCP-like モードは、主に「ツール登録」と「ツール呼び出し」の概念を示します。

`MCPTool`、`register_tool()`、`_TOOLS`、`handle_tool()` によって、ツールを名前、説明、パラメータ、処理関数を持つ項目として整理できます。

完全な MCP protocol ではありませんが、tool-calling アーキテクチャの基本的な形を示すことができます。

これにより、プロジェクトを軽量に保ちながら、次のことを説明できます：

* Discord コマンドがどのようにツール層へ入るか
* ツールがどのように登録されるか
* ツールがどのように呼び出されるか
* API、usage、memory がどのように独立したモジュールへ分割されるか
* 従来型 router と MCP-like アーキテクチャの違い

## あとがき

MCP-style アーキテクチャの利点は、明確で整った構造を持ち、各ツールをはっきり説明できることです。ただし、ツール説明、パラメータ schema、コンテキストをすべて AI に渡す場合、token とリソース消費が高くなる可能性があります。

Router アーキテクチャはよりシンプルで直接的です。小規模プロジェクトでは軽量で、素早く実装しやすいです。ただし、ツール数が増えると router 内部も肥大化し、さらに整理が必要になる場合があります。

そのため、この 2 つは必ずしもどちらかがどちらかを置き換えるものではありません。プロジェクトの規模や目的によって向き不向きがあります。  
この Lite Bot の目的は、完全な MCP システムを作ることではなく、小さな例を通して「従来型の分離」と「ツール登録」という 2 つの考え方の違いを理解することです。

> ここまで読んでくれてありがとうございます :D

## 参考資料

以下のリンクは、本プロジェクトで MCP-like ツール登録、tool-calling、router、分離されたアーキテクチャを理解するために参照した概念資料です。  
本プロジェクトの `mcp_like` モードは簡易デモであり、完全な MCP protocol 実装ではありません。

### MCP / Tool-calling

* Model Context Protocol Introduction: https://modelcontextprotocol.io/docs/getting-started/intro
* MCP Tools Specification: https://modelcontextprotocol.io/specification/2025-06-18/server/tools
* OpenAI Function Calling Guide: https://developers.openai.com/api/docs/guides/function-calling

### Router / 分離アーキテクチャ

* Command Pattern: https://refactoring.guru/design-patterns/command
* Chain of Responsibility Pattern: https://refactoring.guru/design-patterns/chain-of-responsibility
* Strategy Pattern: https://refactoring.guru/design-patterns/strategy
* Refactoring: https://refactoring.com/

これらのリンクは学習と開発の参考用です。  
MCP、tool-calling、クラウド API、自動化ツールを実際に使用する場合は、関連ドキュメント、利用規約、安全制限、データ処理方式を自分で確認する必要があります。
