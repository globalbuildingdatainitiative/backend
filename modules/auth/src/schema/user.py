from strawberry.types import Info

from models import GraphQLUser


async def users_query(info: Info) -> list[GraphQLUser]:
    """Returns all Users"""

    return [GraphQLUser()]
