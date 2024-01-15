import time
from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, EmailStr, constr

from eventplanner.eventplanner_backend.schemas.eventplanner_model_helpers import EventTags


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"


class UserBase(BaseModel):
    username: str
    email: EmailStr
    password: str


class User(UserBase):
    id: str
    role: Role = Role.USER
    event_participation: list[str] = []
    event_created: list[str] = []
    active_invitations: List[dict] = []


class EventBase(BaseModel):
    title: str
    tags: List[str]
    description: str = None
    start_time: datetime
    end_time: datetime
    location: str = None


class Event(EventBase):
    id: str
    organizer_name: str = None
    organizer_id: str = None
    participants: List[str] = []


class InvitationBase(BaseModel):
    time: float
    invited: str
    event: str
class Invitation(InvitationBase):
    id: str
    inviter: str