import copy

import pytest
from fastapi.testclient import TestClient

from app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset mutable app state before each test (AAA: Arrange state)."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_root_redirects_to_static():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code in (302, 307)
    assert response.headers["location"].endswith("/static/index.html")


def test_get_activities():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_for_activity_success():
    # Arrange
    client = TestClient(app)
    new_email = "new_student@mergington.edu"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": new_email})

    # Assert
    assert response.status_code == 200
    assert new_email in activities["Chess Club"]["participants"]
    assert "Signed up" in response.json()["message"]


def test_signup_for_missing_activity_returns_404():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.post("/activities/Nonexistent/signup", params={"email": "a@b.com"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_student_returns_400():
    # Arrange
    client = TestClient(app)
    existing_email = "michael@mergington.edu"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
