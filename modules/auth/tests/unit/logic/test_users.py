from logging import getLogger
from uuid import UUID

import pytest

from logic import get_users
from models import FilterBy

logger = getLogger("main")


@pytest.mark.asyncio
async def test_get_all_users(users):
    _users = await get_users()
    assert isinstance(_users, list)
    assert len(_users) >= len(users)


@pytest.mark.asyncio
async def test_filter_users_by_id(users):
    filters = FilterBy(equal={"id": users[0].get("id")})

    _users = await get_users(filters)

    assert len(_users) == 1
    assert _users[0].id == UUID(filters.equal.get("id"))


@pytest.mark.asyncio
async def test_filter_users_by_organisation_id(users):
    filters = FilterBy(contains={"data": users[1].get("organization_id")})

    _users = await get_users(filters)

    assert len(_users) == 1
    assert _users[0].organization_id == filters.contains.get("data")


@pytest.mark.asyncio
async def test_filter_users_by_email(users):
    filters = FilterBy(equal={"email": users[0].get("email")})

    _users = await get_users(filters)

    assert len(_users) == 1
    assert _users[0].email == filters.equal.get("email")
