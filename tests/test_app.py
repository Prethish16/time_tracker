
import sqlite3

import pytest
import app as tracker


@pytest.fixture()
def client(tmp_path, monkeypatch):
    test_db = tmp_path / "test_time_tracker.db"
    monkeypatch.setattr(tracker, "DB_PATH", test_db)

    tracker.init_db()
    tracker.app.config.update(TESTING=True)

    with tracker.app.test_client() as test_client:
        yield test_client


def get_sessions():
    with sqlite3.connect(tracker.DB_PATH) as connection:
        return connection.execute("""
            SELECT start_time, end_time, duration_seconds
            FROM sessions
        """).fetchall()


def test_home_page_loads(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Time Tracker" in response.data
    assert b"Start Timer" in response.data


def test_start_timer(client):
    response = client.post("/start", follow_redirects=True)

    assert response.status_code == 200
    assert b"Timer started successfully." in response.data

    sessions = get_sessions()
    assert len(sessions) == 1
    assert sessions[0][0] is not None
    assert sessions[0][1] is None


def test_prevent_second_active_timer(client):
    client.post("/start")
    response = client.post("/start", follow_redirects=True)

    assert b"A timer is already running." in response.data
    assert len(get_sessions()) == 1


def test_stop_timer_saves_duration(client):
    client.post("/start")
    response = client.post("/stop", follow_redirects=True)

    assert response.status_code == 200
    assert b"Timer stopped successfully." in response.data

    sessions = get_sessions()
    assert len(sessions) == 1
    assert sessions[0][1] is not None
    assert sessions[0][2] >= 0


def test_stop_without_active_timer(client):
    response = client.post("/stop", follow_redirects=True)

    assert b"No active timer to stop." in response.data
    assert len(get_sessions()) == 0

def test_logs_section_is_displayed(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Time Tracking Logs" in response.data
    assert b"No completed sessions yet." in response.data


def test_completed_session_appears_in_logs(client):
    client.post("/start")
    client.post("/stop")

    response = client.get("/")
    sessions = tracker.get_completed_sessions()

    assert response.status_code == 200
    assert len(sessions) == 1
    assert b"Time Tracking Logs" in response.data
    assert b"Start Time" in response.data
    assert b"End Time" in response.data
    assert b"Duration" in response.data
    assert sessions[0]["date"].encode() in response.data
    assert sessions[0]["duration"].encode() in response.data
