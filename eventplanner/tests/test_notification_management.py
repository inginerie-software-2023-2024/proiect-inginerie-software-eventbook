"""
Test module for notification management related endpoints.

Contains tests for the following endpoints:
    - [POST] /notifications/{user_id}/notify
"""
import sys
import time
import pathlib
from os.path import dirname, realpath

sys.path.append(str(pathlib.Path(dirname(realpath(__file__)) + "../../..").resolve()))

from fastapi.testclient import TestClient
from eventplanner.eventplanner_backend.app.eventplanner_main import app
from eventplanner.eventplanner_backend.eventplanner_database import (
    users_table,
    event_table,
    events_query,
    user_query
)

client = TestClient(app)
def test_user_notified_successfully():
    try:
        # Create a user
        response = client.post(
            "/users/register",
            json={
                "username": "testuser",
                "email": "testuser@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 200
        assert "User created successfully" in response.json()["message"]

        # Get the user ID
        user_id = response.json()["uid"]

        # Notify the user
        response = client.post(
            f"/notifications/{user_id}/notify",
            params={
                "notification_type": "invitation",
                "content": "You have been invited to an event",
            },
        )
        assert response.status_code == 200
        assert "User notified successfully!" in response.json()["message"]

        # Query user table for the user
        user = users_table.search(user_query.id == user_id)[0]

        # Assert if the invitation is in active_invitations field
        assert any(
            notification.message == "You have been invited to an event"
            for notification in user["notifications"]
        )

    finally:
        # Cleanup
        users_table.truncate()
        event_table.truncate()