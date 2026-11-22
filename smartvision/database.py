import sqlite3
from pathlib import Path
from datetime import datetime


DB_PATH = Path(__file__).resolve().parent.parent / "smartvision_alarms.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS alarms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reference_image TEXT NOT NULL,
                duration_seconds INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                triggered_at TEXT,
                stopped_at TEXT,
                status TEXT NOT NULL,
                verification_method TEXT,
                hash_distance INTEGER,
                ssim_score REAL,
                orb_matches INTEGER,
                verification_message TEXT
            )
            """
        )
        connection.commit()


def create_alarm(reference_image: str, duration_seconds: int) -> int:
    created_at = datetime.now().isoformat(timespec="seconds")
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO alarms (reference_image, duration_seconds, created_at, status)
            VALUES (?, ?, ?, 'Scheduled')
            """,
            (reference_image, duration_seconds, created_at),
        )
        connection.commit()
        return int(cursor.lastrowid)


def update_alarm_triggered(alarm_id: int):
    with get_connection() as connection:
        connection.execute(
            "UPDATE alarms SET status='Ringing', triggered_at=? WHERE id=?",
            (datetime.now().isoformat(timespec="seconds"), alarm_id),
        )
        connection.commit()


def update_alarm_stopped(alarm_id: int, method: str, result):
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE alarms
            SET status='Stopped', stopped_at=?, verification_method=?,
                hash_distance=?, ssim_score=?, orb_matches=?,
                verification_message=?
            WHERE id=?
            """,
            (
                datetime.now().isoformat(timespec="seconds"),
                method,
                result.hash_distance,
                result.ssim_score,
                result.orb_good_matches,
                result.message,
                alarm_id,
            ),
        )
        connection.commit()


def update_alarm_cancelled(alarm_id: int):
    with get_connection() as connection:
        connection.execute(
            "UPDATE alarms SET status='Cancelled', stopped_at=? WHERE id=?",
            (datetime.now().isoformat(timespec="seconds"), alarm_id),
        )
        connection.commit()


def get_recent_alarms(limit: int = 20):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, created_at, duration_seconds, status, verification_method,
                   hash_distance, ssim_score, orb_matches
            FROM alarms
            ORDER BY id DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return rows
