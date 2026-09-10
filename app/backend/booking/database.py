import os
import sqlite3
from pathlib import Path


DEFAULT_DB_PATH = Path(__file__).resolve().parent / "bookings.db"
BOOKINGS_TABLE = "restaurant_bookings"


def get_db_path() -> Path:
    custom_path = os.getenv("BOOKINGS_DB_PATH")
    if custom_path:
        return Path(custom_path)
    return DEFAULT_DB_PATH


def get_connection():
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=5, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {BOOKINGS_TABLE} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_uuid TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            contact TEXT NOT NULL,
            party_size INTEGER NOT NULL,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        f"""
        CREATE INDEX IF NOT EXISTS idx_{BOOKINGS_TABLE}_uuid
        ON {BOOKINGS_TABLE}(booking_uuid)
        """
    )
    cursor.execute(
        f"""
        CREATE INDEX IF NOT EXISTS idx_{BOOKINGS_TABLE}_slot
        ON {BOOKINGS_TABLE}(date, time)
        """
    )
    cursor.execute(
        f"""
        CREATE INDEX IF NOT EXISTS idx_{BOOKINGS_TABLE}_contact
        ON {BOOKINGS_TABLE}(contact)
        """
    )

    conn.commit()
    conn.close()
