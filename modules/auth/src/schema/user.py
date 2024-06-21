from logic import get_users, update_user
from models import GraphQLUser, UserFilters, UserSort, UpdateUserInput


async def users_query(filters: UserFilters | None = None, sort_by: UserSort | None = None) -> list[GraphQLUser]:
    """Returns all Users"""

    return await get_users(filters, sort_by)


async def update_user_mutation(user_input: UpdateUserInput) -> GraphQLUser:
    """Update user details"""
    return await update_user(user_input)
