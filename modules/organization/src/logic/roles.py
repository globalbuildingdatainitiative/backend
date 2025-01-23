from enum import Enum
from logging import getLogger
from uuid import UUID

from supertokens_python.recipe.userroles.asyncio import add_role_to_user
from supertokens_python.recipe.userroles.interfaces import UnknownRoleError

from core.exceptions import EntityNotFound

logger = getLogger("main")


class Role(Enum):
    OWNER = "owner"
    MEMBER = "member"
    ADMIN = "admin"


async def assign_role(user_id: str | UUID, role: Role):
    if isinstance(user_id, UUID):
        user_id = str(user_id)

    response = await add_role_to_user("public", user_id, role.value)

    if isinstance(response, UnknownRoleError):
        logger.warning(f"Role: {role.value} does not exist")
        raise EntityNotFound(f"Role: {role.value} does not exist", "Auth")
    elif response.did_user_already_have_role:
        logger.info(f"User: {user_id} have already been assigned role of {role.value}.")
    else:
        logger.info(f"Successfully assigned role of {role.value} to user: {user_id}.")
