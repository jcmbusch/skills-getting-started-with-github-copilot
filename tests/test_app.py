import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]

def test_signup_success():
    response = client.post("/activities/Chess%20Club/signup?email=testuser@example.com")
    assert response.status_code == 200
    assert "Signed up testuser@example.com for Chess Club" in response.json()["message"]

    # Clean up: remove test user
    data = client.get("/activities").json()
    data["Chess Club"]["participants"].remove("testuser@example.com")

def test_signup_already_signed_up():
    # Use an existing participant
    response = client.post("/activities/Chess%20Club/signup?email=michael@mergington.edu")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"

def test_signup_activity_full():
    # Fill up an activity
    activity = "Art Club"
    # Add up to max participants
    for i in range(8):
        client.post(f"/activities/{activity}/signup?email=extrauser{i}@example.com")
    # Now it should be full
    for i in range(2):
        client.post(f"/activities/{activity}/signup?email=extrauserX{i}@example.com")
    response = client.post(f"/activities/{activity}/signup?email=overflow@example.com")
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"
    # Clean up: remove extra users
    data = client.get("/activities").json()
    for i in range(8):
        if f"extrauser{i}@example.com" in data[activity]["participants"]:
            data[activity]["participants"].remove(f"extrauser{i}@example.com")
    for i in range(2):
        if f"extrauserX{i}@example.com" in data[activity]["participants"]:
            data[activity]["participants"].remove(f"extrauserX{i}@example.com")
