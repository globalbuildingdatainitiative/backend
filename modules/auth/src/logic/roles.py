from logging import getLogger
from uuid import UUID

from aiocache import cached
from supertokens_python.recipe.userroles.asyncio import (
    get_roles_for_user,
    add_role_to_user,
    remove_user_role,
    get_all_roles,
    get_permissions_for_role,
)
from supertokens_python.recipe.userroles.interfaces import UnknownRoleError

from core.exceptions import EntityNotFound
from models import Role, Permission, RolePermission

logger = getLogger("main")


@cached(ttl=60 * 10)
async def get_roles():
    """Get all roles and their permissions"""
    logger.debug("Fetching all roles and their permissions")

    roles = (await get_all_roles()).roles
    roles_and_permissions = [
        RolePermission(
            name=Role(role),
            permissions=[Permission(permission) for permission in (await get_permissions_for_role(role)).permissions],
        )
        for role in roles
    ]

    return roles_and_permissions


async def create_roles():
    from supertokens_python.recipe.userroles.asyncio import create_new_role_or_add_permissions

    roles = [
        {"name": Role.ADMIN.value, "permissions": [permission.value for permission in Permission]},
        {
            "name": Role.OWNER.value,
            "permissions": [
                Permission.CONTRIBUTIONS_CREATE.value,
                Permission.CONTRIBUTIONS_READ.value,
                Permission.CONTRIBUTIONS_UPDATE.value,
                Permission.CONTRIBUTIONS_DELETE.value,
                Permission.MEMBERS_READ.value,
                Permission.MEMBERS_CREATE.value,
                Permission.MEMBERS_UPDATE.value,
                Permission.MEMBERS_DELETE.value,
                Permission.ORGANIZATIONS_READ.value,
                Permission.ORGANIZATIONS_UPDATE.value,
            ],
        },
        {
            "name": Role.MEMBER.value,
            "permissions": [
                Permission.CONTRIBUTIONS_CREATE.value,
                Permission.CONTRIBUTIONS_READ.value,
                Permission.CONTRIBUTIONS_UPDATE.value,
                Permission.CONTRIBUTIONS_DELETE.value,
                Permission.MEMBERS_READ.value,
                Permission.MEMBERS_CREATE.value,
                Permission.ORGANIZATIONS_READ.value,
            ],
        },
    ]

    for role in roles:
        response = await create_new_role_or_add_permissions(role.get("name"), role.get("permissions"))
        if not response.created_new_role:
            logger.debug(f"Role: {role.get('name')} already exists")
        else:
            logger.info(f"Role: {role.get('name')} with permissions: {role.get('permissions')} created")


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


async def remove_role(user_id: str | UUID, role: Role):
    if isinstance(user_id, UUID):
        user_id = str(user_id)

    response = await remove_user_role("public", user_id, role.value)

    if isinstance(response, UnknownRoleError):
        logger.warning(f"Role: {role.value} does not exist")
        raise EntityNotFound(f"Role: {role.value} does not exist", "Auth")
    elif response.did_user_have_role is False:
        logger.info(f"User: {user_id} did have role of {role.value}.")
    else:
        logger.info(f"Successfully removed role of {role.value} to user: {user_id}.")


@cached(ttl=60)
async def check_is_admin(user_id: str | UUID) -> bool:
    """Check if the user is an admin"""

    if isinstance(user_id, UUID):
        user_id = str(user_id)

    _user = await get_roles_for_user("public", user_id)
    if Role.ADMIN.value in _user.roles:
        return True

    return False
