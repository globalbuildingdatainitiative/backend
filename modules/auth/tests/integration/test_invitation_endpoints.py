import pytest
from httpx import AsyncClient
from unittest.mock import patch
from uuid import uuid4

from core.auth import FAKE_PASSWORD
from core.config import settings
from logic.user import create_user_meta_data, update_user_metadata
from models import InviteStatus, Role
from logic.roles import assign_role
from supertokens_python.recipe.emailpassword.asyncio import sign_up


@pytest.mark.asyncio
@patch("logic.federation.httpx.AsyncClient.post")  # Mock the HTTP call itself
@patch("logic.federation.create_jwt")  # Mock the JWT creation
@patch("supertokens_python.recipe.emailpassword.asyncio.sign_up")
@patch("supertokens_python.recipe.emailpassword.asyncio.send_reset_password_email")
async def test_invite_users_mutation(
    mock_send_email, mock_sign_up, mock_create_jwt, mock_post, client: AsyncClient, create_user
):
    """Test inviting new users"""
    # Set up mock for HTTP response
    mock_post.return_value = type(
        "Response",
        (),
        {
            "is_error": False,
            "status_code": 200,
            "text": "",
            "json": lambda self: {
                "data": {
                    "inviteUsers": [
                        {"email": "newuser@epfl.ch", "status": "invited", "message": ""},
                        {"email": "anotheruser@epfl.ch", "status": "invited", "message": ""},
                    ]
                }
            },
        },
    )()

    # Set up other mocks
    mock_create_jwt.return_value = "mocked-jwt-token"
    mock_send_email.return_value = None
    mock_sign_up.return_value = type("SignUpOkResult", (), {"user": type("User", (), {"id": "test-user-id"})()})()

    # Update user metadata to include organization_id and make them an owner
    await update_user_metadata(
        str(create_user.id),
        {
            "organization_id": str(create_user.organization_id),
            "first_name": "Test",
            "last_name": "User",
        },
    )
    await assign_role(create_user.id, Role.OWNER)

    mutation = """
        mutation($input: InviteUsersInput!) {
            inviteUsers(input: $input) {
                email
                status
                message
            }
        }
    """

    variables = {"input": {"emails": ["newuser@epfl.ch", "anotheruser@epfl.ch"]}}

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={"query": mutation, "variables": variables},
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors"), f"Got errors: {data.get('errors')}"

    results = data.get("data", {}).get("inviteUsers")
    assert results is not None, "No inviteUsers data in response"
    assert len(results) == 2, f"Expected 2 results, got {len(results) if results else 0}"

    for result in results:
        assert result["status"] == "invited"
        assert "email" in result

    # Verifying that the mutation completed successfully
    assert len(results) == 2


@pytest.mark.asyncio
async def test_accept_invitation_mutation(client: AsyncClient):
    """Test accepting an invitation"""
    # Create a new user with FAKE_PASSWORD
    response = await sign_up("public", "testuser@epfl.ch", FAKE_PASSWORD)
    user_id = response.user.id
    await create_user_meta_data(
        user_id,
        {
            "email": str(response.user.emails[0]),
            "time_joined": response.user.time_joined,
        },
    )

    # Set up the test user with correct metadata
    await update_user_metadata(
        user_id,
        {
            "invited": True,
            "invite_status": InviteStatus.PENDING.value,
            "organization_id": str(uuid4()),
        },
    )

    mutation = """
        mutation($user: AcceptInvitationInput!) {
            acceptInvitation(user: $user)
        }
    """

    variables = {
        "user": {
            "id": user_id,
            "firstName": "John",
            "lastName": "Doe",
            "currentPassword": FAKE_PASSWORD,
            "newPassword": "newPassword123",
        }
    }

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={"query": mutation, "variables": variables},
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    result = data.get("data", {}).get("acceptInvitation")
    assert result is True


@pytest.mark.asyncio
async def test_reject_invitation_mutation(client: AsyncClient):
    """Test rejecting an invitation"""
    # Create a new user
    response = await sign_up("public", "rejectuser@epfl.ch", FAKE_PASSWORD)
    user_id = response.user.id
    await create_user_meta_data(
        user_id,
        {
            "email": str(response.user.emails[0]),
            "time_joined": response.user.time_joined,
        },
    )

    # Set up the test user with correct metadata
    await update_user_metadata(
        user_id,
        {
            "invited": True,
            "invite_status": InviteStatus.PENDING.value,
            "organization_id": str(uuid4()),
        },
    )

    mutation = """
        mutation($userId: String!) {
            rejectInvitation(userId: $userId)
        }
    """

    variables = {"userId": user_id}

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={"query": mutation, "variables": variables},
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    result = data.get("data", {}).get("rejectInvitation")
    assert result is True


@pytest.mark.asyncio
@patch("logic.invite_users.send_reset_password_email")
async def test_resend_invitation_mutation(mock_send_email, client: AsyncClient):
    """Test resending an invitation to a user in pending state"""
    # Create a new user
    email = "resenduser@epfl.ch"
    response = await sign_up("public", email, FAKE_PASSWORD)
    user_id = response.user.id

    # Mock the send_reset_password_email function to accept both user_id and email
    mock_send_email.return_value = None

    # Set up the test user with correct metadata
    await create_user_meta_data(
        user_id,
        {
            "invited": True,
            "invite_status": InviteStatus.PENDING.value,
            "organization_id": str(uuid4()),
        },
    )

    mutation = """
        mutation($userId: String!) {
            resendInvitation(userId: $userId) {
                email
                status
                message
            }
        }
    """

    variables = {"userId": user_id}

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={"query": mutation, "variables": variables},
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    result = data.get("data", {}).get("resendInvitation")
    assert result["status"] == "resent"
    assert result["email"] == email
    assert "message" in result

    # Verify the mock was called correctly
    mock_send_email.assert_called_once()
