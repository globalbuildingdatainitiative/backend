from datetime import datetime

from models import GraphQLUser, UserFilters, UserSort


def filter_users(users: list[GraphQLUser], filters: UserFilters) -> list[GraphQLUser]:
    for filter_key in filters.keys():
        _filter = getattr(filters, filter_key)

        if _filter.equal:
            users = [user for user in users if getattr(user, filter_key) == _filter.equal]

    return users


async def get_users(filters: UserFilters | None = None, sort_by: UserSort | None = None) -> list[GraphQLUser]:
    """Returns all Users"""
    from supertokens_python.recipe.usermetadata.asyncio import get_user_metadata
    from supertokens_python.asyncio import get_users_newest_first

    users = await get_users_newest_first("public")
    gql_users = []

    for user in users.users:
        user_data = user.to_json().get("user")
        user_id = user_data["id"]

        # Fetch metadata for each user
        metadata_response = await get_user_metadata(user_id)
        first_name = metadata_response.metadata.get("first_name")
        last_name = metadata_response.metadata.get("last_name")
        organization_id = metadata_response.metadata.get("organization_id")

        user = GraphQLUser(
            id=user_id,
            email=user_data["email"],
            time_joined=datetime.fromtimestamp(round(user_data["timeJoined"] / 1000)),
            first_name=first_name,
            last_name=last_name,
            organization_id=organization_id,
        )

        gql_users.append(user)

        if filters:
            gql_users = filter_users(gql_users, filters)

    return gql_users
