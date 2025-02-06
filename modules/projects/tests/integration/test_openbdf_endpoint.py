import json
from pathlib import Path

import pytest
from httpx import AsyncClient

from core.config import settings


@pytest.mark.asyncio
async def test_openbdf(client_unauthenticated: AsyncClient):
    response = await client_unauthenticated.get(f"{settings.API_STR}/openbdf")

    assert response.status_code == 200

    data = response.json()
    assert data

    Path('openbdf.json').write_text(json.dumps(data, indent=2))
    assert data.get("title") == "Project"
