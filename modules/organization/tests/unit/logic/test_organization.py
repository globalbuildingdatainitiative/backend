import pytest

from logic import (
    get_organizations,
    create_organizations_mutation,
    update_organizations_mutation,
    delete_organizations_mutation,
)
from models import InputOrganization, CountryCodes


@pytest.mark.asyncio
async def test_get_organizations(organizations):
    """Tests retrieving all organizations"""

    fetched_organizations = await get_organizations()  # Assuming get_organization exists

    assert len(fetched_organizations) == len(organizations)
    for i, organization in enumerate(fetched_organizations):
        assert organization.id == organizations[i].id
        assert organization.name == organizations[i].name


@pytest.mark.asyncio
async def test_create_organizations(app, user, mock_update_user_metadata):
    """Tests creating a new organization"""

    name = "New Organization"
    address = "123 Main St"
    city = "New City"
    country = CountryCodes.USA

    organization_data = InputOrganization(name=name, address=address, city=city, country=country)

    created_organization = await create_organizations_mutation(organizations=[organization_data], current_user=user)

    assert created_organization[0].name == name
    assert created_organization[0].address == address
    assert created_organization[0].city == city
    assert created_organization[0].country == country


@pytest.mark.asyncio
async def test_update_organizations(organizations):
    """Tests updating an existing organization"""

    organization = organizations[0]
    new_name = "Updated Organization"
    new_address = "Updated Address"
    new_city = "Updated City"
    new_country = CountryCodes.PAK

    input_organization = InputOrganization(
        id=organization.id, name=new_name, address=new_address, city=new_city, country=new_country
    )
    updated_organizations = await update_organizations_mutation(organizations=[input_organization])

    updated_organization = updated_organizations[0]

    assert updated_organization.id == organization.id
    assert updated_organization.name == new_name
    assert updated_organization.address == new_address
    assert updated_organization.city == new_city
    assert updated_organization.country == new_country


@pytest.mark.asyncio
async def test_delete_organizations(organizations):
    """Tests deleting an existing organization"""

    organization = organizations[0]

    ids = [organization.id]

    # Call the function with the list of IDs
    deleted_ids = await delete_organizations_mutation(ids=ids)

    # Assert that at least one ID is returned (assuming successful deletion)
    assert deleted_ids and len(deleted_ids) >= 1  # Check for empty list and at least one element
