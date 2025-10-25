import pytest
from httpx import AsyncClient
from unittest.mock import patch
# from uuid import uuid4

from core.auth import FAKE_PASSWORD
from core.config import settings
from models import InviteStatus


@pytest.mark.asyncio
@patch("logic.invite_users.send_reset_password_email")
async def test_invite_users_mutation(mock_send_email, client: AsyncClient, create_user):
    """Test inviting new users via GraphQL mutation"""
    mock_send_email.return_value = None

    mutation = """
        mutation($input: InviteUsersInput!) {
            inviteUsers(input: $input) {
                email
                status
                message
            }
        }
    """

    variables = {"input": {"emails": ["newuser@example.com", "anotheruser@example.com"]}}

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={"query": mutation, "variables": variables},
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors"), f"Got errors: {data.get('errors')}"

    results = data.get("data", {}).get("inviteUsers")
    assert results is not None, "No inviteUsers data in response"
    assert len(results) == 2, f"Expected 2 results, got {len(results)}"

    for result in results:
        assert result["status"] == "invited"
        assert result["email"] in ["newuser@example.com", "anotheruser@example.com"]
        assert "message" in result


@pytest.mark.asyncio
@patch("logic.invite_users.send_reset_password_email")
async def test_accept_invitation_mutation(mock_send_email, client: AsyncClient):
    """Test accepting an invitation via GraphQL mutation"""
    mock_send_email.return_value = None

    # First, invite a user
    invite_mutation = """
        mutation($input: InviteUsersInput!) {
            inviteUsers(input: $input) {
                email
                status
            }
        }
    """

    email = "acceptuser@example.com"
    invite_response = await client.post(
        f"{settings.API_STR}/graphql",
        json={"query": invite_mutation, "variables": {"input": {"emails": [email]}}},
    )

    assert invite_response.status_code == 200
    invite_data = invite_response.json()
    assert not invite_data.get("errors")

    # Get the user ID by querying users
    query_users = """
        query($filterBy: FilterBy) {
            users(filterBy: $filterBy) {
                users {
                    id
                    email
                    inviteStatus
                }
            }
        }
    """

    users_response = await client.post(
        f"{settings.API_STR}/graphql",
        json={"query": query_users, "variables": {"filterBy": {"equal": {"email": email}}}},
    )

    assert users_response.status_code == 200
    users_data = users_response.json()
    assert not users_data.get("errors")

    users = users_data["data"]["users"]["users"]
    assert len(users) == 1
    user_id = users[0]["id"]
    assert users[0]["inviteStatus"] == InviteStatus.PENDING.value

    # Now accept the invitation
    accept_mutation = """
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
        json={"query": accept_mutation, "variables": variables},
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors"), f"Got errors: {data.get('errors')}"
    result = data.get("data", {}).get("acceptInvitation")
    assert result is True

    # Verify the user's invite status changed to ACCEPTED
    verify_response = await client.post(
        f"{settings.API_STR}/graphql",
        json={"query": query_users, "variables": {"filterBy": {"equal": {"email": email}}}},
    )

    verify_data = verify_response.json()
    verified_user = verify_data["data"]["users"]["users"][0]
    assert verified_user["inviteStatus"] == InviteStatus.ACCEPTED.value


@pytest.mark.asyncio
@patch("logic.invite_users.send_reset_password_email")
async def test_reject_invitation_mutation(mock_send_email, client: AsyncClient):
    """Test rejecting an invitation via GraphQL mutation"""
    mock_send_email.return_value = None

    # First, invite a user
    invite_mutation = """
        mutation($input: InviteUsersInput!) {
            inviteUsers(input: $input) {
                email
                status
            }
        }
    """

    email = "rejectuser@example.com"
    invite_response = await client.post(
        f"{settings.API_STR}/graphql",
        json={"query": invite_mutation, "variables": {"input": {"emails": [email]}}},
    )

    assert invite_response.status_code == 200

    # Get the user ID
    query_users = """
        query($filterBy: FilterBy) {
            users(filterBy: $filterBy) {
                users {
                    id
                    email
                    inviteStatus
                }
            }
        }
    """

    users_response = await client.post(
        f"{settings.API_STR}/graphql",
        json={"query": query_users, "variables": {"filterBy": {"equal": {"email": email}}}},
    )

    users_data = users_response.json()
    user_id = users_data["data"]["users"]["users"][0]["id"]

    # Reject the invitation
    reject_mutation = """
        mutation($userId: String!) {
            rejectInvitation(userId: $userId)
        }
    """

    variables = {"userId": user_id}

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={"query": reject_mutation, "variables": variables},
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors"), f"Got errors: {data.get('errors')}"
    result = data.get("data", {}).get("rejectInvitation")
    assert result is True

    # Verify the user's invite status changed to REJECTED
    verify_response = await client.post(
        f"{settings.API_STR}/graphql",
        json={"query": query_users, "variables": {"filterBy": {"equal": {"email": email}}}},
    )

    verify_data = verify_response.json()
    verified_user = verify_data["data"]["users"]["users"][0]
    assert verified_user["inviteStatus"] == InviteStatus.REJECTED.value


@pytest.mark.asyncio
@patch("logic.invite_users.send_reset_password_email")
async def test_resend_invitation_mutation(mock_send_email, client: AsyncClient):
    """Test resending an invitation via GraphQL mutation"""
    mock_send_email.return_value = None

    # First, invite a user
    invite_mutation = """
        mutation($input: InviteUsersInput!) {
            inviteUsers(input: $input) {
                email
                status
            }
        }
    """

    email = "resenduser@example.com"
    invite_response = await client.post(
        f"{settings.API_STR}/graphql",
        json={"query": invite_mutation, "variables": {"input": {"emails": [email]}}},
    )

    assert invite_response.status_code == 200

    # Get the user ID
    query_users = """
        query($filterBy: FilterBy) {
            users(filterBy: $filterBy) {
                users {
                    id
                    email
                    inviteStatus
                }
            }
        }
    """

    users_response = await client.post(
        f"{settings.API_STR}/graphql",
        json={"query": query_users, "variables": {"filterBy": {"equal": {"email": email}}}},
    )

    users_data = users_response.json()
    user = users_data["data"]["users"]["users"][0]
    user_id = user["id"]
    assert user["inviteStatus"] == InviteStatus.PENDING.value

    # Resend the invitation
    resend_mutation = """
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
        json={"query": resend_mutation, "variables": variables},
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors"), f"Got errors: {data.get('errors')}"
    result = data.get("data", {}).get("resendInvitation")
    assert result["status"] == "resent"
    assert result["email"] == email
    assert "message" in result

    # Verify the email sending function was called twice (once for invite, once for resend)
    assert mock_send_email.call_count == 2
