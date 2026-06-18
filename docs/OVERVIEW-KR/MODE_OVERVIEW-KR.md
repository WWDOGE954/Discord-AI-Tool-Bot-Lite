# 모드 개요: Router와 MCP-like 도구 아키텍처

> 번역 안내: 이 문서는 번체 중국어 버전을 기준으로 AI의 도움을 받아 번역되었습니다.  
> 의미가 서로 다를 경우, 번체 중국어 버전을 기본 기준으로 봐 주세요.

이 문서는 본 프로젝트의 두 가지 도구 호출 모드를 설명합니다. 또한 각 모드의 명령 흐름, 도구 등록 원리, 그리고 이 구조를 지원하기 위해 코드를 어떻게 분리했는지도 자세히 설명합니다.

본 프로젝트는 두 가지 모드를 지원합니다:

```env
TOOL_MODE=router
```

전통적인 분리형 도구 라우터를 사용합니다.

```env
TOOL_MODE=mcp_like
```

MCP-like 도구 등록 데모 모드를 사용합니다.

두 모드는 Discord 명령어 관점에서는 대체로 같은 기능을 제공하지만, 내부 도구 구성 방식이 다릅니다.

## 목차

* [서문](#서문)
* [Discord 명령 흐름](#discord-명령-흐름)
* [Discord 명령과 내부 도구 이름 대응](#discord-명령과-내부-도구-이름-대응)
* [Router 모드의 기본 개념](#router-모드의-기본-개념)
* [Router 모드가 도구를 호출하는 방식](#router-모드가-도구를-호출하는-방식)
* [Router 모드의 장점과 한계](#router-모드의-장점과-한계)
* [MCP-like 모드의 기본 개념](#mcp-like-모드의-기본-개념)
* [MCP-like 도구 등록 원리](#mcp-like-도구-등록-원리)
* [`register_tool()`이 하는 일](#register_tool이-하는-일)
* [MCP-like 모드가 도구를 호출하는 방식](#mcp-like-모드가-도구를-호출하는-방식)
* [왜 MCP-like 모드는 여전히 router의 기능 로직을 공유하는가](#왜-mcp-like-모드는-여전히-router의-기능-로직을-공유하는가)
* [요약](#요약)
* [마무리](#마무리)
* [참고 자료](#참고-자료)

## 서문

간단히 말하면, 두 모드는 도구를 정리하는 서로 다른 방식으로 생각할 수 있습니다.

`router` 모드는 다기능 스위스 아미 나이프와 비슷합니다.  
간단하고 직접적이며 리소스 부담이 비교적 작아서, 작은 프로젝트에서 기능을 빠르게 분배하기에 적합합니다. 하지만 도구가 많아지면 내부 조건 분기가 점점 비대해질 수 있고, 이후에는 더 나은 분류와 정리가 필요할 수 있습니다.

`mcp_like` 모드는 잘 정리된 도구 상자에 가깝습니다.  
각 도구는 이름, 설명, 처리 함수를 가지고 있어 구조가 더 명확하며 tool-calling 개념에 더 가깝습니다. 다만 미래에 많은 도구 설명이나 parameter schema를 AI에게 제공하게 된다면 prompt 또는 token 사용량이 증가할 수 있습니다.

> 주의: 본 프로젝트의 `mcp_like`는 매우 간소화된 데모 버전입니다. 완전한 MCP protocol을 구현하지 않았고, AI가 스스로 도구를 선택하는 기능도 없습니다.

---

## Discord 명령 흐름

사용자는 Discord에서 다음과 같은 slash command를 입력합니다:

```text
/ai
/status
/usage
/privacy
/forget
```

이 명령들은 먼저 `main.py`에서 받습니다.

`main.py` 자체가 모든 기능을 직접 처리하지는 않습니다. 대신 현재 선택된 도구 모듈로 요청을 전달합니다.

`main.py`에서는 `.env` 설정에 따라 사용할 도구 모듈을 결정합니다:

```python
if config.TOOL_MODE == "mcp_like":
    from mods.mcp_like_mod import handle_tool
else:
    from mods.tool_router_mod import handle_tool
```

따라서 현재 모드가 `router`이든 `mcp_like`이든, `main.py`는 같은 함수만 호출하면 됩니다:

```python
result = await handle_tool(...)
```

이렇게 하면 `main.py`는 깔끔하게 유지되고, Discord Bot 시작, 명령어 등록, 상호작용 응답에 집중할 수 있습니다.

---

## Discord 명령과 내부 도구 이름 대응

본 프로젝트의 slash commands는 내부 도구 이름에 대응됩니다.

| Discord 명령 | 내부 도구 이름 | 기능 |
| ---------- | --------- | ------------------- |
| `/ai` | `ask_ai` | 사용자 입력을 AI API로 보내고 응답을 반환 |
| `/forget` | `forget` | 사용자의 임시 메모리를 삭제 |
| `/status` | `status` | Bot의 현재 설정과 아키텍처 모드를 표시 |
| `/usage` | `usage` | token 사용량 통계를 표시 |
| `/privacy` | `privacy` | 클라우드 API 개인정보 관련 안내를 표시 |

예를 들어 `/ai` 명령은 다음과 같이 호출됩니다:

```python
handle_tool(
    "ask_ai",
    prompt=prompt,
    user_id=str(interaction.user.id),
    display_name=interaction.user.display_name,
)
```

`main.py`는 `ask_ai` 내부에서 실제로 API를 어떻게 호출하는지 알 필요가 없습니다. 요청을 도구 계층으로 전달하기만 하면 됩니다.

---

## Router 모드의 기본 개념

`tool_router_mod.py`는 전통적인 분리형 도구 라우터 모드입니다.

방식은 다음과 같습니다:  
`main.py`가 도구 이름을 `handle_tool()`에 전달하면, router가 조건 판단으로 어떤 기능을 실행할지 결정합니다.

간단한 예시는 다음과 같습니다:

```python
async def handle_tool(tool_name: str, **kwargs):
    if tool_name == "ask_ai":
        return await _ask_ai_tool(**kwargs)
    if tool_name == "forget":
        return _forget_tool(**kwargs)
    if tool_name == "status":
        return _status_tool()
```

이 방식은 직관적이며 작은 프로젝트에 적합합니다.

장점은 이해하기 쉽고 수정하기 쉽다는 것입니다.  
단점은 도구가 많아질수록 router 안에 `if` 판단이 많이 쌓일 수 있고, 이후 더 나은 분류 방식이 필요할 수 있다는 점입니다.

---

## Router 모드가 도구를 호출하는 방식

`router` 모드에서는 모든 도구 요청이 먼저 `tool_router_mod.py`의 `handle_tool()`로 들어갑니다.

`main.py`는 도구 이름과 필요한 인자만 전달하면 됩니다:

```python
result = await handle_tool(
    "ask_ai",
    prompt=prompt,
    user_id=str(interaction.user.id),
    display_name=interaction.user.display_name,
)
```

그 다음 `tool_router_mod.py`는 `tool_name`에 따라 어떤 기능을 실행할지 판단합니다.

간단한 흐름은 다음과 같습니다:

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

즉, router 모드는 일종의 “기능 분배 센터”와 같습니다.

각 도구를 독립적인 등록 항목으로 정리하지 않고, 조건 판단을 통해 서로 다른 도구 이름을 서로 다른 처리 함수로 연결합니다.

이 도구들은 최종적으로 통일된 `ToolResult`를 반환합니다.

## Router 모드의 장점과 한계

Router 모드의 장점은 간단하고 직관적이며, 작은 프로젝트에 적합하다는 것입니다.

흐름은 대략 다음과 같습니다:

```text
Discord command
↓
main.py
↓
handle_tool(tool_name, ...)
↓
if tool_name == ...
↓
corresponding tool function
↓
ToolResult
↓
Discord response
```

이 방식은 이해하기 쉽고, 별도의 도구 등록표나 schema 설계가 필요하지 않습니다.

하지만 도구 수가 증가하면 `handle_tool()` 안의 조건 판단도 많아지고, router 자체가 비대해질 수 있습니다.

따라서 router 모드는 다음 상황에 적합합니다:

* 작은 프로젝트
* 도구 수가 많지 않은 경우
* 기능 분배를 빠르게 구현하고 싶은 경우
* 프로그램 흐름을 단순하고 읽기 쉽게 유지하고 싶은 경우

나중에 도구가 많아지거나, 각 도구에 더 명확한 이름, 설명, parameter 형식이 필요해진다면 MCP-like 도구 등록 아키텍처를 고려할 수 있습니다.

## MCP-like 모드의 기본 개념

`mcp_like_mod.py`는 작은 MCP-like 도구 등록 아키텍처를 보여 줍니다.

여기서 MCP-like는 공식 MCP server가 아니며, 완전한 MCP protocol도 구현하지 않았습니다.

본 프로젝트는 단순한 방식으로 다음 개념을 보여 줍니다:

* 도구는 등록될 수 있다
* 도구는 이름을 가질 수 있다
* 도구는 설명을 가질 수 있다
* 도구는 parameter 설명을 가질 수 있다
* 도구는 통일된 형식으로 호출될 수 있다

즉, 도구는 단순히 `if` 판단 안에만 쓰이는 것이 아니라 하나하나의 “도구 항목”으로 정리됩니다.

---

## MCP-like 도구 등록 원리

`mcp_like_mod.py`에서는 각 도구가 `MCPTool`로 감싸집니다.

```python
@dataclass
class MCPTool:
    name: str
    description: str
    parameters: dict[str, Any]
    handler: ToolHandler
```

각 도구는 다음을 포함합니다:

| 필드 | 역할 |
| ------------- | ---------------- |
| `name` | 도구 이름, 예: `ask_ai` |
| `description` | 도구의 용도 설명 |
| `parameters` | 도구에 필요한 parameter 설명 |
| `handler` | 실제 기능을 실행하는 함수 |

도구는 `_TOOLS` 딕셔너리에 저장됩니다:

```python
_TOOLS: dict[str, MCPTool] = {}
```

이 `_TOOLS`는 간단한 도구 등록표로 이해할 수 있습니다.

---

## `register_tool()`이 하는 일

`register_tool()`은 도구를 등록하기 위한 decorator입니다.

간단한 개념은 다음과 같습니다:

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

사용 예시는 다음과 같습니다:

```python
@register_tool(
    "ask_ai",
    "Send a user prompt to the configured AI API and return the assistant reply.",
    {"prompt": "string", "user_id": "string", "display_name": "string"},
)
async def _ask_ai(**kwargs):
    return await router_tools.handle_tool("ask_ai", **kwargs)
```

이 코드는 다음을 의미합니다:

1. `ask_ai`라는 이름의 도구를 만든다
2. 도구 설명을 추가한다
3. parameter 형식 설명을 추가한다
4. `_ask_ai()`를 실제 handler로 지정한다
5. 이 도구를 `_TOOLS` 등록표에 넣는다

이후 다음과 같이 호출하면:

```python
handle_tool("ask_ai", ...)
```

프로그램은 `_TOOLS`에서 `ask_ai`를 찾고, 그에 대응하는 handler function을 실행합니다.

---

## MCP-like 모드가 도구를 호출하는 방식

`mcp_like_mod.py`의 `handle_tool()`은 세 가지 일을 합니다:

1. 도구 이름으로 도구를 찾는다
2. 해당 도구의 handler를 실행한다
3. handler가 async라면 완료될 때까지 기다린다

간단한 흐름은 다음과 같습니다:

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

따라서 MCP-like 모드의 개념적 흐름은 다음과 같습니다:

```text
Discord command
↓
main.py
↓
mcp_like_mod.py
↓
_TOOLS tool registry
↓
registered tool handler
↓
ai_client.py / usage_tracker.py / memory
↓
Discord response
```

## 왜 MCP-like 모드는 여전히 router의 기능 로직을 공유하는가

> 간단히 말하면: 경량화와 핵심 개념에 집중하기 위해서입니다.

본 프로젝트에서 `mcp_like_mod.py`는 주로 “도구 등록”과 “도구 호출” 개념을 보여 주기 위해 사용됩니다.

프로젝트를 가볍게 유지하기 위해 `mcp_like` 모드는 AI, usage, memory 처리 로직을 처음부터 다시 작성하지 않습니다. 대신 router 모드에서 이미 정리된 기능을 가능한 한 재사용합니다.

이 방식의 장점은 다음과 같습니다:

* 동일한 기능의 중복 구현을 피할 수 있음
* 두 모드의 사용자 기능을 일관되게 유지할 수 있음
* `mcp_like_mod.py`가 도구 등록 아키텍처 설명에 집중할 수 있음
* 프로젝트를 작고 읽기 쉬우며 비교하기 쉽게 유지할 수 있음

즉, 이 버전의 `mcp_like`는 도구 계층 위에 추가된 “등록 데모 계층”에 가깝고, 모든 하위 기능을 완전히 대체하는 독립 MCP 시스템은 아닙니다.

구현하지 않은 것들:

* MCP client/server 통신
* MCP protocol message format
* 외부 도구 discovery
* 완전한 schema 검증
* AI가 실제로 스스로 도구를 선택하는 기능

현재는 “도구 등록표” 개념을 가볍게 보여 줄 뿐입니다.

즉, 이것에 더 가깝습니다:

```text
MCP-like tool registry demo
```

다음과는 다릅니다:

```text
Full MCP implementation
```

이런 설계를 선택한 이유는 본 프로젝트의 주요 목표가 완전한 MCP 시스템을 구현하는 것이 아니라, 단순하고 읽기 쉬우며 설명하기 쉬운 상태를 유지하는 것이기 때문입니다.

---

## 요약

본 프로젝트의 MCP-like 모드는 주로 “도구 등록”과 “도구 호출” 개념을 보여 줍니다.

`MCPTool`, `register_tool()`, `_TOOLS`, `handle_tool()`을 통해 도구를 이름, 설명, parameter, 처리 함수를 가진 항목으로 정리할 수 있습니다.

완전한 MCP protocol은 아니지만, tool-calling 아키텍처의 기본적인 형태를 보여 줄 수 있습니다.

이를 통해 프로젝트를 가볍게 유지하면서 다음을 설명할 수 있습니다:

* Discord 명령이 어떻게 도구 계층으로 들어가는가
* 도구가 어떻게 등록되는가
* 도구가 어떻게 호출되는가
* API, usage, memory가 어떻게 독립 모듈로 분리되는가
* 전통적인 router와 MCP-like 아키텍처의 차이

## 마무리

MCP-style 아키텍처의 장점은 명확하고 정돈된 구조를 가지며, 각 도구를 명확하게 설명할 수 있다는 점입니다. 하지만 도구 설명, parameter schema, context를 모두 AI에게 제공하면 token 및 리소스 소비가 높아질 수 있습니다.

Router 아키텍처는 더 단순하고 직접적입니다. 작은 프로젝트에서는 더 가볍고 빠르게 구현하기 쉽습니다. 하지만 도구가 많아지면 router 내부도 비대해질 수 있으며, 추가 정리가 필요할 수 있습니다.

따라서 이 두 방식은 반드시 누가 누구를 대체하는 관계는 아닙니다. 프로젝트의 규모와 요구에 따라 적합한 방식이 달라질 수 있습니다.  
이 Lite Bot의 목표는 완전한 MCP 시스템을 만드는 것이 아니라, 작은 예시를 통해 “전통적인 분리”와 “도구 등록”이라는 두 가지 사고방식의 차이를 이해하는 것입니다.

> 여기까지 읽어 주셔서 감사합니다 :D

## 참고 자료

다음 링크들은 본 프로젝트에서 MCP-like 도구 등록, tool-calling, router, 분리형 아키텍처를 이해하기 위해 참고한 개념 자료입니다.  
본 프로젝트의 `mcp_like` 모드는 간소화된 데모일 뿐이며, 완전한 MCP protocol 구현이 아닙니다.

### MCP / Tool-calling

* Model Context Protocol Introduction: https://modelcontextprotocol.io/docs/getting-started/intro
* MCP Tools Specification: https://modelcontextprotocol.io/specification/2025-06-18/server/tools
* OpenAI Function Calling Guide: https://developers.openai.com/api/docs/guides/function-calling

### Router / 분리형 아키텍처

* Command Pattern: https://refactoring.guru/design-patterns/command
* Chain of Responsibility Pattern: https://refactoring.guru/design-patterns/chain-of-responsibility
* Strategy Pattern: https://refactoring.guru/design-patterns/strategy
* Refactoring: https://refactoring.com/

위 링크들은 학습과 개발을 위한 참고용입니다.  
MCP, tool-calling, 클라우드 API 또는 자동화 도구를 실제로 사용할 때는 관련 문서, 서비스 약관, 안전 제한, 데이터 처리 방식을 직접 확인해야 합니다.
