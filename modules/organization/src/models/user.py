from typing import Self
from uuid import UUID

import strawberry

from models import GraphQLOrganization, OrganizationFilter


async def get_user_organization(root: "GraphQLUser") -> GraphQLOrganization | None:
    from logic import get_organizations
    from models.sort_filter import FilterOptions

    if root.organizationId is None:
        return None

    organizations = await get_organizations(
        filters=OrganizationFilter(id=FilterOptions(equal=UUID(root.organizationId)))
    )
    return organizations[0] if organizations else None


@strawberry.federation.type(name="User", keys=["id"])
class GraphQLUser:
    id: UUID
    organizationId: UUID | None
    organization: GraphQLOrganization | None = strawberry.field(resolver=get_user_organization)

    @classmethod
    async def resolve_reference(cls, id: UUID) -> Self:
        from logic import get_auth_user

        return cls(**(await get_auth_user(id)))
