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
    filters = FilterBy(contains={"organization_id": users[1].get("organization_id")})

    _users = await get_users(filters)

    assert len(_users) == 2
    assert _users[0].organization_id == filters.contains.get("organization_id")


@pytest.mark.asyncio
async def test_filter_users_by_email(users):
    filters = FilterBy(equal={"email": users[0].get("email")})

    _users = await get_users(filters)

    assert len(_users) == 1
    assert _users[0].email == filters.equal.get("email")


@pytest.mark.asyncio
async def test_filter_users_by_multiple_keys(users):
    filters = FilterBy(
        contains={"name": users[0].get("firstName").lower(), "organization_id": users[0].get("organization_id")}
    )

    _users = await get_users(filters)

    assert len(_users) == 1
    assert _users[0].first_name.lower() == filters.contains.get("name")
