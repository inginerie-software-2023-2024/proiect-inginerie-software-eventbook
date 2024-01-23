import time
from typing import List, Annotated, Dict
from uuid import uuid4
from http import HTTPStatus
from datetime import datetime

from fastapi import APIRouter, Depends, Body, Query
from fastapi.exceptions import HTTPException

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
)
from eventplanner.eventplanner_backend.schemas.eventplanner_model_helpers import (
    EventTags,
)

event_management_router = APIRouter()


@event_management_router.post("/events/register", tags=[Tags.EVENT])
def register_event(
        title: str,
        description: str,
        location: str,
        tags: Annotated[List[EventTags], Query()],
        start_time: float = time.time(),
        end_time: float = time.time(),
        current_user: User = Depends(auth_helper.get_current_user),
        public: bool = False
):
    id_event = uuid4()
    while event_table.search(events_query.id == id_event):
        id_event = uuid4()

    id_event = str(id_event)

    event_to_store = {
        "id": id_event,
        "title": title,
        "tags": {tag.value for tag in tags},
        "description": description,
        "start_time": start_time,
        "end_time": end_time,
        "location": location,
        "organizer_id": current_user.id,
        "admins": {current_user.id},
        "organizer_name": current_user.username,
        "participants": None,
        "public": public
    }
    event_to_store = Event(**event_to_store)
    event_table.insert(dict(event_to_store))

    users_table.update({"events_created": (current_user.events_created or set()) | {id_event}})
    return {"message": "Event created successfully",
            "id_event": id_event}


@event_management_router.get(
    "/events/{event_title}", tags=[Tags.EVENT], response_model=list[Event]
)
def get_single_event(event_title: str):
    event = event_table.search(events_query.title == event_title)

    if not event:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Event not found")

    return event


@event_management_router.get("/events", tags=[Tags.EVENT], response_model=list[Event])
def get_events(
        title: str = None,
        location: str = None,
        tags: str = None,
        organizer_name: int = None,
        start_date: float = None,
        end_date: float = None,
        public: bool = None
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
        conditions.append(events_query.tags == tags)
    if end_date:
        conditions.append(events_query.end_date <= end_date)
    if public:
        conditions.append(events_query.public == public)

    if conditions:
        results = event_table.search(conditions[0])
        for condition in conditions[1:]:
            results = [event for event in results if condition(event)]
    else:
        results = event_table.all()

    return results


@event_management_router.post("/events/{event_id}/status", tags=[Tags.EVENT])
def change_event_status(
        public: bool,
        event_id: str,
        current_user: User = Depends(auth_helper.get_current_user)
):
    event = shared_functions.get_event_by_id(event_id)
    if current_user.id in event.admins or current_user.id == event.organizer_id:
        event_table.update(
            {"public": public},
            events_query.id == event.id
        )

        return {"message": "Status updated successfully"}

    raise HTTPException(
        status_code=HTTPStatus.BAD_REQUEST,
        detail="You do not have permission to change the status"
    )


@event_management_router.get("/events/{event_id}/join", tags=[Tags.EVENT])
def join_public_event(event_id: str, current_user: User = Depends(auth_helper.get_current_user)):
    event = shared_functions.get_event_by_id(event_id)

    if event.public:
        event_table.update(
            {"participants": event.participants | {current_user.id}},
            events_query.id == event_id
        )

        return {"message": "Successfully joined the event"}

    raise HTTPException(
        status_code=HTTPStatus.BAD_REQUEST,
        detail="Event is not public"
    )


@event_management_router.delete("/events/{event_id}/leave", tags=[Tags.EVENT])
def leave_event(event_id: str, current_user: User = Depends(auth_helper.get_current_user)):
    event = shared_functions.get_event_by_id(event_id)

    if current_user.id in event.participants:
        event_table.update(
            {"participants": event.participants ^ current_user.id},
            events_query.id == event_id
        )
        return {"message": "You successfully left the event"}

    if current_user.id in event.admins:
        event_table.update(
            {"admins": event.admins ^ current_user.id},
            events_query.id == event_id
        )
        return {"message": "You successfully left the event"}

    raise HTTPException(
        status_code=HTTPStatus.BAD_REQUEST,
        detail="Bad request!"
    )


@event_management_router.put("/events/{event_id}/admin", tags=[Tags.EVENT])
def add_admin_event(
        event_id: str,
        username: Annotated[str, Body(embed=True)],
        current_user: User = Depends(auth_helper.get_current_user)
) -> Dict:
    current_event = shared_functions.get_event_by_id(event_id)

    if not current_user.id in current_event.admins:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="You do not have rights to add an admin to this event",
        )

    user = shared_functions.get_user_by_name(username)

    event_table.update(
        {"admins": current_event.admins | {user.id}}, events_query["id"] == event_id
    )

    return {"message": "Admin added successfully to event"}


@event_management_router.put("/events/{event_id}/ownership", tags=[Tags.EVENT])
def change_ownership_event(
        event_id: str,
        username: Annotated[str, Body(embed=True)],
        current_user: User = Depends(auth_helper.get_current_user)
) -> Dict:
    current_event = shared_functions.get_event_by_id(event_id)

    if current_user.id != current_event.organizer_id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="You do not have rights to change ownership to this event",
        )

    user = shared_functions.get_user_by_name(username)

    event_table.update(
        {
            "organizer_id": user.id,
            "organizer_name": user.username
        },
        events_query["id"] == event_id
    )

    return {"message": "Ownership successfully changed"}


@event_management_router.get("/events/{event_id}/participants", tags=[Tags.EVENT])
def get_participants_event(event_id: str):
    event = shared_functions.get_event_by_id(event_id)

    if not event.public:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="This event is private"
        )

    return event.participants


@event_management_router.put("/events/{event_id}", tags=[Tags.EVENT])
def update_event(
        updated_event: EventBase,
        event_id: str,
        current_user: User = Depends(auth_helper.get_current_user),
):
    event = shared_functions.get_event_by_id(event_id)

    updated_event.start_time = str(updated_event.start_time)
    updated_event.end_time = str(updated_event.end_time)

    if current_user.id in event.admins:
        event_table.update(dict(updated_event), events_query.id == event.id)

        return {"message": "Event updated successfully!"}

    raise HTTPException(
        status_code=HTTPStatus.BAD_REQUEST,
        detail="You do not have rights to edit this event",
    )


@event_management_router.delete("/events/{event_id}/admin", tags=[Tags.EVENT])
def remove_admin_status_event(
        event_id: str, admin_id: Annotated[str, Body(embed=True)], current_user=Depends(auth_helper.get_current_user)
):
    event = shared_functions.get_event_by_id(event_id)

    if event.organizer_id == current_user.id:
        event_table.update(
            {"admins": event.admins ^ {admin_id}}, events_query.id == event_id
        )

        return {"message": "Admin removed successfully!"}


@event_management_router.delete(
    "/events/{invitation_id}/guests/{guest_id}", tags=[Tags.EVENT]
)
def remove_guest_from_event():
    pass


@event_management_router.delete("/events", tags=[Tags.EVENT])
def delete_event(
        event_id: str, current_user: User = Depends(auth_helper.get_current_user)
):
    event = shared_functions.get_event_by_id(event_id)

    if event.organizer_id == current_user.id:
        event_table.remove(events_query.id == event_id)

        return {"message": "Event deleted successfully!"}

    raise HTTPException(
        status_code=HTTPStatus.BAD_REQUEST,
        detail="You do not have rights to edit this event",
    )
