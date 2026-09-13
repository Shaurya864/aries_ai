"""
Thin wrapper around the Google GenAI SDK.

Phase 1 only needs plain text-in/text-out chat. Intent routing,
structured Pydantic extraction, and multimodal calls are added in
Phase 2/3 on top of this same client.
"""

from __future__ import annotations

from google import genai

from core.config import GEMINI_MODEL, require_gemini_key

_client: genai.Client | None = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=require_gemini_key())
    return _client


def generate_reply(prompt: str) -> str:
    """
    Send plain text to Gemini and return the plain text reply.

    Raises whatever the SDK raises on network/auth failure — the caller
    (running this on a background thread) is responsible for catching
    it and surfacing a friendly error in the UI.
    """
    client = get_client()
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )
    return response.text or "(no response)"