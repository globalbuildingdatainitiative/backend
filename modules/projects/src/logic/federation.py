import logging
from uuid import UUID

import httpx
from supertokens_python.recipe.jwt import asyncio
from supertokens_python.recipe.jwt.interfaces import CreateJwtOkResult

import core.config as config
import core.exceptions as exc

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


async def filter_users(value: str, organization_id: str) -> list[UUID]:
    query = """
    query($value: String!, $organization_id: String!) {
        users {
            items(filterBy: {contains: {data: $value, organization_id: $organization_id}}) {
                id
            }
        }
    }
    """
    logger.debug(f"Getting users containing {value} from auth service")

    async with httpx.AsyncClient(
        headers={"authorization": f"Bearer {await create_jwt()}"},
    ) as client:
        try:
            response = await client.post(
                f"{config.settings.ROUTER_URL}graphql",
                json={
                    "query": query,
                    "variables": {"value": value, "organization_id": organization_id},
                },
            )
        except httpx.RequestError as e:
            logger.error(f"Error in filter_users: {e.request} for users with: {value}")
            raise exc.MicroServiceConnectionError(f"Could not connect to {e.request.url}") from e
        if response.is_error:
            raise exc.MicroServiceConnectionError(f"Could not receive data from {config.settings.ROUTER_URL}. Got {response.text}")
        data = response.json()
        if errors := data.get("errors"):
            raise exc.MicroServiceResponseError(f"Got error from {config.settings.ROUTER_URL}: {errors}")

    users = [UUID(user.get("id")) for user in data["data"]["users"]["items"]]
    logger.debug(f"Got users: {users}")
    return users
