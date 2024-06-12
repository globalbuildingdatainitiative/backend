from datetime import datetime

from models import GraphQLUser, UserFilters, UserSort


async def get_users(filters: UserFilters | None = None, sort_by: UserSort | None = None) -> list[GraphQLUser]:
    """Returns all Users"""
    from supertokens_python.recipe.usermetadata.asyncio import get_user_metadata
    from supertokens_python.asyncio import get_users_newest_first

    users = await get_users_newest_first("public")
    graphQLUsers = []

    for user in users.users:
        user_data = user.to_json().get("user")
        user_id = user_data["id"]

        # Fetch metadata for each user
        metadata_response = await get_user_metadata(user_id)
        first_name = metadata_response.metadata.get("first_name")
        last_name = metadata_response.metadata.get("last_name")
        organization_id = metadata_response.metadata.get("organization_id")

        graphQLUser = GraphQLUser(
            id=user_id,
            email=user_data["email"],
            time_joined=datetime.fromtimestamp(round(user_data["timeJoined"] / 1000)),
            first_name=first_name,
            last_name=last_name,
            organization_id=organization_id,
        )

        graphQLUsers.append(graphQLUser)

        if filters and filters.id and filters.id.equal:
            graphQLUsers = [
                user for user in graphQLUsers if user.id == filters.id.equal
            ]

    return graphQLUsers
