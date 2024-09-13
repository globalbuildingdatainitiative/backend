'''''
from typing import List, Dict

from supertokens_python.recipe.emailpassword.asyncio import send_reset_password_email, sign_up, get_user_by_email
from supertokens_python.recipe.emailpassword.interfaces import SignUpOkResult
from supertokens_python.recipe.usermetadata.asyncio import update_user_metadata, get_user_metadata
import logging
from models import InviteStatus

FAKE_PASSWORD = "asokdA87fnf30efjoiOI**cwjkn"


async def invite_users(emails: List[str], inviter_id: str) -> List[Dict[str, str]]:
    inviter_metadata = await get_user_metadata(inviter_id)
    inviter_org_id = inviter_metadata.metadata.get("organization_id")

    if not inviter_org_id:
        raise ValueError("Inviter does not belong to an organization")

    results = []
    for email in emails:
        try:
            existing_user = await get_user_by_email("public", email)  # Added "public" as the first argument

            if existing_user:
                user_id = existing_user.user_id
            else:
                sign_up_result = await sign_up("public", email, FAKE_PASSWORD)
                if not isinstance(sign_up_result, SignUpOkResult):
                    raise Exception("Failed to sign up user")
                user_id = sign_up_result.user.user_id

            await update_user_metadata(user_id, {
                "invited": True,
                "invite_status": InviteStatus.PENDING.value,
                "inviter_id": inviter_id,
                "pending_org_id": str(inviter_org_id)
            })

            await send_reset_password_email("public", user_id, user_context={"user_id": user_id})
            logging.info(f"Sent invitation email to {email} with user_id {user_id}")
            results.append({"email": email, "status": "invited"})

        except Exception as e:
            logging.error(f"Error inviting user {email}: {str(e)}")
            results.append({"email": email, "status": "error", "message": str(e)})

    return results
'''

'''''
from typing import List, Dict

from supertokens_python.recipe.emailpassword.asyncio import send_reset_password_email, sign_up, get_user_by_email
from supertokens_python.recipe.emailpassword.interfaces import SignUpOkResult
from supertokens_python.recipe.usermetadata.asyncio import update_user_metadata, get_user_metadata
import logging
from models import InviteStatus

FAKE_PASSWORD = "asokdA87fnf30efjoiOI**cwjkn"


async def invite_users(emails: List[str], inviter_id: str) -> List[Dict[str, str]]:
    inviter_metadata = await get_user_metadata(inviter_id)
    inviter_org_id = inviter_metadata.metadata.get("organization_id")
    inviter_first_name = inviter_metadata.metadata.get("first_name", "")
    inviter_last_name = inviter_metadata.metadata.get("last_name", "")
    inviter_name = f"{inviter_first_name} {inviter_last_name}".strip()

    logging.info(f"Inviter ID: {inviter_id}")
    logging.info(f"Inviter metadata: {inviter_metadata.metadata}")
    logging.info(f"Inviter name: {inviter_name}")

    if not inviter_org_id:
        raise ValueError("Inviter does not belong to an organization")

    results = []
    for email in emails:
        try:
            existing_user = await get_user_by_email("public", email)  # Added "public" as the first argument

            if existing_user:
                user_id = existing_user.user_id
            else:
                sign_up_result = await sign_up("public", email, FAKE_PASSWORD)
                if not isinstance(sign_up_result, SignUpOkResult):
                    raise Exception("Failed to sign up user")
                user_id = sign_up_result.user.user_id

            await update_user_metadata(user_id, {
                "invited": True,
                "invite_status": InviteStatus.PENDING.value,
                "inviter_id": inviter_id,
                "inviter_name": inviter_name,
                "pending_org_id": str(inviter_org_id)
            })

            updated_metadata = await get_user_metadata(user_id)
            logging.info(f"Updated user metadata for {email}: {updated_metadata.metadata}")

            await send_reset_password_email("public", user_id, user_context={"user_id": user_id})
            logging.info(f"Sent invitation email to {email} with user_id {user_id}")
            results.append({"email": email, "status": "invited"})

        except Exception as e:
            logging.error(f"Error inviting user {email}: {str(e)}")
            results.append({"email": email, "status": "error", "message": str(e)})

    return results
'''

from typing import List, Dict

from supertokens_python.recipe.emailpassword.asyncio import send_reset_password_email, sign_up, get_user_by_email
from supertokens_python.recipe.emailpassword.interfaces import SignUpOkResult
from supertokens_python.recipe.usermetadata.asyncio import update_user_metadata, get_user_metadata
import logging
from models import InviteStatus

FAKE_PASSWORD = "asokdA87fnf30efjoiOI**cwjkn"


async def invite_users(emails: List[str], inviter_id: str) -> List[Dict[str, str]]:
    inviter_metadata = await get_user_metadata(inviter_id)
    inviter_org_id = inviter_metadata.metadata.get("organization_id")
    inviter_first_name = inviter_metadata.metadata.get("first_name", "")
    inviter_last_name = inviter_metadata.metadata.get("last_name", "")
    inviter_name = f"{inviter_first_name} {inviter_last_name}".strip()

    logging.info(f"Inviter ID: {inviter_id}")
    logging.info(f"Inviter metadata: {inviter_metadata.metadata}")
    logging.info(f"Inviter name: {inviter_name}")

    if not inviter_org_id:
        raise ValueError("Inviter does not belong to an organization")

    results = []
    for email in emails:
        try:
            existing_user = await get_user_by_email("public", email)

            if existing_user:
                user_id = existing_user.user_id
                # Update existing user's metadata
                await update_user_metadata(user_id, {
                    "invited": True,
                    "invite_status": InviteStatus.PENDING.value,
                    "inviter_id": inviter_id,
                    "inviter_name": inviter_name,
                    "pending_org_id": str(inviter_org_id)
                })
            else:
                sign_up_result = await sign_up("public", email, FAKE_PASSWORD)
                if not isinstance(sign_up_result, SignUpOkResult):
                    raise Exception("Failed to sign up user")
                user_id = sign_up_result.user.user_id
                # Set metadata for new user
                await update_user_metadata(user_id, {
                    "invited": True,
                    "invite_status": InviteStatus.PENDING.value,
                    "inviter_id": inviter_id,
                    "inviter_name": inviter_name,
                    "pending_org_id": str(inviter_org_id)
                })

            updated_metadata = await get_user_metadata(user_id)
            logging.info(f"Updated user metadata for {email}: {updated_metadata.metadata}")

            await send_reset_password_email("public", user_id, user_context={"user_id": user_id})
            logging.info(f"Sent invitation email to {email} with user_id {user_id}")
            results.append({"email": email, "status": "invited"})

        except Exception as e:
            logging.error(f"Error inviting user {email}: {str(e)}")
            results.append({"email": email, "status": "error", "message": str(e)})

    return results