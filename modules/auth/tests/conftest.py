import dataclasses
import json
from datetime import datetime
from typing import Iterator
from uuid import uuid4

import docker
import pytest
import supertokens_python.asyncio
import supertokens_python.recipe.session.asyncio
import supertokens_python.recipe.usermetadata.asyncio
import supertokens_python.recipe.emailpassword
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from fastapi.requests import Request
from httpx import AsyncClient

import core.auth
import core.context
import logic as logic
from core.config import settings
from models import SuperTokensUser, GraphQLUser, UserFilters, UserSort, InviteStatus, Role


@pytest.fixture(scope="session")
def docker_client():
    yield docker.from_env()


@pytest.fixture(scope="session")
def user() -> SuperTokensUser:
    _user = SuperTokensUser(id=uuid4(), organization_id=uuid4())
    yield _user


@pytest.fixture
def mock_update_email_or_password():
    async def fake_update_email_or_password(user_id: str, email: str, password: str):
        return

    return fake_update_email_or_password


@pytest.fixture
def mock_sign_in():
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

    return fake_sign_in


@pytest.fixture
def mock_update_user_metadata(users):
    async def fake_update_user_metadata(user_id: str, metadata: dict):
        for user in users:
            if user["id"] == user_id:
                if "first_name" in metadata:
                    user["firstName"] = metadata.get("first_name")
                if "last_name" in metadata:
                    user["lastName"] = metadata.get("last_name")
                if "email" in metadata:
                    user["email"] = metadata.get("email")
                if "invited" in metadata:
                    user["invited"] = metadata.get("invited")
                if "invite_status" in metadata:
                    user["invite_status"] = metadata.get("invite_status")
                if "inviter_name" in metadata:
                    user["inviter_name"] = metadata.get("inviter_name")
                if "role" in metadata:
                    user["role"] = metadata.get("role")

    return fake_update_user_metadata


@pytest.fixture()
def mock_supertokens(session_mocker, users, mock_sign_in, mock_update_email_or_password, mock_update_user_metadata):
    def fake_supertokens_init():
        pass

    def fake_supertoken_get_instance():
        class FakeUser:
            def __init__(self, user: dict):
                self._user = user

            def to_json(self):
                return {"user": self._user}

        class FakeUsers:
            @property
            def users(self):
                return [FakeUser(_user) for _user in users]

        class FakeRecipes:
            async def get_user_metadata(self, user_id, user_context):
                class FakeMetadata:
                    @property
                    def metadata(self):
                        return {
                            "first_name": "",
                            "last_name": "",
                            "email": "",
                            "organization_id": "",
                            "pending_organization_id": "",
                        }

                return FakeMetadata()

            async def update_user_metadata(self, user_id, _update, context):
                return await mock_update_user_metadata(user_id, _update)

            async def sign_in(self, email, password, tenant_id, user_context):
                return await mock_sign_in(email, password, tenant_id)

            async def update_email_or_password(self, user_id, email, password, *args):
                return await mock_update_email_or_password(user_id, email, password)

        class FakeSuperTokens:
            async def get_users(
                self, tenant_id, time_joined_order, limit, pagination_token, include_recipe_ids, query, user_context
            ):
                return FakeUsers()

            @property
            def recipe_implementation(self):
                return FakeRecipes()

        return FakeSuperTokens()

    session_mocker.patch.object(
        core.auth,
        "supertokens_init",
        fake_supertokens_init,
    )

    session_mocker.patch.object(
        supertokens_python.Supertokens,
        "get_instance",
        fake_supertoken_get_instance,
    )

    session_mocker.patch.object(
        supertokens_python.recipe.emailpassword.EmailPasswordRecipe,
        "get_instance",
        fake_supertoken_get_instance,
    )

    session_mocker.patch.object(
        supertokens_python.recipe.usermetadata.UserMetadataRecipe,
        "get_instance",
        fake_supertoken_get_instance,
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


@pytest.fixture()
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
            invited: bool
            invite_status: str
            inviter_name: str
            role: str

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
                        "invited": self.invited,
                        "invite_status": self.invite_status,
                        "inviter_name": self.inviter_name,
                        "role": self.role,
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
                    "invited": False,
                    "invite_status": InviteStatus.ACCEPTED.value,
                    "inviter_name": "",
                    "role": Role.MEMBER.value,
                }
                return FakeMetadata(metadata=metadata)

    session_mocker.patch.object(
        supertokens_python.recipe.usermetadata.asyncio,
        "get_user_metadata",
        fake_get_user_metadata,
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
                invited=user.get("invited", False),
                invite_status=InviteStatus(user.get("invite_status", InviteStatus.NONE.value)),
                inviter_name=user.get("inviter_name", ""),
                role=Role(user.get("role", Role.MEMBER.value)),
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
