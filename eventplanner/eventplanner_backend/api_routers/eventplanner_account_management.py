from uuid import uuid4
from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from eventplanner.eventplanner_backend.api_routers import shared_functions
from eventplanner.common.eventplanner_common import EventplannerBackendTags as Tags
from eventplanner.eventplanner_backend.schemas.eventplanner_base_models import User, UserBase
from eventplanner.eventplanner_backend.eventplanner_database import users_table, user_query
from eventplanner.eventplanner_backend.authentication import eventplanner_authentication_helper as auth_helper

account_management_router = APIRouter()

@account_management_router.get("/users/me", tags=[Tags.ACCOUNT])
def me_user(current_user: dict= Depends(auth_helper.get_current_user)):
    return {
        "username": current_user["username"],
        "email": current_user["email"],
        "event_created": current_user["event_created"],
        "event_participation": current_user["event_participation"]
    }

@account_management_router.post("/users/register", tags=[Tags.ACCOUNT])
def register_user(input_user: UserBase):
    existing_user = users_table.search(user_query.username == input_user.username)
    existing_mail = users_table.search(user_query.email == input_user.email)
    if existing_user:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Username already registered")
    if existing_mail:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Email already registered")

    uid = str(uuid4())
    while users_table.search(user_query.id == uid):
        uid = str(uuid4())

    input_user.password = auth_helper.get_password_hash(input_user.password)

    user_fields = dict(input_user) | {"id": uid}

    new_user = User(**dict(user_fields))

    users_table.insert(dict(new_user) | {"token_version": 0})

    return {"message": "User created successfully"}


@account_management_router.get("/users/{username}", tags=[Tags.ACCOUNT])
def get_user(username: str):
    user = shared_functions.get_user_by_name(username)

    user_display_fields = {field: user[field] for field in set(user) - {"password", "id", "role", "token_version"}}
    return user_display_fields


@account_management_router.post("/users/logout", tags=[Tags.ACCOUNT])
def user_logout(current_user: dict = Depends(auth_helper.get_current_user)):
    shared_functions.logout_by_id(current_user["id"])
    return {"message": "User logged out successfully"}


@account_management_router.put("/users/update", tags=[Tags.ACCOUNT])
def update_user(update_info: UserBase, current_user: dict = Depends(auth_helper.get_current_user)):
    existing_user = users_table.search(user_query.username == update_info.username)
    existing_mail = users_table.search(user_query.email == update_info.email)

    if existing_user and existing_user[0]["id"] != current_user["id"]:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Username already registered")
    if existing_mail and existing_user[0]["id"] != current_user["id"]:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Email already registered")

    users_table.update({
        "username": update_info.username,
        "password": auth_helper.get_password_hash(update_info.password),
        "email": update_info.email
    }, user_query.id == current_user["id"])

    shared_functions.logout_by_id(current_user["id"])

    return {"message": "User updated successfully"}


@account_management_router.delete("/users/delete", tags=[Tags.ACCOUNT])
def delete_user(current_user: dict = Depends(auth_helper.get_current_user)):
    users_table.remove(user_query.id == current_user["id"])

    return {"message": "Account successfully deleted"}

