"""
Google Workspace Integration for Aries AI (Phase 5).
Manages OAuth2 authentication, Calendar events, and Gmail reading/sending.
"""

from __future__ import annotations
import os
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define required scopes for Calendar and Gmail
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose'
]

def get_workspace_services():
    """Authenticates and returns Google Calendar and Gmail service clients."""
    creds = None
    
    # Explicitly resolve paths relative to the project root (one level up from core/)
    project_root = Path(__file__).resolve().parent.parent
    token_path = project_root / "token.json"
    creds_path = project_root / "credentials.json"

    # token.json stores the user's access and refresh tokens
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not creds_path.exists():
                return None, None, f"[Error] credentials.json not found in project root! Looked at: {creds_path}"
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run to prevent re-auth loops
        token_path.write_text(creds.to_json())

    # Build service instances
    calendar_service = build('calendar', 'v3', credentials=creds)
    gmail_service = build('gmail', 'v1', credentials=creds)
    return calendar_service, gmail_service, None


# --- Calendar Tool Implementations ---
def list_calendar_events(date_query: str = "upcoming") -> str:
    cal_svc, _, err = get_workspace_services()
    if err:
        return err
    try:
        # Call the Calendar API
        now = "2026-09-04T00:00:00Z"  # Or dynamic ISO time
        events_result = cal_svc.events().list(
            calendarId='primary', timeMin=now, maxResults=5, singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        
        if not events:
            return "No upcoming calendar events found."
        
        output = ["Upcoming Calendar Events:"]
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            output.append(f"- {event.get('summary', 'Untitled')} at {start}")
        return "\n".join(output)
    except Exception as e:
        return f"[Calendar Error: {e}]"


# --- Gmail Tool Implementations ---
def check_unread_emails() -> str:
    _, gmail_svc, err = get_workspace_services()
    if err:
        return err
    try:
        results = gmail_svc.users().messages().list(userId='me', q='is:unread', maxResults=5).execute()
        messages = results.get('messages', [])
        
        if not messages:
            return "You have no unread emails."
            
        output = ["Unread Emails:"]
        for msg_summary in messages:
            msg = gmail_svc.users().messages().get(userId='me', id=msg_summary['id']).execute()
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            output.append(f"- From: {sender} | Subject: {subject}")
        return "\n".join(output)
    except Exception as e:
        return f"[Gmail Error: {e}]"