import pytest
from httpx import AsyncClient

from core.config import settings


@pytest.mark.asyncio
async def test_item_query(client: AsyncClient, items):
    query = """
        query {
            items {
                id
                name
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
    assert data.get("data", {}).get("items")


@pytest.mark.asyncio
async def test_item_mutation(client: AsyncClient):
    query = """
        mutation($name: String!) {
            addItem(name: $name) {
                id
                name
            }
        }
    """

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={"query": query, "variables": {"name": "My Item"}},
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    assert data.get("data", {}).get("addItem")
    assert data["data"]["addItem"]["name"] == "My Item"
