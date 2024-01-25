import uuid
import time
import hashlib
from http import HTTPStatus

from geopy import Nominatim
from fastapi.exceptions import HTTPException
from eventplanner.eventplanner_backend.schemas.eventplanner_base_models import (
    User,
    InvitationBase,
    Event,
    NotificationType,
    Notification,
)
from eventplanner.eventplanner_backend.authentication import (
    eventplanner_authentication_helper as auth_helper,
)
from eventplanner.eventplanner_backend.eventplanner_database import (
    users_table,
    user_query,
    event_table,
    events_query,
)


# Helper functions
def fetch_single_record(table, query, detail: str):
    record = table.search(query)
    if record:
        return record[0]
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=detail)


def generate_hash_id(*args):
    string_id = f"{''.join(map(str, args))}{uuid.uuid4()}"
    return hashlib.sha256(string_id.encode()).hexdigest()


# Business logic functions
def get_user_by_id(uid: str) -> User:
    user = fetch_single_record(users_table, user_query.id == uid, "User id not found")
    return User(**user)


def get_user_by_name(username: str) -> User:
    user = fetch_single_record(
        users_table, user_query.username == username, "Username not found"
    )
    return User(**user)


def logout_by_id(id: str) -> None:
    auth_helper.update_token_version(id)


def get_event_organizer_user(event_id: str) -> User:
    event_info = fetch_single_record(
        event_table, events_query.id == event_id, "Event not found with id"
    )
    organizer_id = event_info["organizer"]
    return get_user_by_id(organizer_id)


def get_event_by_id(event_id: str) -> Event:
    event = fetch_single_record(
        event_table, events_query.id == event_id, "Event not found with id"
    )
    return Event(**event)


def generate_invitation_id(invite: InvitationBase) -> str:
    return generate_hash_id(time.time(), invite.event_id, invite.end_user)


def generate_invitation_id_fields(event_id, end_user):
    return generate_hash_id(time.time(), event_id, end_user)


def generate_notification_id(user_id, notification_type, time_stamp) -> str:
    return generate_hash_id(time_stamp, user_id, notification_type)


def notify_user(
    user_id: str, notification_type: NotificationType, content: str
) -> dict:
    notif_time = time.time()
    notification_id = generate_notification_id(
        user_id, notification_type.value, notif_time
    )

    notification = Notification(
        user_id=user_id,
        notification_type=notification_type,
        time=notif_time,
        id=notification_id,
        message=content,
    )

    user = get_user_by_id(user_id)
    user_notifications = user.notifications or set()
    user_notifications.add(notification)

    users_table.update({"notifications": user_notifications}, user_query.id == user.id)

    return {"message": "User notified successfully!"}


def get_location_coordinates(location: str):
    geolocator = Nominatim(user_agent="eventplanner")
    location_data = geolocator.geocode(location)
    return (
        (location_data.latitude, location_data.longitude)
        if location_data
        else (None, None)
    )
