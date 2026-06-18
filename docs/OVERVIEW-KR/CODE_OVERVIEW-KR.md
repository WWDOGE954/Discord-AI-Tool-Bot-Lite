# 코드 아키텍처 개요

> 번역 안내: 이 문서는 번체 중국어 버전을 기준으로 AI의 도움을 받아 번역되었습니다.  
> 의미가 서로 다를 경우, 번체 중국어 버전을 기본 기준으로 봐 주세요.

이 문서는 본 프로젝트의 주요 Python 파일과 전체 기술 구조를 간단히 설명합니다.

주요 목표는 OpenAI-compatible API 연동, 임시 메모리, token 사용량 기록, 그리고 두 가지 간단한 도구 계층 설계를 포함한 가벼운 Discord AI Bot을 보여 주는 것입니다.

도구 라우터와 MCP-like（간소화 버전）아키텍처의 더 자세한 비교는 다음 문서를 참고하세요:

[MODE_OVERVIEW-KR.md](./MODE_OVERVIEW-KR.md)

## 파일 구조

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

## Python 파일 설명

여기서는 각 파일의 용도를 간단히 설명하고, 특히 호출 구조에 초점을 둡니다.  
다른 질문이 있다면 편하게 연락해 주세요.

### `main.py`

`main.py`는 Discord Bot의 주요 진입점입니다.

Bot을 시작하고, 명령어를 등록하며, 사용자 요청을 받고, 해당 요청을 알맞은 도구 모듈로 전달하는 역할을 합니다.

간단히 말하면, `main.py`는 각 파일을 통합하고 Bot의 주요 흐름을 제어합니다.

### `config.py`

`config.py`는 `.env`에서 설정값을 불러옵니다.

이를 통해 Discord token, API key, 모델 이름, 도구 모드 등의 설정을 소스 코드에 직접 쓰지 않고 `.env`에 보관할 수 있습니다.

### `ai_client.py`

`ai_client.py`는 AI API 요청을 처리합니다.

OpenAI-compatible API를 기반으로 설계되어 있으므로 OpenRouter, OpenAI, DeepSeek 또는 기타 호환 API 서비스와 함께 사용할 수 있습니다.

API가 token usage 데이터를 반환하면, `ai_client.py`는 관련 데이터를 `usage_tracker.py`로 전달합니다.

### `usage_tracker.py`

`usage_tracker.py`는 token 사용량을 기록합니다.

API provider가 공식 token usage 데이터를 반환하면 Bot은 API가 반환한 데이터를 우선 사용합니다.  
API가 token 사용량을 반환하지 않으면 Bot은 대략적인 추정값을 사용합니다.

이 기능은 주로 API 사용량을 관찰하고, 서로 다른 도구 모드나 모델 간의 대략적인 token 소비량을 비교하는 데 사용됩니다.

### `views.py`

`views.py`에는 간단한 Discord UI 보조 컴포넌트가 포함되어 있습니다.

간단한 버튼, 안내 메시지 또는 작은 상호작용 인터페이스에 사용할 수 있습니다.

UI 관련 코드를 분리하면 `main.py`가 너무 커지는 것을 피할 수 있습니다.

### `mods/common.py`

`mods/common.py`에는 서로 다른 도구 모듈에서 공통으로 사용하는 구조나 보조 함수가 들어 있습니다.

router 모드와 MCP-like 모드가 일관된 데이터 형식과 반환 로직을 사용할 수 있도록 하는 것이 목적입니다.

### `mods/tool_router_mod.py`

`tool_router_mod.py`는 전통적인 분리형 도구 라우터 모드입니다.

이 모드에서 `main.py`는 도구 요청을 router에 전달하고, router가 어떤 기능을 실행할지 판단합니다.

자세한 설명은 다음 문서를 참고하세요:

[MODE_OVERVIEW-KR.md](./MODE_OVERVIEW-KR.md)

### `mods/mcp_like_mod.py`

`mcp_like_mod.py`는 작은 MCP-like 도구 등록 데모 모드입니다.

도구를 이름, 설명, 처리 함수로 정리하여 tool-calling 아키텍처의 간단한 예시로 보여 줍니다.

본 프로젝트는 완전한 MCP protocol을 구현하지 않았고, 정식 MCP server도 아닙니다.  
여기서의 MCP-like 모드는 도구 등록과 도구 호출 개념을 보여 주기 위한 것입니다.

자세한 설명은 다음 문서를 참고하세요:

[MODE_OVERVIEW-KR.md](./MODE_OVERVIEW-KR.md)

## 모드

`.env`를 통해 두 가지 도구 아키텍처 모드를 전환할 수 있습니다.

```env
TOOL_MODE=router
```

전통적인 분리형 도구 라우터 모드를 사용합니다.

```env
TOOL_MODE=mcp_like
```

MCP-like 도구 등록 데모 모드를 사용합니다.

두 모드는 사용자 입장에서 제공하는 기능은 대체로 같지만, 내부 구조가 다릅니다.

## 주의사항

### `.env`로 설정 관리

대부분의 중요한 설정은 `.env`를 통해 제어됩니다.

API provider, 모델 이름, 도구 모드, 메모리 모드, token 사용량 기록 모드가 포함됩니다.

따라서 `.env`만 수정하면 전체 프로그램을 다시 작성하지 않고도 다른 API provider, 모델 또는 도구 모드로 전환할 수 있습니다.

### 임시 메모리만 사용

이 Lite 버전은 메모리 기능을 활성화했을 때만 RAM 안의 임시 메모리를 사용합니다.

Bot을 다시 시작하면 메모리는 삭제됩니다.

본 프로젝트는 장기 user profile, 관리 기록, case 기록 또는 영구 채팅 로그를 저장하지 않습니다.

> 단, 이는 제3자 API provider에는 해당되지 않습니다. 클라우드 API를 사용할 때는 배포자가 API 서비스의 개인정보 처리방침과 데이터 보관 방식을 직접 확인해야 합니다.

### Token 사용량 기록

Bot은 API가 token usage 데이터를 반환할 때 해당 데이터를 읽을 수 있습니다.

API provider가 token usage를 반환하지 않으면 Bot은 대략적인 추정값을 사용합니다.

추정 결과는 정확하지 않을 수 있으며, 공식 과금 데이터로 간주해서는 안 됩니다.

이 기능은 주로 token 사용량을 관찰하고 router 모드와 MCP-like 모드 사이의 대략적인 차이를 비교하기 위한 것입니다.  
같은 입력을 사용하더라도 모델, API provider, 응답 내용, 임시 메모리 또는 생성 상태에 따라 token 사용량이 달라질 수 있으므로, 결과는 참고용으로만 보아야 합니다.

## 참고 자료

* OpenAI Chat Completions API: https://developers.openai.com/api/reference/chat-completions/
* OpenRouter Chat Completion API: https://openrouter.ai/docs/api/api-reference/chat/send-chat-completion-request
* OpenRouter Quickstart: https://openrouter.ai/docs/quickstart
* DeepSeek API Docs: https://api-docs.deepseek.com/
* Gemini OpenAI Compatibility: https://ai.google.dev/gemini-api/docs/openai

위 링크들은 본 프로젝트에서 OpenAI-compatible API 등록, 요청, 동작을 이해하기 위해 참고한 자료입니다.  
> 주의: OpenAI-compatible API 형식을 학습하거나 개발에 사용할 때에도, 각 API provider의 모델 이름, 가격, 개인정보 처리방침, 데이터 보관 방식, 서비스 약관을 직접 확인해야 합니다.
