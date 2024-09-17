import pytest
from logic import get_users, update_user
from models import UpdateUserInput, InviteStatus


@pytest.mark.asyncio
async def test_get_users(mock_get_users_newest_first, mock_get_user_metadata):
    users = await get_users()
    assert isinstance(users, list)


@pytest.mark.asyncio
async def test_update_user(
    users,
    mock_get_users,
    mock_get_users_newest_first,
    mock_get_user_metadata,
    mock_update_user_metadata,
    mock_update_email_or_password,
    mock_sign_in,
):
    user_id = users[0].get("id")
    user_input = {
        "id": user_id,
        "first_name": "UpdatedFirstName",
        "last_name": "UpdatedLastName",
        "email": "updated@example.com",
        "current_password": "currentPassword123",
        "new_password": "newPassword123",
        "invited": True,
        "invite_status": InviteStatus.ACCEPTED,  # Use the correct enum
        "inviter_name": "John Doe",
    }

    user = await update_user(UpdateUserInput(**user_input))
    print("\nuser:", user)

    assert user.first_name == "UpdatedFirstName"
    assert user.last_name == "UpdatedLastName"
    assert user.email == "updated@example.com"
    assert user.invite_status == InviteStatus.ACCEPTED
    print("\nAssertion Completed")
