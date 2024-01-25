import time
from datetime import datetime
from typing import List, Annotated
from uuid import uuid4
from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException, Query

from eventplanner.eventplanner_backend.api_routers import shared_functions
from eventplanner.common.eventplanner_common import EventplannerBackendTags as Tags
from eventplanner.eventplanner_backend.authentication import (
    eventplanner_authentication_helper as auth_helper,
)
from eventplanner.eventplanner_backend.eventplanner_database import (
    users_table,
    user_query,
    event_table,
    events_query,
)
from eventplanner.eventplanner_backend.schemas.eventplanner_base_models import (
    User,
    EventBase,
    Event,
    Invitation, InvitationType
)
from eventplanner.eventplanner_backend.schemas.eventplanner_model_helpers import (
    EventTags,
)
from eventplanner.eventplanner_backend.api_routers import (
    eventplanner_weather_integration as weather_integration,
)

event_management_router = APIRouter()


# Helper Functions
def generate_unique_event_id():
    event_id = uuid4()
    while event_table.search(events_query.id == event_id):
        event_id = uuid4()
    return str(event_id)


def update_user_events_created(user: User, event_id: str):
    updated_events_created = (user.events_created or set()) | {event_id}
    users_table.update(
        {"events_created": updated_events_created}, user_query.id == user.id
    )


def validate_event_ownership_or_admin(event: Event, user: User):
    if user.id not in event.admins and user.id != event.organizer_id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="You do not have permission to perform this action",
        )


# Event Management Endpoints
@event_management_router.post("/events/register", tags=[Tags.EVENT])
def register_event(
        title: str,
        description: str,
        location: str,
        tags: List[EventTags] = Query([]),
        start_time: float = time.time(),
        end_time: float = time.time(),
        current_user: User = Depends(auth_helper.get_current_user),
        public: bool = False,
):
    id_event = generate_unique_event_id()

    event_to_store = Event(
        id=id_event,
        title=title,
        tags=set(tag.value for tag in tags),
        description=description,
        start_time=start_time,
        end_time=end_time,
        location=location,
        organizer_id=current_user.id,
        admins={current_user.id},
        organizer_name=current_user.username,
        public=public,
    )

    event_table.insert(event_to_store.model_dump())
    update_user_events_created(current_user, id_event)

    return {"message": "Event created successfully", "id_event": id_event}


@event_management_router.get("/events/{event_id}", tags=[Tags.EVENT])
def get_single_event(event_id: str, current_user: User = Depends(auth_helper.get_current_user)):
    event = shared_functions.get_event_by_id(event_id=event_id)

    if not event.public and not current_user.id in (event.participants or set()) | (event.admins or set()):
        return Event(title=event.title, id=event.id, description=event.description, public=event.public)

    latitude, longitude = shared_functions.get_location_coordinates(event.location)
    if latitude is not None and longitude is not None:
        weather = weather_integration.fetch_and_create_weather_data(latitude, longitude)

        event.weather = weather

        return event
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Location not found")


@event_management_router.get("/events", tags=[Tags.EVENT], response_model=List[Event])
def get_events(
        title: str = None,
        location: str = None,
        tags: List[EventTags] = Query([]),
        organizer_name: str = None,
        start_date: float = None,
        end_date: float = None,
        public: bool = None,
):
    conditions = []

    if title:
        conditions.append(events_query.title == title)
    if location:
        conditions.append(events_query.location == location)
    if organizer_name:
        conditions.append(events_query.organizer_name == organizer_name)
    if start_date:
        conditions.append(events_query.start_date >= start_date)
    if tags:
        conditions.append(events_query.tags.any(tag.value for tag in tags))
    if end_date:
        conditions.append(events_query.end_date <= end_date)
    if public is not None:
        conditions.append(events_query.public == public)

    if conditions:
        # Combine all conditions using logical AND
        query = conditions[0]
        for condition in conditions[1:]:
            query &= condition

        events = event_table.search(query)
    else:
        events = event_table.all()

    return events


@event_management_router.post("/events/{event_id}/status", tags=[Tags.EVENT])
def change_event_status(
        public: bool,
        event_id: str,
        current_user: User = Depends(auth_helper.get_current_user),
):
    event = shared_functions.get_event_by_id(event_id)
    validate_event_ownership_or_admin(event, current_user)
    event_table.update({"public": public}, events_query.id == event.id)
    return {"message": "Status updated successfully"}


# Other endpoints (join_public_event, leave_event, add_admin_event, etc.) follow similar refactoring approach...


@event_management_router.get("/events/{event_id}/join", tags=[Tags.EVENT])
def join_event(
        event_id: str, current_user: User = Depends(auth_helper.get_current_user)
):
    event = shared_functions.get_event_by_id(event_id)
    if event.public:
        updated_participants = (event.participants or set()) | {current_user.id}
        event_table.update(
            {"participants": updated_participants}, events_query.id == event_id
        )
        return {"message": "Successfully joined the event"}
    else:
        # Check if the user has already requested to join
        existing_request = any(
            inv for inv in (event.requests_to_join or set())
            if inv.end_user == current_user.id
        )
        if existing_request:
            return {"message": "You have already requested to join this event"}

        inv_id = shared_functions.generate_invitation_id_fields(event_id, current_user.id)

        # Create a new invitation as a join request
        new_request = Invitation(
            start_user=current_user.id,  # Assuming the organizer handles requests
            type=InvitationType.REQUEST,
            event_id=event_id,
            id=inv_id,
            time=str(datetime.now())
        )

        updated_requests = (event.requests_to_join or set()) | {new_request}
        event_table.update(
            {"requests_to_join": updated_requests}, events_query.id == event_id
        )
        return {"message": "Request to join the event sent successfully",
                "id_invitation": inv_id}


@event_management_router.delete("/events/{event_id}/leave", tags=[Tags.EVENT])
def leave_event(
        event_id: str, current_user: User = Depends(auth_helper.get_current_user)
):
    event = shared_functions.get_event_by_id(event_id)

    if current_user.id in event.participants:
        updated_participants = event.participants - {current_user.id}
        event_table.update(
            {"participants": updated_participants}, events_query.id == event_id
        )
        return {"message": "You successfully left the event"}

    if current_user.id in event.admins:
        updated_admins = event.admins - {current_user.id}
        event_table.update({"admins": updated_admins}, events_query.id == event_id)
        return {"message": "You successfully left the event"}

    raise HTTPException(
        status_code=HTTPStatus.BAD_REQUEST,
        detail="You are not a participant or admin of this event",
    )


@event_management_router.put("/events/{event_id}/admin", tags=[Tags.EVENT])
def add_admin_event(
        event_id: str,
        username: str,
        current_user: User = Depends(auth_helper.get_current_user),
):
    current_event = shared_functions.get_event_by_id(event_id)
    validate_event_ownership_or_admin(current_event, current_user)

    user_to_add = shared_functions.get_user_by_name(username)
    updated_admins = current_event.admins | {user_to_add.id}
    event_table.update({"admins": updated_admins}, events_query.id == event_id)

    return {"message": "Admin added successfully to event"}


@event_management_router.put("/events/{event_id}/ownership", tags=[Tags.EVENT])
def change_ownership_event(
        event_id: str,
        username: str,
        current_user: User = Depends(auth_helper.get_current_user),
):
    current_event = shared_functions.get_event_by_id(event_id)
    if current_user.id != current_event.organizer_id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="You do not have rights to change ownership of this event",
        )

    new_organizer = shared_functions.get_user_by_name(username)
    event_table.update(
        {"organizer_id": new_organizer.id, "organizer_name": new_organizer.username},
        events_query.id == event_id,
    )

    return {"message": "Ownership successfully changed"}


@event_management_router.get("/events/{event_id}/participants", tags=[Tags.EVENT])
def get_participants_event(event_id: str, current_user: User = Depends(auth_helper.get_current_user)):
    event = shared_functions.get_event_by_id(event_id)
    if not event.public and current_user.id not in (event.participants or set()) | {event.organizer_id} | (
            event.admins or set()):
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You do not have access to the participants of this private event"
        )
    return list(event.participants or [])


@event_management_router.put("/events/{event_id}", tags=[Tags.EVENT])
def update_event(
        event_id: str,
        updated_event: EventBase,
        current_user: User = Depends(auth_helper.get_current_user),
):
    event = shared_functions.get_event_by_id(event_id)
    validate_event_ownership_or_admin(event, current_user)

    event_table.update(
        updated_event.dict(exclude_unset=True), events_query.id == event_id
    )
    return {"message": "Event updated successfully!"}


@event_management_router.delete("/events/{event_id}/admin", tags=[Tags.EVENT])
def remove_admin_status_event(
        event_id: str,
        admin_id: str,
        current_user: User = Depends(auth_helper.get_current_user),
):
    event = shared_functions.get_event_by_id(event_id)
    if event.organizer_id != current_user.id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="You do not have rights to remove an admin from this event",
        )

    updated_admins = event.admins - {admin_id}
    event_table.update({"admins": updated_admins}, events_query.id == event_id)
    return {"message": "Admin removed successfully!"}


@event_management_router.delete("/events/{event_id}", tags=[Tags.EVENT])
def delete_event(
        event_id: str, current_user: User = Depends(auth_helper.get_current_user)
):
    event = shared_functions.get_event_by_id(event_id)
    if event.organizer_id != current_user.id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="You do not have rights to delete this event",
        )

    event_table.remove(events_query.id == event_id)
    return {"message": "Event deleted successfully!"}


@event_management_router.post("/events/{event_id}/approve_request", tags=[Tags.EVENT])
def approve_join_request(
        event_id: str, invitation_id: str, current_user: User = Depends(auth_helper.get_current_user)
):
    event = shared_functions.get_event_by_id(event_id)
    validate_event_ownership_or_admin(event, current_user)

    invitation = [req for req in event.requests_to_join if req.id == invitation_id]

    if not invitation or invitation[0].type != InvitationType.REQUEST:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Invitation not found")

    invitation = invitation[0]

    updated_participants = (event.participants or set()) | {invitation.end_user}
    event_table.update(
        {"participants": updated_participants}, events_query.id == event_id
    )

    return {"message": "Join request approved"}
