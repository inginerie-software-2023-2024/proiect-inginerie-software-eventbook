"""
Main module for handling event management interactions. Provides utilities for
CRUD operations and some extra  interactions.
"""
from uuid import uuid4
from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from eventplanner.eventplanner_backend.api_routers import shared_functions
from eventplanner.common.eventplanner_common import EventplannerBackendTags as Tags
from eventplanner.eventplanner_backend.schemas.eventplanner_base_models import (
    User,
    UserBase,
)
from eventplanner.eventplanner_backend.eventplanner_database import (
    users_table,
    user_query,
)
from eventplanner.eventplanner_backend.authentication import (
    eventplanner_authentication_helper as auth_helper,
)

account_management_router = APIRouter()


# Helper functions
def generate_unique_user_id():
    uid = str(uuid4())
    while users_table.search(user_query.id == uid):
        uid = str(uuid4())
    return uid


def check_user_existence(username: str, email: str, exclude_id: str = None):
    existing_user = users_table.search(user_query.username == username)
    existing_mail = users_table.search(user_query.email == email)
    if existing_user and (not exclude_id or existing_user[0]["id"] != exclude_id):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Username already registered"
        )
    if existing_mail and (not exclude_id or existing_mail[0]["id"] != exclude_id):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Email already registered"
        )


def manage_friendship(current_user: User, friend_id: str, add: bool):
    friend = shared_functions.get_user_by_id(friend_id)
    if not friend:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Friend not found")

    current_user_friends = current_user.friends or set()
    friend_friends = friend.friends or set()

    if add:
        if friend_id in current_user_friends:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail="Already friends"
            )
        current_user_friends.add(friend_id)
        friend_friends.add(current_user.id)
    else:
        if friend_id not in current_user_friends:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail="Not friends"
            )
        current_user_friends.remove(friend_id)
        friend_friends.remove(current_user.id)

    users_table.update(
        {"friends": current_user_friends}, user_query.id == current_user.id
    )
    users_table.update({"friends": friend_friends}, user_query.id == friend_id)

    return {"message": "Friendship updated successfully"}


# API endpoints
@account_management_router.get("/users/me", tags=[Tags.ACCOUNT])
def me_user(current_user: User = Depends(auth_helper.get_current_user)):
    """
    Endpoint utility for presenting information about the current user logged in.

    ```
    Returns:
        Dictionary with information about user
    Raises:
        [401]UNAUTHORIZED: Invalid credentials
    ```
    Example of valid response:
    ```
    {
        "username": "example",
        "email": "example@email.com",
        "events_participation": null,
        "events_created": null
    }
    ```
    """
    return current_user.model_dump(
        include={"username", "email", "events_created", "events_participation"}
    )


@account_management_router.post("/users/register", tags=[Tags.ACCOUNT])
def register_user(input_user: UserBase):
    """
    Endpoint utility for registering a user.

    ```
    Args:
        input_user: UserBase object used as a front for registering
    Returns:
        A dictionary with corresponding message
    Raises:
        [400]BAD_REQUEST: Username already registered
        [400]BAD_REQUEST: Email already registered
        [401]UNAUTHORIZED: Invalid credentials
    ```

    Example of a valid request body:
    ```
    {
      "username": "example",
      "email": "example@emai.com",
      "password": "example"
    }
    ```

    Example of a valid response:
    ```
    {
      "message": "User created successfully",
      "uid": "d7b01a4d-6f76-4c25-9508-8bd08d869bab"
    }
    ```
    """
    check_user_existence(input_user.username, input_user.email)

    uid = generate_unique_user_id()
    input_user.password = auth_helper.get_password_hash(input_user.password)

    new_user = User(**input_user.model_dump(), id=uid, token_version=0)
    users_table.insert(new_user.model_dump())

    return {"message": "User created successfully", "uid": uid}


# @account_management_router.post("/users/friends/add", tags=[Tags.ACCOUNT])
def add_friend_user(
    friend_id: str, current_user: User = Depends(auth_helper.get_current_user)
):
    return manage_friendship(current_user, friend_id, add=True)


@account_management_router.post("/users/friends/remove", tags=[Tags.ACCOUNT])
def remove_friend_user(
    friend_id: str, current_user: User = Depends(auth_helper.get_current_user)
):
    """
    Endpoint utility for removing a friend from friend list.

    ```
    Args:
        friend_id: ID of the friend to be removed
        current_user: Current user logged in (will be retrieved from access token)

    Returns:
        A dictionary with corresponding message

    Raises:
        [401]UNAUTHORIZED: Invalid credentials
        [400]BAD_REQUEST: Friend not found in list
    ```

    Example of valid request query:
    ```
        "friend_id": 1111-11111-11111-11111
    ```

    Example of valid response body:
    ```
    {
        "message": "Friendship updated successfully"
    }
    ```

    """
    return manage_friendship(current_user, friend_id, add=False)


@account_management_router.get("/users/{username}", tags=[Tags.ACCOUNT])
def get_user(username: str):
    """
    Endpoint utility to retrieve a user by its username.

    ```
    Args:
        username: Users username

    Returns:
        Dictionary with users field

    Raises:
        [404]NOT_FOUND: User not found
    ```
    Example of valid request body:
    ```
        username: example
    ```

    Example of valid response body:
    ```
    {
      "username": "example",
      "email": "example@emai.com",
      "password": "$2b$12$QMlcRwaxFSCx7Wx/1XBR/ORKgAkeuQQAQL1iQ/2AZ7I6gMVGPUk66",
      "id": "d7b01a4d-6f76-4c25-9508-8bd08d869bab",
      "role": "user",
      "events_participation": null,
      "events_created": null,
      "active_invitations": null,
      "notifications": null,
      "token_version": 0,
      "friends": null
    }
    ```
    """
    user = shared_functions.get_user_by_name(username)
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    return user

@account_management_router.get("/users/{user_id}/v1", tags=[Tags.ACCOUNT])
def get_user(user_id: str):
    """
    Endpoint utility to retrieve a user by its username.

    ```
    Args:
        user_id: User's id

    Returns:
        Dictionary with users field

    Raises:
        [404]NOT_FOUND: User not found
    ```
    Example of valid request body:
    ```
        username: example
    ```

    Example of valid response body:
    ```
    {
      "username": "example",
      "email": "example@emai.com",
      "password": "$2b$12$QMlcRwaxFSCx7Wx/1XBR/ORKgAkeuQQAQL1iQ/2AZ7I6gMVGPUk66",
      "id": "d7b01a4d-6f76-4c25-9508-8bd08d869bab",
      "role": "user",
      "events_participation": null,
      "events_created": null,
      "active_invitations": null,
      "notifications": null,
      "token_version": 0,
      "friends": null
    }
    ```
    """
    user = shared_functions.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    return user

@account_management_router.post("/users/all", tags=[Tags.ACCOUNT])
def get_all_users():
    users = users_table.all()
    users = [{"username": user["username"],"email": user["email"]} for user in users]
    return users
@account_management_router.post("/users/logout", tags=[Tags.ACCOUNT])
def user_logout(current_user: User = Depends(auth_helper.get_current_user)):
    """
    Endpoint utility for invalidating a token. It raises the token version by one.

    ```
    Raises:
        [401]NOT_AUTHORIZED: Invalid credentials
    ```

    Example of valid response body:
    ```
    {
        "message": "User logged out successfully"
    }
    ```

    """
    shared_functions.logout_by_id(current_user.id)
    return {"message": "User logged out successfully"}


@account_management_router.put("/users/update", tags=[Tags.ACCOUNT])
def update_user(
    update_info: UserBase, current_user: User = Depends(auth_helper.get_current_user)
):
    """
    Endpoint utility for updating current logged user.
    ```
    Args:
        update_info: UserBase model info

    Returns:
        Dictionary with corresponding message

    Raises:
        [400]BAD_REQUEST: Username already registered
        [400]BAD_REQUEST: Email already registered
        [401]UNAUTHORIZED: Invalid credentials
    ```

    Examples of valid response body:
    ```
    {
        "message": "User logged out successfully"
    }
    ```
    """
    check_user_existence(
        update_info.username, update_info.email, exclude_id=current_user.id
    )
    update_data = update_info
    if update_data.password!= "N/A":
        update_data.password = auth_helper.get_password_hash(update_info.password)
    else:
        update_data.password = current_user.password

    users_table.update(update_data, user_query.id == current_user.id)
    return {"message": "User updated successfully"}


@account_management_router.delete("/users/delete", tags=[Tags.ACCOUNT])
def delete_user(current_user: User = Depends(auth_helper.get_current_user)):
    """
    Endpoint utility for deleting current logged user.

    ```
    Returns:
        Dictionary with corresponding message
    ```

    Examples of valid response body:
    ```
    {
    "message": "Account successfully deleted"
    }
    ```


    """
    users_table.remove(user_query.id == current_user.id)
    return {"message": "Account successfully deleted"}
