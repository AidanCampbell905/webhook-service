import sqlite3

def get_db():
    conn = sqlite3.connect("data/events.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT,
            payload TEXT,
            received_at TEXT
        )
    """)
    conn.commit()