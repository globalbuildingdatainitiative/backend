import logging
from uuid import UUID

from models import DBProject, FilterBy, SortBy, filter_model_query, sort_model_query

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
        logger.error(f"Error fetching projects: {str(e)}")
        raise
