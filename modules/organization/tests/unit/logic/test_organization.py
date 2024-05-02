import pytest

from backend.modules.organization.src.logic import get_organization, create_organization_mutation, update_organization_mutation, delete_organization_mutation


async def test_get_organization(organizations):
    """Tests retrieving all organizations"""

    fetched_organizations = await get_organization()  # Assuming get_organization exists

    assert len(fetched_organizations) == len(organizations)
    for i, organization in enumerate(fetched_organizations):
        assert organization.id == organizations[i].id
        assert organization.name == organizations[i].name


@pytest.mark.asyncio
async def test_create_organization(app):
    """Tests creating a new organization"""

    name = "New Organization"
    created_organization = await create_organization_mutation(name=name)  # Assuming create_organization_mutation exists

    assert created_organization.name == name



@pytest.mark.asyncio
async def test_update_organization(organizations):
    """Tests updating an existing organization"""

    organization = organizations[0]
    new_name = "Updated Organization"

    updated_organization = await update_organization_mutation(id=organization.id, name=new_name)  # Assuming update_organization_mutation exists

    assert updated_organization.id == organization.id
    assert updated_organization.name == new_name



@pytest.mark.asyncio
async def test_delete_organization(organizations):
    """Tests deleting an existing organization"""

    organization = organizations[0]

    deleted = await delete_organization_mutation(id=organization.id)  # Assuming delete_organization_mutation exists

    assert deleted is True
