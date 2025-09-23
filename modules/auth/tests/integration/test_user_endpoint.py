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
async def test_admin_get_users_query(client_admin: AsyncClient, users):
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
    client_user: AsyncClient,
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
            "invited": True,
            "inviteStatus": "ACCEPTED",
            "inviterName": "John Doe",
            "role": "MEMBER",
        }
    }

    response = await client_user.post(
        f"{settings.API_STR}/graphql",
        json={"query": mutation, "variables": variables},
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    user = data.get("data", {}).get("updateUser")
    assert user


@pytest.mark.asyncio
async def test_update_user_password_mutation(
    client_user: AsyncClient,
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
            "currentPassword": "currentPassword123",
            "newPassword": "newSecurePassword456",
        }
    }

    response = await client_user.post(
        f"{settings.API_STR}/graphql",
        json={"query": mutation, "variables": variables},
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    user = data.get("data", {}).get("updateUser")
    assert user


@pytest.mark.asyncio
async def test_update_user_password_invalid_current_password(
    client_user: AsyncClient,
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
            "currentPassword": "wrongPassword",
            "newPassword": "newSecurePassword456",
        }
    }

    response = await client_user.post(
        f"{settings.API_STR}/graphql",
        json={"query": mutation, "variables": variables},
    )

    assert response.status_code == 200
    data = response.json()

    # Should return an error for wrong current password
    assert data.get("errors")
    assert "Current password is incorrect" in data.get("errors")[0].get("message")


@pytest.mark.asyncio
async def test_update_user_email_already_in_use(
    client_user: AsyncClient,
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
            "email": "john@company.com",  # This email is already in use as defined in /modules/auth/tests/datafixtures/users.json
        }
    }

    response = await client_user.post(
        f"{settings.API_STR}/graphql",
        json={"query": mutation, "variables": variables},
    )

    assert response.status_code == 200
    data = response.json()

    # Should return an error for wrong current password
    assert data.get("errors")
    assert "Email is already in use" in data.get("errors")[0].get("message")


@pytest.mark.asyncio
async def test_update_user_password_invalid_new_password(
    client_user: AsyncClient,
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
            "currentPassword": "currentPassword123",
            "newPassword": "qwe",
        }
    }

    response = await client_user.post(
        f"{settings.API_STR}/graphql",
        json={"query": mutation, "variables": variables},
    )

    assert response.status_code == 200
    data = response.json()

    # Should return an error for violation of password policy
    assert data.get("errors")
    assert "Password must" in data.get("errors")[0].get("message")


@pytest.mark.asyncio
async def test_update_user_email_and_password_mutation(
    client_user: AsyncClient,
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
            "email": "mixedupdate@epfl.ch",
            "currentPassword": "currentPassword123",
            "newPassword": "mixedUpdatePassword789",
        }
    }

    response = await client_user.post(
        f"{settings.API_STR}/graphql",
        json={"query": mutation, "variables": variables},
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    user = data.get("data", {}).get("updateUser")
    assert user
    assert user.get("email") == "mixedupdate@epfl.ch"


@pytest.mark.asyncio
async def test_user_with_pending_organization_id(
    client_user: AsyncClient,
    users,
):
    # First, update a user to have a pending organization ID
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
            "organizationId": str(users[1].get("organization_id")),  # Use another user's org ID
            "invited": True,
            "inviteStatus": "PENDING",
        }
    }

    response = await client_user.post(
        f"{settings.API_STR}/graphql",
        json={"query": mutation, "variables": variables},
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    user = data.get("data", {}).get("updateUser")
    assert user

    # Test that we can still query users with pending organization IDs
    query = """
        query {
            users {
                items {
                    id
                    email
                    organizationId
                    invited
                    inviteStatus
                }
                count
            }
        }
    """

    response = await client_user.post(
        f"{settings.API_STR}/graphql",
        json={"query": query},
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    _users = data.get("data", {}).get("users", {}).get("items")
    assert _users is not None


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
