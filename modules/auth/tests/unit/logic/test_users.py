from logging import getLogger
from uuid import UUID

import pytest

from logic import get_users
from models import UserFilters
from models.sort_filter import FilterOptions

logger = getLogger("main")


@pytest.mark.asyncio
async def test_get_all_users(users):
    _users = await get_users()
    assert isinstance(_users, list)
    assert len(_users) == len(users) + 1


@pytest.mark.asyncio
async def test_filter_users_by_id(users):
    filters = UserFilters(id=FilterOptions(equal=users[0].get("id")))

    _users = await get_users(filters)

    assert len(_users) == 1
    assert _users[0].id == UUID(filters.id.equal)


@pytest.mark.asyncio
async def test_filter_users_by_organisation_id(users):
    filters = UserFilters(organization_id=FilterOptions(equal=users[1].get("organization_id")))

    _users = await get_users(filters)

    assert len(_users) == 1
    assert _users[0].organization_id == filters.organization_id.equal


@pytest.mark.asyncio
async def test_filter_users_by_email(users):
    filters = UserFilters(email=FilterOptions(equal=users[0].get("email")))

    _users = await get_users(filters)

    assert len(_users) == 1
    assert _users[0].email == filters.email.equal
