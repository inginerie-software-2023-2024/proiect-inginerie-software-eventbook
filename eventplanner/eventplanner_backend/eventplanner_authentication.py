from http import HTTPStatus


from eventplanner.eventplanner_backend import (
    eventplanner_authentication_helper as auth_helper,
)
from eventplanner.eventplanner_backend.eventplanner_database import (
    users_table,
    user_query,
)
from eventplanner.eventplanner_backend.eventplanner_base_models import User, Role

from fastapi import APIRouter
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


@router.post("/register")
def register_user(user: User):
    existing_user = users_table.search(user_query.username == user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = auth_helper.get_password_hash(user.password)
    user_id = users_table.insert(
        {
            "username": user.username,
            "password": hashed_password,
            "email": user.email,
            "role": user._role.value,
        }
    )
    return {"message": "User created successfully", "user_id": user_id}


@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = auth_helper.create_access_token(data=user)
    return {"access_token": access_token, "token_type": "bearer"}


def authenticate_user(username: str, password: str):
    users = users_table.search(user_query.username == username)
    if users:
        user = users[0]  # Assuming username is unique
        if auth_helper.verify_password(password, user["password"]):
            return user
    return None

def get_current_active_admin(
    current_user: User = Depends(auth_helper.get_current_user),
):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return current_user
