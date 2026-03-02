import os
import sqlite3

# Store the DB inside the project directory (Render-safe)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "events.db")

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
            received_at TEXT,
            project_id INTEGER,
            project_name TEXT,
            project_namespace TEXT,
            event_id TEXT
        )
    """)

    conn.commit()

def has_seen_event(conn, event_id):
    cur = conn.execute("SELECT 1 FROM events WHERE event_id = ?", (event_id,))
    return cur.fetchone() is not None