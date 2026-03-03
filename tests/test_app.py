"""
Test suite for the Mergington High School API FastAPI backend.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# ensure src is on path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, reset_activities, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_state():
    """Restore the in-memory activity state before each test."""
    reset_activities()


class TestRoot:
    def test_redirects_to_static(self):
        r = client.get("/", follow_redirects=False)
        assert r.status_code == 307
        assert r.headers["location"] == "/static/index.html"


class TestActivities:
    def test_get_activities(self):
        r = client.get("/activities")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data

    def test_activity_fields(self):
        r = client.get("/activities")
        activity = r.json()["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert isinstance(activity["participants"], list)


class TestSignup:
    def test_successful_signup(self):
        r = client.post(
            "/activities/Chess Club/signup",
            params={"email": "new@mergington.edu"},
        )
        assert r.status_code == 200
        assert "Signed up new@mergington.edu" in r.json()["message"]

    def test_duplicate_signup(self):
        r = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"},
        )
        assert r.status_code == 400

    def test_invalid_activity(self):
        r = client.post(
            "/activities/Nope/signup",
            params={"email": "a@b.com"},
        )
        assert r.status_code == 404


class TestUnregister:
    def test_successful_unregister(self):
        email = "michael@mergington.edu"
        r = client.post(
            "/activities/Chess Club/unregister",
            params={"email": email},
        )
        assert r.status_code == 200
        # ensure removed
        activities_data = client.get("/activities").json()
        assert email not in activities_data["Chess Club"]["participants"]

    def test_unregister_not_registered(self):
        r = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "not@here"},
        )
        assert r.status_code == 400

    def test_unregister_invalid_activity(self):
        r = client.post(
            "/activities/Nope/unregister",
            params={"email": "a@b.com"},
        )
        assert r.status_code == 404
