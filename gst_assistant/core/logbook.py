"""Log every question and answer to a small SQLite database."""
import json
import sqlite3
import threading
from datetime import datetime, timezone

DEFAULT_PATH = "data/logs.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    question TEXT NOT NULL,
    status TEXT NOT NULL,
    answer TEXT,
    retrieved_ids TEXT,
    cited_ids TEXT,
    tokens_in INTEGER,
    tokens_out INTEGER,
    search_ms REAL,
    llm_ms REAL,
    total_ms REAL,
    feedback INTEGER
)
"""


class LogBook:
    def __init__(self, path=DEFAULT_PATH):
        # A web server handles requests on several threads, so the connection is shared
        # and every use is protected by a lock.
        self.connection = sqlite3.connect(path, check_same_thread=False)
        self.lock = threading.Lock()
        with self.lock:
            self.connection.execute(SCHEMA)
            self.connection.commit()

    def record(self, question, answer):
        with self.lock:
            cursor = self.connection.execute(
                "INSERT INTO requests (created_at, question, status, answer, retrieved_ids, "
                "cited_ids, tokens_in, tokens_out, search_ms, llm_ms, total_ms) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    datetime.now(timezone.utc).isoformat(),
                    question,
                    answer.status,
                    answer.text,
                    json.dumps(answer.retrieved_ids),
                    json.dumps(answer.cited_ids),
                    answer.tokens_in,
                    answer.tokens_out,
                    answer.search_ms,
                    answer.llm_ms,
                    answer.total_ms,
                ),
            )
            self.connection.commit()
            return cursor.lastrowid

    def set_feedback(self, request_id, value):
        """value: 1 for thumbs up, -1 for thumbs down. Returns True if the request exists."""
        with self.lock:
            cursor = self.connection.execute(
                "UPDATE requests SET feedback = ? WHERE id = ?", (value, request_id)
            )
            self.connection.commit()
            return cursor.rowcount > 0
