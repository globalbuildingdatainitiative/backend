from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from core.exceptions import MicroServiceResponseError
from logic.federation import get_auth_user
from logic.organization import create_organizations_mutation
from models import (
    GraphQLUser,
    InputOrganization,
    InputOrganizationMetaData,
    SuperTokensUser,
    CountryCodes,
    StakeholderEnum,
)
from models.user import get_user_organization


@pytest.mark.integration
async def test_end_to_end_user_organization_flow(mock_update_user_metadata):
    """Test the complete flow from organization creation to user profile retrieval"""
    # Given
    organization_data = InputOrganization(
        name="Integration Test Org",
        address="123 Integration St",
        city="Test City",
        country=CountryCodes.CHE,
        meta_data=InputOrganizationMetaData(stakeholders=[StakeholderEnum.BUILDING_DATA_OWNERS]),
    )

    user_id = uuid4()
    current_user = SuperTokensUser(id=user_id, organization_id=None)

    # When - Create organization
    with (
        patch("supertokens_python.recipe.usermetadata.asyncio.update_user_metadata"),
        patch("logic.organization.assign_role"),
        patch("logic.organization.Role") as mock_role,
        patch("logic.organization.DBOrganization") as mock_db_org_class,
    ):
        # Mock the Role enum
        mock_role.OWNER.value = "owner"

        # Mock the database operations
        mock_db_org_instance = AsyncMock()
        mock_db_org_instance.id = uuid4()
        mock_db_org_instance.name = organization_data.name
        mock_db_org_instance.address = organization_data.address
        mock_db_org_instance.city = organization_data.city
        mock_db_org_instance.country = organization_data.country
        mock_db_org_instance.meta_data = organization_data.meta_data

        # Mock the constructor to return our instance
        mock_db_org_class.return_value = mock_db_org_instance

        # Mock the insert method to do nothing (successful insertion)
        mock_db_org_instance.insert = AsyncMock()

        # Mock the get method to return our instance (verification step)
        mock_db_org_class.get = AsyncMock(return_value=mock_db_org_instance)

        organizations = await create_organizations_mutation([organization_data], current_user)
        created_org = organizations[0]

        # Then - Verify organization was created
        assert len(organizations) == 1
        assert organizations[0].name == "Integration Test Org"

        # When - Simulate user profile retrieval
        user = GraphQLUser(id=user_id, organizationId=created_org.id)

        # Mock the get_organizations function to return our created organization
        with patch("logic.get_organizations") as mock_get_organizations:
            mock_get_organizations.return_value = [created_org]

            user_organization = await get_user_organization(user)

            # Then - Verify organization is resolved correctly
            assert user_organization is not None
            assert user_organization.id == created_org.id
            assert user_organization.name == "Integration Test Org"


@pytest.mark.integration
async def test_user_profile_with_missing_organization():
    """Test user profile retrieval when organization doesn't exist"""
    # Given
    user_id = uuid4()
    non_existent_org_id = uuid4()

    user = GraphQLUser(id=user_id, organizationId=non_existent_org_id)

    # When - Simulate user profile retrieval with missing organization
    with patch("logic.get_organizations") as mock_get_organizations:
        # Mock to return empty list (organization not found)
        mock_get_organizations.return_value = []

        user_organization = await get_user_organization(user)

        # Then - Verify None is returned
        assert user_organization is None


@pytest.mark.integration
async def test_federation_user_retrieval_success():
    """Test successful user retrieval through federation"""
    # Given
    user_id = uuid4()

    mock_response_data = {"data": {"users": {"items": [{"id": str(user_id), "organizationId": str(uuid4())}]}}}

    # When
    with patch("logic.federation.create_jwt", return_value="mock_jwt"), patch("httpx.AsyncClient") as mock_client:
        # Mock the HTTP client response
        mock_instance = mock_client.return_value.__aenter__.return_value
        mock_instance.post = AsyncMock(return_value=AsyncMock(is_error=False, json=lambda: mock_response_data))

        user_data = await get_auth_user(user_id)

        # Then
        assert user_data["id"] == str(user_id)
        assert "organizationId" in user_data


@pytest.mark.integration
async def test_federation_user_retrieval_failure():
    """Test failed user retrieval through federation"""
    # Given
    user_id = uuid4()

    mock_response_data = {
        "data": {
            "users": {
                "items": []  # Empty items list
            }
        }
    }

    # When / Then
    with patch("logic.federation.create_jwt", return_value="mock_jwt"), patch("httpx.AsyncClient") as mock_client:
        # Mock the HTTP client response
        mock_instance = mock_client.return_value.__aenter__.return_value
        mock_instance.post = AsyncMock(return_value=AsyncMock(is_error=False, json=lambda: mock_response_data))

        with pytest.raises(MicroServiceResponseError):
            await get_auth_user(user_id)
