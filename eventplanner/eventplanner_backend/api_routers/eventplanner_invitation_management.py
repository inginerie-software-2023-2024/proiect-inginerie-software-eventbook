import time
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

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
    InvitationBase,
    Invitation,
    InvitationType,
)

invitation_management_router = APIRouter()


# Helper functions
def validate_event_organizer_or_admin(event_id: str, user_id: str):
    event = shared_functions.get_event_by_id(event_id)
    if user_id not in event.admins and user_id != event.organizer_id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="You do not have permission to give invites!",
        )


def find_invitation(invitations, invite_id: str):
    for invite in invitations or []:
        if invite.id == invite_id:
            return invite
    return None


def update_invitations(user_id: str, updated_invitations):
    users_table.update(
        {"active_invitations": updated_invitations}, user_query.id == user_id
    )


def create_updated_invite(
    invite: InvitationBase, current_user: User, id_invite: str
) -> Invitation:
    return Invitation(
        **dict(invite)
        | {"start_user": current_user.id, "id": id_invite, "time": str(time.time())}
    )


def handle_event_invitation(
    invite: InvitationBase, current_user: User, updated_invite: Invitation
):
    validate_event_organizer_or_admin(invite.event_id, current_user.id)
    invited_user = shared_functions.get_user_by_id(invite.end_user)
    update_invitations(
        invited_user.id, (invited_user.active_invitations or set()) | {updated_invite}
    )


def handle_request_invitation(invite: InvitationBase, updated_invite: Invitation):
    event = shared_functions.get_event_by_id(invite.event_id)
    event_table.update(
        {"requests_to_join": (event.requests_to_join or set()) | {updated_invite}},
        events_query.id == invite.event_id,
    )


def handle_friend_invitation(
    invite: InvitationBase, current_user: User, updated_invite: Invitation
):
    friend = shared_functions.get_user_by_id(invite.end_user)
    users_table.update(
        {"active_invitations": (friend.active_invitations or set()) | {updated_invite}},
        user_query.id == friend.id,
    )


# Invitation Endpoints
@invitation_management_router.post("/invitations", tags=[Tags.INVITATION])
def give_invitation(
    invite: InvitationBase, current_user: User = Depends(auth_helper.get_current_user)
):
    """
    IMPORTANT:
        ```
        There are 3 types of notification:
            - event: When start_user (current_user.id) is inviting end_user (user_id) to event (Event_id)
            - friend: When start_user (current_user.id) wants to be friend with end_user (user_id), event_id is null
            - request: When start_user (current_user.id) requests to join an event (event_id)
        ```

    Endpoint for sending different types of invitations (event, request, friend) to users.
    ```
    Args:
        invite: An object of InvitationBase containing the invitation details.
        current_user: The user who is sending the invitation, obtained from the authentication.

    Returns:
        A dictionary with a confirmation message and the invitation ID.

    Raises:
        [401]UNAUTHORIZED: If the user is not authenticated.
        [400]BAD_REQUEST: If the invitation type is not recognized.
    ```
    Example of valid request body:
    ```
    {
        "end_user": "12345",
        "event_id": "67890",
        "type": "EVENT"
    }
    ```
    """
    id_invite = shared_functions.generate_invitation_id(invite)
    updated_invite = create_updated_invite(invite, current_user, id_invite)

    if invite.type == InvitationType.EVENT:
        handle_event_invitation(invite, current_user, updated_invite)
        MESSAGE = "User invited successfully"

    elif invite.type == InvitationType.REQUEST:
        handle_request_invitation(invite, updated_invite)
        MESSAGE = "Successfully requested to join event"

    elif invite.type == InvitationType.FRIEND:
        handle_friend_invitation(invite, current_user, updated_invite)
        MESSAGE = "Successfully sent friend request"

    else:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Invitation type not found"
        )

    # [NOTIFICATION]
    return {"message": MESSAGE, "invite_id": id_invite}


@invitation_management_router.get(
    "/invitations/{invite_id}/answer", tags=[Tags.INVITATION]
)
def respond_to_invitation(
    invite_id: str,
    answer: bool,
    event_id: str = None,
    current_user: User = Depends(auth_helper.get_current_user),
):
    """
    IMPORTANT:
        ```
        There are 3 types of notification:
            - event: If you respond to invitation of type event you look into current_user.invitations
            - friend: When start_user (current_user.id) wants to be friend with end_user (user_id), event_id is null
            - request: When start_user (current_user.id) requests to join an event (event_id)
        ```
    Endpoint for users to respond to received invitations.

    Args:
        invite_id: The unique identifier of the invitation.
        answer: Boolean value representing the user's response to the invitation (True for accept, False for decline).
        event_id: The ID of the event associated with the invitation, if applicable.
        current_user: The user who is responding to the invitation, obtained from the authentication.

    Returns:
        A dictionary with a message indicating the response to the invitation has been processed.

    Raises:
        [401]UNAUTHORIZED: If the user is not authenticated.
        [400]BAD_REQUEST: If the invitation is not found or is invalid.

    No request body is required as the response is sent via URL parameters.
    """
    if event_id:
        event = shared_functions.get_event_by_id(event_id)
        invite = find_invitation(event.requests_to_join, invite_id)
    else:
        invite = find_invitation(current_user.active_invitations, invite_id)
    if not invite:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Invitation not found"
        )

    if answer:
        if invite.type == InvitationType.FRIEND:
            handle_friend_acceptance(invite, current_user)
        elif invite.type == InvitationType.REQUEST:
            handle_event_request_acceptance(invite, current_user)
        elif invite.type == InvitationType.EVENT:
            handle_event_invitation_acceptance(invite, current_user)

    # Remove invitation regardless of the answer
    update_invitations(current_user.id, current_user.active_invitations - {invite})

    return {"message": "Invitation response has been successfully processed!"}


def handle_friend_acceptance(invite: Invitation, current_user: User):
    friend = shared_functions.get_user_by_id(invite.end_user)
    current_user.friends = (current_user.friends or set()) | {friend.id}
    friend.friends = (friend.friends or set()) | {current_user.id}
    users_table.update(
        {"friends": current_user.friends}, user_query.id == current_user.id
    )
    users_table.update({"friends": friend.friends}, user_query.id == friend.id)


def handle_event_request_acceptance(invite: Invitation, current_user: User):
    validate_event_organizer_or_admin(invite.event_id, current_user.id)
    event = shared_functions.get_event_by_id(invite.event_id)
    event_table.update(
        {
            "participants": (event.participants or set()) | {invite.end_user},
            "requests_to_join": event.requests_to_join ^ {invite},
        },
        events_query.id == event.id,
    )
    users_table.update(
        {
            "events_participation": (current_user.events_participation or set())
            | {event.id}
        },
        user_query.id == invite.start_user,
    )


def handle_event_invitation_acceptance(invite: Invitation, current_user: User):
    event = shared_functions.get_event_by_id(invite.event_id)
    event_table.update(
        {"participants": (event.participants or set()) | {invite.end_user}},
        events_query.id == event.id,
    )
    users_table.update(
        {
            "events_participation": (current_user.events_participation or set())
            | {event.id}
        },
        user_query.id == invite.end_user,
    )
