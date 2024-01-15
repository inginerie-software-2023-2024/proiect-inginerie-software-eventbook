from fastapi import APIRouter, Depends

from eventplanner.eventplanner_backend.api_routers import shared_functions
from eventplanner.common.eventplanner_common import EventplannerBackendTags as Tags
from eventplanner.eventplanner_backend.authentication import eventplanner_authentication_helper as auth_helper
from eventplanner.eventplanner_backend.eventplanner_database import users_table, user_query, invitation_table, \
    events_query
from eventplanner.eventplanner_backend.schemas.eventplanner_base_models import User, EventBase, Event, InvitationBase, \
    Invitation

invitation_management_router = APIRouter()


@invitation_management_router.post("/invitations/", tags=[Tags.INVITATION])
def invite_guest_event(invite: InvitationBase, current_user: dict = Depends(auth_helper.get_current_user)):
    id_invite = shared_functions.generate_invitation_id(invite)

    invited_user = shared_functions.get_user_by_name(invite.invited)

    invite = Invitation(**(dict(invite) | {"inviter": current_user["id"], "id": id_invite}))
    users_table.update({"active_invitations": invited_user["active_invitations"]+[dict(invite)]}, user_query.id == invited_user["id"])

    return {"message": "User invited successfully"}


@invitation_management_router.get("/events/{invitation_id}/guest", tags=[Tags.INVITATION])
def view_guests_event():
    pass


@invitation_management_router.delete("/events/{invitation_id}/guests/{guest_id}", tags=[Tags.INVITATION])
def delete_guest_from_event():
    pass
