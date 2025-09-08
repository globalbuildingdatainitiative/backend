import asyncio
import time
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from models import GraphQLUser
from models.user import get_user_organization


@pytest.mark.performance
async def test_organization_resolution_latency():
    """Test that organization resolution completes within acceptable time"""
    # Given
    organization_id = uuid4()
    user = GraphQLUser(id=uuid4(), organizationId=organization_id)

    # Mock the get_organizations function to return quickly
    with patch("logic.get_organizations") as mock_get_organizations:
        mock_organization = AsyncMock()
        mock_organization.id = organization_id
        mock_organization.name = "Test Organization"
        mock_get_organizations.return_value = [mock_organization]

        # When
        start_time = time.perf_counter()
        result = await get_user_organization(user)
        end_time = time.perf_counter()

        latency = (end_time - start_time) * 1000  # Convert to milliseconds

        # Then
        assert result is not None
        assert result.id == organization_id
        assert latency < 100  # Should complete within 100ms


@pytest.mark.performance
async def test_concurrent_organization_access():
    """Test that concurrent organization access performs well"""
    # Given
    users = []
    organizations = []

    # Create 10 users and organizations
    for i in range(10):
        org_id = uuid4()
        user = GraphQLUser(id=uuid4(), organizationId=org_id)
        users.append(user)

        mock_org = AsyncMock()
        mock_org.id = org_id
        mock_org.name = f"Organization {i}"
        organizations.append(mock_org)

    # When
    start_time = time.perf_counter()

    # Execute concurrently
    tasks = []
    with patch("logic.get_organizations") as mock_get_organizations:
        for i, user in enumerate(users):
            mock_get_organizations.return_value = [organizations[i]]
            task = get_user_organization(user)
            tasks.append(task)

        results = await asyncio.gather(*tasks)

    end_time = time.perf_counter()
    total_time = (end_time - start_time) * 1000  # Convert to milliseconds

    # Then
    assert len(results) == 10
    assert all(result is not None for result in results)
    # Average time per request should be reasonable
    assert total_time / 10 < 50  # Average < 50ms per request


@pytest.mark.performance
async def test_high_volume_organization_resolution():
    """Test organization resolution under high volume"""
    # Given
    users = []

    # Create 100 users
    for i in range(100):
        org_id = uuid4()
        user = GraphQLUser(id=uuid4(), organizationId=org_id)
        users.append(user)

    # Mock organization
    mock_organization = AsyncMock()
    mock_organization.id = uuid4()
    mock_organization.name = "High Volume Org"

    # When
    start_time = time.perf_counter()

    successful_resolutions = 0
    with patch("logic.get_organizations") as mock_get_organizations:
        mock_get_organizations.return_value = [mock_organization]

        for user in users:
            try:
                result = await get_user_organization(user)
                if result is not None:
                    successful_resolutions += 1
            except Exception:
                pass  # Count failures separately if needed

    end_time = time.perf_counter()
    total_time = (end_time - start_time) * 1000  # Convert to milliseconds

    # Then
    assert successful_resolutions >= 95  # At least 95% success rate
    assert total_time < 5000  # Total time should be less than 5 seconds
