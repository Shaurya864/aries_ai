"""
SQLite persistence for Aries chat history.

Design notes:
- A single module-level connection is reused everywhere. SQLite from
  Python is not safe to share across threads by default, so we open
  the connection with check_same_thread=False and serialize access
  with a lock. All writes/reads should go through this module rather
  than opening ad-hoc connections elsewhere.
"""

from __future__ import annotations

import sqlite3
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from core.config import DB_PATH

_lock = threading.Lock()
_connection: sqlite3.Connection | None = None


@dataclass
class Message:
    id: int
    timestamp: str
    speaker: str  # "user" or "aries"
    content: str


def get_connection() -> sqlite3.Connection:
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        _connection.execute("PRAGMA journal_mode=WAL;")
    return _connection


def init_db(db_path: Path = DB_PATH) -> None:
    """Create the messages table if it doesn't already exist."""
    conn = get_connection()
    with _lock:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                speaker TEXT NOT NULL,
                content TEXT NOT NULL
            )
            """
        )
        conn.commit()


def add_message(speaker: str, content: str) -> Message:
    """Insert a message and return it (thread-safe)."""
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    conn = get_connection()
    with _lock:
        cur = conn.execute(
            "INSERT INTO messages (timestamp, speaker, content) VALUES (?, ?, ?)",
            (ts, speaker, content),
        )
        conn.commit()
        return Message(id=cur.lastrowid, timestamp=ts, speaker=speaker, content=content)


def load_history() -> list[Message]:
    """Load all messages in chronological order (for startup restore)."""
    conn = get_connection()
    with _lock:
        rows = conn.execute(
            "SELECT id, timestamp, speaker, content FROM messages ORDER BY id ASC"
        ).fetchall()
    return [Message(*row) for row in rows]


def export_to_txt(dest_path: Path) -> Path:
    """Write the full history to a plain-text file. Returns the path written."""
    history = load_history()
    lines = [f"[{m.timestamp}] {m.speaker.upper()}: {m.content}" for m in history]
    dest_path.write_text("\n".join(lines), encoding="utf-8")
    return dest_path


def clear_history() -> None:
    """Wipe all messages. Caller is responsible for confirming with the user first."""
    conn = get_connection()
    with _lock:
        conn.execute("DELETE FROM messages")
        conn.commit()