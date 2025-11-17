import json
from pathlib import Path
from typing import AsyncGenerator
from uuid import uuid4, UUID
import os

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

from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, text

from logic.roles import assign_role
from models import SuperTokensUser, Role, InviteStatus
from core.cache import get_user_cache


@pytest.fixture(scope="session")
def docker_client():
    yield docker.from_env()


@pytest.fixture(scope="session")
def postgres_db(docker_client):
    """Spin up a test PostgreSQL database WITHOUT running migrations yet"""
    # Clean up any existing test containers
    try:
        _container = docker_client.containers.get("postgres_auth_test")
        _container.kill()
        sleep(0.2)
    except NotFound:
        pass

    db_user = os.getenv("POSTGRES_USER")
    db_password = os.getenv("POSTGRES_PASSWORD")
    db_name = os.getenv("POSTGRES_DB")

    container_port = 5432  # Default PostgreSQL port
    host_port = os.getenv("POSTGRES_PORT")
    db_hostname = os.getenv("POSTGRES_HOST")

    container = docker_client.containers.run(
        image="postgres:15",
        environment={
            "POSTGRES_USER": db_user,
            "POSTGRES_PASSWORD": db_password,
            "POSTGRES_DB": db_name,
        },
        ports={container_port: host_port},
        name="postgres_auth_test",
        detach=True,
        auto_remove=True,
    )

    test_db_url = f"postgresql://{db_user}:{db_password}@{db_hostname}:{host_port}/{db_name}"

    # Wait for PostgreSQL to be ready
    @retry(
        stop=stop_after_attempt(30),
        wait=wait_fixed(0.5),
        retry=retry_if_exception(lambda e: isinstance(e, Exception)),
    )
    def wait_for_postgres():
        engine = create_engine(test_db_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine.dispose()
        return True

    wait_for_postgres()

    try:
        yield {
            "container": container,
            "url": test_db_url,
            "host_port": host_port,
            "container_port": container_port,
            "user": db_user,
            "password": db_password,
            "database": db_name,
        }
    finally:
        container.stop()


@pytest.fixture(scope="session")
async def supertokens(docker_client, postgres_db):
    # Clean up any existing containers with conflicting names
    for container_name in ["supertokens", "supertokens_auth"]:
        try:
            _container = docker_client.containers.get(container_name)
            _container.kill()
            sleep(0.2)
        except NotFound:
            pass

    # Use the postgres_db fixture info
    postgres_url = f"postgresql://{postgres_db['user']}:{postgres_db['password']}@host.docker.internal:{postgres_db['host_port']}/{postgres_db['database']}"

    container = docker_client.containers.run(
        image="registry.supertokens.io/supertokens/supertokens-postgresql:10.1",
        ports={"3567": "3568"},
        extra_hosts={"host.docker.internal": "host-gateway"},
        environment={
            "POSTGRESQL_CONNECTION_URI": postgres_url,
        },
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
        # Import settings here, after env vars are set
        from core.config import settings

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
def run_migrations(supertokens, postgres_db):
    """Run Alembic migrations AFTER SuperTokens has initialized"""

    # Run Alembic migrations using Python API
    auth_module_root = Path(__file__).parent.parent
    alembic_cfg = Config(str(auth_module_root / "alembic.ini"))
    alembic_cfg.set_main_option("sqlalchemy.url", postgres_db["url"])

    # Run migrations
    command.upgrade(alembic_cfg, "head")

    yield

    # Optional: downgrade migrations before cleanup
    try:
        command.downgrade(alembic_cfg, "base")
    except Exception:
        pass  # Ignore errors during cleanup


@pytest.fixture(scope="session", autouse=True)
def set_test_environment(postgres_db):
    """Set environment variables BEFORE any application code is imported"""
    # Override BOTH database URLs for tests
    os.environ["DATABASE_URL"] = postgres_db["url"]

    yield

    # Cleanup (optional)
    del os.environ["DATABASE_URL"]


@pytest.fixture(scope="session")
async def app(supertokens, postgres_db, run_migrations, set_test_environment) -> FastAPI:
    # Now import the app AFTER environment variables are set
    from main import app

    @app.get("/login/{user_id}")
    async def login(request: Request, user_id: str):  # type: ignore
        res = await create_new_session(request, "public", RecipeUserId(user_id), {}, {})
        return {"token": res.access_token}

    async with LifespanManager(app):
        yield app


@pytest.fixture()
async def create_user_old(app) -> SuperTokensUser:
    response = await sign_up("public", "my@email.com", "currentPassword123")
    await get_user_cache().load_all()
    # should be a call to create_user from logic.users but avoiding circular import
    yield SuperTokensUser(id=UUID(response.user.id), organization_id=uuid4())

    await delete_user(response.user.id)
    await get_user_cache().remove_user(UUID(response.user.id))


@pytest.fixture()
async def create_user(app) -> SuperTokensUser:
    """Create a regular user using sign_up and update_user_metadata"""
    # For test fixtures, we still use sign_up directly since we need a clean user
    # without invitation flow complexity
    response = await sign_up("public", "my@email.com", "currentPassword123")
    user_id = response.user.id
    org_id = uuid4()

    # Set metadata directly via update_user_metadata (like users fixture)
    await update_user_metadata(
        user_id,
        {
            "first_name": "Test",
            "last_name": "User",
            "organization_id": str(org_id),
            "invited": False,
            "invite_status": InviteStatus.ACCEPTED.value,
        },
    )

    # Reload cache
    user_cache = get_user_cache()
    await user_cache.reload_user(UUID(user_id))
    final_user = await user_cache.get_user(UUID(user_id))

    yield SuperTokensUser(id=final_user.id, organization_id=final_user.organization_id)

    await delete_user(str(user_id))
    await get_user_cache().remove_user(UUID(user_id))


@pytest.fixture
async def create_admin_user_old(app) -> SuperTokensUser:
    response = await sign_up("public", "admin@email.com", "currentPassword123")
    _user = SuperTokensUser(id=UUID(response.user.id), organization_id=uuid4())
    await assign_role(_user.id, Role.ADMIN)

    yield _user

    await delete_user(str(_user.id))
    await get_user_cache().remove_user(_user.id)


@pytest.fixture
async def create_admin_user(app) -> SuperTokensUser:
    """Create an admin user using sign_up and update_user_metadata"""

    # Create user via sign_up
    response = await sign_up("public", "admin@email.com", "adminPassword123")
    user_id = UUID(response.user.id)
    org_id = uuid4()

    # Set metadata directly via update_user_metadata (like users fixture)
    await update_user_metadata(
        str(user_id),
        {
            "first_name": "Admin",
            "last_name": "User",
            "organization_id": str(org_id),
            "invited": False,
            "invite_status": InviteStatus.ACCEPTED.value,
        },
    )

    # Assign admin role
    await assign_role(user_id, Role.ADMIN)

    # Reload cache
    user_cache = get_user_cache()
    await user_cache.reload_user(user_id)
    final_user = await user_cache.get_user(user_id)

    yield SuperTokensUser(id=final_user.id, organization_id=final_user.organization_id)

    await delete_user(str(user_id))
    await get_user_cache().remove_user(user_id)


@pytest.fixture()
async def client_admin(app: FastAPI, client_unauthenticated, create_admin_user) -> AsyncGenerator[AsyncClient, None]:
    """Async server client that handles lifespan and teardown"""

    response = await client_unauthenticated.get(f"/login/{create_admin_user.id}")
    response.raise_for_status()

    client_unauthenticated.headers["Authorization"] = f"Bearer {response.json()['token']}"
    yield client_unauthenticated


@pytest.fixture()
async def client(app: FastAPI, client_unauthenticated, create_user) -> AsyncGenerator[AsyncClient, None]:
    """Async server client that handles lifespan and teardown"""

    response = await client_unauthenticated.get(f"/login/{create_user.id}")
    response.raise_for_status()

    client_unauthenticated.headers["Authorization"] = f"Bearer {response.json()['token']}"
    yield client_unauthenticated


@pytest.fixture()
async def client_user(app: FastAPI, client_unauthenticated, users) -> AsyncGenerator[AsyncClient, None]:
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
    user_cache = get_user_cache()
    await user_cache.load_all()
    _temp_users = await user_cache.get_all_users()
    yield users

    # Clean up created users
    for user_id in created_users:
        try:
            await delete_user(user_id)
        except Exception:
            pass  # Ignore errors during cleanup
    await user_cache.clear_cache()


@pytest.fixture()
async def client_unauthenticated(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Async server client that handles lifespan and teardown"""

    from core.config import settings

    async with AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url=str(settings.SERVER_HOST),
    ) as _client:
        try:
            yield _client
        except Exception as exc:
            print(exc)
