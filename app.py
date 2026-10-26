
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
        # Show the final duration only immediately after Stop.
        elapsed_seconds = request.args.get(
            "stopped_duration", default=0, type=int
        )

    return render_template(
        "index.html",
        active_session=active_session,
        elapsed_seconds=elapsed_seconds
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
    app.run(debug=True)
