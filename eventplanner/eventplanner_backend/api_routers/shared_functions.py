import random
from http import HTTPStatus
from fastapi.exceptions import HTTPException

from eventplanner.eventplanner_backend.schemas.eventplanner_base_models import User, UserBase, InvitationBase
from eventplanner.eventplanner_backend.authentication import eventplanner_authentication_helper as auth_helper
from eventplanner.eventplanner_backend.eventplanner_database import users_table, user_query, event_table, events_query


def get_user_by_id(uid: str) -> User:
    user = users_table.search(user_query.id == uid)
    if user:
        return user[0]

    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND,
        detail="User id not found"
    )


def get_user_by_name(username: str) -> User:
    user = users_table.search(user_query.username == username)
    if user:
        return user[0]

    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND,
        detail="Username not found"
    )


def logout_by_id(id: str):
    auth_helper.update_token_version(id)


def get_event_organizer_user(event_id: str):
    event_info = event_table.search(events_query.id == event_id)
    if not event_info:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Event not found with id"
        )
    event_organizer = users_table.search(user_query.id == event_info[0]["organizer"])

    if not event_organizer:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="User not found with id"
        )

    return event_organizer[0]

def get_event_by_id(event_id: str):
    event = event_table.search(events_query.id == event_id)

    if not event_id:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Event not found with id"
        )

    return event[0]

def generate_invitation_id(invite: InvitationBase):
    return hash(f"{invite.time}{invite.event}{invite.invited}{random.Random.randint(1,1000)}")