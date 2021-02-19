from authlib.integrations.starlette_client import OAuth
from fastapi import FastAPI
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from tortoise.contrib.fastapi import register_tortoise

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="!secret")

config = Config(".env")
oauth = OAuth(config)

CONF_URL = "https://accounts.google.com/.well-known/openid-configuration"
oauth.register(
    name="google",
    server_metadata_url=CONF_URL,
    client_kwargs={"scope": "openid email profile"},
)

register_tortoise(
    app,
    db_url="postgres://postgres:postgres@db:5432/postgres",
    modules={"models": ["models", "auth", "images", "comments"]},
    generate_schemas=True,
    add_exception_handlers=True,
)
