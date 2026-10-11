import sqlite3
from Core.models import StoredCase, TriageLogEntry
from datetime import datetime
from pathlib import Path
import json

DB_PATH = str(Path(__file__).parent / "cases.db")


def init_db():
    connection = sqlite3.connect(DB_PATH, timeout=5.0)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            case_id TEXT PRIMARY KEY,
            priority TEXT,
            reasoning TEXT,
            summary TEXT,
            outcome TEXT,
            status TEXT,
            date_submitted TEXT,
            date_updated TEXT,
            raw_case TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS triage_log (
            log_id INTEGER PRIMARY KEY,
            case_id TEXT,
            time_stamp TEXT,
            resulting_priority TEXT,
            outcome TEXT,
            source TEXT,
            processing_duration REAL,
            FOREIGN KEY (case_id) REFERENCES cases(case_id)
        )
    """)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    init_db()


def save_case(stored: StoredCase):
    connection = sqlite3.connect(DB_PATH, timeout=5.0)
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO cases (
            case_id, priority, reasoning, summary,
            outcome, status, date_submitted, date_updated, raw_case
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(case_id) DO UPDATE SET
            priority = excluded.priority,
            reasoning = excluded.reasoning,
            summary = excluded.summary,
            outcome = excluded.outcome,
            raw_case = excluded.raw_case,
            date_updated = excluded.date_updated
        """,
        (
            stored.case_id, stored.priority, stored.reasoning, stored.summary,
            stored.outcome, stored.status, stored.date_submitted,
            stored.date_updated, stored.raw_case,
        ),
    )
    connection.commit()
    connection.close()


def save_log(entry: TriageLogEntry):
    connection = sqlite3.connect(DB_PATH, timeout=5.0)
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO triage_log (
            case_id, time_stamp, resulting_priority,
            outcome, source, processing_duration
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            entry.case_id,
            datetime.now().isoformat(),
            entry.resulting_priority,
            entry.outcome,
            entry.source,
            entry.processing_duration,
        ),
    )
    connection.commit()
    connection.close()


def get_all_cases():
    connection = sqlite3.connect(DB_PATH, timeout=5.0)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    rows = cursor.execute("SELECT * FROM cases").fetchall()
    connection.close()

    cases = []
    for row in rows:
        case = dict(row)
        if case.get("raw_case"):
            try:
                case["raw_case"] = json.loads(case["raw_case"])
            except (json.JSONDecodeError, TypeError):
                pass
        cases.append(case)
    return cases


def update_case_status(case_id: str, status: str):
    connection = sqlite3.connect(DB_PATH, timeout=5.0)
    cursor = connection.cursor()
    cursor.execute(
        """
        UPDATE cases
        SET status = ?, date_updated = ?
        WHERE case_id = ?
        """,
        (status, datetime.now().isoformat(), case_id),
    )
    updated = cursor.rowcount
    connection.commit()
    connection.close()
    return updated


def clear_cases():
    connection = sqlite3.connect(DB_PATH, timeout=5.0)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM triage_log")
    cursor.execute("DELETE FROM cases")
    connection.commit()
    connection.close()

