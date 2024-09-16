from typing import List, Dict
from uuid import UUID
from supertokens_python.recipe.emailpassword.asyncio import send_reset_password_email, sign_up, get_user_by_email
from supertokens_python.recipe.emailpassword.interfaces import SignUpOkResult
from supertokens_python.recipe.usermetadata.asyncio import update_user_metadata, get_user_metadata

from core.exceptions import UserHasNoOrganization, InvitationFailed
from models import InviteStatus, InviteResult


FAKE_PASSWORD = "asokdA87fnf30efjoiOI**cwjkn"


async def invite_users(emails: List[str], inviter_id: UUID) -> List[Dict[str, str]]:
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
            existing_user = await get_user_by_email("public", email)
            if existing_user:
                user_id = existing_user.user_id
            else:
                # Creating a user with fake password
                sign_up_result = await sign_up("public", email, FAKE_PASSWORD)

                if not isinstance(sign_up_result, SignUpOkResult):
                    raise Exception("Failed to sign up user")

                user_id = sign_up_result.user.user_id

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
            await send_reset_password_email("public", user_id, user_context={"user_id": user_id})
            results.append(InviteResult(email=email, status="invited", message=""))

        except Exception as e:
            raise InvitationFailed(f"Failed to invite user {email} due to : {str(e)}", "Auth")
    return results
