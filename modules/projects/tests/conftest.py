from typing import Iterator

import docker
import pytest
from asgi_lifespan import LifespanManager
from core.config import settings
from core.connection import health_check_mongo
from fastapi import FastAPI
from httpx import AsyncClient


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


@pytest.fixture()
async def app(mongo) -> FastAPI:
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
