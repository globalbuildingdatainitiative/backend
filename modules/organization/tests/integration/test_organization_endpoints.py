import pytest
from backend.modules.organization.src.core.config import settings
from backend.modules.organization.src.models import DBOrganization
from httpx import AsyncClient
from backend.modules.organization.src.schema.organization import (create_organization_mutation,
                                                                  update_organization_mutation,
                                                                  delete_organization_mutation)


@pytest.mark.asyncio
async def test_organization_query(client: AsyncClient, organizations):
    query = """
        query {
            organizations {
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
async def test_create_organization_mutation(mongo, client):
    """Tests creating a new organization"""

    name = "New Organization"
    query = """
        mutation($name: String!) {
            createOrganization(name: $name) {
                id
                name
            }
        }
    """

    variables = {"name": name}
    response = await client.post(
        f"{settings.API_STR}/graphql", json={"query": query, "variables": variables}
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    assert data.get("data", {}).get("createOrganization")
    created_organization = data.get("data", {}).get("createOrganization")
    assert created_organization.get("name") == name

    # Optional: Verify organization is inserted in database (you'll need to fetch it)
    organization = await DBOrganization.get(id=created_organization.get("id"))
    assert organization is not None
    assert organization.name == name


@pytest.mark.asyncio
async def test_update_organization_mutation(mongo, organizations, client):
    """Tests updating an existing organization"""

    organization = organizations[0]
    new_name = "Updated Organization"

    query = """
        mutation($id: UUID!, $name: String!) {
            updateOrganization(id: $id, name: $name) {
                id
                name
            }
        }
    """

    variables = {"id": str(organization.id), "name": new_name}
    response = await client.post(
        f"{settings.API_STR}/graphql", json={"query": query, "variables": variables}
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    assert data.get("data", {}).get("updateOrganization")
    updated_organization = data.get("data", {}).get("updateOrganization")
    assert updated_organization.get("id") == str(organization.id)
    assert updated_organization.get("name") == new_name

    # Optional: Verify organization is updated in database (you'll need to fetch it)
    updated_organization = await DBOrganization.get(id=organization.id)
    assert updated_organization.name == new_name


@pytest.mark.asyncio
async def test_delete_organization_mutation(mongo, organizations, client):
    """Tests deleting an existing organization"""

    organization = organizations[0]

    query = """
        mutation($id: UUID!) {
            deleteOrganization(id: $id)
        }
    """

    variables = {"id": str(organization.id)}
    response = await client.post(
        f"{settings.API_STR}/graphql", json={"query": query, "variables": variables}
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    assert data.get("data", {}).get("deleteOrganization") is True

    # Optional: Verify organization is deleted from database (you'll need to check its existence)
    organization = await DBOrganization.get(id=organization.id)
    assert organization is None
