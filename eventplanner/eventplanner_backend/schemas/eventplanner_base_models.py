import enum
import time
from datetime import datetime
from enum import Enum
from typing import Optional, Set

import pydantic
from pydantic import BaseModel, EmailStr, validator, field_validator, field_serializer

from eventplanner.eventplanner_backend.schemas.eventplanner_model_helpers import (
    EventTags,
)


class SetSerializer:
    @staticmethod
    def serialize(value: Set) -> list:
        return list(value)

    @staticmethod
    def deserialize(value: list) -> Set:
        return set(value)


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"


class InvitationType(enum.Enum):
    EVENT = "event"
    FRIEND = "friend"
class InvitationBase(BaseModel):
    user_to_invite: str
    inviter: str
    type: InvitationType
    event_id: str | None

class Invitation(InvitationBase):
    id: str
    time: str

    def __hash__(self):
        return hash(f"{self.time}{self.inviter}{self.user_to_invite}")





class NotificationType(str, Enum):
    INVITATION = "invitation"
    EVENT_UPDATE = "event_update"
    SYSTEM = "system"


class Notification(BaseModel):
    user_id: str
    notification_type: NotificationType
    message: str
    id: str
    time: float
    read: bool = False

    def __hash__(self):
        return hash(f"{self.id}{self.user_id}{self.time}")


class UserBase(BaseModel):
    username: str
    email: EmailStr
    password: str


class User(UserBase):
    id: str
    role: Role = Role.USER
    events_participation: Set[str] | None = None
    events_created: Set[str] | None = None
    active_invitations: Set[Invitation] | None = None
    notifications: Set[Notification] | None = None
    token_version: int = 0
    friends: Set[str] | None = None

    @field_serializer("events_participation", "events_created", "active_invitations", "notifications", when_used='json')
    def serialize_set(self, field: set):
        return list(field)


class Weather(BaseModel):
    temperature: float
    condition: str
    humidity: float
    wind_speed: float
    additional_info: Optional[str] = None

class EventBase(BaseModel):
    title: str
    tags: Set[str] | None
    description: str = None
    start_time: float
    end_time: float
    location: str = None
    public: bool = False
    weather: Weather | None = None


class Event(EventBase):
    id: str
    organizer_name: str = None
    organizer_id: str = None
    admins: Set[str] | None = None
    participants: Set[str] | None = None
