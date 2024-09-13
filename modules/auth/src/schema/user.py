from logic import get_users, update_user, invite_users, reject_invitation
from models import GraphQLUser, UserFilters, UserSort, UpdateUserInput, InviteUsersInput, InviteUsersResponse, InviteResult
from strawberry.types import Info
from supertokens_python.recipe.session.asyncio import get_session
from supertokens_python.recipe.session.exceptions import UnauthorisedError
from supertokens_python.recipe.usermetadata.asyncio import update_user_metadata, get_user_metadata
from models import InviteStatus


async def users_query(filters: UserFilters | None = None, sort_by: UserSort | None = None) -> list[GraphQLUser]:
    """Returns all Users"""

    return await get_users(filters, sort_by)


async def update_user_mutation(user_input: UpdateUserInput) -> GraphQLUser:
    """Update user details"""
    return await update_user(user_input)


async def invite_users_mutation(info: Info, input: InviteUsersInput) -> InviteUsersResponse:
    """Invite users to the organization"""
    try:
        session = await get_session(info.context["request"])
        if session is None:
            raise Exception("User not authenticated")

        user_id = session.get_user_id()
        results = await invite_users(input.emails, user_id)
        return InviteUsersResponse(results=[InviteResult(**r) for r in results])
    except UnauthorisedError:
        raise Exception("User not authenticated")


async def accept_invitation_mutation(info: Info, user_id: str) -> bool:
    """Accept an invitation"""
    try:
        user_metadata = await get_user_metadata(user_id)
        pending_org_id = user_metadata.metadata.get("pending_org_id")

        if not pending_org_id:
            raise Exception("No pending invitation found for this user")

        await update_user_metadata(user_id, {
            "invite_status": InviteStatus.ACCEPTED.value,
            "organization_id": pending_org_id,
            "pending_org_id": None,
        })
        return True
    except Exception as e:
        raise Exception(f"Error accepting invitation: {str(e)}")


async def reject_invitation_mutation(info: Info, user_id: str) -> bool:
    """Reject an invitation"""
    try:
        result = await reject_invitation(user_id)
        return result
    except Exception as e:
        raise Exception(f"Error rejecting invitation: {str(e)}")