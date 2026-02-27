from flask import Flask, request, render_template
from database import get_db, init_db, has_seen_event
from datetime import datetime
from pathlib import Path
from config import WEBHOOK_TOKEN, MAX_AGE_SECONDS
import time
import json

print("WEBHOOK_TOKEN =", WEBHOOK_TOKEN)

app = Flask(__name__)

@app.route("/health")
def health():
    return {"status": "ok"}

def validate_payload(data):
    if not isinstance(data, dict):
        return "Payload must be a JSON object"
    if "project" in data and not isinstance(data["project"], dict):
        return "Project must be an object"
    return None

@app.route("/webhook", methods=["POST"])
def webhook():
    # 1. Token verification
    token = request.headers.get("X-Webhook-Token")
    if token != WEBHOOK_TOKEN:
        app.logger.warning(f"Invalid token from {request.remote_addr}")
        return {"error": "Forbidden"}, 403

    # 2. JSON parsing + validation
    data = request.get_json(silent=True)
    if not data:
        return {"error": "Invalid or missing JSON"}, 400

    error = validate_payload(data)
    if error:
        return {"error": error}, 400

    # 3. Timestamp freshness 
    timestamp = data.get("timestamp")
    if timestamp:
        now = time.time()
        if abs(now - timestamp) > MAX_AGE_SECONDS:
            return {"error": "Stale event"}, 400

    # 4. Replay protection (optional)
    event_id = data.get("event_id")
    conn = get_db()
    if event_id and has_seen_event(conn, event_id):
        return {"error": "Duplicate event"}, 409

    # Determine event type
    event_type = (
        data.get("event_name")
        or data.get("object_kind")
        or request.headers.get("X-Gitlab-Event")
        or "unknown"
    )

    # Extract project metadata
    project = data.get("project", {}) or {}
    project_id = project.get("id")
    project_name = project.get("name")
    project_namespace = project.get("path_with_namespace")

    # Store event
    conn.execute(
        """
        INSERT INTO events (
            event_id,
            event_type,
            project_id,
            project_name,
            project_namespace,
            payload,
            received_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event_id,
            event_type,
            project_id,
            project_name,
            project_namespace,
            json.dumps(data),
            datetime.utcnow().isoformat()
        )
    )
    conn.commit()

    return {"status": "stored"}

@app.route("/dashboard")
def dashboard():
    conn = get_db()

    # Pagination settings
    page = int(request.args.get("page", 1))
    per_page = 20
    offset = (page - 1) * per_page

    # Order toggle (new)
    order = request.args.get("order", "desc")
    if order not in ("asc", "desc"):
        order = "desc"

    # Build list of distinct project names
    projects = conn.execute(
        "SELECT DISTINCT project_name FROM events WHERE project_name IS NOT NULL ORDER BY project_name"
    ).fetchall()
    projects = [p["project_name"] for p in projects]

    selected_project = request.args.get("project")

    # Count total events
    if selected_project and selected_project != "All":
        total = conn.execute(
            "SELECT COUNT(*) FROM events WHERE project_name = ?",
            (selected_project,)
        ).fetchone()[0]

        events = conn.execute(
            f"SELECT * FROM events WHERE project_name = ? ORDER BY id {order} LIMIT ? OFFSET ?",
            (selected_project, per_page, offset)
        ).fetchall()
    else:
        total = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]

        events = conn.execute(
            f"SELECT * FROM events ORDER BY id {order} LIMIT ? OFFSET ?",
            (per_page, offset)
        ).fetchall()

    # New: total pages
    total_pages = (total + per_page - 1) // per_page

    has_next = (page * per_page) < total
    has_prev = page > 1

    return render_template(
        "dashboard.html",
        events=events,
        projects=projects,
        selected_project=selected_project,
        page=page,
        has_next=has_next,
        has_prev=has_prev,
        total_pages=total_pages,
        order=order
    )

# Initialize DB if missing
if not Path("data/events.db").exists():
    init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)