from typing import Optional
from pydantic import BaseModel, EmailStr
from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"


class User(BaseModel):
    username: str
    email: EmailStr
    password: str  # This will be hashed
    role: Role = Role.USER
