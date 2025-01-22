import logging

from logic.roles import get_roles, assign_role
from models import RolePermission, Role

logger = logging.getLogger("main")


async def roles_query() -> list[RolePermission]:
    """Returns all Roles and their permissions"""

    roles = await get_roles()

    logger.info(f"Got {len(roles)} roles")
    return roles


async def make_admin_mutation(user_id: str) -> bool:
    """Assign admin role to a user"""

    await assign_role(user_id, Role.ADMIN)

    logger.info(f"User {user_id} became admin")

    return True
