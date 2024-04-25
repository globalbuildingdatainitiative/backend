import pytest
from core.config import settings
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_contributions_query(client: AsyncClient, contributions):
    query = """
        query {
            contributions {
                id
                uploadedAt
                userId
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
    assert data.get("data", {}).get("contributions")


@pytest.mark.asyncio
async def test_add_contributions_mutation(client: AsyncClient):
    query = """
        mutation($contributions: [InputContribution!]!) {
            addContributions(contributions: $contributions) {
                id
                uploadedAt
                userId
            }
        }
    """

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={
            "query": query,
            "variables": {"contributions": [{"project": {"name": "Project 0"}}, {"project": {"name": "Project 1"}}]}
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    assert data.get("data", {}).get("addContributions")
    assert len(data.get("data", {}).get("addContributions")) == 2
