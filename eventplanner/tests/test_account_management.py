"""
Test module for account management related endpoints.

It contains tests for the following endpoints:
    - [POST] /users/register
    - [POST] /users/friends/add
    - [POST] /users/friends/remove
    - [GET] /users/{username}
    - [PUT] /users/update
    - [DELETE] /users/delete
"""
import sys
import pathlib
from os.path import dirname, realpath

sys.path.append(str(pathlib.Path(dirname(realpath(__file__)) + "../../..").resolve()))

from fastapi.testclient import TestClient
from eventplanner.eventplanner_backend.app.eventplanner_main import app
from eventplanner.eventplanner_backend.eventplanner_database import (
    users_table,
    event_table,
    user_query,
)


client = TestClient(app)


def test_unique_username_and_email_success():
    try:
        response = client.post(
            "/users/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 200
        assert "User created successfully" in response.json()["message"]

        # Cleanup
    finally:
        users_table.truncate()
        event_table.truncate()


#
# def test_add_friend_success():
#     try:
#         # Register a new user
#         response = client.post(
#             "/users/register",
#             json={
#                 "username": "user1",
#                 "email": "user1@example.com",
#                 "password": "password123",
#             },
#         )
#         # Get user1 id
#         user1_id = response.json()["uid"]
#
#         assert response.status_code == 200
#         assert "User created successfully" in response.json()["message"]
#
#         # Register another user
#         response = client.post(
#             "/users/register",
#             json={
#                 "username": "user2",
#                 "email": "user2@example.com",
#                 "password": "password123",
#             },
#         )
#         # Get user2 id
#         user2_id = response.json()["uid"]
#
#         assert response.status_code == 200
#         assert "User created successfully" in response.json()["message"]
#
#         # Login as user1
#         response = client.post(
#             "/token",
#             data={"username": "user1", "password": "password123"},
#         )
#         assert response.status_code == 200
#         assert "access_token" in response.json()
#
#         # Add user2 as a friend
#         access_token = response.json()["access_token"]
#         headers = {"Authorization": f"Bearer {access_token}"}
#         response = client.post(
#             f"/users/friends/add?friend_id={user2_id}", headers=headers
#         )
#         assert response.status_code == 200
#         assert "Friendship updated successfully" in response.json()["message"]
#
#     # Cleanup - Delete the users from the database
#     finally:
#         users_table.truncate()
#         event_table.truncate()


def test_remove_friend_successfully():
    try:
        # Create a user
        response = client.post(
            "/users/register",
            json={
                "username": "user1",
                "email": "user1@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 200
        assert "User created successfully" in response.json()["message"]

        # Get user id
        user1_id = response.json()["uid"]

        response = client.post(
            "/users/register",
            json={
                "username": "user2",
                "email": "user2@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 200
        assert "User created successfully" in response.json()["message"]

        # Get user id
        user2_id = response.json()["uid"]

        # Get access token
        response = client.post(
            "/token",
            data={
                "username": "user1",
                "password": "password123",
            },
        )
        assert response.status_code == 200
        access_token = response.json()["access_token"]

        # Add a friend
        user1 = users_table.search(user_query.id == user1_id)[0]
        users_table.update(
            {"friends": (user1["friends"] or []) + [(user2_id)]},
            user_query.id == user1_id,
        )

        user2 = users_table.search(user_query.id == user2_id)[0]
        users_table.update(
            {"friends": (user2["friends"] or []) + [(user1_id)]},
            user_query.id == user2_id,
        )

        # Remove the friend
        response = client.post(
            f"/users/friends/remove?friend_id={user2_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"friend_id": user2_id},
        )
        assert response.status_code == 200
        assert "Friendship updated successfully" in response.json()["message"]

    # Cleanup
    finally:
        users_table.truncate()
        event_table.truncate()


def test_delete_user_with_valid_token():
    try:
        # Register a new user
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

        # Login to obtain authentication token
        response = client.post(
            "/token",
            data={
                "username": "testuser",
                "password": "password123",
            },
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

        # Delete user account using authentication token
        access_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.delete("/users/delete", headers=headers)
        assert response.status_code == 200
        assert "Account successfully deleted" in response.json()["message"]
    finally:
        users_table.truncate()
        event_table.truncate()


def test_update_user_success():
    try:
        # Register a new user
        response = client.post(
            "/users/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123",
            },
        )

        newuser_uid = response.json()["uid"]
        assert response.status_code == 200
        assert "User created successfully" in response.json()["message"]

        # Login with the new user
        response = client.post(
            "/token",
            data={
                "username": "newuser",
                "password": "password123",
            },
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

        # Update the user's information
        access_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.put(
            "/users/update",
            headers=headers,
            json={
                "username": "updateduser",
                "email": "updateduser@example.com",
                "password": "newpassword123",
            },
        )
        assert response.status_code == 200
        assert "User updated successfully" in response.json()["message"]

        response = client.get("/users/updateduser")

        assert response.status_code == 200

        # Cleanup
    finally:
        users_table.truncate()
        event_table.truncate()


def test_get_existing_user_by_username():
    try:
        # Create a new user
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

        # Get the user id
        uid = response.json()["uid"]

        # Get the access token
        response = client.post(
            "/token",
            data={
                "username": "testuser",
                "password": "password123",
            },
        )
        assert response.status_code == 200
        access_token = response.json()["access_token"]

        # Get the user by username
        response = client.get(
            f"/users/testuser",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200

        # Check if the returned user matches the created user
        assert response.json()["username"] == "testuser"
        assert response.json()["email"] == "testuser@example.com"

        # Cleanup
    finally:
        users_table.truncate()
        event_table.truncate()
