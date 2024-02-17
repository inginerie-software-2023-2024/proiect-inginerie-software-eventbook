"""
Module for providing models for interacting with database
"""
import enum
from datetime import datetime
from enum import Enum
from typing import Optional, Set, List


from pydantic import BaseModel, field_serializer


class SetSerializer:
    """
    Serializer class for sets
    """

    @staticmethod
    def serialize(value: Set) -> list:
        return list(value)

    @staticmethod
    def deserialize(value: list) -> Set:
        return set(value)


class TimeInterval(enum.Enum):
    """
    Enum class for timeinterval options
    """

    DAY_1 = "1"
    DAY_3 = "3"
    DAY_7 = "7"
    DAY_14 = "14"
    DAY_16 = "16"


class Role(str, Enum):
    """
    Enum class for role types
    """

    ADMIN = "admin"
    USER = "user"


class InvitationType(enum.Enum):
    """
    Enum class for types of invitation
    """

    EVENT = "event"
    FRIEND = "friend"
    REQUEST = "request"


class InvitationBase(BaseModel):
    """
    Pydantic base model for invitation object
    """

    end_user: str | None = None
    start_user: str | None = None
    type: InvitationType
    event_id: str | None = None


class Invitation(InvitationBase):
    """
    Pydantic model for Invitation object
    """

    id: str
    time: str

    def __hash__(self):
        return hash(f"{self.time}{self.start_user}{self.end_user}")


class NotificationType(str, Enum):
    """
    Enum class for types of notification
    """

    INVITATION = "invitation"
    EVENT_UPDATE = "event_update"
    SYSTEM = "system"


class Notification(BaseModel):
    """
    Pydantic model for notification object
    """

    user_id: str
    notification_type: NotificationType
    message: str
    id: str
    time: float
    read: bool = False
    event_id: str = "0"

    def __hash__(self):
        return hash(f"{self.id}{self.user_id}{self.time}")


class UserBase(BaseModel):
    """
    Pydantic model for userbase info
    """

    username: str
    email: str
    password: str


class User(UserBase):
    """
    Pydantic model for user object
    """

    id: str
    role: Role = Role.USER
    events_participation: Set[str] | None = None
    events_created: Set[str] | None = None
    active_invitations: Set[Invitation] | None = None
    notifications: Set[Notification] | None = None
    token_version: int = 0
    friends: Set[str] | None = None

    @field_serializer(
        "events_participation",
        "events_created",
        "active_invitations",
        "notifications",
        "friends",
        when_used="json",
    )
    def serialize_set(self, field: set):
        if field:
            return list(field)
        return None


class HourlyWeatherData(BaseModel):
    """
    Pydantic model for hourly weather data
    """

    time: datetime
    temperature_2m: float
    relative_humidity_2m: float
    dew_point_2m: float
    apparent_temperature: float
    precipitation_probability: float
    precipitation: float
    rain: float
    snowfall: float
    snow_depth: float
    wind_speed_80m: float
    temperature_180m: Optional[float] = None  # Optional if not always present
    soil_temperature_6cm: Optional[float] = None  # Optional if not always present


class DailyWeatherData(BaseModel):
    """
    Pydantic model for daily weather data
    """

    date: datetime
    hourly_data: List[HourlyWeatherData]


class Weather(BaseModel):
    """
    Pydantic model for weather
    """

    hourly_data: List[HourlyWeatherData]


class EventBase(BaseModel):
    """
    Pydantic base model for event class
    """

    title: str
    tags: Set[str] | None = None
    description: str | None = None
    start_time: float | None = None
    end_time: float | None = None
    location: str | None = None
    public: bool = False


class Event(EventBase):
    """
    Pydantic model for event class
    """

    id: str
    organizer_name: str | None = None
    organizer_id: str | None = None
    admins: Set[str] | None = None
    participants: Set[str] | None = None
    requests_to_join: Set[Invitation] | None = None
    weather: List[DailyWeatherData] | None = None
