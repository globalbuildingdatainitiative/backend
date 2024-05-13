from models import GraphQLUser, UserFilters, UserSort


async def get_users(filters: UserFilters | None = None, sort_by: UserSort | None = None) -> list[GraphQLUser]:
    """Returns all Users"""
    from supertokens_python.asyncio import get_users_newest_first

    users = await get_users_newest_first("public")
    return [GraphQLUser.from_supertokens(user.to_json().get("user")) for user in users.users]
