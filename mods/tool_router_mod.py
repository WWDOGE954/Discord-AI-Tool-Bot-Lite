from __future__ import annotations

import asyncio

import config
from ai_client import ask_ai, reset_user_memory
from usage_tracker import record_usage, read_usage_summary
from .common import ToolResult


async def handle_tool(tool_name: str, **kwargs) -> ToolResult:
    """Traditional decoupled tool router.

    main.py calls this router, and the router decides which function to run.
    """
    if tool_name == "ask_ai":
        return await _ask_ai_tool(**kwargs)
    if tool_name == "forget":
        return _forget_tool(**kwargs)
    if tool_name == "status":
        return _status_tool()
    if tool_name == "usage":
        return _usage_tool(**kwargs)
    if tool_name == "privacy":
        return _privacy_tool()
    return ToolResult(False, f"Unknown tool: {tool_name}")


async def _ask_ai_tool(prompt: str, user_id: str, display_name: str, **_) -> ToolResult:
    try:
        ai_response = await asyncio.to_thread(ask_ai, prompt, user_id, display_name)
        usage = record_usage(
            user_id=user_id,
            display_name=display_name,
            model=config.AI_MODEL,
            prompt=prompt,
            completion=ai_response.text,
            api_usage=ai_response.usage,
        )
        suffix = ""
        if usage.get("enabled"):
            mark = "~" if usage.get("estimated") else ""
            suffix = f"\n\n`tokens: {mark}{usage.get('total_tokens', 0)}`"
        return ToolResult(True, ai_response.text + suffix, {"usage": usage})
    except Exception as exc:
        return ToolResult(False, f"AI error: {exc}")


def _forget_tool(user_id: str, **_) -> ToolResult:
    reset_user_memory(user_id)
    return ToolResult(True, "Temporary memory cleared for this user.")


def _status_tool() -> ToolResult:
    return ToolResult(
        True,
        "\n".join(
            [
                "**Discord AI Bot Lite Status**",
                f"Provider: `{config.AI_PROVIDER}`",
                f"Model: `{config.AI_MODEL or 'not set'}`",
                f"Tool mode: `router`",
                f"Memory mode: `{config.MEMORY_MODE}`",
                f"Usage mode: `{config.USAGE_MODE}`",
            ]
        ),
    )


def _usage_tool(user_id: str | None = None, **_) -> ToolResult:
    summary = read_usage_summary(user_id)
    return ToolResult(
        True,
        "\n".join(
            [
                "**Token Usage Summary**",
                f"Requests: `{summary['requests']}`",
                f"Prompt tokens: `{summary['prompt_tokens']}`",
                f"Completion tokens: `{summary['completion_tokens']}`",
                f"Total tokens: `{summary['total_tokens']}`",
                f"Estimated requests: `{summary['estimated_requests']}`",
            ]
        ),
        {"summary": summary},
    )


def _privacy_tool() -> ToolResult:
    return ToolResult(
        True,
        "Cloud API mode may send prompts, user context, and generated replies "
        "to the configured third-party API provider. Do not put private tokens, "
        "passwords, personal data, or sensitive moderation records into prompts. "
        "For privacy-sensitive servers, local AI deployment is recommended.",
    )
