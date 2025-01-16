import json
from pathlib import Path
from typing import Iterator
from uuid import uuid4, UUID

import docker
import httpx
import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from fastapi.requests import Request
from httpx import AsyncClient
from supertokens_python import RecipeUserId
from supertokens_python.recipe.emailpassword.asyncio import sign_up
from supertokens_python.recipe.session.asyncio import create_new_session
from time import sleep

from core.config import settings
from models import SuperTokensUser


@pytest.fixture(scope="session")
def docker_client():
    yield docker.from_env()


@pytest.fixture(scope="session")
async def supertokens(docker_client):
    container = docker_client.containers.run(
        image="registry.supertokens.io/supertokens/supertokens-postgresql",
        ports={"3567": "3567"},
        name="supertokens",
        detach=True,
        auto_remove=True,
    )
    while True:
        sleep(0.1)
        try:
            response = httpx.get(f"{settings.CONNECTION_URI}/hello")
            if response.status_code == 200 and response.text.strip() == "Hello":
                break
        except httpx.HTTPError:
            pass
    try:
        yield container
    finally:
        container.stop()


@pytest.fixture(scope="session")
async def app(supertokens) -> FastAPI:
    from main import app

    @app.get("/login/{user_id}")
    async def login(request: Request, user_id: str):  # type: ignore
        res = await create_new_session(request, "public", RecipeUserId(user_id), {}, {})
        return {"token": res.access_token}

    async with LifespanManager(app):
        yield app


@pytest.fixture(scope="session")
async def create_user(app) -> SuperTokensUser:
    response = await sign_up("public", "my@email.com", "currentPassword123")
    yield SuperTokensUser(id=UUID(response.user.id), organization_id=uuid4())


@pytest.fixture()
async def client(app: FastAPI, client_unauthenticated, create_user) -> Iterator[AsyncClient]:
    """Async server client that handles lifespan and teardown"""

    response = await client_unauthenticated.get(f"/login/{create_user.id}")
    response.raise_for_status()

    client_unauthenticated.headers["Authorization"] = f"Bearer {response.json()['token']}"
    yield client_unauthenticated


@pytest.fixture(scope="session")
async def users(app):
    users = json.loads((Path(__file__).parent / "datafixtures" / "users.json").read_text())
    for user in users:
        response = await sign_up("public", user.get("email"), "currentPassword123")
        user.update({"id": response.user.id})
    yield users


@pytest.fixture()
async def client_unauthenticated(app: FastAPI) -> Iterator[AsyncClient]:
    """Async server client that handles lifespan and teardown"""

    async with AsyncClient(
        app=app,
        base_url=str(settings.SERVER_HOST),
    ) as _client:
        try:
            yield _client
        except Exception as exc:
            print(exc)
