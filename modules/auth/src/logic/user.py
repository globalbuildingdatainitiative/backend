import json
from copy import deepcopy
from datetime import datetime
from logging import getLogger
from uuid import UUID

import strawberry
from fastapi.requests import Request
from sqlmodel import select, col, or_
from sqlmodel.ext.asyncio.session import AsyncSession
from strawberry import UNSET
from supertokens_python.asyncio import get_user
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
from supertokens_python.recipe.usermetadata.asyncio import (
    update_user_metadata as _update_user_metadata,
    get_user_metadata,
)
from supertokens_python.recipe.userroles.asyncio import get_roles_for_user
from supertokens_python.types import User

from core import exceptions
from core.connection import get_postgres_engine
from core.exceptions import EntityNotFound
from logic.roles import assign_role, remove_role
from logic.utils import to_snake
from models import GraphQLUser, UpdateUserInput, InviteStatus, Role, AcceptInvitationInput
from models.sort_filter import FilterBy, SortBy
from models.user import UserMetadata

logger = getLogger("main")


async def get_users(
    filter_by: FilterBy | None = None, sort_by: SortBy | None = None, limit: int | None = None, offset: int = 0
) -> list[GraphQLUser]:
    """Returns all Users & their metadata"""

    logger.debug(f"Fetching users with filters: {filter_by} and sort_by: {sort_by}")

    async with AsyncSession(get_postgres_engine()) as session:
        query = select(UserMetadata)

        if filter_by:
            for _filter, fields in filter_by.items():
                if not fields:
                    continue

                for _field, value in fields.items():
                    if not _field or value is UNSET:
                        continue
                    _field = to_snake(_field)
                    if isinstance(value, UUID):
                        value = str(value)

                    if _filter == "contains":
                        if _field == "name":
                            query = query.where(
                                or_(_get_field("first_name").icontains(value), _get_field("last_name").icontains(value))
                            )
                        else:
                            query = query.where(_get_field(_field).icontains(value))
                    elif _filter == "equal":
                        query = query.where(_get_field(_field) == value)
                    elif _filter == "not_equal":
                        query = query.where(_get_field(_field) != value)
                    elif _filter == "_in":
                        query = query.where(_get_field(_field).in_(value))
                    elif _filter == "gt":
                        query = query.where(_get_field(_field) > value)
                    elif _filter == "gte":
                        query = query.where(_get_field(_field) >= value)
                    elif _filter == "lt":
                        query = query.where(_get_field(_field) < value)
                    elif _filter == "lte":
                        query = query.where(_get_field(_field) <= value)
                    elif _filter == "is_true" and value is not None:
                        query = query.where(_get_field(_field) is True)

        if sort_by and sort_by.asc:
            query = query.order_by(col(sort_by.asc))
        elif sort_by and sort_by.dsc:
            query = query.order_by(col(sort_by.dsc).desc())
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        users = (await session.exec(query)).all()

    logger.debug(f"Found {len(users)} users")
    gql_users = []
    for user in users:
        try:
            gql_user = await GraphQLUser.from_sqlmodel(user)
            gql_users.append(gql_user)
        except Exception as e:
            logger.warning(f"Failed to construct GraphQLUser for user {user.id}: {e}")
            continue
    return gql_users


def _get_field(field):
    if field == "id":
        return UserMetadata.id
    else:
        return UserMetadata.meta_data[field].astext


async def _apply_additional_id_filters(gql_users: list[GraphQLUser], filter_by: FilterBy | None) -> list[GraphQLUser]:
    """
    Apply additional filtering logic for ID-based queries with multiple filters.

    When querying by ID with additional filters, this function ensures that:
    1. Additional filters are applied selectively to avoid losing the user
    2. If additional filters contradict the ID filter, the original user is preserved

    Args:
        gql_users: List of GraphQLUser objects from initial filtering
        filter_by: FilterBy object containing the filter criteria

    Returns:
        List of GraphQLUser objects after applying additional ID filter logic
    """
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
        if isinstance(obj, UUID):
            return str(obj)

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
        await update_user_metadata(user_id, {"email": str(new_email)})
        # Refresh user object after email update to ensure we have the latest email for password verification
        user = await get_user(user_id)

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
        user = await get_user(user_id)

    # Use the latest user object instead of fetching again
    user_metadata = await get_user_metadata(user_id)
    updated_user = await GraphQLUser.from_supertokens(user, user_metadata.metadata)

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


async def update_user_metadata(user_id: str, metadata: dict):
    logger.debug(f"Updating user metadata for {user_id}")
    async with AsyncSession(get_postgres_engine()) as session:
        user = await session.get(UserMetadata, user_id)
        if not user:
            raise EntityNotFound(f"User metadata not found for user_id: {user_id}", "Auth")
        _metadata = deepcopy(user.meta_data)

        for key, value in metadata.items():
            if value is None:
                try:
                    del _metadata[key]
                except KeyError:
                    continue
            else:
                _metadata[key] = value

        user.meta_data = _metadata
        session.add(user)
        await session.commit()
        await session.refresh(user)

    await _update_user_metadata(user_id, metadata)
    return metadata


async def create_user_meta_data(user_id: str, meta_data: dict) -> UserMetadata:
    logger.info(f"Creating user metadata for {user_id}")
    async with AsyncSession(get_postgres_engine()) as session:
        user = UserMetadata(id=user_id, meta_data=meta_data)
        session.add(user)
        await session.commit()
        await session.refresh(user)

    await _update_user_metadata(user_id, meta_data)
    return user
