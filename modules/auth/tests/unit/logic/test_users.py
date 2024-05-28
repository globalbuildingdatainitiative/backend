import pytest

from logic import get_users


@pytest.mark.asyncio
async def test_get_users(mock_get_users_newest_first, mock_get_user_metadata):
    users = await get_users()
    assert isinstance(users, list)
