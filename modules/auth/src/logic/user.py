import json
from datetime import datetime
from logging import getLogger
from uuid import UUID

import strawberry
from fastapi.requests import Request
from strawberry import UNSET
from supertokens_python.asyncio import get_user, get_users_newest_first, list_users_by_account_info
from supertokens_python.recipe.emailpassword.asyncio import update_email_or_password, verify_credentials
from supertokens_python.recipe.emailpassword.interfaces import WrongCredentialsError
from supertokens_python.recipe.session.asyncio import create_new_session
from supertokens_python.recipe.session.interfaces import SessionContainer
from supertokens_python.recipe.usermetadata.asyncio import update_user_metadata, get_user_metadata
from supertokens_python.recipe.userroles.asyncio import get_roles_for_user
from supertokens_python.types import AccountInfo, User

from core import exceptions
from core.exceptions import EntityNotFound
from logic.roles import assign_role, remove_role
from models import GraphQLUser, UpdateUserInput, InviteStatus, Role, AcceptInvitationInput
from models.sort_filter import FilterBy, SortBy

logger = getLogger("main")


async def get_users(
    filter_by: FilterBy | None = None, sort_by: SortBy | None = None, limit: int | None = None, offset: int = 0
) -> list[GraphQLUser]:
    """Returns all Users & their metadata"""

    logger.debug(f"Fetching users with filters: {filter_by} and sort_by: {sort_by}")

    # Log the individual filter components for debugging
    if filter_by and filter_by.equal:
        logger.debug(f"Equal filters: {filter_by.equal}")

    gql_users = []

    # Handle special case filters first
    if filter_by and filter_by.equal:
        # ID filter - direct lookup (prioritize ID filter even with other filters)
        if filter_by.equal.get("id"):
            _user = await get_user_by_id(str(filter_by.equal.get("id")))
            if _user:
                gql_users = [await construct_graphql_user(_user)]
            else:
                gql_users = []
        # Email filter - use SuperTokens account info lookup (only when it's the sole filter)
        elif filter_by.equal.get("email") and len(filter_by.equal) == 1:
            users = await list_users_by_account_info("public", AccountInfo(email=filter_by.equal.get("email")))
            gql_users = [await construct_graphql_user(_user) for _user in users]
        # Combined filters or other filters - fetch all users and apply post-filtering
        else:
            gql_users = [await construct_graphql_user(_user) for _user in await get_all_users()]
            gql_users = filter_users(gql_users, filter_by)
    else:
        # No equal filters - fetch all users and apply post-filtering
        gql_users = [await construct_graphql_user(_user) for _user in await get_all_users()]

        if filter_by:
            gql_users = filter_users(gql_users, filter_by)

    # Apply additional filters if there are more than just the ID filter
    # But only if we actually found a user with the ID filter
    if filter_by and filter_by.equal and filter_by.equal.get("id") and len(filter_by.equal) > 1 and gql_users:
        # For ID-based queries, we should be more selective about additional filters
        # Only apply filters that don't contradict the fact that we found a specific user
        id_only_filter = FilterBy(equal={"id": filter_by.equal.get("id")})
        gql_users = filter_users(gql_users, id_only_filter)

        # If we lost the user after filtering, it means the additional filters were contradictory
        # In that case, return the original user (since ID filter takes precedence)
        if not gql_users:
            # Re-fetch the user by ID only
            _user = await get_user_by_id(str(filter_by.equal.get("id")))
            if _user:
                gql_users = [await construct_graphql_user(_user)]
            else:
                gql_users = []

    if sort_by:
        gql_users = sort_users(gql_users, sort_by)

    if limit is not None:
        gql_users = gql_users[offset : offset + limit]
    else:
        gql_users = gql_users[offset:]

    return gql_users


async def update_user(user_input: UpdateUserInput) -> GraphQLUser:
    """Update user details & metadata"""

    metadata_update = strawberry.asdict(user_input)
    user_id = str(metadata_update.pop("id"))

    user = await get_user(user_id)
    if not user:
        raise EntityNotFound(f"No user found with the provided ID: {user_input.id}", "Auth")

    # Store email before removing it from metadata_update
    new_email = metadata_update.get("email")
    current_email = str(user.emails[0]) if user.emails else None

    del metadata_update["current_password"]
    del metadata_update["new_password"]
    if metadata_update["organization_id"] is UNSET or metadata_update["organization_id"] is None:
        roles = await get_roles_for_user("public", user_id)
        for role in roles.roles:
            if role == "admin":
                continue
            await remove_role(user_id, Role(role))

    def custom_serializer(obj):
        if isinstance(obj, InviteStatus):
            return obj.value

    metadata_update = json.dumps(
        {key: value for key, value in metadata_update.items() if value is not UNSET}, default=custom_serializer
    )

    if metadata_update:
        await update_user_metadata(user_id, json.loads(metadata_update))

    # Update email if provided and different from current
    if new_email is not UNSET and new_email != current_email:
        await update_email_or_password(
            recipe_user_id=user.login_methods[0].recipe_user_id,
            email=str(new_email),
            tenant_id_for_password_policy=user.tenant_ids[0],
        )
        # Refresh user object after email update to ensure we have the latest email for password verification
        user = await get_user(user_id)

    # Update password if current password and new password are provided
    if user_input.current_password and user_input.new_password:
        is_password_valid = await verify_credentials("public", str(user.emails[0]), str(user_input.current_password))
        if isinstance(is_password_valid, WrongCredentialsError):
            raise exceptions.WrongCredentialsError("Current password is incorrect")

        await update_email_or_password(
            recipe_user_id=user.login_methods[0].recipe_user_id,
            password=user_input.new_password,
            tenant_id_for_password_policy=user.tenant_ids[0],
        )

    # Return fresh data
    _user = await get_user(user_id)
    user_metadata = await get_user_metadata(user_id)
    updated_user = await GraphQLUser.from_supertokens(_user, user_metadata.metadata)

    return updated_user


async def accept_invitation(user: AcceptInvitationInput) -> bool:
    """Updates user metadata when invitation is accepted"""

    await update_user(UpdateUserInput(**strawberry.asdict(user)))

    current_metadata = await get_user_metadata(str(user.id))
    update_data = {
        "invite_status": InviteStatus.ACCEPTED.value,
        "invited": None,
        "pending_org_id": None,
    }
    await assign_role(user.id, Role.MEMBER)

    if "pending_org_id" in current_metadata.metadata:
        update_data["organization_id"] = current_metadata.metadata["pending_org_id"]

    if "inviter_name" in current_metadata.metadata:
        update_data["inviter_name"] = current_metadata.metadata["inviter_name"]

    await update_user_metadata(str(user.id), update_data)
    return True


async def reject_invitation(user_id: str) -> bool:
    """Updates user metadata when invitation is rejected"""

    current_metadata = await get_user_metadata(user_id)
    update_data = {
        "invite_status": InviteStatus.REJECTED.value,
        "invited": True,
    }

    if "pending_org_id" in current_metadata.metadata:
        update_data["pending_org_id"] = current_metadata.metadata["pending_org_id"]

    if "inviter_name" in current_metadata.metadata:
        update_data["inviter_name"] = current_metadata.metadata["inviter_name"]

    await update_user_metadata(user_id, update_data)
    return True


def filter_users(users: list[GraphQLUser], filters: FilterBy) -> list[GraphQLUser]:
    filtered_users = users.copy()

    for _filter, fields in filters.items():
        if not fields:
            continue

        # Map frontend field names to model attributes
        field_mapping = {
            "timeJoined": "time_joined",
            "organizationId": "organization_id",
            "firstName": "first_name",
            "lastName": "last_name",
            "inviteStatus": "invite_status",
            "inviterName": "inviter_name",
        }

        for _field, value in fields.items():
            if not _field or value is UNSET:
                continue

            model_field = field_mapping.get(_field, _field)

            if _filter == "equal":
                filtered_users = [
                    user
                    for user in filtered_users
                    if (model_field == "role" and user.role and user.role.value.lower() == str(value).lower())
                    or (model_field != "role" and str(getattr(user, model_field, None)).lower() == str(value).lower())
                ]
            elif _filter == "contains":
                filtered_users = [
                    user
                    for user in filtered_users
                    if (model_field == "role" and user.role and value.lower() in user.role.value.lower())
                    or (model_field != "role" and value.lower() in str(getattr(user, model_field, "")).lower())
                ]
            elif _filter == "is_true":
                filtered_users = [user for user in filtered_users if bool(getattr(user, model_field, False)) == value]

    return filtered_users


def sort_users(users: list[GraphQLUser], sort_by: SortBy | None = None) -> list[GraphQLUser]:
    if not sort_by:
        return users

    sorted_users = users.copy()

    field = None
    reverse = False

    if sort_by.asc is not strawberry.UNSET:
        field = sort_by.asc
        reverse = False
    elif sort_by.dsc is not strawberry.UNSET:
        field = sort_by.dsc
        reverse = True

    if not field:
        return sorted_users

    field_mapping = {
        "name": "first_name",
        "firstName": "first_name",
        "lastName": "last_name",
        "timeJoined": "time_joined",
        "organizationId": "organization_id",
        "inviteStatus": "invite_status",
        "inviterName": "inviter_name",
    }

    sort_field = field_mapping.get(field, field)

    def get_sort_key(user):
        value = getattr(user, sort_field, None)
        if value is None:
            return (True, "")  # None values go last

        # Handle special cases
        if sort_field == "role":
            return (False, value.value if value else "")  # Convert enum to string value
        elif sort_field == "first_name" and field == "name":
            return (False, f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}")
        elif isinstance(value, (datetime, UUID)):
            return (False, str(value))
        else:
            return (False, str(value))

    sorted_users.sort(key=get_sort_key, reverse=reverse)
    return sorted_users


async def impersonate_user(request: Request, user_id: str) -> SessionContainer:
    user = await get_user(user_id)

    if not user:
        raise EntityNotFound(f"No user found with the provided ID: {user_id}", "Auth")

    return await create_new_session(
        request,
        "public",
        user.login_methods[0].recipe_user_id,
        {"isImpersonation": True},
    )


async def get_user_by_id(user_id: str) -> User:
    logger.debug(f"Looking up user by ID: {user_id}")
    user = await get_user(user_id)
    if user is None:
        logger.debug(f"No user found with ID: {user_id}")
    else:
        logger.debug(f"Found user with ID: {user_id}")
    return user


async def construct_graphql_user(user: User) -> GraphQLUser:
    metadata = (await get_user_metadata(user.id)).metadata
    logger.debug(f"Constructing GraphQLUser for {user.id} with metadata: {metadata}")
    return await GraphQLUser.from_supertokens(user, metadata)


async def get_all_users() -> list[User]:
    return (await get_users_newest_first("public", limit=500)).users
