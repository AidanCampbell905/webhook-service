import sqlite3

def get_db():
    conn = sqlite3.connect("data/events.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()

    # Create base table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT,
            payload TEXT,
            received_at TEXT
        )
    """)

    # Add new columns if missing
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

    conn.commit()