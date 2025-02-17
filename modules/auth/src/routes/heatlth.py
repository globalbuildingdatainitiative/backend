from typing import Any

import httpx
from fastapi import APIRouter

from core.config import settings
from core.exceptions import MicroServiceConnectionError

health_router = APIRouter(
    prefix="/health",
)


@health_router.get("")
async def get_health_check() -> Any:
    response = httpx.get(f"{settings.CONNECTION_URI}/hello")
    if response.status_code == 200 and response.text.strip() == "Hello":
        return True

    raise MicroServiceConnectionError("Connection to Supertokens failed")
