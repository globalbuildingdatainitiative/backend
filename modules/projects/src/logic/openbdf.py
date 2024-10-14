from models.openbdf import GraphQLProject
from .json_schema import get_schema


async def serialize_openbdf_schema() -> dict:
    return get_schema(GraphQLProject)
