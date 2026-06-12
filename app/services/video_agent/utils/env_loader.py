"""Load environment variables from the project-root .env file."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


def _find_env_path() -> Path:
    """Walk up from this file to locate the project-root .env file."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / ".env"
        if candidate.exists():
            return candidate
    # Best-effort default: project root is 5 levels up
    # (utils -> video_agent -> services -> app -> project root).
    return here.parents[4] / ".env"


ENV_PATH = _find_env_path()

_loaded = False


def load_project_env() -> None:
    """Load .env from project root regardless of current working directory."""
    global _loaded
    if _loaded:
        return
    load_dotenv(ENV_PATH, override=False)
    _loaded = True


def get_groq_api_key() -> str:
    """Return a trimmed Groq API key or raise a clear configuration error."""
    load_project_env()
    api_key = (os.getenv("GROQ_API_KEY") or "").strip().strip('"').strip("'")
    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError(
            "GROQ_API_KEY is missing or still a placeholder. "
            f"Set it in {ENV_PATH}"
        )
    if not api_key.startswith("gsk_"):
        raise ValueError(
            "GROQ_API_KEY does not look valid (expected a key starting with 'gsk_'). "
            "Create a new key at https://console.groq.com/keys"
        )
    return api_key


def get_groq_model() -> str:
    load_project_env()
    return (os.getenv("GROQ_MODEL") or "llama-3.3-70b-versatile").strip()


def get_groq_max_tokens(default: int = 4096) -> int:
    """Return max completion tokens for Groq chat calls."""
    load_project_env()
    raw = (os.getenv("GROQ_MAX_TOKENS") or str(default)).strip()
    try:
        return max(256, int(raw))
    except ValueError:
        return default
