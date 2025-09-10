from datetime import datetime
from enum import Enum
from typing import Self, List
from uuid import UUID
from sqlalchemy import Column

import strawberry
from pydantic import BaseModel
from sqlmodel import SQLModel, Field
from strawberry import UNSET
from strawberry.federation.schema_directives import Shareable
from supertokens_python.recipe.userroles.asyncio import get_roles_for_user
from supertokens_python.types import User
from sqlalchemy.dialects.postgresql import JSON
from core.auth import FAKE_PASSWORD
from models.roles import Role
from .scalers import EmailAddress
from .sort_filter import FilterBy


@strawberry.enum
class InviteStatus(Enum):
    ACCEPTED = "accepted"
    PENDING = "pending"
    REJECTED = "rejected"
    NONE = "none"


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
            id=UUID(user.id if hasattr(user, 'id') else user.user_id),
            email=user.emails[0] if hasattr(user, "emails") else user.email,
            time_joined=datetime.fromtimestamp(round(user.time_joined / 1000)),
            first_name=metadata.get("first_name"),
            last_name=metadata.get("last_name"),
            organization_id=effective_org_id,
            invited=invited,
            invite_status=InviteStatus(metadata.get("invite_status", InviteStatus.NONE)),
            inviter_name=metadata.get("inviter_name"),
            roles=[Role(role) for role in (await get_roles_for_user("public", user.id if hasattr(user, 'id') else user.user_id)).roles],
        )

    @classmethod
    async def resolve_reference(cls, id: UUID) -> "GraphQLUser":
        from logic import get_users

        return (await get_users(filter_by=FilterBy(equal={"id": id})))[0]


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


class EmailPasswordUser(SQLModel, table=True):
    __tablename__ = "emailpassword_users"
    app_id: str = Field(primary_key=True)
    user_id: str = Field(primary_key=True)
    email: str
    # password_hash: str
    time_joined: int


class UserMetadata(SQLModel, table=True):
    __tablename__ = "user_metadata"
    app_id: str = Field(primary_key=True)
    user_id: str = Field(primary_key=True)
    user_metadata: dict = Field(default=dict, sa_column=Column(JSON))