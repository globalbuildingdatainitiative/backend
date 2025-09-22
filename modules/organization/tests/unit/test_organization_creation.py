import logging
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from logic.organization import create_organizations_mutation
from models import (
    InputOrganization,
    InputOrganizationMetaData,
    SuperTokensUser,
    CountryCodes,
    StakeholderEnum,
)


@pytest.mark.asyncio
async def test_valid_organization_creation(mock_db, mock_update_user_metadata):
    """Test that valid organization data creates an organization successfully"""
    # Given
    organization_data = InputOrganization(
        name="Test Organization",
        address="123 Test Street",
        city="Test City",
        country=CountryCodes.CHE,  # Switzerland
        meta_data=InputOrganizationMetaData(stakeholders=[StakeholderEnum.BUILDING_DATA_OWNERS]),
    )

    current_user = SuperTokensUser(id=uuid4(), organization_id=None)

    # When
    with (
        patch("logic.organization.assign_role") as mock_assign_role,
    ):
        result = await create_organizations_mutation([organization_data], current_user)

        # Then
        assert len(result) == 1
        assert result[0].name == "Test Organization"
        assert result[0].address == "123 Test Street"
        assert result[0].city == "Test City"
        assert result[0].country == CountryCodes.CHE
        assert isinstance(result[0].id, uuid4().__class__)

        # Verify that user metadata was updated
        mock_assign_role.assert_called_once()


@pytest.mark.asyncio
async def test_organization_creation_with_verification(caplog, mock_db):
    """Test that organization creation includes verification step"""
    # Given
    organization_data = InputOrganization(
        name="Test Organization",
        address="123 Test Street",
        city="Test City",
        country=CountryCodes.CHE,
        meta_data=InputOrganizationMetaData(stakeholders=[StakeholderEnum.BUILDING_DATA_OWNERS]),
    )

    current_user = SuperTokensUser(id=uuid4(), organization_id=None)

    # Capture logs at warning level
    with caplog.at_level(logging.WARNING):
        with (
            patch("supertokens_python.recipe.usermetadata.asyncio.update_user_metadata"),
            patch("logic.organization.assign_role"),
            patch("models.DBOrganization.get", new_callable=AsyncMock) as mock_get,
        ):
            # Mock the verification to return a valid organization
            mock_organization = AsyncMock()
            mock_organization.id = uuid4()
            mock_get.return_value = mock_organization

            # When
            result = await create_organizations_mutation([organization_data], current_user)

            # Then
            assert len(result) == 1
            # Verify that the get method was called for verification
            mock_get.assert_called_once_with(result[0].id)
            # No warning should be logged for successful verification
            assert "was not immediately queryable after insertion" not in caplog.text


@pytest.mark.asyncio
async def test_organization_creation_verification_warning(caplog, mock_db):
    """Test that organization creation logs warning when verification fails"""
    # Given
    organization_data = InputOrganization(
        name="Test Organization",
        address="123 Test Street",
        city="Test City",
        country=CountryCodes.CHE,
        meta_data=InputOrganizationMetaData(stakeholders=[StakeholderEnum.BUILDING_DATA_OWNERS]),
    )

    current_user = SuperTokensUser(id=uuid4(), organization_id=None)

    # Capture logs at warning level
    with caplog.at_level(logging.WARNING, logger="main"):
        with (
            patch("supertokens_python.recipe.usermetadata.asyncio.update_user_metadata"),
            patch("logic.organization.assign_role"),
            patch("models.DBOrganization.get", new_callable=AsyncMock) as mock_get,
        ):
            # Mock the verification to return None (simulating timing issue)
            mock_get.return_value = None

            # When
            result = await create_organizations_mutation([organization_data], current_user)

            # Then
            assert len(result) == 1
            # Verify that warning is logged for failed verification
            assert "was not immediately queryable after insertion" in caplog.text


@pytest.mark.asyncio
async def test_organization_creation_verification_exception(caplog, mock_db):
    """Test that organization creation handles verification exceptions"""
    # Given
    organization_data = InputOrganization(
        name="Test Organization",
        address="123 Test Street",
        city="Test City",
        country=CountryCodes.CHE,
        meta_data=InputOrganizationMetaData(stakeholders=[StakeholderEnum.BUILDING_DATA_OWNERS]),
    )

    current_user = SuperTokensUser(id=uuid4(), organization_id=None)

    # Capture logs at warning level
    with caplog.at_level(logging.WARNING, logger="main"):
        with (
            patch("supertokens_python.recipe.usermetadata.asyncio.update_user_metadata"),
            patch("logic.organization.assign_role"),
            patch("models.DBOrganization.get", new_callable=AsyncMock) as mock_get,
        ):
            # Mock the verification to raise an exception
            mock_get.side_effect = Exception("Database connection failed")

            # When
            result = await create_organizations_mutation([organization_data], current_user)

            # Then
            assert len(result) == 1
            # Verify that warning is logged for verification exception
            assert "Error verifying organization" in caplog.text


@pytest.mark.asyncio
async def test_multiple_organizations_creation(mock_db, mock_update_user_metadata):
    """Test that multiple organizations can be created at once"""
    # Given
    org_data_1 = InputOrganization(
        name="Test Organization 1",
        address="123 Test Street",
        city="Test City 1",
        country=CountryCodes.CHE,
        meta_data=InputOrganizationMetaData(stakeholders=[StakeholderEnum.BUILDING_DATA_OWNERS]),
    )

    org_data_2 = InputOrganization(
        name="Test Organization 2",
        address="456 Test Avenue",
        city="Test City 2",
        country=CountryCodes.USA,
        meta_data=InputOrganizationMetaData(stakeholders=[StakeholderEnum.DESIGN_PROFESSIONALS]),
    )

    current_user = SuperTokensUser(id=uuid4(), organization_id=None)

    # When
    with (
        patch("logic.organization.assign_role") as mock_assign_role,
    ):
        result = await create_organizations_mutation([org_data_1, org_data_2], current_user)

        # Then
        assert len(result) == 2
        assert result[0].name == "Test Organization 1"
        assert result[1].name == "Test Organization 2"

        # Verify that user metadata was updated with the first organization ID
        mock_assign_role.assert_called_once()
