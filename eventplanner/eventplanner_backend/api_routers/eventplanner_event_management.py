import time
from uuid import uuid4
from typing import List
from http import HTTPStatus
from datetime import datetime
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
    Invitation,
    InvitationType,
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
    """
    Endpoint utility for registering a new event.
    ```
    Args:
        title: The title of the event
        description: A detailed description of the event
        location: The location where the event will take place
        tags: A list of tags associated with the event (optional)
        start_time: The start time of the event (default is current time)
        end_time: The end time of the event (default is current time)
        current_user: Current logged-in user (retrieved via authentication)
        public: A boolean indicating if the event is public or private (default is False)

    Returns:
        A dictionary with a message and the event ID

    Raises:
        [401]UNAUTHORIZED: Invalid credentials or not logged in
    ```

    Example of valid request body:
    ```
    {
        "title": "Summer Picnic",
        "description": "A fun summer gathering",
        "location": "Central Park",
        "tags": ["#outdoors", "#summer"],
        "start_time": 1656523200,  # Unix Timestamp
        "end_time": 1656530400,    # Unix Timestamp
        "public": true
    }
    ```

    Example of valid response body:
    ```
    {
      "message": "Event created successfully",
      "id_event": "1111-1111-111-11111-11111"
    }
    ```
    """
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
def get_single_event(
    event_id: str, current_user: User = Depends(auth_helper.get_current_user)
):
    """
        Endpoint utility for retrieving a single event by its ID.
        ```
        Args:
            event_id: The unique identifier of the event
            current_user: Current logged-in user (retrieved via authentication)

        Returns:
            Event object with details if the user is authorized to view it

        Raises:
            [401]UNAUTHORIZED: Invalid credentials or not logged in
            [404]NOT_FOUND: Event not found or location not found for weather data
            [403]FORBIDDEN: User not authorized to view the event
        ```
        Examples of valid request body:
        ```
        event_id: 111-11111111-111111-11
        ```

        Examples of valid response body:
        ```
    {
      "title": "tt",
      "tags": [
        "#business",
        "#art"
      ],
      "description": "ttt",
      "start_time": 1706194243.8539546,
      "end_time": 1706194243.8539546,
      "location": "ttt",
      "public": true,
      "id": "9a1d8924-cc97-43eb-8432-6ed9f0da9a62",
      "organizer_name": "example",
      "organizer_id": "d7b01a4d-6f76-4c25-9508-8bd08d869bab",
      "admins": [
        "d7b01a4d-6f76-4c25-9508-8bd08d869bab"
      ],
      "participants": null,
      "requests_to_join": null,
      "weather": [
        {
          "date": "2024-01-25T00:00:00",
          "hourly_data": [
            {
              "time": "2024-01-25T00:00:00",
              "temperature_2m": 5.8,
              "relative_humidity_2m": 97,
              "dew_point_2m": 5.4,
              "apparent_temperature": 4.5,
              "precipitation_probability": 0,
              "precipitation": 0,
              "rain": 0,
              "snowfall": 0,
              "snow_depth": 0,
              "wind_speed_80m": 7.4,
              "temperature_180m": 11.6,
              "soil_temperature_6cm": 5
            },
            {
              "time": "2024-01-25T01:00:00",
              "temperature_2m": 5.8,
              "relative_humidity_2m": 96,
              "dew_point_2m": 5.2,
              "apparent_temperature": 4.5,
              "precipitation_probability": 0,
              "precipitation": 0,
              "rain": 0,
              "snowfall": 0,
              "snow_depth": 0,
              "wind_speed_80m": 6.5,
              "temperature_180m": 11,
              "soil_temperature_6cm": 4.6
            }, },
        {
          "date": "2024-01-26T00:00:00",
          "hourly_data": [
            {
              "time": "2024-01-26T00:00:00",
              "temperature_2m": 8,
              "relative_humidity_2m": 90,
              "dew_point_2m": 6.4,
              "apparent_temperature": 6.6,
              "precipitation_probability": 0,
              "precipitation": 0,
              "rain": 0,
              "snowfall": 0,
              "snow_depth": 0,
              "wind_speed_80m": 4.7,
              "temperature_180m": 10.1,
              "soil_temperature_6cm": 6.5
            },
            {
              "time": "2024-01-26T01:00:00",
              "temperature_2m": 7.7,
              "relative_humidity_2m": 92,
              "dew_point_2m": 6.5,
              "apparent_temperature": 6.6,
              "precipitation_probability": 0,
              "precipitation": 0,
              "rain": 0,
              "snowfall": 0,
              "snow_depth": 0,
              "wind_speed_80m": 4.9,
              "temperature_180m": 10.2,
              "soil_temperature_6cm": 6.4
            },
            etc
            }
          ]
        }
      ]
    }
        ```
    """
    event = shared_functions.get_event_by_id(event_id=event_id)

    if not event.public and not current_user.id in (event.participants or set()) | (
        event.admins or set()
    ):
        return Event(
            title=event.title,
            id=event.id,
            description=event.description,
            public=event.public,
        )

    latitude, longitude = shared_functions.get_location_coordinates(event.location)
    if latitude is not None and longitude is not None:
        weather = weather_integration.fetch_and_create_weather_data(latitude, longitude)

        event.weather = weather

        return event
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Location not found")

@event_management_router.get("/events/{event_id}/v2", tags=[Tags.EVENT])
def get_single_event_v2(
    event_id: str, current_user: User = Depends(auth_helper.get_current_user)
):
    """
        Endpoint utility for retrieving a single event by its ID.
        ```
        Args:
            event_id: The unique identifier of the event
            current_user: Current logged-in user (retrieved via authentication)

        Returns:
            Event object with details if the user is authorized to view it

        Raises:
            [401]UNAUTHORIZED: Invalid credentials or not logged in
            [404]NOT_FOUND: Event not found or location not found for weather data
            [403]FORBIDDEN: User not authorized to view the event
        ```
        Examples of valid request body:
        ```
        event_id: 111-11111111-111111-11
        ```

        Examples of valid response body:
        ```
    {
      "title": "tt",
      "tags": [
        "#business",
        "#art"
      ],
      "description": "ttt",
      "start_time": 1706194243.8539546,
      "end_time": 1706194243.8539546,
      "location": "ttt",
      "public": true,
      "id": "9a1d8924-cc97-43eb-8432-6ed9f0da9a62",
      "organizer_name": "example",
      "organizer_id": "d7b01a4d-6f76-4c25-9508-8bd08d869bab",
      "admins": [
        "d7b01a4d-6f76-4c25-9508-8bd08d869bab"
      ],
      "participants": null,
      "requests_to_join": null,
      "weather: null
            }
          ]
        }
      ]
    }
    ```
    """
    event = shared_functions.get_event_by_id(event_id=event_id)

    if not event.public and not current_user.id in (event.participants or set()) | (
        event.admins or set()
    ):
        return Event(
            title=event.title,
            id=event.id,
            description=event.description,
            public=event.public,
        )
    return event


@event_management_router.get("/events", tags=[Tags.EVENT], response_model=List[Event])
def get_events(
    title: str = None,
    location: str = None,
    tags: EventTags = Query([]),
    organizer_name: str = None,
    start_date: float = None,
    end_date: float = None,
    public: bool = None,
):
    """
    Endpoint utility for retrieving a list of events based on filters.

    ```
    Args:
        title: Filter for events by title (optional)
        location: Filter for events by location (optional)
        tags: Filter for events by tags (optional)
        organizer_name: Filter for events by organizer's name (optional)
        start_date: Filter for events starting after this date (optional)
        end_date: Filter for events ending before this date (optional)
        public: Filter for events by their public/private status (optional)

    Returns:
        A list of Event objects that match the given filters

    Raises:
        [401]UNAUTHORIZED: Invalid credentials or not logged in
    ```


    Examples of valid response body:
    ```
    [
      {
        "title": "tt",
        "tags": [
          "#business",
          "#art"
        ],
        "description": "ttt",
        "start_time": 1706194243.8539546,
        "end_time": 1706194243.8539546,
        "location": "ttt",
        "public": true,
        "id": "9a1d8924-cc97-43eb-8432-6ed9f0da9a62",
        "organizer_name": "example",
        "organizer_id": "d7b01a4d-6f76-4c25-9508-8bd08d869bab",
        "admins": [
          "d7b01a4d-6f76-4c25-9508-8bd08d869bab"
        ],
        "participants": null,
        "requests_to_join": null,
        "weather": null
      }
    ]
    ```

    """
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
    """
    Endpoint utility for changing the public/private status of an event.

    Args:
        public: A boolean indicating the new status of the event
        event_id: The unique identifier of the event
        current_user: Current logged in user (retrieved via authentication)

    Returns:
        A dictionary with a success message

    Raises:
        [401]UNAUTHORIZED: Invalid credentials or not logged in
        [400]BAD_REQUEST: User not authorized to change the event status

    Examples of valid request body:
    ```
    event_id: 111111-11111-11111
    public: True
    ```

    Examples of valid response body:
    ```
    {
        "message": "Status updated successfully"
    }
    ```
    """
    event = shared_functions.get_event_by_id(event_id)
    validate_event_ownership_or_admin(event, current_user)
    event_table.update({"public": public}, events_query.id == event.id)
    return {"message": "Status updated successfully"}


# Other endpoints (join_public_event, leave_event, add_admin_event, etc.) follow similar refactoring approach...


@event_management_router.get("/events/{event_id}/join", tags=[Tags.EVENT])
def join_event(
    event_id: str, current_user: User = Depends(auth_helper.get_current_user)
):
    """
    Endpoint utility for joining a public event or sending a join request for a private event.

    Args:
        event_id: The unique identifier of the event
        current_user: Current logged in user (retrieved via authentication)

    Returns:
        A dictionary with a success message or a message indicating a join request has been sent

    Raises:
        [401]UNAUTHORIZED: Invalid credentials or not logged in
        [403]FORBIDDEN: Event is private and user is not authorized to join
        [400]BAD_REQUEST: User has already sent a join request

    Examples of valid request body:
    ```
    event_id: 1111111-11111-11111-111
    ```

    Examples of valid response body:
    ```
    {
    "message": "Successfully joined the event"
    }
    ```
    """
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
            inv
            for inv in (event.requests_to_join or set())
            if inv.end_user == current_user.id
        )
        if existing_request:
            return {"message": "You have already requested to join this event"}

        inv_id = shared_functions.generate_invitation_id_fields(
            event_id, current_user.id
        )

        # Create a new invitation as a join request
        new_request = Invitation(
            start_user=current_user.id,  # Assuming the organizer handles requests
            type=InvitationType.REQUEST,
            event_id=event_id,
            id=inv_id,
            time=str(datetime.now()),
        )

        updated_requests = (event.requests_to_join or set()) | {new_request}
        event_table.update(
            {"requests_to_join": updated_requests}, events_query.id == event_id
        )
        return {
            "message": "Request to join the event sent successfully",
            "id_invitation": inv_id,
        }


@event_management_router.delete("/events/{event_id}/leave", tags=[Tags.EVENT])
def leave_event(
    event_id: str, current_user: User = Depends(auth_helper.get_current_user)
):
    """
    Endpoint utility for a user to leave an event.

    Args:
        event_id: The unique identifier of the event
        current_user: Current logged in user (retrieved via authentication)

    Returns:
        A dictionary with a success message

    Raises:
        [401]UNAUTHORIZED: Invalid credentials or not logged in
        [400]BAD_REQUEST: User is not a participant or admin of this event
    """
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
    """
    Endpoint utility for adding a user as an admin to an event.

    Args:
        event_id: The unique identifier of the event
        username: The username of the user to be added as an admin
        current_user: Current logged in user (retrieved via authentication)

    Returns:
        A dictionary with a success message

    Raises:
        [401]UNAUTHORIZED: Invalid credentials or not logged in
        [400]BAD_REQUEST: User not authorized to add an admin

    Example of valid request body:
    {
        "username": "example_user"
    }
    """
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
    """
    Endpoint utility for changing the ownership of an event.

    Args:
        event_id: The unique identifier of the event
        username: The username of the new organizer
        current_user: Current logged in user (retrieved via authentication)

    Returns:
        A dictionary with a success message

    Raises:
        [401]UNAUTHORIZED: Invalid credentials or not logged in
        [400]BAD_REQUEST: User not authorized to change event ownership

    Example of valid request body:
    {
        "username": "new_organizer"
    }
    """
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
def get_participants_event(
    event_id: str, current_user: User = Depends(auth_helper.get_current_user)
):
    """
    Endpoint utility for retrieving the list of participants of an event.

    Args:
        event_id: The unique identifier of the event
        current_user: Current logged in user (retrieved via authentication)

    Returns:
        A list of participant IDs

    Raises:
        [401]UNAUTHORIZED: Invalid credentials or not logged in
        [403]FORBIDDEN: User not authorized to view participants of a private event
    """
    event = shared_functions.get_event_by_id(event_id)
    if not event.public and current_user.id not in (event.participants or set()) | {
        event.organizer_id
    } | (event.admins or set()):
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You do not have access to the participants of this private event",
        )
    return list(event.participants or [])


@event_management_router.put("/events/{event_id}", tags=[Tags.EVENT])
def update_event(
    event_id: str,
    updated_event: EventBase,
    current_user: User = Depends(auth_helper.get_current_user),
):
    """
    Endpoint utility for updating the details of an event.

    Args:
        event_id: The unique identifier of the event
        updated_event: EventBase model with updated event information
        current_user: Current logged in user (retrieved via authentication)

    Returns:
        A dictionary with a success message

    Raises:
        [401]UNAUTHORIZED: Invalid credentials or not logged in
        [400]BAD_REQUEST: User not authorized to update the event
    """
    event = shared_functions.get_event_by_id(event_id)
    validate_event_ownership_or_admin(event, current_user)

    event_table.update(
        updated_event.model_dump(exclude_unset=True), events_query.id == event_id
    )
    return {"message": "Event updated successfully!"}


@event_management_router.delete("/events/{event_id}/admin", tags=[Tags.EVENT])
def remove_admin_status_event(
    event_id: str,
    admin_id: str,
    current_user: User = Depends(auth_helper.get_current_user),
):
    """
    Endpoint utility for removing admin status from a user for a specific event.

    Args:
        event_id: The unique identifier of the event
        admin_id: The ID of the admin to be removed
        current_user: Current logged in user (retrieved via authentication)

    Returns:
        A dictionary with a success message

    Raises:
        [401]UNAUTHORIZED: Invalid credentials or not logged in
        [400]BAD_REQUEST: User not authorized to remove an admin from the event
    """
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
    """
    Endpoint utility for deleting an event.

    Args:
        event_id: The unique identifier of the event
        current_user: Current logged in user (retrieved via authentication)

    Returns:
        A dictionary with a success message

    Raises:
        [401]UNAUTHORIZED: Invalid credentials or not logged in
        [400]BAD_REQUEST: User not authorized to delete this event
    """
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
    event_id: str,
    invitation_id: str,
    current_user: User = Depends(auth_helper.get_current_user),
):
    """
    Endpoint utility for approving a join request to an event.

    Args:
        event_id: The unique identifier of the event
        invitation_id: The unique identifier of the join request invitation
        current_user: Current logged in user (retrieved via authentication)

    Returns:
        A dictionary with a success message

    Raises:
        [401]UNAUTHORIZED: Invalid credentials or not logged in
        [400]BAD_REQUEST: User not authorized to approve join requests
        [404]NOT_FOUND: Invitation not found or invalid request type
    """
    event = shared_functions.get_event_by_id(event_id)
    validate_event_ownership_or_admin(event, current_user)

    invitation = [req for req in event.requests_to_join if req.id == invitation_id]

    if not invitation or invitation[0].type != InvitationType.REQUEST:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Invitation not found"
        )

    invitation = invitation[0]

    updated_participants = (event.participants or set()) | {invitation.end_user}
    event_table.update(
        {"participants": updated_participants}, events_query.id == event_id
    )

    return {"message": "Join request approved"}
