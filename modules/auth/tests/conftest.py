import dataclasses
import json
from typing import Iterator
from uuid import uuid4

import docker
import pytest
import supertokens_python.asyncio
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient

import core.auth
import core.context
from core.config import settings
from models import SuperTokensUser


@pytest.fixture(scope="session")
def docker_client():
    yield docker.from_env()


@pytest.fixture(scope="session")
def user() -> SuperTokensUser:
    _user = SuperTokensUser(id=uuid4(), organization_id=uuid4())
    yield _user


@pytest.fixture(scope="session")
def mock_supertokens(session_mocker):
    def fake_supertokens_init():
        pass

    session_mocker.patch.object(
        core.auth,
        "supertokens_init",
        fake_supertokens_init,
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
async def app(mock_supertokens, mock_get_context) -> FastAPI:
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


@pytest.fixture
def users(datafix_dir):
    yield json.loads((datafix_dir / "users.json").read_text())


@pytest.fixture
def mock_get_users_newest_first(users, session_mocker):
    async def fake_get_users_newest_first(tenant_id: str):
        @dataclasses.dataclass
        class FakeUser:
            id: str
            email: str
            timeJoined: int
            tenantIds: list[str]

            def to_json(self):
                return {
                    "user": {
                        "id": self.id,
                        "email": self.email,
                        "timeJoined": self.timeJoined,
                        "tenantIds": self.tenantIds,
                    }
                }

        @dataclasses.dataclass
        class FakeResponse:
            users: list[FakeUser]

        return FakeResponse(users=[FakeUser(**user) for user in users])

    session_mocker.patch.object(
        supertokens_python.asyncio,
        "get_users_newest_first",
        fake_get_users_newest_first,
    )
