from flask import Flask, request, render_template
from database import get_db
from datetime import datetime
import json

app = Flask(__name__)

@app.route("/health")
def health():
    return {"status": "ok"}

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    event_type = data.get("event_name", "unknown")

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

if __name__ == "__main__":
    app.run(debug=True, port=5000)