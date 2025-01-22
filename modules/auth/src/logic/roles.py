from logging import getLogger
from uuid import UUID

from aiocache import cached
from supertokens_python.recipe.userroles.asyncio import get_roles_for_user, add_role_to_user
from supertokens_python.recipe.userroles.interfaces import UnknownRoleError

from core.exceptions import EntityNotFound

logger = getLogger("main")


async def create_roles():
    from supertokens_python.recipe.userroles.asyncio import create_new_role_or_add_permissions

    roles = [
        {"name": "admin", "permissions": ["all"]},
        {"name": "owner", "permissions": [
            "contributions::read", "contributions::write", "contributions::update", "contributions::delete",
            "members::read", "members::write", "members::update", "members::delete",
        ]},
        {"name": "member", "permissions": [
            "contributions::read", "contributions::write", "contributions::update", "contributions::delete",
            "members::read", "members::write", "members::update",
        ]},
    ]

    for role in roles:
        response = await create_new_role_or_add_permissions(role.get("name"), role.get("permissions"))
        if not response.created_new_role:
            logger.debug(f"Role: {role.get('name')} already exists")
        else:
            logger.info(f"Role: {role.get('name')} with permissions: {role.get('permissions')} created")


async def assign_role(user_id: str, role: str):
    response = await add_role_to_user("public", user_id, role)

    if isinstance(response, UnknownRoleError):
        logger.warning(f"Role: {role} does not exist")
        raise EntityNotFound(f"Role: {role} does not exist", "Auth")
    elif response.did_user_already_have_role:
        logger.info(f"User: {user_id} have already been assigned role of {role}.")
    else:
        logger.info(f"Successfully assigned role of {role} to user: {user_id}.")


@cached(ttl=60)
async def check_is_admin(user_id: str | UUID) -> bool:
    """Check if the user is an admin"""

    if isinstance(user_id, UUID):
        user_id = str(user_id)

    _user = await get_roles_for_user("public", user_id)
    if "admin" in _user.roles:
        return True

    return False
