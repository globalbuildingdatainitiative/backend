import typing

import strawberry
from strawberry.permission import BasePermission

from core.context import get_user
from logic.roles import check_is_admin


class IsAuthenticated(BasePermission):
    message = "User is not authenticated"

    def has_permission(self, source: typing.Any, info: strawberry.Info, **kwargs) -> bool:
        if get_user(info):
            return True
        else:
            return False


class IsAdmin(BasePermission):
    message = "User is not an admin"

    async def has_permission(self, source: typing.Any, info: strawberry.Info, **kwargs) -> bool:
        user = get_user(info)
        if await check_is_admin(user.id):
            return True
        else:
            return False
