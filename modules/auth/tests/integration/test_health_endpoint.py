import pytest
from httpx import AsyncClient

from core.config import settings


@pytest.mark.asyncio
async def test_health(client_unauthenticated: AsyncClient):
    response = await client_unauthenticated.get(f"{settings.API_STR}/health")

    assert response.status_code == 200

    data = response.json()
    assert data
