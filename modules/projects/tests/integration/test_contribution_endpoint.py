import lcax
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


@pytest.mark.asyncio
async def test_add_contributions_mutation(client: AsyncClient, datafix_dir):
    query = """
        mutation($contributions: [InputContribution!]!) {
            addContributions(contributions: $contributions) {
                id
                uploadedAt
                userId
            }
        }
    """

    input_project = lcax.convert_lcabyg((datafix_dir / "project.json").read_text(), as_type=lcax.Project).model_dump(
        mode="json", by_alias=True
    )
    assemblies = []
    for assembly in input_project.get("assemblies").values():
        # del assembly["category"]
        assembly.update({"products": list(assembly.get("products").values())})
        assemblies.append(assembly)

    input_project.update({"assemblies": assemblies})
    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={
            "query": query,
            "variables": {"contributions": [{"project": input_project}]},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    assert data.get("data", {}).get("addContributions")
    assert len(data.get("data", {}).get("addContributions")) == 1


@pytest.mark.asyncio
async def test_contributions_query_filter(client: AsyncClient, contributions):
    query = """
        query($id: UUID!) {
            contributions {
                items(filterBy: {equal: {organizationId: $id}}) {
                    id
                    organizationId
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
    assert data.get("data", {}).get("contributions", {}).get("items", []) == [
        contribution.model_dump(include={"id"}, mode="json")
        for contribution in sorted(contributions, key=lambda p: p.uploaded_at)
    ]
