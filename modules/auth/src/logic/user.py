import json
from logging import getLogger
from uuid import UUID

import strawberry
from fastapi.requests import Request
from strawberry import UNSET
from supertokens_python import RecipeUserId
from supertokens_python.recipe.emailpassword.asyncio import update_email_or_password, verify_credentials
from supertokens_python.recipe.emailpassword.interfaces import (
    WrongCredentialsError,
    PasswordPolicyViolationError,
    UpdateEmailOrPasswordEmailChangeNotAllowedError,
    EmailAlreadyExistsError,
    UnknownUserIdError,
)
from supertokens_python.recipe.session.asyncio import create_new_session
from supertokens_python.recipe.session.interfaces import SessionContainer
from supertokens_python.recipe.usermetadata.asyncio import update_user_metadata

from core import exceptions
from core.exceptions import EntityNotFound
from logic.roles import assign_role
from models import GraphQLUser, UpdateUserInput, InviteStatus, Role, AcceptInvitationInput
from models.sort_filter import FilterBy, SortBy
from core.cache import get_user_cache


logger = getLogger("main")


async def get_users(
    filter_by: FilterBy | None = None, sort_by: SortBy | None = None, limit: int | None = None, offset: int = 0
) -> tuple[list[GraphQLUser], int]:
    """Returns all Users & their metadata with total count
    filter
    sort
    offset
    limit
    """
    gql_users = []
    # Handle special case: ID filter with direct lookup
    # This optimizes performance for ID-based queries
    if filter_by and filter_by.equal and filter_by.equal.get("id"):
        return await _apply_id_filter_cached(filter_by)

    user_cache = get_user_cache()
    # Else fetch all users from cache and apply filters/sorting/pagination
    gql_users = await user_cache.get_all_users()

    if filter_by:
        gql_users = filter_users(gql_users, filter_by)
    if sort_by:
        gql_users = sort_users(gql_users, sort_by)
    # Store total count before pagination
    total_count = len(gql_users)
    # Apply pagination
    if limit is not None:
        gql_users = gql_users[offset : offset + limit]
    else:
        gql_users = gql_users[offset:]
    return gql_users, total_count


# Map frontend field names to model attributes
field_mapping = {
    "name": "first_name",
    "firstName": "first_name",
    "email": "email",
    "lastName": "last_name",
    "timeJoined": "time_joined",
    "invited": "invited",
    "organizationId": "organization_id",
    "inviteStatus": "invite_status",
    "inviterName": "inviter_name",
    "roles": "roles",
}


def filter_users(users: list[GraphQLUser], filters: FilterBy) -> list[GraphQLUser]:
    if not filters:
        return users
    filtered_users = users

    SUPPORTED_FILTERS = {"equal", "contains", "is_true"}

    for _filter, fields in filters.items():
        if not fields:
            continue

        # Raise error for unsupported filter types
        if _filter not in SUPPORTED_FILTERS:
            raise ValueError(
                f"Filter type '{_filter}' is not supported for in-memory user filtering. "
                f"Supported filters: {', '.join(SUPPORTED_FILTERS)}"
            )

        for _field, value in fields.items():
            if not _field or value is UNSET:
                continue

            model_field = field_mapping.get(_field, _field)
            if _field == "name":
                # special case for name which is not a field but a combination of first_name and last_name
                filtered_users = [
                    user
                    for user in filtered_users
                    if _matches_filter(
                        f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip().lower(),
                        value,
                        _filter,
                    )
                ]
            else:
                filtered_users = [
                    user for user in filtered_users if _matches_filter(getattr(user, model_field, None), value, _filter)
                ]

    return filtered_users


def _matches_filter(field_value, filter_value, filter_type: str) -> bool:
    """
    Check if field value matches the filter.
    Supports 'equal', 'contains', and 'is_true' filter types.
    Handles UUIDs, Enums, Lists, and basic string comparisons.
    """
    if field_value is None:
        return False

    # Handle is_true for boolean fields
    if filter_type == "is_true":
        return bool(field_value) == filter_value

    # Handle UUID - exact match
    if isinstance(field_value, UUID):
        field_str = str(field_value).lower()
        filter_str = str(filter_value).lower()
        if filter_type == "equal":
            return field_str == filter_str
        elif filter_type == "contains":
            return filter_str in field_str
        return False

    # Handle enum (InviteStatus, Role) - case-insensitive value comparison
    if hasattr(field_value, "value"):
        field_str = field_value.value.lower()
        filter_str = str(filter_value).lower()
        if filter_type == "equal":
            return field_str == filter_str
        elif filter_type == "contains":
            return filter_str in field_str
        return False
    # Handle list (roles field) - check if any item matches
    if isinstance(field_value, list):
        return any(_matches_filter(item, filter_value, filter_type) for item in field_value)

    # Default: case-insensitive string comparison
    field_str = str(field_value).lower()
    filter_str = str(filter_value).lower()
    if filter_type == "equal":
        return field_str == filter_str
    elif filter_type == "contains":
        return filter_str in field_str
    return False


def sort_users(users: list[GraphQLUser], sort_by: SortBy | None = None) -> list[GraphQLUser]:
    if not sort_by:
        return users

    field = sort_by.asc if sort_by.asc is not UNSET else sort_by.dsc
    reverse = sort_by.dsc is not UNSET
    sort_field = field_mapping.get(field, field)

    return sorted(
        users,
        key=lambda u: (getattr(u, sort_field, None) is None, str(getattr(u, sort_field, "") or "")),
        reverse=reverse,
    )


async def _apply_id_filter_cached(filter_by: FilterBy) -> tuple[list[GraphQLUser], int]:
    """Optimized user retrieval when filtering by ID using cache"""
    user_id = filter_by.equal.get("id")
    user_cache = get_user_cache()
    try:
        if gql_user := await user_cache.get_user(UUID(user_id)):
            return [gql_user], 1
        else:
            return [], 0
    except EntityNotFound as e:
        logger.warning(f"User not found in cache: {e}")
        raise e


async def update_user(user_input: UpdateUserInput) -> GraphQLUser:
    """Update user details & metadata"""

    metadata_update = strawberry.asdict(user_input)
    user_id = UUID(metadata_update.pop("id"))

    user_cache = get_user_cache()
    user = await user_cache.get_user(user_id)
    if not user:
        raise EntityNotFound(f"No user found with the provided ID: {user_input.id}", "Auth")

    # Store email before removing it from metadata_update
    new_email = metadata_update.get("email")
    current_email = user.email if user.email else None

    del metadata_update["current_password"]
    del metadata_update["new_password"]
    # Handle organization role removal if organization_id is unset or None
    # This ensures user roles stay in sync with organization membership
    # not sure if we need this
    # if metadata_update["organization_id"] is UNSET or metadata_update["organization_id"] is None:
    #     await remove_role(user_id, Role(role))

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
        email_update_result = await update_email_or_password(
            recipe_user_id=user.login_methods[0].recipe_user_id,
            email=str(new_email),
            tenant_id_for_password_policy=user.tenant_ids[0],
        )
        if isinstance(email_update_result, UnknownUserIdError):
            raise exceptions.UnknownUserError("User not found")
        if isinstance(email_update_result, UpdateEmailOrPasswordEmailChangeNotAllowedError):
            raise exceptions.UpdateEmailOrPasswordError(email_update_result.reason)
        if isinstance(email_update_result, EmailAlreadyExistsError):
            raise exceptions.EmailAlreadyInUseError("Email is already in use by another user")

        user_cache.reload_user(user_id)
        # Refresh user object after email update to ensure we have the latest email for password verification
        user = await user_cache.get_user(user_id)

    # Update password if current password and new password are provided
    if user_input.current_password and user_input.new_password:
        # Use the latest user object for password verification
        is_password_valid = await verify_credentials("public", str(user.emails[0]), str(user_input.current_password))
        if isinstance(is_password_valid, WrongCredentialsError):
            raise exceptions.WrongCredentialsError("Current password is incorrect")

        password_update_result = await update_email_or_password(
            recipe_user_id=user.login_methods[0].recipe_user_id,
            password=user_input.new_password,
            tenant_id_for_password_policy=user.tenant_ids[0],
        )
        if isinstance(password_update_result, UnknownUserIdError):
            raise exceptions.UnknownUserError("User not found")
        if isinstance(password_update_result, UpdateEmailOrPasswordEmailChangeNotAllowedError):
            raise exceptions.UpdateEmailOrPasswordError(password_update_result.reason)
        if isinstance(password_update_result, PasswordPolicyViolationError):
            raise exceptions.PasswordRequirementsViolationError(password_update_result.failure_reason)

        # Refresh user object after password update
        user_cache.reload_user(user_id)
        # Refresh user object after email update to ensure we have the latest email for password verification
        user = await user_cache.get_user(user_id)

    return user


async def accept_invitation(user: AcceptInvitationInput) -> bool:
    """Updates user metadata when invitation is accepted"""

    await update_user(UpdateUserInput(**strawberry.asdict(user)))
    user_cache = get_user_cache()
    user_cache.reload_user(user.id)
    user = await user_cache.get_user(user.id)
    update_data = {
        "invite_status": InviteStatus.ACCEPTED.value,
        "invited": None,
        "pending_org_id": None,
    }
    await assign_role(user.id, Role.MEMBER)

    if "pending_org_id" in user:
        update_data["organization_id"] = user.pending_org_id

    if "inviter_name" in user:
        update_data["inviter_name"] = user.inviter_name

    await update_user_metadata(str(user.id), update_data)
    return True


async def reject_invitation(user_id: str) -> bool:
    """Updates user metadata when invitation is rejected"""
    user_cache = get_user_cache()
    user = await user_cache.get_user(UUID(user_id))
    update_data = {
        "invite_status": InviteStatus.REJECTED.value,
        "invited": True,
    }

    if "pending_org_id" in user:
        update_data["pending_org_id"] = user.pending_org_id

    if "inviter_name" in user:
        update_data["inviter_name"] = user.inviter_name

    await update_user_metadata(user_id, update_data)
    await user_cache.reload_user(UUID(user_id))
    return True


async def impersonate_user(request: Request, user_id: str) -> SessionContainer:
    user_cache = get_user_cache()
    user = await user_cache.get_user(user_id)

    if not user:
        raise EntityNotFound(f"No user found with the provided ID: {user_id}", "Auth")

    return await create_new_session(
        request,
        "public",
        RecipeUserId(str(user.id)),
        {"isImpersonation": True},
    )
