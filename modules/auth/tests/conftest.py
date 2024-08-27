from datetime import datetime

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
import supertokens_python.recipe.session.asyncio
import supertokens_python.recipe.usermetadata.asyncio
from fastapi.requests import Request

import core.auth
import core.context
import logic as logic
from core.config import settings
from models import SuperTokensUser, GraphQLUser, UserFilters, UserSort


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
            firstName: str
            lastName: str
            organizationId: str

            def to_json(self):
                return {
                    "user": {
                        "id": self.id,
                        "email": self.email,
                        "timeJoined": self.timeJoined,
                        "tenantIds": self.tenantIds,
                        "firstName": self.firstName,
                        "lastName": self.lastName,
                        "organizationId": self.organizationId,
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


@pytest.fixture
def mock_get_user_metadata(session_mocker, users):
    @dataclasses.dataclass
    class FakeMetadata:
        metadata: dict

    async def fake_get_user_metadata(user_id: str):
        for user in users:
            if user["id"] == user_id:
                metadata = {
                    "first_name": user["firstName"],
                    "last_name": user["lastName"],
                    "organization_id": f"org-{user_id}",
                }
                return FakeMetadata(metadata=metadata)

    session_mocker.patch.object(
        supertokens_python.recipe.usermetadata.asyncio,
        "get_user_metadata",
        fake_get_user_metadata,
    )


@pytest.fixture
def mock_update_user_metadata(session_mocker, users):
    async def fake_update_user_metadata(user_id: str, metadata: dict):
        for user in users:
            if user["id"] == user_id:
                if "first_name" in metadata:
                    user["firstName"] = metadata.get("first_name")
                if "last_name" in metadata:
                    user["lastName"] = metadata.get("last_name")
                if "email" in metadata:
                    user["email"] = metadata.get("email")

    session_mocker.patch.object(
        supertokens_python.recipe.usermetadata.asyncio,
        "update_user_metadata",
        fake_update_user_metadata,
    )


@pytest.fixture
def mock_update_email_or_password(session_mocker):
    async def fake_update_email_or_password(user_id: str, email: str, password: str):
        return

    session_mocker.patch.object(
        supertokens_python.recipe.emailpassword.asyncio,
        "update_email_or_password",
        fake_update_email_or_password,
    )


@pytest.fixture
def mock_sign_in(session_mocker):
    @dataclasses.dataclass
    class SignInOkResult:
        status: str = "OK"

    @dataclasses.dataclass
    class SignInWrongCredentialsError:
        status: str = "WRONG_CREDENTIALS_ERROR"

    async def fake_sign_in(tenant_id: str, email: str, password: str):
        if password == "currentPassword123":
            return SignInOkResult()
        else:
            return SignInWrongCredentialsError()

    session_mocker.patch.object(
        supertokens_python.recipe.emailpassword.asyncio,
        "sign_in",
        fake_sign_in,
    )


@pytest.fixture
def mock_get_users(session_mocker, users):
    async def fake_get_users(filters: UserFilters = None, sort_by: UserSort = None):
        filtered_users = [
            GraphQLUser(
                id=user["id"],
                email=user["email"],
                time_joined=datetime.fromtimestamp(user["timeJoined"] / 1000),
                first_name=user["firstName"],
                last_name=user["lastName"],
                organization_id=user["organizationId"],
            )
            for user in users
            if not filters or (filters.id and filters.id.equal == user["id"])
        ]

        return filtered_users

    session_mocker.patch.object(
        logic,
        "get_users",
        fake_get_users,
    )


@pytest.fixture
async def app_unauthenticated(mock_supertokens, mock_get_session) -> FastAPI:
    from main import app

    async with LifespanManager(app):
        yield app


@pytest.fixture(scope="session")
def mock_get_session(session_mocker):
    async def fake_get_session(request: Request):
        return {}

    session_mocker.patch.object(
        supertokens_python.recipe.session.asyncio,
        "get_session",
        fake_get_session,
    )


@pytest.fixture()
async def client_unauthenticated(app_unauthenticated: FastAPI) -> Iterator[AsyncClient]:
    """Async server client that handles lifespan and teardown"""

    async with AsyncClient(
        app=app_unauthenticated,
        base_url=str(settings.SERVER_HOST),
    ) as _client:
        try:
            yield _client
        except Exception as exc:
            print(exc)
