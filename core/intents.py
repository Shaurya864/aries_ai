"""
Intent schema for Aries — Phase 6 (Device Control Integrated).

Each Intent maps to a Pydantic model describing the parameters Gemini
should extract from the user's message via function calling. These
models are the single source of truth for both:
  - the function declarations sent to Gemini (via .model_json_schema())
  - validating/parsing whatever Gemini returns before dispatch
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Intent(str, Enum):
    CHECK_CALENDAR = "CHECK_CALENDAR"
    CHECK_EMAILS = "CHECK_EMAILS"
    CREATE_EVENT = "CREATE_EVENT"
    SEARCH_FILES = "SEARCH_FILES"
    SEND_EMAIL = "SEND_EMAIL"
    DEVICE_CONTROL = "DEVICE_CONTROL"
    SCREEN_VISION = "SCREEN_VISION"
    GENERAL_CHAT = "GENERAL_CHAT"


class CheckCalendarParams(BaseModel):
    date: str | None = Field(
        default=None,
        description="ISO date (YYYY-MM-DD) or relative phrase like 'today', "
        "'tomorrow', 'next week'. Omit if the user didn't specify one.",
    )


class CheckEmailsParams(BaseModel):
    unread_only: bool = Field(default=True, description="Only look at unread emails.")
    max_results: int = Field(default=10, description="Max number of emails to check.")


class CreateEventParams(BaseModel):
    title: str = Field(description="Short title/summary of the event.")
    date: str = Field(description="ISO date (YYYY-MM-DD) the event occurs on.")
    start_time: str | None = Field(default=None, description="24h HH:MM start time, if given.")
    end_time: str | None = Field(default=None, description="24h HH:MM end time, if given.")
    attendees: list[str] = Field(default_factory=list, description="Names or emails of attendees mentioned.")


class SearchFilesParams(BaseModel):
    query: str = Field(description="Filename or content keywords to search for.")
    directory: str | None = Field(default=None, description="Directory to restrict the search to, if mentioned.")


class SendEmailParams(BaseModel):
    to: str = Field(description="Recipient name or email address.")
    subject: str = Field(description="Email subject line.")
    body: str = Field(description="Email body content.")


class DeviceControlParams(BaseModel):
    action: str = Field(description="The phone command, hardware state check (e.g., 'battery'), or action to perform.")


class ScreenVisionParams(BaseModel):
    question: str | None = Field(
        default=None, description="What to look for or ask about on the current screen."
    )


class GeneralChatParams(BaseModel):
    """No structured parameters — the raw message is handled as plain chat."""


# Single source of truth mapping each intent to its parameter model.
INTENT_PARAM_MODELS: dict[Intent, type[BaseModel]] = {
    Intent.CHECK_CALENDAR: CheckCalendarParams,
    Intent.CHECK_EMAILS: CheckEmailsParams,
    Intent.CREATE_EVENT: CreateEventParams,
    Intent.SEARCH_FILES: SearchFilesParams,
    Intent.SEND_EMAIL: SendEmailParams,
    Intent.DEVICE_CONTROL: DeviceControlParams,
    Intent.SCREEN_VISION: ScreenVisionParams,
    Intent.GENERAL_CHAT: GeneralChatParams,
}


class ClassifiedIntent(BaseModel):
    """Result of routing a user message: which intent, with what parameters."""

    intent: Intent
    parameters: BaseModel

    class Config:
        arbitrary_types_allowed = True