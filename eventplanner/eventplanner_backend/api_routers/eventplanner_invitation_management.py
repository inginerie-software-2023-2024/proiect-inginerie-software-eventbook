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
    InvitationType
)

invitation_management_router = APIRouter()


@invitation_management_router.post("/invitations", tags=[Tags.INVITATION])
def give_invitation(
        invite: InvitationBase, current_user: User = Depends(auth_helper.get_current_user)
):

    id_invite = shared_functions.generate_invitation_id(invite)
    event = shared_functions.get_event_by_id(invite.event_id)
    invited_user = shared_functions.get_user_by_name(invite.user_to_invite)


    if current_user.id not in (event.admins | {event.organizer_id}):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="You do not have permission to give invites!"
        )

    invite = Invitation(
        **(
                dict(invite)
                | {"inviter": current_user.id, "id": id_invite, "time": str(time.time())}
        )
    )
    users_table.update(
        {"active_invitations": (invited_user.active_invitations or set()) | {invite}},
        user_query.id == invited_user.id
    )
    # [NOTIFICATION]

    return {"message": "User invited successfully",
            "invite_id": id_invite}


@invitation_management_router.get("/invitations/{invite_id}/answer", tags=[Tags.INVITATION])
def join_event_via_invite(invite_id: str, answer: bool, current_user: User = Depends(auth_helper.get_current_user)):
    invite = None
    for inv in (current_user.active_invitations or []):
        invite = invite if inv.id != invite_id else inv

    if not invite:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invitation not found"
        )

    if answer:
        event = shared_functions.get_event_by_id(invite.event_id)
        event_table.update(
            {"participants": (event.participants or set()) | {current_user.id}},
            events_query.id == event.id
        )
        users_table.update({"events_participation": (current_user.events_participation or set()) | {current_user.id}},
                           user_query.id == current_user.id)

    users_table.update(
        {
            "active_invitation": current_user.active_invitations ^ {invite}},
        user_query.id == current_user.id
    )

     # [NOTIFICATION]

    return {"message": "Invite as been successfully answered!"}

@invitation_management_router.delete("/invitations/{invitation_id}/revoke", tags=[Tags.INVITATION])
def revoke_invitation(invitation_id: str, user_id: str, current_user: User= Depends(auth_helper.get_current_user)):
    user = shared_functions.get_user_by_id(user_id)
    invitation = None
    for inv in user.active_invitations:
        if invitation_id in inv:
            invitation = inv

    if not invitation:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Invitation not found"
        )

    if invitation.inviter == current_user.id:
        users_table.update(
            {"active_invitation": user.active_invitations ^ {invitation}},
            user_query.id == current_user.id
        )

        return {"message": "Invitation returned successfully!"}

    raise HTTPException(
        status_code=HTTPStatus.BAD_REQUEST,
        detail="You do not have enough rights to revoke invitation"
    )

