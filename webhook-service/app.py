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
    conn = get_db()
    conn.execute(
        """
        INSERT INTO events (
            event_type,
            project_id,
            project_name,
            project_namespace,
            payload,
            received_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
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

    # Build list of distinct project names for dropdown
    projects = conn.execute(
        "SELECT DISTINCT project_name FROM events WHERE project_name IS NOT NULL ORDER BY project_name"
    ).fetchall()
    projects = [p["project_name"] for p in projects]

    # Read selected project from query params
    selected_project = request.args.get("project")

    # Filter events by project if selected
    if selected_project and selected_project != "All":
        events = conn.execute(
            "SELECT * FROM events WHERE project_name = ? ORDER BY id DESC",
            (selected_project,)
        ).fetchall()
    else:
        events = conn.execute(
            "SELECT * FROM events ORDER BY id DESC"
        ).fetchall()

    return render_template(
        "dashboard.html",
        events=events,
        projects=projects,
        selected_project=selected_project
    )

# Initialize DB if missing
if not Path("data/events.db").exists():
    init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)