import typing

import strawberry
from strawberry.permission import BasePermission


class IsAuthenticated(BasePermission):
    message = "User is not authenticated"

    def has_permission(self, source: typing.Any, info: strawberry.Info, **kwargs) -> bool:
        if info.context.get("user"):
            return True
        else:
            return False
