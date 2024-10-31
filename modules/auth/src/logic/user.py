from datetime import datetime

import strawberry
from strawberry import UNSET
from supertokens_python.asyncio import get_users_newest_first
from supertokens_python.recipe.emailpassword.asyncio import update_email_or_password, sign_in
from supertokens_python.recipe.usermetadata.asyncio import update_user_metadata, get_user_metadata

from core.exceptions import EntityNotFound
from models import GraphQLUser, UserFilters, UserSort, UpdateUserInput, InviteStatus, Role, AcceptInvitationInput
from models.sort_filter import FilterOptions


async def get_users(filters: UserFilters | None = None, sort_by: UserSort | None = None) -> list[GraphQLUser]:
    """Returns all Users & their metadata"""

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
        pending_org_id = metadata_response.metadata.get("pending_org_id")
        invited = metadata_response.metadata.get("invited", False)
        invite_status = metadata_response.metadata.get("invite_status", InviteStatus.NONE.value)
        inviter_name = metadata_response.metadata.get("inviter_name", "")
        role = metadata_response.metadata.get("role", Role.MEMBER.value)

        effective_org_id = organization_id if not invited else pending_org_id

        user = GraphQLUser(
            id=user_id,
            email=user_data.get("email"),
            time_joined=datetime.fromtimestamp(round(user_data.get("timeJoined", 0) / 1000)),
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

    return gql_users


async def update_user(user_input: UpdateUserInput) -> GraphQLUser:
    """Update user details & metadata"""

    metadata_update = {}
    if user_input.first_name is not None:
        metadata_update["first_name"] = user_input.first_name
    if user_input.last_name is not None:
        metadata_update["last_name"] = user_input.last_name
    if user_input.email is not None:
        metadata_update["email"] = user_input.email
    if user_input.invited is not None:
        metadata_update["invited"] = user_input.invited
    if user_input.invite_status is not None:
        metadata_update["invite_status"] = user_input.invite_status.value
    if user_input.inviter_name is not None:
        metadata_update["inviter_name"] = user_input.inviter_name
    if user_input.role is not None:
        metadata_update["role"] = user_input.role.value
    if user_input.organization_id is not UNSET:
        metadata_update["organization_id"] = user_input.organization_id
        if user_input.organization_id is None:
            metadata_update["role"] = None
    if metadata_update:
        await update_user_metadata(str(user_input.id), metadata_update)

    # Update password if current password and new password are provided

    if user_input.current_password and user_input.new_password:
        user_email = (await get_users(UserFilters(id=FilterOptions(equal=str(user_input.id)))))[0].email
        await sign_in("public", str(user_email), str(user_input.current_password))
        await update_email_or_password(
            user_id=str(user_input.id),
            email=user_email,
            password=user_input.new_password,
        )

    user_data = await get_users(UserFilters(id=FilterOptions(equal=str(user_input.id))))

    if not user_data:
        raise EntityNotFound("No user found with the provided ID", "Auth")

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
    filtered_users = []

    for filter_key, filter_value in filters.__dict__.items():
        if filter_value and filter_value.equal is not None:
            if filter_key == "organizationId":
                filtered_users = [
                    user for user in filtered_users if str(user.organization_id) == str(filter_value.equal)
                ]
            elif hasattr(users[0], filter_key):
                filtered_users = [user for user in users if getattr(user, filter_key) == filter_value.equal]

    return filtered_users
