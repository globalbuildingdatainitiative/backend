import pytest

from logic import get_users


@pytest.mark.asyncio
async def test_get_users(mock_get_users_newest_first):
    users = await get_users()
    assert isinstance(users, list)
