from enum import Enum

from pydantic import BaseModel, EmailStr



class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"


class User(BaseModel):
    username: str
    email: EmailStr
    password: str  # This will be hashed
    _role: Role = Role.USER


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None

