import json
from datetime import datetime
from logging import getLogger
from uuid import UUID

import strawberry
from strawberry import UNSET
from supertokens_python.asyncio import get_user, get_users_newest_first
from supertokens_python.recipe.emailpassword.asyncio import update_email_or_password, verify_credentials
from supertokens_python.recipe.emailpassword.interfaces import WrongCredentialsError
from supertokens_python.recipe.session.asyncio import create_new_session
from supertokens_python.recipe.session.interfaces import SessionContainer
from supertokens_python.recipe.usermetadata.asyncio import update_user_metadata, get_user_metadata
from fastapi.requests import Request
from core import exceptions
from core.exceptions import EntityNotFound
from models import GraphQLUser, UserFilters, UserSort, UpdateUserInput, InviteStatus, Role, AcceptInvitationInput
from models.sort_filter import FilterOptions

logger = getLogger("main")


async def get_users(filters: UserFilters | None = None, sort_by: UserSort | None = None) -> list[GraphQLUser]:
    """Returns all Users & their metadata"""

    users = await get_users_newest_first("public")

    gql_users = []

    for user in users.users:
        # Fetch metadata for each user
        metadata_response = await get_user_metadata(user.id)
        first_name = metadata_response.metadata.get("first_name")
        last_name = metadata_response.metadata.get("last_name")
        organization_id = metadata_response.metadata.get("organization_id")
        pending_org_id = metadata_response.metadata.get("pending_org_id")
        invited = metadata_response.metadata.get("invited", False)
        invite_status = metadata_response.metadata.get("invite_status", InviteStatus.NONE.value)
        inviter_name = metadata_response.metadata.get("inviter_name", "")
        role = metadata_response.metadata.get("role", Role.MEMBER.value)

        effective_org_id = organization_id if not invited else pending_org_id

        user = GraphQLUser(
            id=user.id,
            email=user.emails[0],
            time_joined=datetime.fromtimestamp(round(user.time_joined / 1000)),
            first_name=first_name,
            last_name=last_name,
            organization_id=effective_org_id,
            invited=invited,
            invite_status=InviteStatus(invite_status.lower()),
            inviter_name=inviter_name,
            role=Role(role.lower()) if role else Role.MEMBER,
        )

        gql_users.append(user)

    if filters:
        gql_users = filter_users(gql_users, filters)
    if sort_by:
        gql_users = sort_users(gql_users, sort_by)

    return gql_users


async def update_user(user_input: UpdateUserInput) -> GraphQLUser:
    """Update user details & metadata"""

    metadata_update = strawberry.asdict(user_input)
    user_id = str(metadata_update.pop("id"))

    user = await get_user(user_id)
    if not user:
        raise EntityNotFound(f"No user found with the provided ID: {user_input.id}", "Auth")

    del metadata_update["current_password"]
    del metadata_update["new_password"]
    if metadata_update["organization_id"] is UNSET or metadata_update["organization_id"] is None:
        metadata_update["role"] = metadata_update["organization_id"]

    def custom_serializer(obj):
        if isinstance(obj, InviteStatus):
            return obj.value

    metadata_update = json.dumps(
        {key: value for key, value in metadata_update.items() if value is not UNSET}, default=custom_serializer
    )

    if metadata_update:
        await update_user_metadata(user_id, json.loads(metadata_update))

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

    user_data = await get_users(UserFilters(id=FilterOptions(equal=user_id)))

    return user_data[0]


async def accept_invitation(user: AcceptInvitationInput) -> bool:
    """Updates user metadata when invitation is accepted"""

    await update_user(UpdateUserInput(**strawberry.asdict(user)))

    current_metadata = await get_user_metadata(str(user.id))
    update_data = {
        "invite_status": InviteStatus.ACCEPTED.value,
        "invited": None,
        "pending_org_id": None,
        "role": Role.MEMBER.value,
    }

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


def filter_users(users: list[GraphQLUser], filters: UserFilters) -> list[GraphQLUser]:
    filtered_users = users.copy()

    for field_name, filter_value in filters.__dict__.items():
        if not filter_value:
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

        model_field = field_mapping.get(field_name, field_name)

        if filter_value.equal is not None:
            filtered_users = [
                user
                for user in filtered_users
                if (model_field == "role" and user.role and user.role.value.lower() == str(filter_value.equal).lower())
                or (
                    model_field != "role"
                    and str(getattr(user, model_field, None)).lower() == str(filter_value.equal).lower()
                )
            ]
        elif filter_value.contains is not None:
            filtered_users = [
                user
                for user in filtered_users
                if (model_field == "role" and user.role and filter_value.contains.lower() in user.role.value.lower())
                or (
                    model_field != "role"
                    and filter_value.contains.lower() in str(getattr(user, model_field, "")).lower()
                )
            ]
        elif filter_value.is_true is not None:
            filtered_users = [
                user for user in filtered_users if bool(getattr(user, model_field, False)) == filter_value.is_true
            ]

    return filtered_users


def sort_users(users: list[GraphQLUser], sort_by: UserSort | None = None) -> list[GraphQLUser]:
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
