import pytest
from core.config import settings
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_app(client: AsyncClient):
    response = await client.get(f"{settings.API_STR}/graphql")

    assert response.status_code == 200
