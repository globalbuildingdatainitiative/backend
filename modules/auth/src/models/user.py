from datetime import datetime
from typing import Self, Optional
from uuid import UUID

import strawberry
from pydantic import BaseModel

from .sort_filter import BaseFilter, FilterOptions, SortOptions


class SuperTokensUser(BaseModel):
    id: UUID
    organization_id: UUID | None


@strawberry.type(name="User")
class GraphQLUser:
    id: UUID
    first_name: str | None
    last_name: str | None
    email: str
    time_joined: datetime
    organization_id: UUID | None

    @classmethod
    def from_supertokens(cls, supertokens_user: dict) -> Self:
        return cls(
            id=supertokens_user["id"],
            email=supertokens_user["email"],
            time_joined=datetime.fromtimestamp(round(supertokens_user["timeJoined"] / 1000)),
            first_name=supertokens_user.get("firstName"),
            last_name=supertokens_user.get("lastName"),
            organization_id=supertokens_user.get("organization_id"),
        )


@strawberry.input
class UserFilters(BaseFilter):
    id: FilterOptions | None = None
    first_name: FilterOptions | None = None
    last_name: FilterOptions | None = None
    email: FilterOptions | None = None
    organization_id: FilterOptions | None = None


@strawberry.input
class UserSort(BaseFilter):
    id: SortOptions | None = None
    first_name: SortOptions | None = None
    last_name: SortOptions | None = None
    name: SortOptions | None = None
    organization_id: SortOptions | None = None


@strawberry.input
class UpdateUserInput:
    id: UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None
