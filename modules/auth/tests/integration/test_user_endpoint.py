import pytest
from httpx import AsyncClient

from core.config import settings


@pytest.mark.asyncio
async def test_users_query(client: AsyncClient, mock_get_users_newest_first):
    query = """
        query {
            users {
                id
                email
                timeJoined
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
