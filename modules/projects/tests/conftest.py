from typing import Iterator
from uuid import uuid4

import docker
import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient

import core.auth
import core.context
from core.config import settings
from core.connection import health_check_mongo, create_mongo_client
from models import User


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
def user() -> User:
    _user = User(id=uuid4(), organization_id=uuid4())
    yield _user


@pytest.fixture(scope="session")
def mock_supertokens(session_mocker):
    def fake_supertokens():
        pass

    session_mocker.patch.object(
        core.auth,
        "supertokens_init",
        fake_supertokens,
    )


@pytest.fixture(scope="session")
def mock_get_context(user, session_mocker):
    async def fake_get_context():
        return {"user": user}

    session_mocker.patch.object(
        core.context,
        "get_context",
        fake_get_context,
    )


@pytest.fixture
def database(mongo):
    yield
    client = create_mongo_client()
    client.drop_database(settings.MONGO_DB)


@pytest.fixture
async def app(database, mock_supertokens, mock_get_context) -> FastAPI:
    from main import app

    async with LifespanManager(app):
        yield app


@pytest.fixture()
async def client(app: FastAPI) -> Iterator[AsyncClient]:
    """Async server client that handles lifespan and teardown"""

    async with AsyncClient(
            app=app,
            base_url=settings.SERVER_HOST.__str__(),
    ) as _client:
        try:
            yield _client
        except Exception as exc:
            print(exc)
