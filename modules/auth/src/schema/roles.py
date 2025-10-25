import logging

from logic.roles import get_roles, assign_role, remove_role
from core.cache import get_user_cache
from models import RolePermission, Role
import uuid

logger = logging.getLogger("main")


async def roles_query() -> list[RolePermission]:
    """Returns all Roles and their permissions"""

    roles = await get_roles()

    logger.info(f"Got {len(roles)} roles")
    return roles


async def make_admin_mutation(user_id: str) -> bool:
    """Assign admin role to a user"""

    await assign_role(user_id, Role.ADMIN)
    user_cache = get_user_cache()
    await user_cache.reload_user(user_id)
    logger.info(f"User {user_id} became admin")

    return True


async def unmake_admin_mutation(user_id: str) -> bool:
    """Remove admin role from a user"""

    await remove_role(user_id, Role.ADMIN)
    user_cache = get_user_cache()
    await user_cache.reload_user(user_id)
    # just to be sure, we do not remove other roles check if roles empty
    user = await user_cache.get_user(uuid.UUID(user_id))
    if user and not user.roles:
        # assign member role if no roles left
        await assign_role(user_id, Role.MEMBER)
        await user_cache.reload_user(user_id)

    logger.info(f"User {user_id} is no longer admin")

    return True
