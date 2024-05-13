from logic import get_users
from models import GraphQLUser, UserFilters, UserSort


async def users_query(filters: UserFilters | None = None, sort_by: UserSort | None = None) -> list[GraphQLUser]:
    """Returns all Users"""

    return await get_users(filters, sort_by)
