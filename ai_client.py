from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import requests

import config


@dataclass
class AIResponse:
    text: str
    usage: dict[str, Any]
    raw: dict[str, Any]


_user_memory: dict[str, list[dict[str, str]]] = {}


def reset_user_memory(user_id: str | None = None) -> None:
    """Clear temporary in-memory conversation context."""
    if user_id is None:
        _user_memory.clear()
        return
    _user_memory.pop(str(user_id), None)


def _chat_completions_url(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/chat/completions"):
        return base
    return f"{base}/chat/completions"


def _build_messages(prompt: str, user_id: str, display_name: str) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = [
        {"role": "system", "content": config.SYSTEM_PROMPT},
    ]

    if config.MEMORY_MODE == "temp":
        history = _user_memory.get(str(user_id), [])
        messages.extend(history[-config.MAX_MEMORY_PER_USER :])

    messages.append(
        {
            "role": "user",
            "content": f"Discord display name: {display_name}\nMessage: {prompt}",
        }
    )
    return messages


def ask_ai(prompt: str, user_id: str = "default", display_name: str = "User") -> AIResponse:
    """Call an OpenAI-compatible chat completions API."""
    if config.AI_PROVIDER != "openai_compatible":
        raise RuntimeError(f"Unsupported AI_PROVIDER: {config.AI_PROVIDER}")
    if not config.AI_API_BASE_URL:
        raise RuntimeError("AI_API_BASE_URL is not set.")
    if not config.AI_API_KEY:
        raise RuntimeError("AI_API_KEY is not set.")
    if not config.AI_MODEL:
        raise RuntimeError("AI_MODEL is not set.")

    messages = _build_messages(prompt, user_id, display_name)
    payload = {
        "model": config.AI_MODEL,
        "messages": messages,
        "temperature": config.AI_TEMPERATURE,
        "max_tokens": config.AI_MAX_TOKENS,
    }
    headers = {
        "Authorization": f"Bearer {config.AI_API_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        _chat_completions_url(config.AI_API_BASE_URL),
        headers=headers,
        json=payload,
        timeout=config.AI_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    data = response.json()

    try:
        text = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected API response format: {data}") from exc

    text = str(text).strip()
    usage = data.get("usage") or {}

    if config.MEMORY_MODE == "temp":
        history = _user_memory.setdefault(str(user_id), [])
        history.append({"role": "user", "content": prompt})
        history.append({"role": "assistant", "content": text})
        max_items = max(config.MAX_MEMORY_PER_USER * 2, 2)
        del history[:-max_items]

    return AIResponse(text=text, usage=usage, raw=data)
