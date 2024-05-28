import pytest
from httpx import AsyncClient

from core.config import settings


@pytest.mark.asyncio
async def test_users_query(client: AsyncClient, mock_get_users_newest_first, mock_get_user_metadata):
    query = """
        query {
            users {
                id
                email
                timeJoined
                firstName
                lastName
                organizationId
            }
        }
    """

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={
            "query": query,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    assert data.get("data", {}).get("users")

    for user in data["data"]["users"]:
        assert "id" in user
        assert "email" in user
        assert "timeJoined" in user
        assert "firstName" in user
        assert "lastName" in user
        assert "organizationId" in user
