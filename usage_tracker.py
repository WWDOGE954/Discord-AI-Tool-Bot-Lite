from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from typing import Any

import config


def estimate_tokens(text: str) -> int:
    """Very rough token estimate.

    API-provided usage is preferred. This fallback is only for providers that do
    not return usage data.
    """
    if not text:
        return 0
    cjk_count = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    other_count = max(len(text) - cjk_count, 0)
    return max(1, int(cjk_count / 1.6 + other_count / 4))


def normalize_usage(prompt: str, completion: str, api_usage: dict[str, Any] | None) -> dict[str, Any]:
    mode = config.USAGE_MODE
    api_usage = api_usage or {}

    has_api_usage = all(
        key in api_usage for key in ("prompt_tokens", "completion_tokens", "total_tokens")
    )

    if mode == "disabled":
        return {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "estimated": False,
            "enabled": False,
        }

    if mode in {"api", "api_or_estimate"} and has_api_usage:
        return {
            "prompt_tokens": int(api_usage.get("prompt_tokens", 0)),
            "completion_tokens": int(api_usage.get("completion_tokens", 0)),
            "total_tokens": int(api_usage.get("total_tokens", 0)),
            "estimated": False,
            "enabled": True,
        }

    if mode in {"estimate", "api_or_estimate"}:
        prompt_tokens = estimate_tokens(prompt)
        completion_tokens = estimate_tokens(completion)
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "estimated": True,
            "enabled": True,
        }

    return {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "estimated": False,
        "enabled": True,
    }


def record_usage(
    *,
    user_id: str,
    display_name: str,
    model: str,
    prompt: str,
    completion: str,
    api_usage: dict[str, Any] | None = None,
) -> dict[str, Any]:
    usage = normalize_usage(prompt, completion, api_usage)
    if config.USAGE_MODE == "disabled":
        return usage

    event = {
        "time": datetime.now(timezone.utc).isoformat(),
        "user_id": str(user_id),
        "display_name": display_name,
        "model": model,
        **usage,
    }

    try:
        with open(config.USAGE_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except OSError:
        pass

    return usage


def read_usage_summary(user_id: str | None = None) -> dict[str, int]:
    summary = {
        "requests": 0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "estimated_requests": 0,
    }
    if not os.path.exists(config.USAGE_LOG_FILE):
        return summary

    try:
        with open(config.USAGE_LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if user_id is not None and str(event.get("user_id")) != str(user_id):
                    continue
                summary["requests"] += 1
                summary["prompt_tokens"] += int(event.get("prompt_tokens", 0))
                summary["completion_tokens"] += int(event.get("completion_tokens", 0))
                summary["total_tokens"] += int(event.get("total_tokens", 0))
                if event.get("estimated"):
                    summary["estimated_requests"] += 1
    except OSError:
        pass
    return summary
