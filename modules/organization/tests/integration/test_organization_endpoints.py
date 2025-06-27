import pytest
from httpx import AsyncClient

from core.config import settings
from models import StakeholderEnum, CountryCodes


@pytest.mark.asyncio
async def test_organizations_query(client: AsyncClient, organizations):
    query = """
        query {
            organizations {
                items {
                    id
                    name
                    metaData {
                        stakeholders
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
    _organizations = data.get("data", {}).get("organizations", {}).get("items")
    assert _organizations
    assert all("metaData" in org and "stakeholders" in org["metaData"] for org in _organizations)


@pytest.mark.asyncio
async def test_create_organizations_mutation(client: AsyncClient, mock_update_user_metadata):
    """Tests creating a new organization"""

    name = "New Organization"
    address = "123 Main St"
    city = "New City"
    country = CountryCodes.USA.value
    stakeholders = [StakeholderEnum.BUILDING_USERS.name, StakeholderEnum.CIVIL_SOCIETY.name]

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={
            "query": """
                    mutation($organizations: [InputOrganization!]!) {
                        createOrganizations(organizations: $organizations) {
                            id
                            name
                            address
                            city
                            country
                            metaData {
                                stakeholders
                            }
                        }
                    }
                """,
            "variables": {
                "organizations": [
                    {
                        "name": name,
                        "address": address,
                        "city": city,
                        "country": country,
                        "metaData": {"stakeholders": stakeholders},
                    }
                ]
            },
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert not data.get("errors")
    assert data.get("data", {}).get("createOrganizations")

    # Verify the created organization
    created_organization_data = data["data"]["createOrganizations"][0]
    assert created_organization_data["name"] == name
    assert created_organization_data["address"] == address
    assert created_organization_data["city"] == city
    assert created_organization_data["country"] == country
    assert created_organization_data["metaData"]["stakeholders"] == stakeholders


@pytest.mark.asyncio
async def test_update_organizations_mutation(client: AsyncClient, organizations):
    """Tests updating an existing organization"""

    organization = organizations[0]
    new_name = "Updated Organization"
    new_address = "Updated Address"
    new_city = "Updated City"
    new_country = CountryCodes.PAK.value
    new_stakeholders = [StakeholderEnum.CONSTRUCTION_COMPANIES.name, StakeholderEnum.FACILITY_MANAGERS.name]

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={
            "query": """
                    mutation($organizations: [InputOrganization!]!) {
                        updateOrganizations(organizations: $organizations) {
                            id
                            name
                            address
                            city
                            country
                            metaData {
                                stakeholders
                            }
                        }
                    }
                """,
            "variables": {
                "organizations": [
                    {
                        "id": str(organization.id),
                        "name": new_name,
                        "address": new_address,
                        "city": new_city,
                        "country": new_country,
                        "metaData": {"stakeholders": new_stakeholders},
                    }
                ]
            },
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert not data.get("errors")
    assert data.get("data", {}).get("updateOrganizations")

    # Verify the updated organization
    updated_organization_data = data["data"]["updateOrganizations"][0]
    assert updated_organization_data["name"] == new_name
    assert updated_organization_data["address"] == new_address
    assert updated_organization_data["city"] == new_city
    assert updated_organization_data["country"] == new_country
    assert updated_organization_data["metaData"]["stakeholders"] == new_stakeholders


@pytest.mark.asyncio
async def test_delete_organizations_mutation(client: AsyncClient, organizations):
    """Tests deleting an existing organization"""

    organization = organizations[0]
    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={
            "query": """
                    mutation($ids: [UUID!]!) {
                        deleteOrganizations(ids: $ids)
                    }
                """,
            "variables": {"ids": [str(organization.id)]},
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert not data.get("errors")
    assert data.get("data", {}).get("deleteOrganizations")

    # Verify the deleted organization ID
    deleted_organization_id = data["data"]["deleteOrganizations"][0]
    assert str(organization.id) == deleted_organization_id
