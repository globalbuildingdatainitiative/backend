import logging
from uuid import UUID

from models import DBProject, FilterBy, SortBy, filter_model_query, sort_model_query
from core.exceptions import (
    EntityNotFound,
    DatabaseError,
    DatabaseConfigurationError,
)

logger = logging.getLogger("main")


async def get_projects(
    organization_id: UUID,
    filter_by: FilterBy | None = None,
    sort_by: SortBy | None = None,
    limit: int | None = None,
    offset: int = 0,
):
    try:
        # Initialize base query with organization filter
        base_query = DBProject.find({"contribution.organizationId": organization_id})

        # Apply filters if any
        if filter_by:
            base_query = filter_model_query(DBProject, filter_by, base_query)

        # Always fetch related links
        base_query = base_query.find({}, fetch_links=True)

        # Apply sorting if any
        if sort_by:
            base_query = sort_model_query(DBProject, sort_by, base_query)

        # Apply limit if specified
        if limit is not None:
            base_query = base_query.limit(limit)

        # Apply offset if specified
        if offset:
            base_query = base_query.skip(offset)

        # Execute query
        projects = await base_query.to_list()

        logger.debug(f"Found {len(projects)} projects for organization {organization_id}")
        return projects

    except Exception as e:
        if "Document not found" in str(e):
            raise EntityNotFound(message=f"No projects found for organization {organization_id}", name="Projects")
        elif "Collection was not initialized" in str(e):
            raise DatabaseConfigurationError("Database collection was not properly initialized")
        else:
            raise DatabaseError(f"Database operation failed: {str(e)}")
