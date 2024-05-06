import pytest
from httpx import AsyncClient

from core.config import settings
from logic import create_organizations_mutation, update_organizations_mutation, delete_organizations_mutation
from models import InputOrganization


@pytest.mark.asyncio
async def test_organizations_query(client: AsyncClient, organizations):
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
    assert data.get("data", {}).get("organizations")


@pytest.mark.asyncio
async def test_create_organizations_mutation(mongo, client, organizations):
    """Tests creating a new organization"""

    name = "New Organization"
    organization_data = InputOrganization(name=name)  # Create InputOrganization object

    # Create a list containing the organization data
    organizations_data = [organization_data]

    # Pass the list of InputOrganization objects to the mutation
    created_organization = await create_organizations_mutation(organizations=organizations_data)

    assert created_organization[0].name == name


@pytest.mark.asyncio
async def test_update_organizations_mutation(mongo, client, organizations):
    """Tests updating an existing organization"""

    organization = organizations[0]
    new_name = "Updated Organization"

    # Update the organization
    updated_organization = await update_organizations_mutation([InputOrganization(id=organization.id, name=new_name)])

    # Assert the organization is updated
    assert updated_organization[0].name == new_name


@pytest.mark.asyncio
async def test_delete_organizations_mutation(mongo, client, organizations):
    """Tests deleting an existing organization"""

    organization = organizations[0]
    organization_id = organization.id

    # Delete the organization
    deleted_ids = await delete_organizations_mutation([organization_id])

    # Assert the organization is deleted
    assert organization_id in deleted_ids
