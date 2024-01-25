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
    NotificationType,
)

notification_management_router = APIRouter()


# Helper function
def create_and_store_notification(
    user_id: str, notification_type: NotificationType, content: str
):
    notification_id = shared_functions.generate_notification_id(
        user_id, notification_type.value, time.time()
    )
    new_notification = Notification(
        user_id=user_id,
        notification_type=notification_type,
        time=time.time(),
        id=notification_id,
        message=content,
    )
    return new_notification


@notification_management_router.post(
    "/notifications/{user_id}/notify", tags=[Tags.NOTIFICATION]
)
def notify_user(user_id: str, notification_type: NotificationType, content: str):
    """
    Endpoint utility for sending a notification to a specified user.

    This function creates a notification based on the provided type and content,
    associates it with the given user ID, and updates the user's notification list
    in the database.

    ```
    Args:
        user_id: The unique identifier of the user to whom the notification is sent.
        notification_type: The type of the notification, defined by the NotificationType enum.
        content: The message content of the notification.

    Returns:
        A dictionary with a message indicating successful notification delivery.

    Raises:
        [404]NOT_FOUND: If the specified user ID does not exist in the database.
        [400]BAD_REQUEST: If the notification type is invalid or the content is empty.
    ```
    Example of valid request body:
    ```
    {
        "notification_type": "INVITATION",
        "user_id": 11111-1111111-11-11111,
        "content": "Example",
    }
    ```
    """
    user = shared_functions.get_user_by_id(user_id)
    notification = create_and_store_notification(user_id, notification_type, content)

    updated_notifications = user.notifications or set()
    updated_notifications.add(notification)
    users_table.update(
        {"notifications": updated_notifications}, user_query.id == user.id
    )

    return {"message": "User notified successfully!"}
