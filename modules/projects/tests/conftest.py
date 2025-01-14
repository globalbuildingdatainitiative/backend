import json
from datetime import datetime
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
from supertokens_python.asyncio import delete_user
from supertokens_python.recipe.emailpassword.asyncio import sign_up
from supertokens_python.recipe.session.asyncio import create_new_session
from supertokens_python.recipe.usermetadata.asyncio import update_user_metadata
from time import sleep

from core.config import settings
from core.connection import health_check_mongo, create_mongo_client
from models import SuperTokensUser


@pytest.fixture(scope="session")
def docker_client():
    yield docker.from_env()


@pytest.fixture(scope="session")
async def mongo(docker_client):
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
            response = httpx.get(f"{settings.SUPERTOKENS_CONNECTION_URI}/hello")
            if response.status_code == 200 and response.text.strip() == "Hello":
                break
        except httpx.HTTPError:
            pass
    try:
        yield container
    finally:
        container.stop()


@pytest.fixture
async def create_user(app) -> SuperTokensUser:
    response = await sign_up("public", "my@email.com", "currentPassword123")
    user_id = response.user.id
    organization_id = str(uuid4())
    await update_user_metadata(user_id, {"organization_id": organization_id})
    yield SuperTokensUser(id=UUID(user_id), organization_id=UUID(organization_id))

    await delete_user(user_id)


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
        app=app,
        base_url=str(settings.SERVER_HOST),
    ) as _client:
        try:
            yield _client
        except Exception as exc:
            print(exc)


@pytest.fixture
async def projects(datafix_dir):
    """Create test projects linked to contributions"""
    from models import DBProject

    # Load project template from JSON
    project_data = json.loads((datafix_dir / "project.json").read_text())

    # Create multiple test projects
    _projects = []
    for i in range(3):  # Create 3 test projects
        project_data["id"] = str(uuid4())
        project_data["name"] = f"Test Project {i}"
        project = DBProject(**project_data)
        await project.insert()
        _projects.append(project)

    return _projects


@pytest.fixture
async def contributions(user, projects):
    """Create test contributions linked to projects"""
    from models import DBContribution

    _contributions = []
    for project in projects:
        contribution = DBContribution(
            id=uuid4(),
            project=project,
            user_id=user.id,
            organization_id=user.organization_id,
            uploaded_at=datetime.now(),
            public=True,
        )
        await contribution.insert()
        _contributions.append(contribution)

    return _contributions
