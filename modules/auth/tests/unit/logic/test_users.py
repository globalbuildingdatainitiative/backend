from logging import getLogger
from uuid import UUID

import pytest

from logic import get_users
from models import FilterBy

logger = getLogger("main")


@pytest.mark.asyncio
async def test_get_all_users(users):
    _users, _count = await get_users()
    assert isinstance(_users, list)
    assert len(_users) >= len(users)


@pytest.mark.asyncio
async def test_filter_users_by_id(users):
    filters = FilterBy(equal={"id": users[0].get("id")})

    _users, _count = await get_users(filters)

    assert len(_users) == 1
    assert _users[0].id == UUID(filters.equal.get("id"))


@pytest.mark.asyncio
async def test_filter_users_by_organisation_id(users):
    filters = FilterBy(equal={"organization_id": users[1].get("organization_id")})

    _users, _count = await get_users(filters)

    assert len(_users) == 2
    assert str(_users[0].organization_id) == filters.equal.get("organization_id")


@pytest.mark.asyncio
async def test_filter_users_by_email(users):
    filters = FilterBy(equal={"email": users[0].get("email")})

    _users, _count = await get_users(filters)

    assert len(_users) == 1
    assert _users[0].email == filters.equal.get("email")
