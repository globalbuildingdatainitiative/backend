import pytest

from logic import get_users
from models import FilterBy


@pytest.mark.asyncio
async def test_filter_users_by_email_with_no_matches(users):
    """Test email filtering combined with a filter that excludes the user"""
    filters = FilterBy(
        equal={
            "email": users[0].get("email"),
            "organization_id": users[2].get("organization_id"),  # Different org ID
        }
    )

    _users = await get_users(filters)

    # Should return no users since the filters contradict each other
    assert len(_users) == 0


@pytest.mark.asyncio
async def test_filter_users_by_email_contains_and_organization_id(users):
    """Test email filtering with contains filter and organization ID"""
    # Get the email domain
    email_domain = users[0].get("email").split("@")[1]

    filters = FilterBy(equal={"organization_id": users[0].get("organization_id")}, contains={"email": email_domain})

    _users = await get_users(filters)

    # Should return users with the same organization ID and email domain
    assert len(_users) >= 1
    for user in _users:
        assert user.organization_id == filters.equal.get("organization_id")
        assert email_domain in user.email


@pytest.mark.asyncio
async def test_multiple_users_same_email_domain_filter(users):
    """Test filtering multiple users by email domain"""
    # Get the email domain from the first user
    email_domain = users[0].get("email").split("@")[1]

    filters = FilterBy(contains={"email": email_domain})

    _users = await get_users(filters)

    # Should return all users with the same email domain
    assert len(_users) >= 1
    for user in _users:
        assert email_domain in user.email
