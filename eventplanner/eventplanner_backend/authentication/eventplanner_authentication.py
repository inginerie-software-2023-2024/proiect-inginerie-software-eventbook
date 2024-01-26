"""
Module for authentication related endpoints
"""


from fastapi import APIRouter
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from eventplanner.eventplanner_backend.authentication import (
    eventplanner_authentication_helper as auth_helper,
)
from eventplanner.eventplanner_backend.eventplanner_database import (
    users_table,
    user_query,
)
from eventplanner.common.eventplanner_common import EventplannerBackendTags as Tags
from eventplanner.eventplanner_backend.schemas.eventplanner_base_models import (
    User,
    Role,
)

auth_router = APIRouter()


@auth_router.post("/token", tags=[Tags.AUTH])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = auth_helper.create_access_token(
        data=user, version=user.token_version
    )
    return {"access_token": access_token, "token_type": "bearer"}


def authenticate_user(username: str, password: str) -> User | None:
    users = users_table.search(user_query.username == username)
    if users:
        user = users[0]  # Assuming username is unique
        if auth_helper.verify_password(password, user["password"]):
            return User(**user)
    return None


def get_current_active_admin(
    current_user: User = Depends(auth_helper.get_current_user),
):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return current_user
