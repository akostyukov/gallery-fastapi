import logging

from authlib.integrations.starlette_client import OAuth
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from tortoise.contrib.fastapi import register_tortoise

from auth import auth_router
from comments import comments_router
from images import images_router

app = FastAPI(redoc_url=None)

routers = [auth_router, comments_router, images_router]


for auth_router in routers:
    app.include_router(auth_router)


origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


es = AsyncElasticsearch(hosts="elasticsearch")

app.add_middleware(SessionMiddleware, secret_key="!secret")

config = Config(".env")
oauth = OAuth(config)

CONF_URL = "https://accounts.google.com/.well-known/openid-configuration"
oauth.register(
    name="google",
    server_metadata_url=CONF_URL,
    client_kwargs={"scope": "openid email profile"},
)


@app.on_event("startup")
async def on_startup():
    logger_uvicorn = logging.getLogger("uvicorn")
    logger_uvicorn.propagate = False


register_tortoise(
    app,
    db_url="postgres://postgres:postgres@db:5432/postgres",
    modules={"models": ["models", "auth", "images", "comments"]},
    generate_schemas=True,
    add_exception_handlers=True,
)
