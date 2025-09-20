import pytest
from unittest.mock import AsyncMock, patch
from uuid import UUID

# from logic.user import _apply_additional_id_filters
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
async def test_apply_additional_id_filters_no_filter_by():
    """Test _apply_additional_id_filters when filter_by is None"""
    gql_users = [AsyncMock()]

    result = await _apply_additional_id_filters(gql_users, None)

    # Should return the same list unchanged
    assert result == gql_users


@pytest.mark.asyncio
async def test_apply_additional_id_filters_no_id_filter():
    """Test _apply_additional_id_filters when there's no ID filter"""
    gql_users = [AsyncMock()]
    filter_by = FilterBy(equal={"email": "test@example.com"})

    result = await _apply_additional_id_filters(gql_users, filter_by)

    # Should return the same list unchanged
    assert result == gql_users


# @pytest.mark.asyncio
# async def test_apply_additional_id_filters_single_id_filter():
#     """Test _apply_additional_id_filters when there's only an ID filter (no additional filters)"""
#     gql_users = [AsyncMock()]
#     filter_by = FilterBy(equal={"id": "5c650110-2224-4bc7-8cd9-45617e97e712"})
#
#     result = await _apply_additional_id_filters(gql_users, filter_by)
#
#     # Should return the same list unchanged
#     assert result == gql_users


@pytest.mark.asyncio
@patch("logic.user.filter_users")
@patch("logic.user.get_user_by_id")
@patch("logic.user.construct_graphql_user")
async def test_apply_additional_id_filters_with_additional_filters_no_conflict(
    mock_construct_graphql_user, mock_get_user_by_id, mock_filter_users, mock_graphql_user
):
    """Test _apply_additional_id_filters when additional filters don't conflict"""
    # Setup
    original_user = mock_graphql_user
    gql_users = [original_user]

    filter_by = FilterBy(equal={"id": "5c650110-2224-4bc7-8cd9-45617e97e712", "email": "test@example.com"})

    # Mock filter_users to return the same user (no conflict)
    mock_filtered_users = [original_user]
    mock_filter_users.return_value = mock_filtered_users
    mock_filter_users.side_effect = lambda users, filter_obj: mock_filtered_users

    # Execute
    result = await _apply_additional_id_filters(gql_users, filter_by)

    # Verify
    assert result == mock_filtered_users
    mock_filter_users.assert_called()
    mock_get_user_by_id.assert_not_called()
    mock_construct_graphql_user.assert_not_called()


@pytest.mark.asyncio
@patch("logic.user.filter_users")
@patch("logic.user.get_user_by_id")
@patch("logic.user.construct_graphql_user")
async def test_apply_additional_id_filters_with_conflicting_filters(
    mock_construct_graphql_user, mock_get_user_by_id, mock_filter_users, mock_graphql_user
):
    """Test _apply_additional_id_filters when additional filters conflict with ID filter"""
    # Setup
    original_user = mock_graphql_user
    gql_users = [original_user]

    filter_by = FilterBy(
        equal={
            "id": "5c650110-2224-4bc7-8cd9-45617e97e712",
            "email": "conflicting@example.com",  # This email doesn't match our user
        }
    )

    # Mock filter_users to return empty list (conflict)
    mock_filter_users.return_value = []
    mock_filter_users.side_effect = lambda users, filter_obj: []

    # Mock get_user_by_id to return the original user
    mock_get_user_by_id.return_value = AsyncMock()
    mock_construct_graphql_user.return_value = original_user

    # Execute
    result = await _apply_additional_id_filters(gql_users, filter_by)

    # Verify
    assert result == [original_user]
    mock_filter_users.assert_called()
    mock_get_user_by_id.assert_called_once_with("5c650110-2224-4bc7-8cd9-45617e97e712")
    mock_construct_graphql_user.assert_called_once()


@pytest.mark.asyncio
@patch("logic.user.filter_users")
@patch("logic.user.get_user_by_id")
async def test_apply_additional_id_filters_with_conflicting_filters_user_not_found(
    mock_get_user_by_id, mock_filter_users, mock_graphql_user
):
    """Test _apply_additional_id_filters when conflicting filters and user not found"""
    # Setup
    original_user = mock_graphql_user
    gql_users = [original_user]

    filter_by = FilterBy(equal={"id": "5c650110-2224-4bc7-8cd9-45617e97e712", "email": "conflicting@example.com"})

    # Mock filter_users to return empty list (conflict)
    mock_filter_users.return_value = []
    mock_filter_users.side_effect = lambda users, filter_obj: []

    # Mock get_user_by_id to return None (user not found)
    mock_get_user_by_id.return_value = None

    # Execute
    result = await _apply_additional_id_filters(gql_users, filter_by)

    # Verify
    assert result == []
    mock_filter_users.assert_called()
    mock_get_user_by_id.assert_called_once_with("5c650110-2224-4bc7-8cd9-45617e97e712")
