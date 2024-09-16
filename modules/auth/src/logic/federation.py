import logging
from uuid import UUID

import httpx
from supertokens_python.recipe.jwt import asyncio
from supertokens_python.recipe.jwt.interfaces import CreateJwtOkResult

from core.config import settings
from exceptions.exceptions import MicroServiceConnectionError, MicroServiceResponseError

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


async def get_organization_name(organization_id: UUID) -> str:
    query = """
    query($id: String!) {
        organizations(filters: {id: {equal: $id}}) {
            name
        }
    }
    """

    try:
        jwt_token = await create_jwt()
        logger.debug(f"Fetching organization with id: {organization_id}")

        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {jwt_token}",
                "Content-Type": "application/json",
            }

            response = await client.post(
                f"{settings.ROUTER_URL}graphql",
                json={
                    "query": query,
                    "variables": {"id": str(organization_id)},
                },
                headers=headers,
            )

            if response.is_error:
                raise MicroServiceConnectionError(
                    f"Could not receive data from {settings.ROUTER_URL}. Got {response.text}"
                )

            data = response.json()
            if "errors" in data:
                raise MicroServiceResponseError(f"Got error from {settings.ROUTER_URL}: {data['errors']}")

            organizations = data.get("data", {}).get("organizations", [])
            if organizations:
                return organizations[0]["name"]

    except Exception as e:
        logging.error(f"Error in get_organization_name: {str(e)}")
        raise

    return "Unknown Organization"
