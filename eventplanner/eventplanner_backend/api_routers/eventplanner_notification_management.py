import time


from fastapi import APIRouter

from eventplanner.eventplanner_backend.api_routers import shared_functions
from eventplanner.common.eventplanner_common import EventplannerBackendTags as Tags

from eventplanner.eventplanner_backend.eventplanner_database import (
    users_table,
    user_query,
)
from eventplanner.eventplanner_backend.schemas.eventplanner_base_models import (
    Notification,
    NotificationType
)

notification_management_router = APIRouter()

@notification_management_router.post("/notifications/{user_id}/notify", tags=[Tags.NOTIFICATION])
def notify_user(user_id: str, notification_type: NotificationType, content: str ):

    notif_time = time.time()

    notification_id = shared_functions.generate_notification_id(
        user_id=user_id,
        notification_type=notification_type.value,
        time=notif_time
    )

    notification = Notification(
        user_id=user_id,
        notification_type= notification_type,
        time=time.time(),
        id=notification_id,
        message=content,
    )
    user = shared_functions.get_user_by_id(user_id)

    users_table.update(
        {"notifications": user.notifications or set() | {notification}},
        user_query.id == user.id
    )

    return {
        "message": "User notified successfully!"
    }


