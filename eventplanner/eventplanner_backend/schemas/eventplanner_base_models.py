from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"

class UserBase(BaseModel):
    username: str
    email: EmailStr
    password: str


class User(UserBase):
    id: str
    role:Role= Role.USER
    event_participation: list[str]= []
    event_created: list[str]= []

class EventBase(BaseModel):
    title: str
    description: str = None
    start_time: datetime
    end_time: datetime
    location: str = None
    organizers: list[str]
    participants: list[str]

class Event(EventBase):
    id: str