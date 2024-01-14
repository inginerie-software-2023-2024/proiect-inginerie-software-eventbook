from uuid import uuid4
from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from eventplanner.eventplanner_backend.api_routers import shared_functions
from eventplanner.common.eventplanner_common import EventplannerBackendTags as Tags
from eventplanner.eventplanner_backend.schemas.eventplanner_base_models import User, UserBase
from eventplanner.eventplanner_backend.authentication import eventplanner_authentication_helper as auth_helper
from eventplanner.eventplanner_backend.eventplanner_database import users_table, user_query, event_table, events_query

event_management_router = APIRouter()

@event_management_router.post("/events/register", tags=[Tags.EVENT])
def register_event():
    pass

@event_management_router.get("/events/{event_id}", tags=[Tags.EVENT])
def get_single_event():
    pass

@event_management_router.get("/events", tags=[Tags.EVENT])
def get_event(filter):
    pass

@event_management_router.put("/events/{event_id}", tags=[Tags.EVENT])
def update_event():
    pass

@event_management_router.delete("/events/{event_id}", tags=[Tags.EVENT])
def delete_event():
    pass



@event_management_router.put("/events/{event_id}/invite", tags=[Tags.EVENT])
def invite_guest_event():
    pass

@event_management_router.get("/events/{event_id}/guest", tags=[Tags.EVENT])
def view_guests_event():
    pass

@event_management_router.delete("/events/{event_id}/guests/{guest_id}", tags=[Tags.EVENT])
def delete_guest_from_event():
    pass


