import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from eventplanner.common import eventplanner_common as common
from eventplanner.eventplanner_backend.authentication.eventplanner_authentication import auth_router
from eventplanner.eventplanner_backend.api_routers.eventplanner_event_management import event_management_router
from eventplanner.eventplanner_backend.api_routers.eventplanner_account_management import account_management_router
from eventplanner.eventplanner_backend.api_routers.eventplanner_invitation_management import invitation_management_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(account_management_router)
app.include_router(event_management_router)
app.include_router(invitation_management_router)

@app.get("/", include_in_schema=False)
def redirect():
    return RedirectResponse("/docs")


if __name__ == "__main__":
    uvicorn.run(
        app=common.EVENTPLANNER_BACKEND_APP,
        port=common.EVENTPLANNER_BACKEND_PORT,
        host=common.EVENTPLANNER_BACKEND_HOST
    )
