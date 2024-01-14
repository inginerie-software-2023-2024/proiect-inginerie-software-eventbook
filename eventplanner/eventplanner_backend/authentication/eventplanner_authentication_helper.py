from typing import Annotated
from datetime import datetime, timedelta

import jwt

from fastapi import Depends
from starlette import status
from passlib.context import CryptContext
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer

from eventplanner.eventplanner_backend.eventplanner_database import (
    users_table,
    user_query,
)
from eventplanner.eventplanner_backend.schemas.eventplanner_base_models import User, UserBase


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Constants (these should be in your config or environment variables)
SECRET_KEY = "3245d4b2cef8db37d893f54df31c42d7f936b109d397c5384334043d2765eb4c"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_delta: timedelta | None = None, version: int= 0) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire, "ver": version})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def update_token_version(uid: str) -> User:
    user = users_table.search(user_query.id == uid)[0]
    new_version = user.get("token_version", 0) + 1
    users_table.update({"token_version": new_version}, user_query.id == uid)
    return new_version


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise HTTPException(
                status_code=401, detail="Invalid authentication credentials"
            )
        return username
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)])-> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    uid: str = payload.get("id")
    token_version: int = payload.get("ver")
    if uid is None:
        raise credentials_exception
    try:
        user = users_table.search(user_query.id == uid)[0]
    except IndexError:
        raise credentials_exception

    if user is None:
        raise credentials_exception
    if user["token_version"] != token_version:
        raise credentials_exception
    return user
