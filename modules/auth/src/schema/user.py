import logging

from strawberry.types import Info

from core.context import get_user
from logic import (
    update_user,
    invite_users,
    accept_invitation,
    reject_invitation,
    resend_invitation,
    impersonate_user,
)
from models import (
    GraphQLUser,
    UpdateUserInput,
    InviteUsersInput,
    InviteResult,
    AcceptInvitationInput,
)

logger = logging.getLogger("main")


async def update_user_mutation(user_input: UpdateUserInput) -> GraphQLUser:
    """Update user details"""

    return await update_user(user_input)


async def invite_users_mutation(info: Info, input: InviteUsersInput) -> list[InviteResult]:
    """Invite users to the organization"""
    user = get_user(info)
    results = await invite_users(input.emails, user.id, info.context.get("request"))
    return results


async def accept_invitation_mutation(user: AcceptInvitationInput) -> bool:
    """Accept an invitation"""

    result = await accept_invitation(user)
    logger.info(f"Invitation accepted by {user.id}")

    return result


async def reject_invitation_mutation(user_id: str) -> bool:
    """Reject an invitation"""

    result = await reject_invitation(user_id)
    logger.info(f"Invitation rejected by {user_id}")

    return result


async def resend_invitation_mutation(info: Info, user_id: str) -> InviteResult:
    """Resend an invitation"""

    result = await resend_invitation(user_id=user_id, request=info.context.get("request"))
    return result


async def impersonate_mutation(info: Info, user_id: str) -> bool:
    """Impersonate a different user"""

    session = await impersonate_user(info.context.get("request"), user_id)

    logger.info(f"User {user_id} impersonated by {get_user(info).id}")

    return True if session else False
