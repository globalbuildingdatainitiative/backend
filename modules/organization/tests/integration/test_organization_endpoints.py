import pytest
from httpx import AsyncClient

from core.config import settings
from logic import (
    create_organizations_mutation,
    update_organizations_mutation,
    delete_organizations_mutation,
    add_organization,
)
from models import InputOrganization, User


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
    address = "123 Main St"
    city = "New City"
    country = "USA"

    organization_data = InputOrganization(
        name=name, address=address, city=city, country=country
    )  # Create InputOrganization object

    # Create a list containing the organization data
    organizations_data = [organization_data]

    # Pass the list of InputOrganization objects to the mutation
    created_organization = await create_organizations_mutation(organizations=organizations_data)

    assert created_organization[0].name == name
    assert created_organization[0].address == address
    assert created_organization[0].city == city
    assert created_organization[0].country == country


@pytest.mark.asyncio
async def test_add_organization_mutation(mongo, client, organizations):
    """Tests adding a single organization"""

    name = "New Organization"
    address = "123 Main St"
    city = "New City"
    country = "USA"

    organization_data = InputOrganization(name=name, address=address, city=city, country=country)
    current_user: User = organizations[0]
    # Add the organization
    added_organization = await add_organization(organization=organization_data, current_user=current_user)

    assert added_organization.name == name
    assert added_organization.address == address
    assert added_organization.city == city
    assert added_organization.country == country
    assert added_organization.id == current_user._organization_id


@pytest.mark.asyncio
async def test_update_organizations_mutation(mongo, client, organizations):
    """Tests updating an existing organization"""

    organization = organizations[0]
    new_name = "Updated Organization"
    new_address = "Updated Address"
    new_city = "Updated City"
    new_country = "Updated Country"

    # Update the organization
    updated_organization = await update_organizations_mutation(
        [InputOrganization(id=organization.id, name=new_name, address=new_address, city=new_city, country=new_country)]
    )

    # Assert the organization is updated
    assert updated_organization[0].name == new_name
    assert updated_organization[0].address == new_address
    assert updated_organization[0].city == new_city
    assert updated_organization[0].country == new_country


@pytest.mark.asyncio
async def test_delete_organizations_mutation(mongo, client, organizations):
    """Tests deleting an existing organization"""

    organization = organizations[0]
    organization_id = organization.id

    # Delete the organization
    deleted_ids = await delete_organizations_mutation([organization_id])

    # Assert the organization is deleted
    assert organization_id in deleted_ids
