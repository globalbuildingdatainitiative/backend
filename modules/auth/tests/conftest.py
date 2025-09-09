import json
from pathlib import Path
from typing import Iterator
from uuid import uuid4, UUID

import docker
import httpx
import pytest
from asgi_lifespan import LifespanManager
from docker.errors import NotFound
from fastapi import FastAPI
from fastapi.requests import Request
from httpx import AsyncClient
from supertokens_python import RecipeUserId
from supertokens_python.asyncio import delete_user
from supertokens_python.recipe.emailpassword.asyncio import sign_up
from supertokens_python.recipe.session.asyncio import create_new_session
from supertokens_python.recipe.usermetadata.asyncio import update_user_metadata
from supertokens_python.recipe.userroles.asyncio import add_role_to_user
from tenacity import stop_after_attempt, wait_fixed, retry_if_exception, retry
from time import sleep

from core.config import settings
from logic.roles import assign_role
from models import SuperTokensUser, Role


@pytest.fixture(scope="session")
def docker_client():
    yield docker.from_env()


@pytest.fixture(scope="session")
async def supertokens(docker_client):
    # Clean up any existing containers with conflicting names
    for container_name in ["supertokens", "supertokens_auth"]:
        try:
            _container = docker_client.containers.get(container_name)
            _container.kill()
            sleep(0.2)
        except NotFound:
            pass

    container = docker_client.containers.run(
        image="registry.supertokens.io/supertokens/supertokens-postgresql:10.1",
        ports={"3567": "3568"},
        name="supertokens_auth",
        detach=True,
        auto_remove=True,
    )

    @retry(
        stop=stop_after_attempt(20),
        wait=wait_fixed(0.2),
        retry=retry_if_exception(lambda e: isinstance(e, httpx.HTTPError)),
    )
    def wait_for_container():
        response = httpx.get(f"{settings.CONNECTION_URI}/hello")
        if response.status_code == 200 and response.text.strip() == "Hello":
            return True

    while True:
        if wait_for_container():
            break
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


@pytest.fixture
async def create_admin_user(app) -> SuperTokensUser:
    response = await sign_up("public", "admin@email.com", "currentPassword123")
    _user = SuperTokensUser(id=UUID(response.user.id), organization_id=uuid4())
    await assign_role(_user.id, Role.ADMIN)

    yield _user

    await delete_user(str(_user.id))


@pytest.fixture()
async def client_admin(app: FastAPI, client_unauthenticated, create_admin_user) -> Iterator[AsyncClient]:
    """Async server client that handles lifespan and teardown"""

    response = await client_unauthenticated.get(f"/login/{create_admin_user.id}")
    response.raise_for_status()

    client_unauthenticated.headers["Authorization"] = f"Bearer {response.json()['token']}"
    yield client_unauthenticated


@pytest.fixture()
async def client(app: FastAPI, client_unauthenticated, create_user) -> Iterator[AsyncClient]:
    """Async server client that handles lifespan and teardown"""

    response = await client_unauthenticated.get(f"/login/{create_user.id}")
    response.raise_for_status()

    client_unauthenticated.headers["Authorization"] = f"Bearer {response.json()['token']}"
    yield client_unauthenticated


@pytest.fixture()
async def client_user(app: FastAPI, client_unauthenticated, users) -> Iterator[AsyncClient]:
    """Async server client that authenticates as the first user from the users fixture"""

    user_id = users[0]["id"]
    response = await client_unauthenticated.get(f"/login/{user_id}")
    response.raise_for_status()

    client_unauthenticated.headers["Authorization"] = f"Bearer {response.json()['token']}"
    yield client_unauthenticated


@pytest.fixture
async def users(app):
    created_users = []
    users = json.loads((Path(__file__).parent / "datafixtures" / "users.json").read_text())
    for user in users:
        response = await sign_up("public", user.get("email"), "currentPassword123")
        user_id = response.user.id
        await update_user_metadata(
            user_id,
            {
                "firstName": user.get("firstName"),
                "lastName": user.get("lastName"),
                "organization_id": user.get("organization_id"),
                "invited": user.get("invited"),
                "invite_status": user.get("invite_status"),
                "inviter_name": user.get("inviter_name"),
            },
        )
        for role in user.get("roles", []):
            await add_role_to_user("public", user_id, role)
        user.update({"id": user_id})
        created_users.append(user_id)

    yield users

    # Clean up created users
    for user_id in created_users:
        try:
            await delete_user(user_id)
        except Exception:
            pass  # Ignore errors during cleanup


@pytest.fixture()
async def client_unauthenticated(app: FastAPI) -> Iterator[AsyncClient]:
    """Async server client that handles lifespan and teardown"""

    async with AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url=str(settings.SERVER_HOST),
    ) as _client:
        try:
            yield _client
        except Exception as exc:
            print(exc)
