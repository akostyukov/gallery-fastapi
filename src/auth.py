from typing import List

from authlib.integrations.starlette_client import OAuthError
from fastapi import APIRouter, HTTPException
from starlette.requests import Request

from models import User, User_Pydantic

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.get("/login")
async def login(request: Request):
    from main import oauth

    redirect_uri = request.url_for("auth")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@auth_router.get("/")
async def auth(request: Request):
    from main import oauth

    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return {"error": error.error}

    user = await oauth.google.parse_id_token(request, token)
    request.session["user"] = dict(user)

    await User.get_or_create(email=user.email, username=user.email.split("@")[0])

    return {"response": "login succeed"}


@auth_router.post("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return {"response": "logout succeed"}


@auth_router.get("/users/", response_model=List[User_Pydantic])
async def get_users():
    return await User_Pydantic.from_queryset(User.all())


@auth_router.get("/users/me")
async def get_me(request: Request):
    return {"me": (await get_current_user(request)).email}


async def get_current_user(request: Request):
    try:
        return await User.get(email=request.session.get("user").get("email"))
    except:
        raise HTTPException(status_code=401, detail="User is not authenticated")
