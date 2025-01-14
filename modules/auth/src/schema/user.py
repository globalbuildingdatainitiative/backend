import logging

from strawberry.types import Info
from core.context import get_user
from logic import (
    get_users,
    update_user,
    invite_users,
    accept_invitation,
    reject_invitation,
    resend_invitation,
    impersonate_user,
)
from logic.roles import check_is_admin
from models import (
    GraphQLUser,
    UserFilters,
    UserSort,
    UpdateUserInput,
    InviteUsersInput,
    InviteResult,
    AcceptInvitationInput,
)
from models.sort_filter import FilterOptions

logger = logging.getLogger("main")


async def users_query(
    info: Info, filters: UserFilters | None = None, sort_by: UserSort | None = None
) -> list[GraphQLUser]:
    """Returns all Users"""

    is_admin = await check_is_admin(get_user(info).id)
    if is_admin:
        return await get_users(filters, sort_by)
    else:
        filters = filters or UserFilters()
        filters.organization_id = FilterOptions(equal=get_user(info).organization_id)
        return await get_users(filters, sort_by)


async def update_user_mutation(info: Info, user_input: UpdateUserInput) -> GraphQLUser:
    """Update user details"""

    return await update_user(info.context.get("request"), user_input)


async def invite_users_mutation(info: Info, input: InviteUsersInput) -> list[InviteResult]:
    """Invite users to the organization"""
    user = get_user(info)
    results = await invite_users(input.emails, user.id, info.context.get("request"))
    return results


async def accept_invitation_mutation(user: AcceptInvitationInput) -> bool:
    """Accept an invitation"""
    result = await accept_invitation(user)
    return result


async def reject_invitation_mutation(user_id: str) -> bool:
    """Reject an invitation"""
    result = await reject_invitation(user_id)
    return result


async def resend_invitation_mutation(info: Info, user_id: str) -> InviteResult:
    """Resend an invitation"""

    result = await resend_invitation(user_id=user_id, request=info.context.get("request"))
    return result


async def impersonate_mutation(info: Info, user_id: str) -> bool:
    """Impersonate a different user"""

    return await impersonate_user(info.context.get("request"), None, user_id)
