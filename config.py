import os
from dotenv import load_dotenv

load_dotenv()


def _get_int(name: str, default: int = 0) -> int:
    value = os.getenv(name, str(default)).strip()
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _get_float(name: str, default: float = 0.0) -> float:
    value = os.getenv(name, str(default)).strip()
    if not value:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


# Discord
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
TARGET_CHANNEL_ID = _get_int("TARGET_CHANNEL_ID", 0)
GUILD_ID = _get_int("GUILD_ID", 0)
REPLY_ON_MENTION = _get_bool("REPLY_ON_MENTION", True)

# AI API
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai_compatible").strip().lower()
AI_API_BASE_URL = os.getenv("AI_API_BASE_URL", "").strip()
AI_API_KEY = os.getenv("AI_API_KEY", "").strip()
AI_MODEL = os.getenv("AI_MODEL", "").strip()
AI_TEMPERATURE = _get_float("AI_TEMPERATURE", 0.7)
AI_MAX_TOKENS = _get_int("AI_MAX_TOKENS", 800)
AI_TIMEOUT_SECONDS = _get_int("AI_TIMEOUT_SECONDS", 60)
SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "You are a helpful Discord AI assistant. Keep replies clear, safe, and concise.",
).strip()

# Architecture mode
# router / mcp_like
TOOL_MODE = os.getenv("TOOL_MODE", "router").strip().lower()

# Memory mode
# none / temp
MEMORY_MODE = os.getenv("MEMORY_MODE", "temp").strip().lower()
MAX_MEMORY_PER_USER = _get_int("MAX_MEMORY_PER_USER", 10)

# Token usage
# disabled / api / estimate / api_or_estimate
USAGE_MODE = os.getenv("USAGE_MODE", "api_or_estimate").strip().lower()
USAGE_LOG_FILE = os.getenv("USAGE_LOG_FILE", "usage_logs.jsonl").strip()
