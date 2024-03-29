import time
from typing import Iterator

import docker
import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import SQLModel

from core.config import settings
from core.connection import create_postgres_engine


@pytest.fixture(scope="session")
def docker_client():
    yield docker.from_env()


@pytest.fixture(scope="session")
def postgres(docker_client):
    container = docker_client.containers.run(
        "postgres:13.1-alpine",
        ports={"5432": settings.POSTGRES_PORT},
        environment={
            "POSTGRES_DB": settings.POSTGRES_DB,
            "POSTGRES_PASSWORD": settings.POSTGRES_PASSWORD,
            "POSTGRES_USER": settings.POSTGRES_USER,
        },
        detach=True,
        auto_remove=True,
    )

    time.sleep(3)
    try:
        yield container
    finally:
        container.stop()


@pytest.fixture()
async def db(postgres) -> AsyncEngine:
    engine = create_postgres_engine()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture()
async def app(db) -> FastAPI:
    from main import app

    async with LifespanManager(app):
        yield app


@pytest.fixture()
async def client(app: FastAPI) -> Iterator[AsyncClient]:
    """Async server client that handles lifespan and teardown"""

    async with AsyncClient(
        app=app,
        base_url=settings.SERVER_HOST,
    ) as _client:
        try:
            yield _client
        except Exception as exc:
            print(exc)
