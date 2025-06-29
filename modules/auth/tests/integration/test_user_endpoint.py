import pytest
from httpx import AsyncClient

from core.config import settings


@pytest.mark.asyncio
async def test_users_query(client: AsyncClient):
    query = """
        query {
            users {
                items {
                    id
                    email
                    timeJoined
                    firstName
                    lastName
                    organizationId
                    invited
                    inviteStatus
                    inviterName
                    roles
                }
                count
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
    _users = data.get("data", {}).get("users", {}).get("items")
    assert _users is not None

    for user in _users:
        assert "id" in user
        assert "email" in user
        assert "timeJoined" in user
        assert "firstName" in user
        assert "lastName" in user
        assert "organizationId" in user
        assert "invited" in user
        assert "inviteStatus" in user
        assert "inviterName" in user
        assert "roles" in user


@pytest.mark.asyncio
async def test_admin_get_users_query(client_admin: AsyncClient):
    query = """
        query {
            users {
                items {
                    id
                }
            }
        }
    """

    response = await client_admin.post(
        f"{settings.API_STR}/graphql",
        json={"query": query},
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    _users = data.get("data", {}).get("users", {}).get("items")

    assert _users
    assert len(_users) > 1


@pytest.mark.asyncio
async def test_update_user_mutation(
    client: AsyncClient,
    users,
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
                roles
            }
        }
    """

    user_id = users[0].get("id")
    variables = {
        "userInput": {
            "id": user_id,
            "firstName": "UpdatedFirstName",
            "lastName": "UpdatedLastName",
            "email": "updated@epfl.ch",
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


@pytest.mark.asyncio
async def test_admin_impersonate_user(client_admin: AsyncClient, users):
    mutation = """
        mutation($userId: String!) {
            impersonate(userId: $userId)
        }
    """

    response = await client_admin.post(
        f"{settings.API_STR}/graphql",
        json={"query": mutation, "variables": {"userId": users[0].get("id")}},
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    user = data.get("data", {}).get("impersonate")
    assert user


@pytest.mark.asyncio
async def test_impersonate_user(client: AsyncClient, users):
    mutation = """
        mutation($userId: String!) {
            impersonate(userId: $userId)
        }
    """

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={"query": mutation, "variables": {"userId": users[0].get("id")}},
    )

    assert response.status_code == 200
    data = response.json()

    assert data.get("errors")[0].get("message") == "User is not an admin"
