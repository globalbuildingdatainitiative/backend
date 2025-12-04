import logging
from uuid import UUID
import httpx

from core.exceptions import EntityNotFound
from core.cache import get_organization_cache
from logic.roles import assign_role, Role
from models import (
    DBOrganization,
    InputOrganization,
    SuperTokensUser,
    OrganizationMetaDataModel,
)
from models.sort_filter import FilterBy, SortBy
from strawberry import UNSET


logger = logging.getLogger("main")


# Map frontend field names to model attributes
field_mapping = {
    "id": "id",
    "name": "name",
    "address": "address",
    "city": "city",
    "country": "country",
}


async def get_organizations(
    filter_by: FilterBy | None = None,
    sort_by: SortBy | None = None,
    limit: int | None = None,
    offset: int = 0,
) -> tuple[list[DBOrganization], int, int]:
    """Returns all Organizations with total count and unique count
    filter
    sort
    offset
    limit
    """
    # Handle special case: ID filter with direct lookup
    # This optimizes performance for ID-based queries
    if filter_by and filter_by.equal and filter_by.equal.get("id"):
        return await _apply_id_filter_cached(filter_by)

    organization_cache = get_organization_cache()
    # Else fetch all organizations from cache and apply filters/sorting/pagination
    organizations = await organization_cache.get_all_organizations()

    if filter_by:
        organizations = filter_organizations(organizations, filter_by)
    if sort_by:
        organizations = sort_organizations(organizations, sort_by)

    # Store total count before pagination
    total_count = len(organizations)
    unique_count = len(set(f"{org.name.lower()};{org.country}" for org in organizations))

    # Apply pagination
    if limit is not None:
        organizations = organizations[offset : offset + limit]
    else:
        organizations = organizations[offset:]

    logger.debug(f"Found {len(organizations)} organizations (total: {total_count})")
    return organizations, total_count, unique_count


def filter_organizations(organizations: list[DBOrganization], filters: FilterBy) -> list[DBOrganization]:
    filtered_organizations = organizations

    SUPPORTED_FILTERS = {"equal", "contains", "is_true"}

    for _filter, fields in filters.items():
        if not fields:
            continue

        # Raise error for unsupported filter types
        if _filter not in SUPPORTED_FILTERS:
            raise ValueError(
                f"Filter type '{_filter}' is not supported for in-memory organization filtering. "
                f"Supported filters: {', '.join(SUPPORTED_FILTERS)}"
            )

        for _field, value in fields.items():
            if not _field or value is UNSET:
                continue

            model_field = field_mapping.get(_field, _field)
            filtered_organizations = [
                org
                for org in filtered_organizations
                if _matches_filter(getattr(org, model_field, None), value, _filter)
            ]

    return filtered_organizations


def _matches_filter(field_value, filter_value, filter_type: str) -> bool:
    """
    Check if field value matches the filter.
    Supports 'equal', 'contains', and 'is_true' filter types.
    Handles UUIDs and basic string comparisons.
    """
    if field_value is None:
        return False

    # Handle is_true for boolean fields
    if filter_type == "is_true":
        return bool(field_value) == filter_value

    # Handle UUID - exact match
    if isinstance(field_value, UUID):
        return str(field_value) == str(filter_value)

    # Default: case-insensitive string comparison
    field_str = str(field_value).lower()
    filter_str = str(filter_value).lower()
    return filter_str in field_str if filter_type == "contains" else field_str == filter_str


def sort_organizations(organizations: list[DBOrganization], sort_by: SortBy | None = None) -> list[DBOrganization]:
    if not sort_by:
        return organizations

    field = sort_by.asc if sort_by.asc is not UNSET else sort_by.dsc
    reverse = sort_by.dsc is not UNSET
    sort_field = field_mapping.get(field, field)

    return sorted(
        organizations,
        key=lambda o: (getattr(o, sort_field, None) is None, str(getattr(o, sort_field, "") or "")),
        reverse=reverse,
    )


async def _apply_id_filter_cached(filter_by: FilterBy) -> tuple[list[DBOrganization], int]:
    """Optimized organization retrieval when filtering by ID using cache"""
    org_id = filter_by.equal.get("id")
    try:
        org_uuid = UUID(org_id) if isinstance(org_id, str) else org_id
        organization_cache = get_organization_cache()
        if org := await organization_cache.get_organization(org_uuid):
            return [org], 1
        else:
            return [], 0
    except EntityNotFound as e:
        logger.warning(f"Organization not found in cache: {e}")
        raise e


async def _refresh_user_cache_in_auth_service(user_id: UUID):
    """Call auth service directly to refresh user cache after metadata updates"""
    from core.config import settings
    from supertokens_python.recipe.jwt import asyncio as jwt_asyncio
    from supertokens_python.recipe.jwt.interfaces import CreateJwtOkResult

    mutation = """
    mutation RefreshUserCache($userId: String!) {
        refreshUserCache(userId: $userId)
    }
    """

    try:
        # Create JWT token for inter-service authentication
        logger.debug(f"Creating JWT for inter-service communication to refresh cache for user {user_id}")
        jwt_response = await jwt_asyncio.create_jwt({"source": "microservice"})

        if not isinstance(jwt_response, CreateJwtOkResult):
            logger.error("Failed to create JWT for inter-service communication")
            return

        jwt_token = jwt_response.jwt

        # Use configured auth service URL, fall back to router if not set
        auth_url = (
            f"{str(settings.AUTH_SERVICE_URL).rstrip('/')}/api/graphql"
            if settings.AUTH_SERVICE_URL
            else f"{settings.ROUTER_URL}/graphql"
        )
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                auth_url,
                json={"query": mutation, "variables": {"userId": str(user_id)}},
                headers={"Authorization": f"Bearer {jwt_token}", "Content-Type": "application/json"},
            )

            if response.is_error:
                logger.warning(
                    f"Failed to refresh user cache in auth service at {auth_url}: "
                    f"Status {response.status_code} - {response.text}"
                )
            else:
                result = response.json()
                if "errors" in result:
                    logger.warning(f"GraphQL errors refreshing user cache: {result['errors']}")
                else:
                    logger.info(f"Successfully refreshed user cache for user {user_id}")
    except Exception as e:
        logger.error(f"Error calling auth service to refresh user cache: {e}", exc_info=True)


async def create_organizations_mutation(
    organizations: list[InputOrganization], current_user: SuperTokensUser
) -> list[DBOrganization]:
    from supertokens_python.recipe.usermetadata.asyncio import update_user_metadata

    logger.info(
        f"Creating organizations for user: {current_user.id} with organization_id: {current_user.organization_id}"
    )

    new_organizations = []
    for organization_data in organizations:
        new_organization = DBOrganization(
            name=organization_data.name,
            address=organization_data.address,
            city=organization_data.city,
            country=organization_data.country,
            meta_data=OrganizationMetaDataModel(stakeholders=organization_data.meta_data.stakeholders),
        )
        await new_organization.insert()
        new_organizations.append(new_organization)

        # Add to cache immediately
        organization_cache = get_organization_cache()
        await organization_cache.add_organization(new_organization)

        # Verify the organization was inserted and is queryable
        try:
            verification = await DBOrganization.get(new_organization.id)
            if verification is None:
                logger.warning(f"Organization {new_organization.id} was not immediately queryable after insertion")
        except Exception as e:
            logger.warning(f"Error verifying organization {new_organization.id} after insertion: {e}")

    # Only update user metadata and assign role if at least one organization was created
    if new_organizations:
        logger.info(f"Updating user metadata for user {current_user.id} with organization ID {new_organizations[0].id}")
        await update_user_metadata(str(current_user.id), {"organization_id": str(new_organizations[0].id)})
        await assign_role(current_user.id, Role.OWNER)

        # Refresh the user cache in auth service
        await _refresh_user_cache_in_auth_service(current_user.id)

    return new_organizations


async def update_organizations_mutation(organizations: list[InputOrganization]) -> list[DBOrganization]:
    """Updates a list of existing Organizations"""

    updated_organizations = []
    for organization_data in organizations:
        organization_id = organization_data.id
        organization = await DBOrganization.get(document_id=organization_id)
        if organization:
            update_doc = {
                "$set": {
                    "name": organization_data.name,
                    "address": organization_data.address,
                    "city": organization_data.city,
                    "country": organization_data.country,
                    "meta_data": OrganizationMetaDataModel(
                        stakeholders=organization_data.meta_data.stakeholders
                    ).dict(),
                }
            }
            await organization.update(update_doc)
            updated_organizations.append(organization)

            # Reload in cache
            organization_cache = get_organization_cache()
            await organization_cache.reload_organization(organization_id)
        else:
            raise EntityNotFound("Organization Not Found", organization_data.name)

    return updated_organizations


async def delete_organizations_mutation(ids: list[UUID]) -> list[UUID]:
    """Deletes a list of Organizations by their IDs and returns a list of deleted IDs"""

    deleted_ids = []
    for organization_id in ids:
        organization = await DBOrganization.get(document_id=organization_id)
        if organization:
            await organization.delete()
            deleted_ids.append(organization_id)

            # Remove from cache
            organization_cache = get_organization_cache()
            await organization_cache.remove_organization(organization_id)
        else:
            raise EntityNotFound("Organization Not Found", str(organization_id))

    return deleted_ids
