from datetime import datetime
from enum import Enum
from typing import List
from uuid import UUID

import logging
import strawberry
from pydantic import BaseModel
from strawberry import UNSET

from core.auth import FAKE_PASSWORD
from models.roles import Role
from .scalers import EmailAddress
from .sort_filter import FilterBy

logger = logging.getLogger(__name__)


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
    organization_id: UUID | None = strawberry.field(name="organizationId")
    roles: list[Role] | None
    last_login: datetime | None = strawberry.field(name="lastLogin")
    # optional fields for invited users
    invited: bool = False
    invite_status: InviteStatus = InviteStatus.NONE
    inviter_name: str | None = None
    pending_org_id: UUID | None = None

    @classmethod
    async def resolve_reference(cls, id: UUID) -> "GraphQLUser":
        from logic import get_users
        from core.exceptions import EntityNotFound

        users, _ = await get_users(filter_by=FilterBy(equal={"id": id}))

        # Handle case where user is not found to prevent "list index out of range" error
        if not users:
            logger.warning(f"No user found with id {id}")
            raise EntityNotFound("User Not Found", str(id))

        return users[0]


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


@strawberry.type
class UserStatistics:
    active_last_30_days: int = strawberry.field(name="activeLast30Days")
    active_last_60_days: int = strawberry.field(name="activeLast60Days")
    active_last_90_days: int = strawberry.field(name="activeLast90Days")


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
