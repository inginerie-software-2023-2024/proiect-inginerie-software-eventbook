"""
Test module for notification management related endpoints.

Contains tests for the following endpoints:
    - [POST] /invitations
    - [GET] /invitations/{invite_id}/answer
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


def test_inviting_user_with_valid_data_and_authentication_returns_success_message_and_invite_id():
    try:
        user_data = {
            "username": "test_user",
            "email": "test_user@example.com",
            "password": "password123"
        }
        response = client.post("/users/register", json=user_data)
        assert response.status_code == 200
        assert "User created successfully" in response.json()["message"]

        # Get the user id
        user_id = response.json()["uid"]

        user_data1 = {
            "username": "test_user1",
            "email": "test_user1@example.com",
            "password": "password123"
        }
        response = client.post("/users/register", json=user_data1)
        assert response.status_code == 200
        assert "User created successfully" in response.json()["message"]

        # Get the user id
        user1_id = response.json()["uid"]

        # Get access token
        token_response = client.post("/token",
                                     data={"username": user_data["username"], "password": user_data["password"]})
        assert token_response.status_code == 200
        access_token = token_response.json()["access_token"]

        event1 = client.post("/events/register",
                             params={"title": "Event 1", "location": "test", "description": "Description 1",
                                     "public": True}, headers={"Authorization": f"Bearer {access_token}"}).json()

        # Invite a user
        response = client.post(
            "/invitations",
            json={
                "start_user": user_id,
                "end_user": user1_id,
                "type": "event",
                "event_id": event1["id_event"],
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        assert "User invited successfully" in response.json()["message"]
        assert len(users_table.search(user_query.id == user1_id)[0]["active_invitations"])

    finally:
        # Cleanup
        users_table.truncate()
        event_table.truncate()

def test_valid_invitation_given_to_valid_user_with_request_to_join():
    try:
        # Create a test user
        user_data = {
            "username": "test_user",
            "email": "test_user@example.com",
            "password": "password123"
        }
        response = client.post("/users/register", json=user_data)
        assert response.status_code == 200
        assert "User created successfully" in response.json()["message"]

        # Get the user id
        user_id = response.json()["uid"]

        # Create another test user
        user_data1 = {
            "username": "test_user1",
            "email": "test_user1@example.com",
            "password": "password123"
        }
        response = client.post("/users/register", json=user_data1)
        assert response.status_code == 200
        assert "User created successfully" in response.json()["message"]

        # Get the user id
        user1_id = response.json()["uid"]

        # Get access token for the first user
        token_response = client.post("/token",
                                     data={"username": user_data["username"], "password": user_data["password"]})
        assert token_response.status_code == 200
        access_token = token_response.json()["access_token"]

        # Create an event
        event1 = client.post("/events/register",
                             params={"title": "Event 1", "location": "test", "description": "Description 1",
                                     "public": True}, headers={"Authorization": f"Bearer {access_token}"}).json()

        # Invite the second user to the event with a request to join
        response = client.post(
            "/invitations",
            json={
                "start_user": user_id,
                "end_user": user_id,
                "type": "request",
                "event_id": event1["id_event"],
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200

        # Check if the second user has the invitation in their requests_to_join
        event = event_table.search(events_query.id == event1["id_event"])[0]
        assert len(event["requests_to_join"])

    finally:
        # Cleanup
        users_table.truncate()
        event_table.truncate()
