"""
Tool handlers — Aries Phase 6 (Android ADB Device Control & Workspace Integrated).

Integrates local Android ADB device control, Google Workspace calendar/emails,
local file search, and screen vision.
"""

from __future__ import annotations

from core.intents import (
    CheckCalendarParams,
    CheckEmailsParams,
    CreateEventParams,
    DeviceControlParams,
    Intent,
    ScreenVisionParams,
    SearchFilesParams,
    SendEmailParams,
)
from core.tools import search_local_files, capture_and_analyze_screen
from core.workspace import list_calendar_events, check_unread_emails
from core.messaging import execute_adb_command  # Phase 6 ADB Import


def handle_check_calendar(params: CheckCalendarParams) -> str:
    """Real Phase 5 implementation for Google Calendar lookup."""
    date_query = getattr(params, 'date', 'upcoming')
    return list_calendar_events(date_query)


def handle_check_emails(params: CheckEmailsParams) -> str:
    """Real Phase 5 implementation for reading Gmail unread messages."""
    return check_unread_emails()


def handle_create_event(params: CreateEventParams) -> str:
    return (
        f"[STUB:CREATE_EVENT] would create '{params.title}' on {params.date} "
        f"{params.start_time or '?'}–{params.end_time or '?'} "
        f"attendees={params.attendees or 'none'}"
    )


def handle_search_files(params: SearchFilesParams) -> str:
    """Real Phase 3 implementation for local file search using pathlib."""
    query = params.query or ""
    scope = params.directory or None
    return search_local_files(query, scope)


def handle_send_email(params: SendEmailParams) -> str:
    return f"[STUB:SEND_EMAIL] would email {params.to} — subject: {params.subject!r}"


def handle_device_control(params: DeviceControlParams) -> str:
    """Real Phase 6 implementation for executing local ADB phone commands."""
    action = getattr(params, 'action', 'battery').lower()
    
    if "battery" in action:
        return execute_adb_command(['shell', 'dumpsys', 'battery'])
    elif "home" in action:
        return execute_adb_command(['shell', 'input', 'keyevent', '3'])
    else:
        return execute_adb_command(['shell', action])


def handle_screen_vision(params: ScreenVisionParams) -> str:
    """Real Phase 3 implementation for screen capture & multimodal analysis."""
    prompt = params.question or "Analyze this screenshot and summarize what you see on my screen."
    return capture_and_analyze_screen(prompt)


# Dispatch table. GENERAL_CHAT is intentionally absent — main.py routes
# that intent straight to generate_reply() instead of a tool handler.
TOOL_HANDLERS = {
    Intent.CHECK_CALENDAR: handle_check_calendar,
    Intent.CHECK_EMAILS: handle_check_emails,
    Intent.CREATE_EVENT: handle_create_event,
    Intent.SEARCH_FILES: handle_search_files,
    Intent.SEND_EMAIL: handle_send_email,
    Intent.DEVICE_CONTROL: handle_device_control,
    Intent.SCREEN_VISION: handle_screen_vision,
}