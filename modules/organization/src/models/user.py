import logging
from typing import Self
from uuid import UUID

import strawberry
from strawberry.federation.schema_directives import Shareable

from models import GraphQLOrganization

logger = logging.getLogger("main")


async def get_user_organization(root: "GraphQLUser") -> GraphQLOrganization | None:
    from logic import get_organizations
    from models import FilterBy

    if root.organizationId is None:
        return None

    logger.debug(f"Resolving user organization reference: {root.organizationId}")

    org_id = root.organizationId if isinstance(root.organizationId, UUID) else UUID(root.organizationId)
    organizations = await get_organizations(filter_by=FilterBy(equal={"id": org_id}))

    logger.debug(f"Found {len(organizations)} organizations for user {root.id}")

    return organizations[0] if organizations else None


@strawberry.federation.type(name="User", keys=["id"])
class GraphQLUser:
    id: UUID
    organizationId: UUID | None = strawberry.field(directives=[Shareable()])
    organization: GraphQLOrganization | None = strawberry.field(resolver=get_user_organization)

    @classmethod
    async def resolve_reference(cls, id: UUID) -> Self:
        from logic import get_auth_user

        return cls(**(await get_auth_user(id)))
