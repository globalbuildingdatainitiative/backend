import pytest
from httpx import AsyncClient

from core.config import settings


@pytest.mark.asyncio
async def test_admin_make_admin(client_admin: AsyncClient, users):
    mutation = """
        mutation($userId: String!) {
            makeAdmin(userId: $userId)
        }
    """

    response = await client_admin.post(
        f"{settings.API_STR}/graphql",
        json={"query": mutation, "variables": {"userId": users[0].get("id")}},
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    user = data.get("data", {}).get("makeAdmin")
    assert user


@pytest.mark.asyncio
async def test_make_admin(client: AsyncClient, users):
    mutation = """
        mutation($userId: String!) {
            makeAdmin(userId: $userId)
        }
    """

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={"query": mutation, "variables": {"userId": users[0].get("id")}},
    )

    assert response.status_code == 200
    data = response.json()

    assert data.get("errors")[0].get("message") == "User is not an admin"


@pytest.mark.asyncio
async def test_get_roles(client: AsyncClient):
    query = """
        query {
            roles {
                name
                permissions
            }
        }
    """

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={"query": query},
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    roles = data.get("data", {}).get("roles")
    assert roles
