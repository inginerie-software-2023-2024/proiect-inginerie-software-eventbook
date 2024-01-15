from typing import List, Annotated
from uuid import uuid4
from http import HTTPStatus
from datetime import datetime

from fastapi import APIRouter, Depends, Body, Query
from fastapi.exceptions import HTTPException

from eventplanner.eventplanner_backend.api_routers import shared_functions
from eventplanner.common.eventplanner_common import EventplannerBackendTags as Tags
from eventplanner.eventplanner_backend.authentication import eventplanner_authentication_helper as auth_helper
from eventplanner.eventplanner_backend.eventplanner_database import users_table, user_query, event_table, events_query
from eventplanner.eventplanner_backend.schemas.eventplanner_base_models import User, EventBase, Event
from eventplanner.eventplanner_backend.schemas.eventplanner_model_helpers import EventTags

event_management_router = APIRouter()


@event_management_router.post("/events/register", tags=[Tags.EVENT])
def register_event(
        title: str,
        description: str,
        location: str,
        tags: Annotated[List[EventTags], Query()],
        start_time: datetime= datetime.utcnow(),
        end_time: datetime= datetime.utcnow(),
        current_user: dict = Depends(auth_helper.get_current_user)
):
    id_event = uuid4()
    while event_table.search(events_query.id == id_event):
        id_event = uuid4()

    id_event = str(id_event)

    event_to_store = {
        "id": id_event,
        "title": title,
        "tags": [tag.value for tag in tags],
        "description": description,
        "start_time": str(start_time),
        "end_time": str(end_time),
        "location": location,
        "organizer_id": current_user["id"],
        "organizer_name": current_user["username"]
    }


    event_table.insert(event_to_store)

    users_table.update({"event_created": current_user['event_created'] + [id_event]})
    return {"message": "Event created successfully"}


@event_management_router.get("/events/{event_title}", tags=[Tags.EVENT], response_model=list[Event])
def get_single_event(event_title: str):
    event = event_table.search(events_query.title == event_title)

    if not event:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Event not found"
        )

    return event


@event_management_router.get("/events", tags=[Tags.EVENT], response_model=list[Event])
def get_events(
        title: str = None,
        location: str = None,
        tags: str = None,
        organizer_name: str = None,
        start_date: datetime = None,
        end_date: datetime = None,

):
    conditions = []

    if title:
        conditions.append(events_query.title == title)
    if location:
        conditions.append(events_query.location == location)
    if organizer_name:
        conditions.append(events_query.organizer_name == organizer_name)
    if start_date:
        conditions.append(events_query.start_date.isoformat() >= start_date.isoformat())
    if tags:
        conditions.append(events_query.tags == tags)
    if end_date:
        conditions.append(events_query.end_date.isoformat() <= end_date.isoformat())

    if conditions:
        results = event_table.search(conditions[0])
        for condition in conditions[1:]:
            results = [event for event in results if condition(event)]
    else:
        results = event_table.all()

    return results


@event_management_router.put("/events/{event_id}", tags=[Tags.EVENT])
def update_event(updated_event: EventBase, event_id: str, current_user: dict = Depends(auth_helper.get_current_user)):
    event = shared_functions.get_event_by_id(event_id)

    updated_event.start_time = str(updated_event.start_time)
    updated_event.end_time = str(updated_event.end_time)

    if event["organizer_id"] == current_user["id"]:
        event_table.update(dict(updated_event), events_query.id == event["id"])

        return {"message": "Event updated successfully!"}

    raise HTTPException(
        status_code=HTTPStatus.BAD_REQUEST,
        detail="You do not have rights to edit this event"
    )



@event_management_router.delete("/events", tags=[Tags.EVENT])
def delete_event(event_id: str, current_user: dict= Depends(auth_helper.get_current_user)):
    event = shared_functions.get_event_by_id(event_id)

    if event["organizer_id"] == current_user["id"]:
        event_table.remove(events_query.id == event_id)

        return {"message": "Event deleted successfully!"}

    raise HTTPException(
        status_code=HTTPStatus.BAD_REQUEST,
        detail="You do not have rights to edit this event"
    )


