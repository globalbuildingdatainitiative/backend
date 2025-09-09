import json
from uuid import uuid4

import pytest
from httpx import AsyncClient

from core.config import settings


@pytest.mark.asyncio
async def test_contributions_query(client: AsyncClient, contributions):
    query = """
        query {
            contributions {
                items {
                    id
                    project {
                        name
                    }
                    user {
                        id
                    }
                }
                count
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
    assert data.get("data", {}).get("contributions", {}).get("items")
    assert data.get("data", {}).get("contributions", {}).get("count")
    assert "user" in data["data"]["contributions"]["items"][0]


@pytest.mark.asyncio
async def test_add_contributions_mutation(client: AsyncClient, datafix_dir):
    query = """
        mutation($contributions: [InputContribution!]!) {
            addContributions(contributions: $contributions) {
                id
                uploadedAt
                user {
                  id
                }
            }
        }
    """
    input_project = json.loads((datafix_dir / "project.json").read_text())
    # Remove createdBy field if it exists (it should be set automatically by the backend)
    input_project.pop("createdBy", None)

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={
            "query": query,
            "variables": {"contributions": [{"project": input_project}]},
        },
    )

    assert response.status_code == 200
    data = response.json()

    if data.get("errors"):
        print("GraphQL errors:", data.get("errors"))

    assert not data.get("errors"), f"GraphQL errors: {data.get('errors')}"
    assert data.get("data", {}).get("addContributions")
    assert len(data.get("data", {}).get("addContributions")) == 1
    assert "user" in data["data"]["addContributions"][0]
    assert "id" in data["data"]["addContributions"][0]["user"]


@pytest.mark.asyncio
async def test_contributions_query_filter(client: AsyncClient, contributions):
    query = """
        query($id: UUID!) {
            contributions {
                items(filterBy: {equal: {organizationId: $id}}) {
                    id
                    organizationId
                    user {
                        id
                    }
                }
            }
        }
    """

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={"query": query, "variables": {"id": str(contributions[0].organization_id)}},
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    assert len(data.get("data", {}).get("contributions", {}).get("items")) == 3
    assert data.get("data", {}).get("contributions", {}).get("items", [])[0].get("organizationId") == str(
        contributions[0].organization_id
    )


@pytest.mark.asyncio
async def test_contributions_query_sort(client: AsyncClient, contributions):
    query = """
        query {
            contributions {
                items(sortBy: {asc: "uploadedAt"}) {
                    id
                    user {
                        id
                    }
                }
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
    assert data.get("data", {}).get("contributions", {}).get("items")

    expected_items = [
        contribution.model_dump(include={"id"}, mode="json")
        for contribution in sorted(contributions, key=lambda p: p.uploaded_at)
    ]

    actual_items = [{"id": item["id"]} for item in data.get("data", {}).get("contributions", {}).get("items", [])]

    assert actual_items == expected_items


@pytest.mark.asyncio
async def test_delete_contributions_mutation(client: AsyncClient, contributions):
    query = """
        mutation($contributions: [UUID!]!) {
            deleteContributions(contributions: $contributions)
        }
    """

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={
            "query": query,
            "variables": {"contributions": [str(contributions[0].id)]},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors"), f"GraphQL errors: {data.get('errors')}"
    assert data.get("data", {}).get("deleteContributions")
    assert len(data.get("data", {}).get("deleteContributions")) == 1


@pytest.mark.asyncio
async def test_update_contributions_mutation(client: AsyncClient, contributions):
    query = """
        mutation($contributions: [UpdateContribution!]!) {
            updateContributions(contributions: $contributions) {
                id
                public
            }
        }
    """

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={
            "query": query,
            "variables": {"contributions": [{"id": str(contributions[0].id), "public": True}]},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors"), f"GraphQL errors: {data.get('errors')}"
    assert data.get("data", {}).get("updateContributions")
    assert len(data.get("data", {}).get("updateContributions")) == 1

    assert data.get("data", {}).get("updateContributions")[0].get("public") is True
