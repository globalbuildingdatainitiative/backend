import pytest
from httpx import AsyncClient
from core.config import settings


@pytest.mark.asyncio
async def test_users_query(client: AsyncClient, mock_get_users_newest_first, mock_get_user_metadata):
    query = """
        query {
            users {
                id
                email
                timeJoined
                firstName
                lastName
                organizationId
                invited
                inviteStatus
                inviterName
                role
            }
        }
    """

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={"query": query},
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    users = data.get("data", {}).get("users")
    assert users is not None

    for user in users:
        assert "id" in user
        assert "email" in user
        assert "timeJoined" in user
        assert "firstName" in user
        assert "lastName" in user
        assert "organizationId" in user
        assert "invited" in user
        assert "inviteStatus" in user
        assert "inviterName" in user
        assert "role" in user


@pytest.mark.asyncio
async def test_update_user_mutation(
    client: AsyncClient,
    users,
    mock_get_users,
    mock_get_users_newest_first,
    mock_get_user_metadata,
    mock_update_user_metadata,
    mock_update_email_or_password,
    mock_sign_in,
):
    mutation = """
        mutation($userInput: UpdateUserInput!) {
            updateUser(userInput: $userInput) {
                id
                firstName
                lastName
                email
                timeJoined
                organizationId
                invited
                inviteStatus
                inviterName
                role
            }
        }
    """

    user_id = users[0].get("id")
    variables = {
        "userInput": {
            "id": user_id,
            "firstName": "UpdatedFirstName",
            "lastName": "UpdatedLastName",
            "email": "updated@example.com",
            "currentPassword": "currentPassword123",
            "newPassword": "newPassword123",
            "invited": True,
            "inviteStatus": "ACCEPTED",
            "inviterName": "John Doe",
            "role": "MEMBER",
        }
    }

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={"query": mutation, "variables": variables},
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    user = data.get("data", {}).get("updateUser")
    assert user
    assert user["firstName"] == "UpdatedFirstName"
    assert user["lastName"] == "UpdatedLastName"
    assert user["email"] == "updated@example.com"
    assert user["inviteStatus"] == "ACCEPTED"
    assert user["role"] == "MEMBER"
