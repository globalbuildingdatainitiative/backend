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

    # Handle case where organization is not found to prevent "list index out of range" error
    if not organizations:
        logger.warning(f"No organization found for user {root.id} with organizationId {org_id}")
        return None

    return organizations[0]


@strawberry.federation.type(name="User", keys=["id"])
class GraphQLUser:
    id: UUID
    organizationId: UUID | None = strawberry.field(default=None, directives=[Shareable()])
    organization: GraphQLOrganization | None = strawberry.field(resolver=get_user_organization)

    @classmethod
    async def resolve_reference(cls, id: UUID) -> Self:
        from logic import get_auth_user
        from core.exceptions import MicroServiceResponseError

        try:
            user_data = await get_auth_user(id)
            return cls(**user_data)
        except MicroServiceResponseError as e:
            # If user not found in auth service, create a minimal user object
            # This can happen when the user ID is from a different context (e.g., JWT source)
            logger.warning(f"User {id} not found in auth service, creating minimal user object: {e}")
            return cls(id=id, organizationId=None)
        except Exception as e:
            # Log the error but still create a minimal user object to prevent complete failure
            logger.error(f"Error resolving user reference for {id}: {e}")
            return cls(id=id, organizationId=None)
