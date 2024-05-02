import pytest

from logic import get_organizations, create_organizations_mutation, \
    update_organizations_mutation, delete_organizations_mutation


async def test_get_organizations(organizations):
    """Tests retrieving all organizations"""

    fetched_organizations = await get_organizations()  # Assuming get_organization exists

    assert len(fetched_organizations) == len(organizations)
    for i, organization in enumerate(fetched_organizations):
        assert organization.id == organizations[i].id
        assert organization.name == organizations[i].name


@pytest.mark.asyncio
async def test_create_organizations(app):
    """Tests creating a new organization"""

    name = "New Organization"
    created_organization = await create_organizations_mutation(
        name=name)  # Assuming create_organization_mutation exists

    assert created_organization.name == name


@pytest.mark.asyncio
async def test_update_organizations(organizations):
    """Tests updating an existing organization"""

    organization = organizations[0]
    new_name = "Updated Organization"

    updated_organization = await update_organizations_mutation(id=organization.id,
                                                               name=new_name)  # Assuming update_organization_mutation exists

    assert updated_organization.id == organization.id
    assert updated_organization.name == new_name


@pytest.mark.asyncio
async def test_delete_organizations(organizations):
    """Tests deleting an existing organization"""

    organization = organizations[0]

    deleted = await delete_organizations_mutation(id=organization.id)  # Assuming delete_organization_mutation exists

    assert deleted is True
