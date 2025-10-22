import logging
from typing import Self
from uuid import UUID

import strawberry
from strawberry.federation.schema_directives import Shareable

from models import GraphQLOrganization
from core.cache import organization_cache

logger = logging.getLogger("main")


async def get_user_organization(root: "GraphQLUser") -> GraphQLOrganization | None:
    """Resolve the organization for a user. Returns None if not found or on error."""
    from logic import get_organizations
    from models import FilterBy

    try:
        if root.organizationId is None:
            logger.debug(f"User {root.id} has no organizationId, returning None")
            return None

        logger.debug(f"Resolving user organization reference: {root.organizationId}")

        org_id = root.organizationId if isinstance(root.organizationId, UUID) else UUID(root.organizationId)
        # Use cache instead of database query
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
