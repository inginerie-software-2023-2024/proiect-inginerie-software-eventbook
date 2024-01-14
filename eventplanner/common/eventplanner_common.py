from enum import Enum

EVENTPLANNER_BACKEND_PORT = 8080
EVENTPLANNER_BACKEND_HOST = "127.0.0.1"
EVENTPLANNER_BACKEND_APP = "eventplanner_main:app"


class EventplannerBackendTags(Enum):
    AUTH: str = "Authentication"
    ACCOUNT: str = "Account"
    EVENT: str = "Event"
    NOTIFICATION: str = "Notification"
    WEATHER: str = "Weather"
