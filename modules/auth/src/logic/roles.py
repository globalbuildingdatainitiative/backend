from logging import getLogger
from uuid import UUID

from aiocache import cached

logger = getLogger("main")


async def create_roles():
    from supertokens_python.recipe.userroles.asyncio import create_new_role_or_add_permissions

    roles = [{"name": "admin", "permissions": ["all"]}]

    for role in roles:
        response = await create_new_role_or_add_permissions(role.get("name"), role.get("permissions"))
        if not response.created_new_role:
            logger.debug(f"Role: {role.get('name')} already exists")
        else:
            logger.info(f"Role: {role.get('name')} with permissions: {role.get('permissions')} created")


@cached(ttl=60)
async def check_is_admin(user_id: str | UUID) -> bool:
    """Check if the user is an admin"""
    from supertokens_python.recipe.userroles.asyncio import get_roles_for_user

    if isinstance(user_id, UUID):
        user_id = str(user_id)

    _user = await get_roles_for_user("public", user_id)
    if "admin" in _user.roles:
        return True

    return False
