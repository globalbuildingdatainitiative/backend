import logging
from uuid import UUID

import httpx
from supertokens_python.recipe.jwt import asyncio
from supertokens_python.recipe.jwt.interfaces import CreateJwtOkResult

from core.config import settings
from exceptions.exceptions import MicroServiceConnectionError, MicroServiceResponseError


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
        logging.info(f"Created JWT token: {jwt_token[:10]}...")  # Log first 10 characters of token

        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {jwt_token}",
                "Content-Type": "application/json",
            }
            logging.info(f"Sending request to {settings.ROUTER_URL}graphql with headers: {headers}")

            response = await client.post(
                f"{settings.ROUTER_URL}graphql",
                json={
                    "query": query,
                    "variables": {"id": str(organization_id)},
                },
                headers=headers,
            )

            logging.info(f"Received response with status code: {response.status_code}")
            logging.info(f"Response content: {response.text}")

            if response.is_error:
                raise MicroServiceConnectionError(f"Could not receive data from {settings.ROUTER_URL}. Got {response.text}")

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