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
        users(filters: {id: {equal: $id}}) {
            id
            organizationId
        }
    }
    """
    logger.debug(f"Getting user {uid} from auth service")

    async with httpx.AsyncClient(
        headers={"authorization": f"Bearer {await create_jwt()}"},
    ) as client:
        try:
            response = await client.post(
                f"{settings.ROUTER_URL}graphql",
                json={
                    "query": query,
                    "variables": {"id": str(uid)},
                },
            )
        except httpx.RequestError as e:
            logger.error(f"Error in get_auth_user: {e.request} for user: {uid}")
            raise MicroServiceConnectionError(f"Could not connect to {e.request.url}") from e
        if response.is_error:
            raise MicroServiceConnectionError(f"Could not receive data from {settings.ROUTER_URL}. Got {response.text}")
        data = response.json()
        if errors := data.get("errors"):
            raise MicroServiceResponseError(f"Got error from {settings.ROUTER_URL}: {errors}")
    user = data["data"]["users"][0]

    return user
