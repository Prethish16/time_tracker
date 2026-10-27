
from contextlib import closing
from datetime import datetime
from pathlib import Path
import sqlite3

from flask import Flask, flash, redirect, render_template, url_for, request
app = Flask(__name__)
app.secret_key = "time-tracker-dev-key"

DB_PATH = Path(__file__).resolve().with_name("time_tracker.db")


def init_db():
    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration_seconds INTEGER
            )
        """)
        connection.commit()


def get_active_session():
    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute("""
            SELECT *
            FROM sessions
            WHERE end_time IS NULL
            ORDER BY id DESC
            LIMIT 1
        """).fetchone()
        return dict(row) if row else None


def get_completed_sessions():
    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute("""
            SELECT id, start_time, end_time, duration_seconds
            FROM sessions
            WHERE end_time IS NOT NULL
            ORDER BY id DESC
            LIMIT 50
        """).fetchall()

    sessions = []

    for row in rows:
        start = datetime.fromisoformat(row["start_time"])
        end = datetime.fromisoformat(row["end_time"])
        duration = row["duration_seconds"] or 0

        sessions.append({
            "id": row["id"],
            "date": start.strftime("%d %b %Y"),
            "start": start.strftime("%I:%M:%S %p"),
            "end": end.strftime("%I:%M:%S %p"),
            "duration": (
                f"{duration // 3600:02d}:"
                f"{(duration % 3600) // 60:02d}:"
                f"{duration % 60:02d}"
            )
        })

    return sessions

def get_total_tracked_seconds():
    with closing(sqlite3.connect(DB_PATH)) as connection:
        row = connection.execute("""
            SELECT COALESCE(SUM(duration_seconds), 0)
            FROM sessions
            WHERE end_time IS NOT NULL
        """).fetchone()

    return int(row[0] or 0)


@app.route("/")
def index():
    active_session = get_active_session()
    elapsed_seconds = 0

    if active_session:
        start = datetime.fromisoformat(
            active_session["start_time"]
        )
        now = datetime.now().astimezone()
        elapsed_seconds = max(
            0, int((now - start).total_seconds())
        )
    else:
        elapsed_seconds = request.args.get(
            "stopped_duration", default=0, type=int
        )

    sessions = get_completed_sessions()

    total_tracked_seconds = get_total_tracked_seconds()
    total_hours = total_tracked_seconds / 3600

    total_duration = (
        f"{total_tracked_seconds // 3600:02d}:"
        f"{(total_tracked_seconds % 3600) // 60:02d}:"
        f"{total_tracked_seconds % 60:02d}"
    )

    return render_template(
        "index.html",
        active_session=active_session,
        elapsed_seconds=elapsed_seconds,
        sessions=sessions,
        total_hours=total_hours,
        total_duration=total_duration
    )



@app.post("/start")
def start_timer():
    with closing(sqlite3.connect(DB_PATH)) as connection:
        active = connection.execute("""
            SELECT id FROM sessions
            WHERE end_time IS NULL
            LIMIT 1
        """).fetchone()

        if active:
            flash("A timer is already running.", "error")
        else:
            start = datetime.now().astimezone().isoformat(
                timespec="seconds"
            )
            connection.execute(
                "INSERT INTO sessions (start_time) VALUES (?)",
                (start,)
            )
            connection.commit()
            flash("Timer started successfully.", "success")

    return redirect(url_for("index"))


@app.post("/stop")
def stop_timer():
    active = get_active_session()

    if not active:
        flash("No active timer to stop.", "error")
        return redirect(url_for("index"))

    start = datetime.fromisoformat(active["start_time"])
    end = datetime.now().astimezone()
    duration = max(0, int((end - start).total_seconds()))

    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.execute("""
            UPDATE sessions
            SET end_time = ?, duration_seconds = ?
            WHERE id = ?
        """, (
            end.isoformat(timespec="seconds"),
            duration,
            active["id"]
        ))
        connection.commit()

    flash("Timer stopped successfully.", "success")
    return redirect(url_for("index", stopped_duration=duration))


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
