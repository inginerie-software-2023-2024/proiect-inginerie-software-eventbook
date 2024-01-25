"""
Test module for event management related endpoint.

Contains tests for the following endpoints:
    - [POST] /events/register
    - [GET] /events
    - [PUT] /events/update
    - [DELETE] /events/delete
    - [GET] /events/{event_id}/join
    - [POST] /events/{event_id}/status
    - [DELETE] /events/{event_id}/leave
    - [PUT] /events/{event_id}/admin
    - [DELETE] /events/{event_id}/admin
    - [PUT ] /events/{event_id}/ownership

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
)

client = TestClient(app)


def test_register_event_with_required_parameters():
    try:
        # Create a new user
        user = {
            "username": "test_user",
            "email": "test_user@example.com",
            "password": "password123",
        }
        response = client.post("/users/register", json=user)
        assert response.status_code == 200
        assert "User created successfully" in response.json()["message"]

        # Get the user id
        user_id = response.json()["uid"]

        # Get the access token
        response = client.post(
            "/token", data={"username": user["username"], "password": user["password"]}
        )
        assert response.status_code == 200
        access_token = response.json()["access_token"]

        # Register a new event
        event = {
            "title": "Test Event",
            "description": "This is a test event",
            "location": "Test Location",
            "start_time": time.time(),
            "end_time": time.time(),
            "current_user": user_id,
            "tags": ["#art"],
            "public": False,
        }
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post("/events/register", params=event, headers=headers)
        assert response.status_code == 200
        assert "Event created successfully" in response.json()["message"]
    finally:
        users_table.truncate()
        event_table.truncate()


def test_retrieve_public_event_with_valid_event_id_and_current_user():
    # Create a user
    try:
        user_data = {
            "username": "test_user",
            "email": "test_user@example.com",
            "password": "password123",
        }
        response = client.post("/users/register", json=user_data)
        assert response.status_code == 200
        assert "User created successfully" in response.json()["message"]

        # Get the user id
        user_id = response.json()["uid"]

        # Get access token
        token_response = client.post(
            "/token",
            data={"username": user_data["username"], "password": user_data["password"]},
        )
        assert token_response.status_code == 200
        access_token = token_response.json()["access_token"]

        # Create a public event
        event_data = {
            "title": "Public Event",
            "public": True,
            "description": "Public event",
            "location": "Test",
        }

        event_response = client.post(
            "/events/register",
            params=event_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert event_response.status_code == 200
        event_id = event_response.json()["id_event"]

        # Retrieve the public event
        get_event_response = client.get(
            f"/events/{event_id}", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert get_event_response.status_code == 200

        # Check the event details
        event = get_event_response.json()
        assert event["title"] == event_data["title"]
        assert event["id"] == event_id
        assert event["public"] == event_data["public"]

    finally:
        # Clean up
        users_table.truncate()
        event_table.truncate()


def test_returns_list_of_events_with_valid_query_parameters():
    # Create test events using the client

    try:
        user_data = {
            "username": "test_user",
            "email": "test_user@example.com",
            "password": "password123",
        }
        response = client.post("/users/register", json=user_data)
        assert response.status_code == 200
        assert "User created successfully" in response.json()["message"]

        # Get the user id
        user_id = response.json()["uid"]

        # Get access token
        token_response = client.post(
            "/token",
            data={"username": user_data["username"], "password": user_data["password"]},
        )
        assert token_response.status_code == 200
        access_token = token_response.json()["access_token"]

        event1 = client.post(
            "/events/register",
            params={
                "title": "Event 1",
                "location": "test",
                "description": "Description 1",
                "public": True,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        ).json()
        event2 = client.post(
            "/events/register",
            params={
                "title": "Event 2",
                "location": "test",
                "description": "Description 2",
                "public": False,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        ).json()
        event3 = client.post(
            "/events/register",
            params={
                "title": "Event 3",
                "location": "test",
                "description": "Description 3",
                "public": True,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        ).json()

        # Call the get_events endpoint with valid query parameters
        response = client.get("/events", params={"public": True})
        assert response.status_code == 200

        # Check that the response contains a list of events
        events = response.json()
        assert isinstance(events, list)
        assert len(events) == 2

        # Check the details of each event
        assert events[0]["title"] == "Event 1"
        assert events[0]["description"] == "Description 1"
        assert events[0]["public"] == True

        assert events[1]["title"] == "Event 3"
        assert events[1]["description"] == "Description 3"
        assert events[1]["public"] == True

    finally:
        # Clean up
        users_table.truncate()
        event_table.truncate()


def test_update_event_status_to_public_when_user_is_organizer_or_admin():
    try:
        user_data = {
            "username": "test_user",
            "email": "test_user@example.com",
            "password": "password123",
        }
        response = client.post("/users/register", json=user_data)
        assert response.status_code == 200
        assert "User created successfully" in response.json()["message"]

        # Get the user id
        user_id = response.json()["uid"]

        user_data1 = {
            "username": "test_user1",
            "email": "test_user1@example.com",
            "password": "password123",
        }
        response = client.post("/users/register", json=user_data1)
        assert response.status_code == 200
        assert "User created successfully" in response.json()["message"]

        # Get the user id
        user1_id = response.json()["uid"]

        # Get access token
        token_response = client.post(
            "/token",
            data={"username": user_data["username"], "password": user_data["password"]},
        )
        assert token_response.status_code == 200
        access_token = token_response.json()["access_token"]

        event1 = client.post(
            "/events/register",
            params={
                "title": "Event 1",
                "location": "test",
                "description": "Description 1",
                "public": True,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        ).json()

        response = client.put(
            f"/events/{event1['id_event']}/admin",
            params={"username": "test_user1"},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        assert "Admin added successfully to event" in response.json()["message"]

        token_response = client.post(
            "/token",
            data={
                "username": user_data1["username"],
                "password": user_data1["password"],
            },
        )
        assert token_response.status_code == 200
        access_token = token_response.json()["access_token"]

        # Call the change_event_status endpoint with public=True and token in authorization header
        response = client.post(
            f"/events/{event1['id_event']}/status",
            params={"public": False},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        # Assert that the status code is 200
        assert response.status_code == 200

        # Assert that the message is "Status updated successfully"
        assert response.json()["message"] == "Status updated successfully"

        # Assert that the event's public status is True
        event = client.get(
            f"/events/{event1['id_event']}",
            headers={"Authorization": f"Bearer {access_token}"},
        ).json()
        assert event["public"] == False

    finally:
        # Cleanup
        event_table.truncate()
        users_table.truncate()


def test_user_join_event_successfully():
    try:
        user_data = {
            "username": "test_user",
            "email": "test_user@example.com",
            "password": "password123",
        }
        response = client.post("/users/register", json=user_data)
        assert response.status_code == 200
        assert "User created successfully" in response.json()["message"]

        # Get the user id
        user_id = response.json()["uid"]

        user_data1 = {
            "username": "test_user1",
            "email": "test_user1@example.com",
            "password": "password123",
        }
        response = client.post("/users/register", json=user_data1)
        assert response.status_code == 200
        assert "User created successfully" in response.json()["message"]

        # Get the user id
        user1_id = response.json()["uid"]

        # Get access token
        token_response = client.post(
            "/token",
            data={"username": user_data["username"], "password": user_data["password"]},
        )
        assert token_response.status_code == 200
        access_token = token_response.json()["access_token"]

        event_public = client.post(
            "/events/register",
            params={
                "title": "Event 1",
                "location": "test",
                "description": "Description 1",
                "public": True,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )
        event_private = client.post(
            "/events/register",
            params={
                "title": "Event 2",
                "location": "test",
                "description": "Description 2",
                "public": False,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert event_private.status_code == 200
        assert event_public.status_code == 200

        token_response = client.post(
            "/token",
            data={
                "username": user_data1["username"],
                "password": user_data1["password"],
            },
        )
        assert token_response.status_code == 200
        access_token = token_response.json()["access_token"]

        join_public_event = client.get(
            f"/events/{event_public.json()['id_event']}/join",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        join_private_event = client.get(
            f"/events/{event_private.json()['id_event']}/join",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert join_public_event.status_code == 200
        assert join_private_event.status_code == 200

        private_ev = event_table.search(
            events_query.id == event_private.json()["id_event"]
        )
        public_ev = event_table.search(
            events_query.id == event_public.json()["id_event"]
        )

        assert len(private_ev) != 0
        assert len(public_ev) != 0

        ids_start_user_active_requests_private = [
            req.start_user for req in private_ev[0]["requests_to_join"]
        ]

        assert user1_id in ids_start_user_active_requests_private
        assert user1_id in public_ev[0]["participants"]

    finally:
        event_table.truncate()
        users_table.truncate()


def test_user_leaves_event_successfully():
    try:
        user_data = {
            "username": "test_user",
            "email": "test_user@example.com",
            "password": "password123",
        }
        response = client.post("/users/register", json=user_data)
        assert response.status_code == 200
        assert "User created successfully" in response.json()["message"]

        # Get the user id
        user_id = response.json()["uid"]

        user_data1 = {
            "username": "test_user1",
            "email": "test_user1@example.com",
            "password": "password123",
        }
        response = client.post("/users/register", json=user_data1)
        assert response.status_code == 200
        assert "User created successfully" in response.json()["message"]

        # Get the user id
        user1_id = response.json()["uid"]

        # Get access token
        token_response = client.post(
            "/token",
            data={"username": user_data["username"], "password": user_data["password"]},
        )
        assert token_response.status_code == 200
        access_token = token_response.json()["access_token"]

        event_public = client.post(
            "/events/register",
            params={
                "title": "Event 1",
                "location": "test",
                "description": "Description 1",
                "public": True,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert event_public.status_code == 200

        token_response = client.post(
            "/token",
            data={
                "username": user_data1["username"],
                "password": user_data1["password"],
            },
        )

        assert token_response.status_code == 200
        access_token = token_response.json()["access_token"]

        join_public_event = client.get(
            f"/events/{event_public.json()['id_event']}/join",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert join_public_event.status_code == 200
        public_ev = event_table.search(
            events_query.id == event_public.json()["id_event"]
        )
        assert user1_id in public_ev[0]["participants"]

        response = client.delete(
            f"/events/{event_public.json()['id_event']}/leave",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        public_ev = event_table.search(
            events_query.id == event_public.json()["id_event"]
        )
        assert not user1_id in public_ev[0]["participants"]

    # Cleanup
    finally:
        event_table.truncate()
        users_table.truncate()


def test_add_admin_event_success():
    try:
        user_data = {
            "username": "test_user",
            "email": "test_user@example.com",
            "password": "password123",
        }
        response = client.post("/users/register", json=user_data)
        assert response.status_code == 200
        assert "User created successfully" in response.json()["message"]

        # Get the user id
        user_id = response.json()["uid"]

        user_data1 = {
            "username": "test_user1",
            "email": "test_user1@example.com",
            "password": "password123",
        }
        response = client.post("/users/register", json=user_data1)
        assert response.status_code == 200
        assert "User created successfully" in response.json()["message"]

        # Get the user id
        user1_id = response.json()["uid"]

        # Get access token
        token_response = client.post(
            "/token",
            data={"username": user_data["username"], "password": user_data["password"]},
        )
        assert token_response.status_code == 200
        access_token = token_response.json()["access_token"]

        event_public = client.post(
            "/events/register",
            params={
                "title": "Event 1",
                "location": "test",
                "description": "Description 1",
                "public": True,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert event_public.status_code == 200

        response = client.put(
            f"/events/{event_public.json()['id_event']}/admin",
            params={"username": "test_user1"},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        assert response.json() == {"message": "Admin added successfully to event"}
        public_ev = event_table.search(
            events_query.id == event_public.json()["id_event"]
        )
        assert user1_id in public_ev[0]["admins"]

    finally:
        event_table.truncate()
        users_table.truncate()


def test_remove_admin_event_success():
    try:
        user_data = {
            "username": "test_user",
            "email": "test_user@example.com",
            "password": "password123",
        }
        response = client.post("/users/register", json=user_data)
        assert response.status_code == 200
        assert "User created successfully" in response.json()["message"]

        # Get the user id
        user_id = response.json()["uid"]

        user_data1 = {
            "username": "test_user1",
            "email": "test_user1@example.com",
            "password": "password123",
        }
        response = client.post("/users/register", json=user_data1)
        assert response.status_code == 200
        assert "User created successfully" in response.json()["message"]

        # Get the user id
        user1_id = response.json()["uid"]

        # Get access token
        token_response = client.post(
            "/token",
            data={"username": user_data["username"], "password": user_data["password"]},
        )
        assert token_response.status_code == 200
        access_token = token_response.json()["access_token"]

        event_public = client.post(
            "/events/register",
            params={
                "title": "Event 1",
                "location": "test",
                "description": "Description 1",
                "public": True,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert event_public.status_code == 200

        response = client.put(
            f"/events/{event_public.json()['id_event']}/admin",
            params={"username": "test_user1"},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        assert response.json() == {"message": "Admin added successfully to event"}
        public_ev = event_table.search(
            events_query.id == event_public.json()["id_event"]
        )
        assert user1_id in public_ev[0]["admins"]

        response = client.delete(
            f"/events/{event_public.json()['id_event']}/admin",
            params={"admin_id": user1_id},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        public_ev = event_table.search(
            events_query.id == event_public.json()["id_event"]
        )
        assert not user1_id in public_ev[0]["admins"]

    finally:
        event_table.truncate()
        users_table.truncate()


def test_change_ownership_successfully():
    try:
        user_data = {
            "username": "test_user",
            "email": "test_user@example.com",
            "password": "password123",
        }
        response = client.post("/users/register", json=user_data)
        assert response.status_code == 200
        assert "User created successfully" in response.json()["message"]

        # Get the user id
        user_id = response.json()["uid"]

        user_data1 = {
            "username": "test_user1",
            "email": "test_user1@example.com",
            "password": "password123",
        }
        response = client.post("/users/register", json=user_data1)
        assert response.status_code == 200
        assert "User created successfully" in response.json()["message"]

        # Get the user id
        user1_id = response.json()["uid"]

        # Get access token
        token_response = client.post(
            "/token",
            data={"username": user_data["username"], "password": user_data["password"]},
        )
        assert token_response.status_code == 200
        access_token = token_response.json()["access_token"]

        event_public = client.post(
            "/events/register",
            params={
                "title": "Event 1",
                "location": "test",
                "description": "Description 1",
                "public": True,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert event_public.status_code == 200

        response = client.put(
            f"/events/{event_public.json()['id_event']}/ownership",
            params={"username": "test_user1"},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        public_ev = event_table.search(
            events_query.id == event_public.json()["id_event"]
        )
        assert user1_id == public_ev[0]["organizer_id"]
    finally:
        event_table.truncate()
        users_table.truncate()


def test_update_event_success():
    try:
        user_data = {
            "username": "test_user",
            "email": "test_user@example.com",
            "password": "password123",
        }

        response = client.post("/users/register", json=user_data)
        assert response.status_code == 200
        assert "User created successfully" in response.json()["message"]

        # Get the user id
        user_id = response.json()["uid"]

        # Get access token
        token_response = client.post(
            "/token",
            data={"username": user_data["username"], "password": user_data["password"]},
        )
        assert token_response.status_code == 200
        access_token = token_response.json()["access_token"]
        # Create a new event
        response = client.post(
            "/events/register",
            params={
                "title": "Test Event",
                "tags": ["#art", "#bookclub"],
                "description": "Test description",
                "start_time": 1630000000,
                "end_time": 1630003600,
                "location": "Test location",
                "public": True,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Event created successfully"
        event_id = response.json()["id_event"]

        initial_event = event_table.search(events_query.id == event_id)
        # Update the event
        response = client.put(
            f"/events/{event_id}",
            json={
                "title": "Updated Event",
                "tags": ["tag3", "tag4"],
                "description": "Updated description",
                "start_time": 1630007200,
                "end_time": 1630010800,
                "location": "Updated location",
                "public": False,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )
        updated_event = event_table.search(events_query.id == event_id)
        assert response.status_code == 200
        assert response.json()["message"] == "Event updated successfully!"
        assert initial_event != updated_event
    finally:
        # Cleanup
        event_table.truncate()
        users_table.truncate()
