import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "bookings.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_uuid TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        service TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        contact TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(date, time)
    )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_booking_uuid ON bookings(booking_uuid)
    """)

    conn.commit()
    conn.close()    
