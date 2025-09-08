import logging
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from models import GraphQLUser
from models.user import get_user_organization


@pytest.mark.asyncio
async def test_successful_organization_resolution(organizations, mock_db):
    """Test that user with valid organization ID resolves organization correctly"""
    # Given
    organization = organizations[0]
    user = GraphQLUser(id=uuid4(), organizationId=organization.id)

    # When
    result = await get_user_organization(user)

    # Then
    assert result is not None
    assert result.id == organization.id
    assert result.name == organization.name


@pytest.mark.asyncio
async def test_missing_organization_resolution(caplog, mock_db):
    """Test that user with missing organization ID returns None and logs warning"""
    # Given
    non_existent_org_id = uuid4()
    user = GraphQLUser(id=uuid4(), organizationId=non_existent_org_id)

    # Capture logs at warning level
    with caplog.at_level(logging.WARNING, logger="main"):
        with patch("logic.get_organizations", new_callable=AsyncMock) as mock_get_organizations:
            mock_get_organizations.return_value = []

            # When
            result = await get_user_organization(user)

            # Then
            assert result is None
            assert f"No organization found for user {user.id} with organizationId {non_existent_org_id}" in caplog.text


@pytest.mark.asyncio
async def test_none_organization_id(mock_db):
    """Test that user with None organization ID returns None"""
    # Given
    user = GraphQLUser(id=uuid4(), organizationId=None)

    # When
    result = await get_user_organization(user)

    # Then
    assert result is None


@pytest.mark.asyncio
async def test_user_without_organization_field(mock_db):
    """Test that user without organizationId field returns None"""
    # Given
    user = GraphQLUser(id=uuid4())

    # When
    result = await get_user_organization(user)

    # Then
    assert result is None
