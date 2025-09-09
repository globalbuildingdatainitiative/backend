import logging
from uuid import UUID

import httpx
from supertokens_python.recipe.jwt import asyncio
from supertokens_python.recipe.jwt.interfaces import CreateJwtOkResult

from core.config import settings
from core.exceptions import MicroServiceConnectionError, MicroServiceResponseError

logger = logging.getLogger("main")


async def create_jwt() -> str:
    jwt_response = await asyncio.create_jwt(
        {
            "source": "microservice",
        }
    )

    if isinstance(jwt_response, CreateJwtOkResult):
        return jwt_response.jwt
    else:
        raise Exception("Unable to create JWT. Should never come here.")


async def get_auth_user(uid: UUID) -> dict[str, str]:
    query = """
    query($id: String!) {
        users {
            items(filterBy: {equal: {id: $id}}, limit: 1) {
                id
                organizationId
            }
        }
    }
    """
    logger.debug(f"Getting user {uid} from auth service")
    logger.debug(f"Making request to {settings.ROUTER_URL}graphql with query and variables: {{'id': '{uid}'}}")

    jwt_token = await create_jwt()
    logger.debug(f"Created JWT token: {jwt_token[:20]}...")  # Log first 20 chars of token for debugging

    async with httpx.AsyncClient(
        headers={"authorization": f"Bearer {jwt_token}"},
    ) as client:
        try:
            response = await client.post(
                f"{settings.ROUTER_URL}graphql",
                json={
                    "query": query,
                    "variables": {"id": str(uid)},
                },
            )
            logger.debug(f"Received response from auth service with status: {response.status_code}")
            logger.debug(f"Response content: {response.text}")
        except httpx.RequestError as e:
            logger.error(f"Error in get_auth_user: {e.request} for user: {uid}")
            raise MicroServiceConnectionError(f"Could not connect to {e.request.url}") from e
        if response.is_error:
            raise MicroServiceConnectionError(f"Could not receive data from {settings.ROUTER_URL}. Got {response.text}")
        data = response.json()
        logger.debug(f"Parsed response data: {data}")
        if errors := data.get("errors"):
            logger.error(f"GraphQL errors in get_auth_user for user {uid}: {errors}")
            raise MicroServiceResponseError(f"Got error from {settings.ROUTER_URL}: {errors}")

    # Check if user data exists before accessing it
    users_data = data.get("data", {}).get("users", {}).get("items", [])
    logger.debug(f"Found {len(users_data)} users in response")
    if not users_data:
        logger.error(f"No user found in auth service for uid: {uid}")
        raise MicroServiceResponseError(f"No user found in auth service for uid: {uid}")

    user = users_data[0]
    logger.debug(f"Returning user data: {user}")

    return user
