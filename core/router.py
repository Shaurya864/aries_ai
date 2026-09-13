"""
Intent router — Aries Phase 2.

Classifies a user message into one of the Intent values and extracts
that intent's parameters, using Gemini function calling: each Intent's
Pydantic model becomes a callable "tool", the model is forced to pick
exactly one (tool_config mode=ANY), and we validate whatever arguments
it returns against the matching Pydantic model before dispatch.

This is a classification step only — no tool handler here talks to a
real calendar/inbox/filesystem yet. See core/tool_handlers.py for the
Phase 2 stub handlers, replaced with real integrations in later phases.
"""

from __future__ import annotations

from google.genai import types

from core.ai_client import get_client
from core.config import GEMINI_MODEL
from core.intents import (
    INTENT_PARAM_MODELS,
    ClassifiedIntent,
    Intent,
)

SYSTEM_INSTRUCTION = (
    "You are the intent router for Aries, a personal AI assistant. "
    "Given the user's message, call exactly one of the available functions: "
    "the one matching what the user wants done. "
    "If the message is just conversation, a question, or doesn't clearly "
    "match any specific action, call GENERAL_CHAT. "
    "Only fill in parameters the user actually stated or clearly implied — "
    "leave optional fields empty rather than guessing."
)


def _build_function_declarations() -> list[types.FunctionDeclaration]:
    declarations = []
    for intent, model in INTENT_PARAM_MODELS.items():
        schema = model.model_json_schema()
        # Gemini's function schema doesn't want a top-level "title" key.
        schema.pop("title", None)
        declarations.append(
            types.FunctionDeclaration(
                name=intent.value,
                description=model.__doc__ or f"Handle the {intent.value} intent.",
                parameters_json_schema=schema,
            )
        )
    return declarations


def classify_intent(text: str) -> ClassifiedIntent:
    """
    Send the user's message to Gemini and return the intent it matched,
    with parameters validated against that intent's Pydantic model.

    Falls back to GENERAL_CHAT (with the raw text folded in, no params)
    if Gemini doesn't return a usable function call for any reason.
    """
    client = get_client()
    tools = [types.Tool(function_declarations=_build_function_declarations())]

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=text,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=tools,
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(mode="ANY")
            ),
        ),
    )

    call = _extract_function_call(response)
    if call is None:
        return ClassifiedIntent(intent=Intent.GENERAL_CHAT, parameters=INTENT_PARAM_MODELS[Intent.GENERAL_CHAT]())

    try:
        intent = Intent(call.name)
    except ValueError:
        # Model hallucinated a function name outside our declared set.
        return ClassifiedIntent(intent=Intent.GENERAL_CHAT, parameters=INTENT_PARAM_MODELS[Intent.GENERAL_CHAT]())

    model_cls = INTENT_PARAM_MODELS[intent]
    args = dict(call.args or {})
    try:
        parameters = model_cls(**args)
    except Exception:
        # Gemini returned args that don't validate — fall back safely
        # rather than crashing the chat loop on a malformed extraction.
        return ClassifiedIntent(intent=Intent.GENERAL_CHAT, parameters=INTENT_PARAM_MODELS[Intent.GENERAL_CHAT]())

    return ClassifiedIntent(intent=intent, parameters=parameters)


def _extract_function_call(response) -> types.FunctionCall | None:
    candidates = getattr(response, "candidates", None) or []
    if not candidates:
        return None
    content = candidates[0].content
    if content is None or not content.parts:
        return None
    for part in content.parts:
        if part.function_call is not None:
            return part.function_call
    return None
