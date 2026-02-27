import os
import sqlite3

DB_PATH = "/var/data/events.db"
os.makedirs("/var/data", exist_ok=True)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()

    # Base table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT,
            payload TEXT,
            received_at TEXT
        )
    """)

    # Add new columns if missing (safe, idempotent)
    try:
        conn.execute("ALTER TABLE events ADD COLUMN project_id INTEGER")
    except:
        pass

    try:
        conn.execute("ALTER TABLE events ADD COLUMN project_name TEXT")
    except:
        pass

    try:
        conn.execute("ALTER TABLE events ADD COLUMN project_namespace TEXT")
    except:
        pass

    # New: event_id for replay protection
    try:
        conn.execute("ALTER TABLE events ADD COLUMN event_id TEXT")
    except:
        pass

    conn.commit()

def has_seen_event(conn, event_id):
    cur = conn.execute("SELECT 1 FROM events WHERE event_id = ?", (event_id,))
    return cur.fetchone() is not None