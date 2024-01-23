import hashlib
import random
import time
import uuid
from http import HTTPStatus
from fastapi.exceptions import HTTPException

from eventplanner.eventplanner_backend.schemas.eventplanner_base_models import (
    User,
    UserBase,
    InvitationBase, Event,
    NotificationType,
    Notification
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


def get_user_by_id(uid: str) -> User:
    user = users_table.search(user_query.id == uid)
    if user:
        return User(**user[0])

    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User id not found")


def get_user_by_name(username: str) -> User:
    user = users_table.search(user_query.username == username)
    if user:
        return User(**user[0])

    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Username not found")


def logout_by_id(id: str) -> None:
    auth_helper.update_token_version(id)


def get_event_organizer_user(event_id: str) -> User:
    event_info = event_table.search(events_query.id == event_id)
    if not event_info:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Event not found with id"
        )
    event_organizer = users_table.search(user_query.id == event_info[0]["organizer"])

    if not event_organizer:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="User not found with id"
        )

    return User(**event_organizer[0])


def get_event_by_id(event_id: str):
    event = event_table.search(events_query.id == event_id)

    if not event:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Event not found with id"
        )

    return Event(**event[0])


def generate_invitation_id(invite: InvitationBase):
    string_id = f"{time.time()}{invite.event_id}{invite.user_to_invite}{uuid.uuid4()}"
    hash_object = hashlib.sha256(string_id.encode())
    return hash_object.hexdigest()


def generate_notification_id(user_id, notification_type, time):
    string_id = f"{time}{user_id}{notification_type}{uuid.uuid4()}"
    hash_object = hashlib.sha256(string_id.encode())
    return hash_object.hexdigest()


def notify_user(user_id: str, notification_type: NotificationType, content: str):
    notif_time = time.time()

    notification_id = generate_notification_id(
        user_id=user_id,
        notification_type=notification_type.value,
        time=notif_time
    )

    notification = Notification(
        user_id=user_id,
        notification_type=notification_type,
        time=time.time(),
        id=notification_id,
        message=content,
    )
    user = get_user_by_id(user_id)

    users_table.update(
        {"notifications": user.notifications or set() | {notification}},
        user_query.id == user.id
    )

    return {
        "message": "User notified successfully!"
    }
