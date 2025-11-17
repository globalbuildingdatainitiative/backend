import pytest
from unittest.mock import AsyncMock
from uuid import UUID

from logic.user import filter_users
from models import GraphQLUser, FilterBy


@pytest.fixture
def mock_graphql_user():
    """Create a mock GraphQLUser for testing"""
    user = AsyncMock(spec=GraphQLUser)
    user.id = UUID("5c650110-2224-4bc7-8cd9-45617e97e712")
    user.email = "test@example.com"
    user.first_name = "Test"
    user.last_name = "User"
    return user


@pytest.mark.asyncio
async def test_apply_filter_by(mock_graphql_user):
    """Test _apply_additional_id_filters when filter_by is None"""
    gql_users = [AsyncMock()]

    result = filter_users(gql_users, None)

    # Should return the same list unchanged
    assert result == gql_users


@pytest.mark.asyncio
async def test_apply_filter_by_no_id_filter(mock_graphql_user):
    """Test _apply_filter_by when there's no ID filter"""
    gql_users = [mock_graphql_user]
    filter_by = FilterBy(equal={"email": "test@example.com"})

    result = filter_users(gql_users, filter_by)

    # Should return the same list unchanged
    assert result == gql_users


@pytest.mark.asyncio
async def test_apply_filter_by_single_id_filter(mock_graphql_user):
    """Test _apply_filter_by when there's only an ID filter (no additional filters)"""
    gql_users = [mock_graphql_user]
    filter_by = FilterBy(equal={"id": "5c650110-2224-4bc7-8cd9-45617e97e712"})

    result = filter_users(gql_users, filter_by)

    # Should return the same list unchanged
    assert result == gql_users
