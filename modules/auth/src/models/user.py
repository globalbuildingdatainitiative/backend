from datetime import datetime
from typing import Self, List
from uuid import UUID
from enum import Enum

import strawberry
from pydantic import BaseModel
from strawberry import UNSET
from strawberry.federation.schema_directives import Shareable
from supertokens_python.recipe.userroles.asyncio import get_roles_for_user
from supertokens_python.types import User

from core.auth import FAKE_PASSWORD
from .scalers import EmailAddress
from .sort_filter import BaseFilter, FilterOptions


@strawberry.enum
class InviteStatus(Enum):
    ACCEPTED = "accepted"
    PENDING = "pending"
    REJECTED = "rejected"
    NONE = "none"


@strawberry.enum
class Role(Enum):
    OWNER = "owner"
    MEMBER = "member"
    ADMIN = "admin"


class SuperTokensUser(BaseModel):
    id: UUID
    organization_id: UUID | None


@strawberry.federation.type(name="User", keys=["id"])
class GraphQLUser:
    id: UUID
    first_name: str | None
    last_name: str | None
    email: str
    time_joined: datetime
    organization_id: UUID | None = strawberry.field(directives=[Shareable()])
    invited: bool = False
    invite_status: InviteStatus = InviteStatus.NONE
    inviter_name: str | None = None
    roles: list[Role] | None

    @classmethod
    async def from_supertokens(cls, user: User, metadata: dict) -> Self:
        invited = metadata.get("invited", False)
        effective_org_id = metadata.get("organization_id") if not invited else metadata.get("pending_org_id")

        return cls(
            id=UUID(user.id),
            email=user.emails[0],
            time_joined=datetime.fromtimestamp(round(user.time_joined / 1000)),
            first_name=metadata.get("firstName"),
            last_name=metadata.get("lastName"),
            organization_id=effective_org_id,
            invited=invited,
            invite_status=InviteStatus(metadata.get("invite_status", InviteStatus.NONE)),
            inviter_name=metadata.get("inviter_name"),
            roles=[Role(role) for role in (await get_roles_for_user("public", user.id)).roles]
        )

    @classmethod
    async def resolve_reference(cls, id: UUID) -> "GraphQLUser":
        from logic import get_users

        return (await get_users(filters=UserFilters(id=FilterOptions(equal=id))))[0]


@strawberry.input
class UserFilters(BaseFilter):
    id: FilterOptions | None = None
    first_name: FilterOptions | None = None
    last_name: FilterOptions | None = None
    email: FilterOptions | None = None
    organization_id: FilterOptions | None = None
    invited: FilterOptions | None = None
    invite_status: FilterOptions | None = None
    inviter_name: FilterOptions | None = None
    time_joined: FilterOptions | None = None


@strawberry.input(one_of=True)
class UserSort(BaseFilter):
    asc: str | None = strawberry.UNSET
    dsc: str | None = strawberry.UNSET


@strawberry.input
class UpdateUserInput:
    id: UUID
    first_name: str | None = UNSET
    last_name: str | None = UNSET
    email: EmailAddress | None = UNSET
    current_password: str | None = UNSET
    new_password: str | None = UNSET
    invited: bool | None = UNSET
    invite_status: InviteStatus | None = UNSET
    inviter_name: str | None = UNSET
    role: Role | None = UNSET
    organization_id: UUID | None = UNSET


@strawberry.input
class InviteUsersInput:
    emails: List[str]


@strawberry.type
class InviteResult:
    email: str
    status: str
    message: str = ""


@strawberry.input
class AcceptInvitationInput:
    id: UUID
    first_name: str | None = None
    last_name: str | None = None
    current_password: str = FAKE_PASSWORD
    new_password: str | None = None
