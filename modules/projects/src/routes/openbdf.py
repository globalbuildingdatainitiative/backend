
from typing import Any

from fastapi import APIRouter

from logic import serialize_openbdf_schema

openbdf_router = APIRouter(
    prefix="/openbdf",
)



@openbdf_router.get("")
async def get_openbdf_schema() -> Any:
    return await serialize_openbdf_schema()

