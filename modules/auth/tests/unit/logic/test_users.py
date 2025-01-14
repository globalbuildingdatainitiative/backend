import pytest

from logic import get_users


@pytest.mark.asyncio
async def test_get_users(users):
    users = await get_users()
    assert isinstance(users, list)
