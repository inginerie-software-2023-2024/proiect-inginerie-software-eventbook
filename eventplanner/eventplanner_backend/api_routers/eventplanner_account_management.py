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
    return current_user.dict(
        include={"username", "email", "events_created", "events_participation"}
    )


@account_management_router.post("/users/register", tags=[Tags.ACCOUNT])
def register_user(input_user: UserBase):
    check_user_existence(input_user.username, input_user.email)

    uid = generate_unique_user_id()
    input_user.password = auth_helper.get_password_hash(input_user.password)

    new_user = User(**input_user.model_dump(), id=uid, token_version=0)
    users_table.insert(new_user.model_dump())

    return {"message": "User created successfully", "uid": uid}


@account_management_router.post("/users/friends/add", tags=[Tags.ACCOUNT])
def add_friend_user(
    friend_id: str, current_user: User = Depends(auth_helper.get_current_user)
):
    return manage_friendship(current_user, friend_id, add=True)


@account_management_router.post("/users/friends/remove", tags=[Tags.ACCOUNT])
def remove_friend_user(
    friend_id: str, current_user: User = Depends(auth_helper.get_current_user)
):
    return manage_friendship(current_user, friend_id, add=False)


@account_management_router.get("/users/{username}", tags=[Tags.ACCOUNT])
def get_user(username: str):
    user = shared_functions.get_user_by_name(username)
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    return user

@account_management_router.post("/users/logout", tags=[Tags.ACCOUNT])
def user_logout(current_user: User = Depends(auth_helper.get_current_user)):
    shared_functions.logout_by_id(current_user.id)
    return {"message": "User logged out successfully"}


@account_management_router.put("/users/update", tags=[Tags.ACCOUNT])
def update_user(
    update_info: UserBase, current_user: User = Depends(auth_helper.get_current_user)
):
    check_user_existence(
        update_info.username, update_info.email, exclude_id=current_user.id
    )
    update_data = update_info.dict(exclude_unset=True)
    update_data["password"] = auth_helper.get_password_hash(update_info.password)

    users_table.update(update_data, user_query.id == current_user.id)
    return {"message": "User updated successfully"}


@account_management_router.delete("/users/delete", tags=[Tags.ACCOUNT])
def delete_user(current_user: User = Depends(auth_helper.get_current_user)):
    users_table.remove(user_query.id == current_user.id)
    return {"message": "Account successfully deleted"}
