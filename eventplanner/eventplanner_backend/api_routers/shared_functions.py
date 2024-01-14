from http import HTTPStatus
from fastapi.exceptions import HTTPException

from eventplanner.eventplanner_backend.schemas.eventplanner_base_models import User, UserBase
from eventplanner.eventplanner_backend.eventplanner_database import users_table, user_query
from eventplanner.eventplanner_backend.authentication import eventplanner_authentication_helper as auth_helper


def get_user_by_id(uid: str) -> User:
    user = users_table.search(user_query.id == uid)
    if user:
        return user[0]

    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND,
        detail="User id not found"
    )


def get_user_by_name(username: str) -> User:
    user = users_table.search(user_query.username == username)
    if user:
        return user[0]

    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND,
        detail="Username not found"
    )

def logout_by_id(id: str):
    auth_helper.update_token_version(id)