import typing

import strawberry
from strawberry.permission import BasePermission

from core.context import MICROSERVICE_USER_ID
from models.roles import Role
from core.cache import get_user_cache
import logging


logger = logging.getLogger("main")


class IsAuthenticated(BasePermission):
    message = "User is not authenticated"

    def has_permission(self, source: typing.Any, info: strawberry.Info, **kwargs) -> bool:
        if info.context.get("user") is not None:
            return True
        else:
            return False


class IsAdmin(BasePermission):
    message = "User is not an admin"

    async def has_permission(self, source: typing.Any, info: strawberry.Info, **kwargs) -> bool:
        user_id = info.context.get("user").id
        is_admin = False
        # Check if this is a microservice request
        if user_id == MICROSERVICE_USER_ID:
            logger.info(f"Microservice request detected (UUID: {user_id}). Treating as admin access.")
            is_admin = True
        else:
            user_cache = get_user_cache()
            # Regular user - fetch from cache
            user = await user_cache.get_user(user_id)

            # Handle case where user is not found in cache
            if user is None:
                logger.warning(f"User {user_id} not found in cache during query")
                is_admin = False
            else:
                is_admin = Role.ADMIN in user.roles
        return is_admin
