from typing import Annotated

import uvicorn
from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse


from eventplanner.eventplanner_backend.eventplanner_base_models import User
from eventplanner.eventplanner_backend import (
    eventplanner_authentication_helper as auth_helper,
)
from eventplanner.eventplanner_backend.eventplanner_authentication import router
from eventplanner.eventplanner_backend.eventplanner_database import user_items, items_query
app = FastAPI()
app.include_router(router)


@app.get("/", include_in_schema=False)
def redirect():
    return RedirectResponse("/docs")


@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(auth_helper.get_current_user)]
):
    return current_user

@app.get("/user/add-items")
async def add_items(
        current_user: Annotated[User, Depends(auth_helper.get_current_user)],
        item1: str,
        item2: str,
        item3: str
):
    items = user_items.search(items_query.user==current_user)
    items = {} if not items else items[0]
    items = items | {"user": current_user, 1:item1, 2: item2, 3:item3}
    user_items.remove(items_query.user==current_user)

    user_items.insert(items)

@app.get("/user/get-items")
async def get_items(
        current_user: Annotated[User, Depends(auth_helper.get_current_user)]
):
    return user_items.search(items_query.user==current_user)





if __name__ == "__main__":
    uvicorn.run(
        app=app,
    )
