import time
from fastapi import APIRouter
from fastapi import APIRouter, Depends, HTTPException, Query
from http import HTTPStatus


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
    user_id: str, notification_type: NotificationType, content: str, event_id: str = "0"
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
        event_id=event_id
    )
    return new_notification


@notification_management_router.post(
    "/notifications/{user_id}/notify", tags=[Tags.NOTIFICATION]
)
def notify_user(user_id: str, content: str, notification_type: NotificationType = NotificationType.EVENT_UPDATE, event_id: str = "0"):
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
    notification = create_and_store_notification(user_id, notification_type, content, event_id)

    updated_notifications = user.notifications or set()
    updated_notifications.add(notification)
    users_table.update(
        {"notifications": updated_notifications}, user_query.id == user.id
    )

    return {"message": "User notified successfully!",
            "notification_id": notification.id,
            "event_id": event_id}



@notification_management_router.delete(
    "/notifications/{user_id}/{notify_id}", tags=[Tags.NOTIFICATION]
)
def remove_notification(user_id: str, notify_id: str):
    """
    Endpoint utility for removing a notification for a specified user.

    This function removes the notification with the given notify_id from the
    list of notifications associated with the provided user_id.

    Args:
        user_id: The unique identifier of the user whose notification is being removed.
        notify_id: The unique identifier of the notification to be removed.

    Returns:
        A dictionary with a message indicating successful notification removal.

    Raises:
        [404]NOT_FOUND: If the specified user ID does not exist in the database
        or if the notification ID does not exist in the user's notifications list.
    """
    user = shared_functions.get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")


    for notifications in user.notifications:
        if notify_id == notifications.id:
            updated_notifications = {notif for notif in user.notifications if notif.id != notify_id}
            users_table.update(
                {"notifications": updated_notifications}, user_query.id == user.id
            )
            return {"message": "You successfully deleted the notification"}

    if user.notifications is None or notify_id not in {notification.id for notification in user.notifications}:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Notification not found for this user",
        )



@notification_management_router.get(
    "/notifications/{user_id}", tags=[Tags.NOTIFICATION]
)
def get_notif(user_id: str):
    """
    Endpoint utility for getting the notifications of a specified user.

    ```
    Args:
        user_id: The unique identifier of the user to whom the notification is sent.

    Returns:
        A dictionary with all the notifications and a message indicating successful notifications delivery.

    """
    user = shared_functions.get_user_by_id(user_id)

    notifications = user.notifications

    return {"message": "User notifications extracted successfully!",
            "notification_id": notifications}




