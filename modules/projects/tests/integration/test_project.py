import pytest
from core.config import settings
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_projects_query(client: AsyncClient, projects):
    query = """
        query {
            projects {
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
    assert data.get("data", {}).get("projects")


@pytest.mark.asyncio
async def test_projects_mutation(client: AsyncClient):
    query = """
        mutation($names: [String!]!) {
            addProjects(names: $names) {
                id
                name
            }
        }
    """

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={"query": query, "variables": {"names": ["My Project"]}},
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    assert data.get("data", {}).get("addProjects")
    assert data["data"]["addProjects"][0]["name"] == "My Project"
