import pytest

from logic import (
    get_organizations,
    create_organizations_mutation,
    update_organizations_mutation,
    delete_organizations_mutation,
)
from models import InputOrganization


@pytest.mark.asyncio
async def test_get_organizations(organizations):
    """Tests retrieving all organizations"""

    fetched_organizations = await get_organizations()  # Assuming get_organization exists

    assert len(fetched_organizations) == len(organizations)
    for i, organization in enumerate(fetched_organizations):
        assert organization.id == organizations[i].id
        assert organization.name == organizations[i].name


@pytest.mark.asyncio
async def test_create_organizations(organizations):
    """Tests creating a new organization"""

    name = "New Organization"
    organization_data = InputOrganization(name=name)  # Create InputOrganization object

    created_organization = await create_organizations_mutation(
        organizations=[organization_data],  # Pass list of InputOrganization objects
    )

    assert created_organization[0].name == name


@pytest.mark.asyncio
async def test_update_organizations(organizations):
    """Tests updating an existing organization"""

    organization = organizations[0]
    new_name = "Updated Organization"

    input_organization = InputOrganization(id=organization.id, name=new_name)
    updated_organizations = await update_organizations_mutation(
        organizations=[input_organization]
    )  # Assuming update_organization_mutation exists
    updated_organization = updated_organizations[0]
    assert updated_organization.id == organization.id
    assert updated_organization.name == new_name


@pytest.mark.asyncio
async def test_delete_organizations(organizations):
    """Tests deleting an existing organization"""

    organization = organizations[0]

    ids = [organization.id]

    # Call the function with the list of IDs
    deleted_ids = await delete_organizations_mutation(ids=ids)

    # Assert that at least one ID is returned (assuming successful deletion)
    assert deleted_ids and len(deleted_ids) >= 1  # Check for empty list and at least one element
