import lcax
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
