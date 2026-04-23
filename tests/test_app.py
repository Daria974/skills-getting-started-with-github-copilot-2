"""
Tests for Mergington High School Activities API.
Uses FastAPI's TestClient (via httpx) — no running server needed.
Each test resets participant state via an autouse fixture.
"""

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the original participants list after every test."""
    original = {name: list(data["participants"]) for name, data in activities.items()}
    yield
    for name, data in activities.items():
        data["participants"] = original[name]


@pytest.fixture
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

class TestGetActivities:
    def test_returns_all_activities(self, client):
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_activity_has_required_fields(self, client):
        response = client.get("/activities")
        for name, details in response.json().items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

class TestSignup:
    def test_signup_success(self, client):
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "new_student@mergington.edu"},
        )
        assert response.status_code == 200
        assert "new_student@mergington.edu" in response.json()["message"]

    def test_signup_adds_participant(self, client):
        client.post(
            "/activities/Chess Club/signup",
            params={"email": "new_student@mergington.edu"},
        )
        participants = client.get("/activities").json()["Chess Club"]["participants"]
        assert "new_student@mergington.edu" in participants

    def test_signup_unknown_activity_returns_404(self, client):
        response = client.post(
            "/activities/Underwater Basket Weaving/signup",
            params={"email": "student@mergington.edu"},
        )
        assert response.status_code == 404

    def test_signup_missing_email_returns_422(self, client):
        response = client.post("/activities/Chess Club/signup")
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

class TestUnregister:
    def test_unregister_success(self, client):
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"},
        )
        assert response.status_code == 200
        assert "michael@mergington.edu" in response.json()["message"]

    def test_unregister_removes_participant(self, client):
        client.delete(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"},
        )
        participants = client.get("/activities").json()["Chess Club"]["participants"]
        assert "michael@mergington.edu" not in participants

    def test_unregister_unknown_activity_returns_404(self, client):
        response = client.delete(
            "/activities/Underwater Basket Weaving/signup",
            params={"email": "student@mergington.edu"},
        )
        assert response.status_code == 404

    def test_unregister_non_participant_returns_404(self, client):
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "ghost@mergington.edu"},
        )
        assert response.status_code == 404
