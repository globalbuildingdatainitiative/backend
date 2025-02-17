import logging
from typing import List
from uuid import UUID

from starlette.requests import Request
from supertokens_python.asyncio import get_user, list_users_by_account_info
from supertokens_python.recipe.emailpassword.asyncio import (
    send_reset_password_email,
    sign_up,
)
from supertokens_python.recipe.emailpassword.interfaces import SignUpOkResult
from supertokens_python.recipe.usermetadata.asyncio import update_user_metadata, get_user_metadata
from supertokens_python.types import AccountInfo

from core.auth import FAKE_PASSWORD
from core.exceptions import UserHasNoOrganization, InvitationFailed
from models import InviteStatus, InviteResult


logger = logging.getLogger("main")


async def invite_users(emails: List[str], inviter_id: UUID, request: Request) -> list[InviteResult]:
    inviter_metadata = await get_user_metadata(str(inviter_id))
    inviter_org_id = inviter_metadata.metadata.get("organization_id")
    inviter_first_name = inviter_metadata.metadata.get("first_name", "")
    inviter_last_name = inviter_metadata.metadata.get("last_name", "")
    inviter_name = f"{inviter_first_name} {inviter_last_name}".strip()

    if not inviter_org_id:
        raise UserHasNoOrganization("User doesn't belong to an organization", "Auth")

    results = []
    for email in emails:
        try:
            existing_users = await list_users_by_account_info("public", AccountInfo(email=email))
            if existing_users:
                user_id = existing_users[0].id
            else:
                # Creating a user with fake password
                sign_up_result = await sign_up("public", email, FAKE_PASSWORD)

                if not isinstance(sign_up_result, SignUpOkResult):
                    raise InvitationFailed("Failed to sign up user", "Auth")

                user_id = sign_up_result.user.id

            # Updating the user-metadata with invitation details
            await update_user_metadata(
                user_id,
                {
                    "invited": True,
                    "invite_status": InviteStatus.PENDING.value,
                    "inviter_id": str(inviter_id),
                    "inviter_name": inviter_name,
                    "pending_org_id": str(inviter_org_id),
                },
            )
            await send_reset_password_email(
                "public", user_id, email, user_context={"user_id": user_id, "request": request}
            )
            results.append(InviteResult(email=email, status="invited", message=""))

        except Exception as e:
            raise InvitationFailed(f"Failed to invite user {email} due to : {str(e)}", "Auth")
    return results


async def resend_invitation(user_id: str, request: Request) -> InviteResult:
    user = await get_user(user_id)
    if not user:
        raise InvitationFailed("User not found", "Auth")

    user_email = user.emails[0]

    if not user_email:
        raise InvitationFailed("User not found or has no email", "Auth")

    user_metadata = await get_user_metadata(user_id)
    invite_status = user_metadata.metadata.get("invite_status", InviteStatus.NONE.value)

    if invite_status.lower() != "pending":
        raise InvitationFailed("User's invitation is not in pending state", "Auth")

    try:
        await send_reset_password_email(
            "public", user_id, user_email, user_context={"user_id": user_id, "request": request}
        )
        return InviteResult(email=user_email, status="resent", message="Invitation resent successfully")
    except Exception as e:
        logger.error(f"Failed to resend invitation to user {user_email}: {str(e)}")
        raise InvitationFailed(f"Failed to resend invitation to user {user_email} due to: {str(e)}", "Auth")
