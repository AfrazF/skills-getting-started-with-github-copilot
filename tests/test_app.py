import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client(monkeypatch):
    test_activities = {
        "Chess Club": {
            "description": "Learn chess",
            "schedule": "Fridays",
            "max_participants": 12,
            "participants": ["student@example.com"],
        },
        "Art Club": {
            "description": "Explore art",
            "schedule": "Thursdays",
            "max_participants": 18,
            "participants": [],
        },
    }
    monkeypatch.setattr(app_module, "activities", test_activities)
    return TestClient(app_module.app)


def test_root_redirects_to_activity_page(client):
    # Arrange

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_current_activities(client):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()["Chess Club"]["participants"] == ["student@example.com"]
    assert response.json()["Art Club"]["participants"] == []


def test_signup_adds_student_to_activity(client):
    # Arrange
    email = "new-student@example.com"

    # Act
    response = client.post("/activities/Art%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Art Club"}
    assert email in client.get("/activities").json()["Art Club"]["participants"]


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    email = "new-student@example.com"

    # Act
    response = client.post("/activities/Unknown%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_rejects_duplicate_registration(client):
    # Arrange
    email = "student@example.com"

    # Act
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }


def test_unregister_removes_student_from_activity(client):
    # Arrange
    email = "student@example.com"

    # Act
    response = client.delete("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in client.get("/activities").json()["Chess Club"]["participants"]


def test_unregister_returns_not_found_for_unknown_activity(client):
    # Arrange
    email = "student@example.com"

    # Act
    response = client.delete("/activities/Unknown%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_returns_not_found_for_missing_registration(client):
    # Arrange
    email = "not-signed-up@example.com"

    # Act
    response = client.delete("/activities/Art%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
