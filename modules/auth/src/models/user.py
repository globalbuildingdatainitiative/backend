from datetime import datetime
from typing import Self, Optional, List
from uuid import UUID
from enum import Enum

import strawberry
from pydantic import BaseModel
from strawberry.federation.schema_directives import Shareable

from core.auth import FAKE_PASSWORD
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
    role: Role | None

    @classmethod
    def from_supertokens(cls, supertokens_user: dict) -> Self:
        return cls(
            id=supertokens_user["id"],
            email=supertokens_user["email"],
            time_joined=datetime.fromtimestamp(round(supertokens_user["timeJoined"] / 1000)),
            first_name=supertokens_user.get("firstName"),
            last_name=supertokens_user.get("lastName"),
            organization_id=supertokens_user.get("organization_id"),
            invited=supertokens_user.get("invited", False),
            invite_status=InviteStatus(supertokens_user.get("invite_status", InviteStatus.NONE)),
            inviter_name=supertokens_user.get("inviter_name"),
            role=Role(supertokens_user.get("role", Role.MEMBER)),
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
    role: FilterOptions | None = None
    time_joined: FilterOptions | None = None


@strawberry.input(one_of=True)
class UserSort(BaseFilter):
    asc: str | None = strawberry.UNSET
    dsc: str | None = strawberry.UNSET


@strawberry.input
class UpdateUserInput:
    id: UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None
    invited: Optional[bool] = None
    invite_status: Optional[InviteStatus] = None
    inviter_name: Optional[str] = None
    role: Optional[Role] = None
    organization_id: Optional[UUID] = None


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
