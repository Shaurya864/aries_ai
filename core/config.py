"""
Central configuration for Aries.

Loads settings from a local .env file (never commit this file with real
secrets). See .env.example for the full list of variables used across
all phases of the project.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Resolve paths relative to the project root, not the current working
# directory, so this works correctly both in dev and once packaged
# with PyInstaller.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

load_dotenv(dotenv_path=ENV_PATH)

# --- Core AI settings ---
GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL: str = "gemini-3.6-flash"

# --- Database ---
DB_PATH: Path = PROJECT_ROOT / "jarvis_history.db"

# --- App metadata ---
APP_NAME: str = "ARIES"


def require_gemini_key() -> str:
    """Return the Gemini API key or raise a clear, actionable error."""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        raise RuntimeError(
            "GEMINI_API_KEY is not set.\n\n"
            "1. Get a free key at https://aistudio.google.com/apikey\n"
            "2. Copy .env.example to .env in the project root\n"
            "3. Paste your key as GEMINI_API_KEY=... in that .env file\n"
        )
    return GEMINI_API_KEY