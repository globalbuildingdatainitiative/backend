from time import sleep
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
from supertokens_python.recipe.userroles.asyncio import create_new_role_or_add_permissions
from tenacity import stop_after_attempt, wait_fixed, retry, retry_if_exception

from core.config import settings
from core.connection import health_check_mongo, create_mongo_client
from models import SuperTokensUser


@pytest.fixture(scope="session")
def docker_client():
    yield docker.from_env()


@pytest.fixture(scope="session")
async def mongo(docker_client):
    try:
        _container = docker_client.containers.get("mongo_database")
        _container.kill()
    except NotFound:
        pass

    container = docker_client.containers.run(
        "mongo:7",
        ports={"27017": settings.MONGO_PORT},
        environment={
            "MONGO_INITDB_DATABASE": settings.MONGO_DB,
            "MONGO_INITDB_ROOT_USERNAME": settings.MONGO_USER,
            "MONGO_INITDB_ROOT_PASSWORD": settings.MONGO_PASSWORD,
        },
        name="mongo_database",
        detach=True,
        auto_remove=True,
    )

    await health_check_mongo()
    try:
        yield container
    finally:
        container.stop()


@pytest.fixture(scope="session")
async def supertokens(docker_client):
    # Clean up any existing container with the same name
    try:
        _container = docker_client.containers.get("supertokens_organization")
        _container.kill()
        sleep(0.2)
    except NotFound:
        pass
    
    container = docker_client.containers.run(
        image="registry.supertokens.io/supertokens/supertokens-postgresql:10.1",
        ports={"3567": "3569"},
        name="supertokens_organization",
        detach=True,
        auto_remove=True,
    )

    @retry(
        stop=stop_after_attempt(30),  # Increase retry attempts
        wait=wait_fixed(0.5),  # Increase wait time between retries
        retry=retry_if_exception(lambda e: isinstance(e, (httpx.HTTPError, httpx.ConnectError))),
    )
    def wait_for_container():
        try:
            response = httpx.get(f"{settings.SUPERTOKENS_CONNECTION_URI}/hello", timeout=10.0)
            if response.status_code == 200 and response.text.strip() == "Hello":
                return True
        except Exception as e:
            print(f"Waiting for SuperTokens container to be ready... Error: {e}")
            raise

    while True:
        if wait_for_container():
            break
    try:
        yield container
    finally:
        container.stop()


@pytest.fixture
def database(mongo):
    yield
    client = create_mongo_client()
    client.drop_database(settings.MONGO_DB)


@pytest.fixture
async def app(supertokens, mongo) -> FastAPI:
    from main import app

    @app.get("/login/{user_id}")
    async def login(request: Request, user_id: str):  # type: ignore
        res = await create_new_session(request, "public", RecipeUserId(user_id), {}, {})
        return {"token": res.access_token}

    async with LifespanManager(app):
        yield app


@pytest.fixture
async def create_owner():
    await create_new_role_or_add_permissions("owner", [])


@pytest.fixture
async def create_user(app, create_owner) -> SuperTokensUser:
    response = await sign_up("public", "my@email.com", "currentPassword123")
    user_id = response.user.id
    yield SuperTokensUser(id=UUID(user_id), organization_id=uuid4())

    await delete_user(user_id)


@pytest.fixture()
async def client(app: FastAPI, client_unauthenticated, create_user) -> Iterator[AsyncClient]:
    """Async server client that handles lifespan and teardown"""

    response = await client_unauthenticated.get(f"/login/{create_user.id}")
    response.raise_for_status()

    client_unauthenticated.headers["Authorization"] = f"Bearer {response.json()['token']}"
    yield client_unauthenticated


@pytest.fixture()
async def client_unauthenticated(app: FastAPI, database) -> Iterator[AsyncClient]:
    """Async server client that handles lifespan and teardown"""

    async with AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url=str(settings.SERVER_HOST),
    ) as _client:
        try:
            yield _client
        except Exception as exc:
            print(exc)
