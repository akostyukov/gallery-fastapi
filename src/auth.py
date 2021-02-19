import json
from typing import List

from authlib.integrations.starlette_client import OAuthError
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse

from main import app, oauth
from models import User, User_Pydantic


@app.route("/")
async def homepage(request: Request):
    user = request.session.get("user")
    if user:
        data = json.dumps(user)
        html = f"<pre>{data}</pre>" '<a href="/logout">logout</a>'
        return HTMLResponse(html)
    return HTMLResponse('<a href="/login">login</a>')


@app.route("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.route("/auth")
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return JSONResponse({"error": error.error})

    user = await oauth.google.parse_id_token(request, token)
    request.session["user"] = dict(user)

    await User.get_or_create(email=user.email, username=user.email.split("@")[0])

    return JSONResponse({"response": "login succeed"})


@app.post("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return JSONResponse({"response": "logout succeed"})


@app.get("/users/", response_model=List[User_Pydantic])
async def get_users():
    return await User_Pydantic.from_queryset(User.all())


async def get_current_user(request: Request):
    return await User.get(email=request.session.get("user").get("email"))
