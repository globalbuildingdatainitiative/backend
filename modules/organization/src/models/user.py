import logging
from typing import Self
from uuid import UUID

import strawberry

from models import GraphQLOrganization
from core.cache import get_organization_cache

logger = logging.getLogger("main")


async def get_user_organization(root: "GraphQLUser") -> GraphQLOrganization | None:
    """Resolve the organization for a user. Returns None if not found or on error."""
    try:
        logger.debug(f"get_user_organization called for user {root.id}, organizationId={root.organizationId}")

        if root.organizationId is None:
            logger.warning(f"User {root.id} has no organizationId, returning None")
            return None

        logger.debug(f"Resolving user organization reference: {root.organizationId}")

        org_id = root.organizationId if isinstance(root.organizationId, UUID) else UUID(root.organizationId)
        # Use organization cache - NO MongoDB queries
        organization_cache = get_organization_cache()
        organization = await organization_cache.get_organization(org_id)

        if not organization:
            logger.warning(f"No organization found for user {root.id} with organizationId {org_id}")
            return None

        logger.debug(f"Found organization {organization.id} for user {root.id}")
        return organization
    except Exception as e:
        # Catch any exception to prevent the entire User object from becoming null
        logger.error(f"Error resolving organization for user {root.id}: {e}", exc_info=True)
        return None


@strawberry.federation.type(name="User", keys=["id"], extend=True)
class GraphQLUser:
    id: UUID = strawberry.federation.field(external=True)
    organizationId: UUID | None = strawberry.federation.field(external=True, default=None)
    organization: GraphQLOrganization | None = strawberry.federation.field(
        resolver=get_user_organization, requires=["organizationId"]
    )

    @classmethod
    async def resolve_reference(cls, id: UUID, organizationId: UUID | None = None, **kwargs) -> Self:
        """
        Resolve user reference in federation.

        The router should provide organizationId via @external and @requires directives.
        """
        logger.info(f"resolve_reference called: id={id}, organizationId={organizationId}, kwargs={kwargs}")
        return cls(id=id, organizationId=organizationId)
