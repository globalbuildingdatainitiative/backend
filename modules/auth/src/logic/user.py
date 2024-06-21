from datetime import datetime

from core.exceptions import EntityNotFound
from models import GraphQLUser, UserFilters, UserSort, UpdateUserInput
from models.sort_filter import FilterOptions


def filter_users(users: list[GraphQLUser], filters: UserFilters) -> list[GraphQLUser]:
    for filter_key in filters.keys():
        _filter = getattr(filters, filter_key)

        if _filter.equal:
            users = [user for user in users if getattr(user, filter_key) == _filter.equal]

    return users


async def get_users(filters: UserFilters | None = None, sort_by: UserSort | None = None) -> list[GraphQLUser]:
    """Returns all Users"""
    from supertokens_python.asyncio import get_users_newest_first
    from supertokens_python.recipe.usermetadata.asyncio import get_user_metadata

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


async def update_user(user_input: UpdateUserInput) -> GraphQLUser:
    """Update user details"""
    from supertokens_python.recipe.usermetadata.asyncio import update_user_metadata
    from supertokens_python.recipe.emailpassword.asyncio import update_email_or_password, sign_in

    metadata_update = {}
    if user_input.first_name is not None:
        metadata_update["first_name"] = user_input.first_name
    if user_input.last_name is not None:
        metadata_update["last_name"] = user_input.last_name
    if user_input.email is not None:
        metadata_update["email"] = user_input.email

    if metadata_update:
        await update_user_metadata(str(user_input.id), metadata_update)

    """Update password if current password and new password are provided"""
    if user_input.current_password and user_input.new_password:
        user_email = (await get_users(UserFilters(id=FilterOptions(equal=str(user_input.id)))))[0].email
        await sign_in("public", str(user_email), str(user_input.current_password))
        await update_email_or_password(
            user_id=str(user_input.id),
            email=user_email,
            password=user_input.new_password,
        )

    # Fetch the updated user data to return
    user_data = await get_users(UserFilters(id=FilterOptions(equal=str(user_input.id))))

    if not user_data:
        raise EntityNotFound("No user found with the provided ID", "Auth")

    return user_data[0]
