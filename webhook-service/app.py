from flask import Flask, request, render_template
from database import get_db, init_db
from datetime import datetime
from pathlib import Path
import json

app = Flask(__name__)

@app.route("/health")
def health():
    return {"status": "ok"}

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    if not data:
        return {"error": "Invalid or missing JSON"}, 400

    event_type = (
        data.get("event_name")
        or data.get("object_kind")
        or request.headers.get("X-Gitlab-Event")
        or "unknown"
    )

    conn = get_db()
    conn.execute(
        "INSERT INTO events (event_type, payload, received_at) VALUES (?, ?, ?)",
        (event_type, json.dumps(data), datetime.utcnow().isoformat())
    )
    conn.commit()

    return {"status": "stored"}

@app.route("/dashboard")
def dashboard():
    conn = get_db()
    events = conn.execute("SELECT * FROM events ORDER BY id DESC").fetchall()
    return render_template("dashboard.html", events=events)

if not Path("data/events.db").exists():
    init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)