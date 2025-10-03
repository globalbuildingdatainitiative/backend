from datetime import datetime
from enum import Enum
from typing import Self, List
from uuid import UUID
from sqlalchemy import Column

import logging
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
            id=UUID(user.id if hasattr(user, "id") else user.user_id),
            email=user.emails[0] if hasattr(user, "emails") else user.email,
            time_joined=datetime.fromtimestamp(round(user.time_joined / 1000)),
            first_name=metadata.get("first_name") or metadata.get("firstName"),
            last_name=metadata.get("last_name") or metadata.get("lastName"),
            organization_id=effective_org_id,
            invited=invited,
            invite_status=InviteStatus(metadata.get("invite_status", InviteStatus.NONE)),
            inviter_name=metadata.get("inviter_name"),
            roles=[
                Role(role)
                for role in (await get_roles_for_user("public", user.id if hasattr(user, "id") else user.user_id)).roles
            ],
        )

    @classmethod
    async def from_sqlmodel(cls, user: "UserMetadata") -> Self:
        """
        Construct a GraphQLUser from the custom UserMetadata SQLModel.
        
        For optimal performance and compatibility with old users:
        - Prioritize data from our custom metadata table
        - Only fetch from SuperTokens if data is missing
        - As last resort, query SuperTokens database directly
        """
        from supertokens_python.asyncio import get_user as get_st_user
        from supertokens_python.recipe.usermetadata.asyncio import get_user_metadata
        from sqlmodel import select
        from sqlmodel.ext.asyncio.session import AsyncSession
        from core.connection import get_postgres_engine
        
        invited = user.meta_data.get("invited", False)
        effective_org_id = (
            user.meta_data.get("organization_id") if not invited else user.meta_data.get("pending_org_id")
        )

        # Try to get email and time_joined from our custom metadata first
        email = user.meta_data.get("email")
        time_joined_ms = user.meta_data.get("time_joined")
        time_joined = None
        
        if time_joined_ms is not None:
            time_joined = datetime.fromtimestamp(round(time_joined_ms / 1000))
        
        # Only fetch from SuperTokens if we're missing email or time_joined
        if not email or not time_joined:
            st_user = await get_st_user(user.id)
            
            if st_user:
                # Found user in SuperTokens - use that data
                if not email and st_user.emails:
                    email = st_user.emails[0]
                if not time_joined:
                    time_joined = datetime.fromtimestamp(round(st_user.time_joined / 1000))
            else:
                # User not found by get_user() - try SuperTokens user_metadata table
                # This can happen for old users where the ID mapping is different
                try:
                    st_metadata = await get_user_metadata(user.id)
                    if not email:
                        email = st_metadata.metadata.get("email")
                    if not time_joined and st_metadata.metadata.get("time_joined"):
                        time_joined = datetime.fromtimestamp(round(st_metadata.metadata["time_joined"] / 1000))
                except Exception:
                    pass  # Ignore errors from user_metadata lookup
                
                # Last resort: query SuperTokens database directly for emailpassword users  
                if not email or not time_joined:
                    try:
                        from sqlalchemy import text as sql_text
                        async with AsyncSession(get_postgres_engine()) as st_session:
                            # Query emailpassword_users table directly
                            query = sql_text("SELECT email, time_joined FROM emailpassword_users WHERE user_id = :user_id")
                            result = await st_session.execute(query, {"user_id": user.id})
                            row = result.first()
                            if row:
                                if not email:
                                    email = row[0]
                                if not time_joined:
                                    time_joined = datetime.fromtimestamp(round(row[1] / 1000))
                    except Exception as e:
                        logger.warning(f"Failed to query SuperTokens database directly for user {user.id}: {e}")
        
        # Final validation
        if not email:
            raise ValueError(f"No email found for user {user.id}")
        if not time_joined:
            raise ValueError(f"No time_joined found for user {user.id}")

        return cls(
            id=UUID(user.id),
            email=email,
            time_joined=time_joined,
            first_name=user.meta_data.get("first_name"),
            last_name=user.meta_data.get("last_name"),
            organization_id=effective_org_id,
            invited=invited,
            invite_status=InviteStatus(user.meta_data.get("invite_status", InviteStatus.NONE)),
            inviter_name=user.meta_data.get("inviter_name"),
            roles=[Role(role) for role in (await get_roles_for_user("public", user.id)).roles],
        )

    @classmethod
    async def resolve_reference(cls, id: UUID) -> "GraphQLUser":
        from logic import get_users
        from core.exceptions import EntityNotFound

        users = await get_users(filter_by=FilterBy(equal={"id": id}))

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


class UserMetadata(SQLModel, table=True):
    id: str = Field(primary_key=True)
    meta_data: dict = Field(default=dict, sa_column=Column(JSON))
