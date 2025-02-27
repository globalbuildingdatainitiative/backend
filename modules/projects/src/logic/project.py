# import logging
# from uuid import UUID
#
# from beanie.exceptions import DocumentNotFound, CollectionWasNotInitialized, RevisionIdWasChanged
# from beanie.odm.operators.find.logical import Or
#
# from core.exceptions import (
#     EntityNotFound,
#     DatabaseError,
#     DatabaseConfigurationError,
# )
# from models import DBProject, FilterBy, SortBy, filter_model_query, sort_model_query
#
# logger = logging.getLogger("main")
#
#
# async def get_projects(
#     organization_id: UUID,
#     filter_by: FilterBy | None = None,
#     sort_by: SortBy | None = None,
#     limit: int | None = None,
#     offset: int = 0,
# ):
#     try:
#         # Initialize base query with organization filter
#         base_query = DBProject.find(
#             Or(DBProject.contribution.organizationId == organization_id, DBProject.contribution.public == True)  # noqa: E712
#         )
#
#         # Apply filters if any
#         if filter_by:
#             base_query = filter_model_query(DBProject, filter_by, base_query)
#
#         # Always fetch related links
#         base_query = base_query.find({}, fetch_links=True)
#
#         # Apply sorting if any
#         if sort_by:
#             base_query = sort_model_query(DBProject, sort_by, base_query)
#
#         # Apply limit if specified
#         if limit is not None:
#             base_query = base_query.limit(limit)
#
#         # Apply offset if specified
#         if offset:
#             base_query = base_query.skip(offset)
#
#         # Execute query
#         projects = await base_query.to_list()
#
#         logger.debug(f"Found {len(projects)} projects for organization {organization_id}")
#         return projects
#
#     except DocumentNotFound:
#         raise EntityNotFound(message=f"No projects found for organization {organization_id}", name="Projects")
#     except CollectionWasNotInitialized:
#         raise DatabaseConfigurationError("Database collection was not properly initialized")
#     except RevisionIdWasChanged:
#         raise DatabaseError("Database revision ID was changed")


import logging
from uuid import UUID

from beanie.exceptions import DocumentNotFound, CollectionWasNotInitialized, RevisionIdWasChanged
from beanie.odm.operators.find.logical import Or

from core.exceptions import (
    EntityNotFound,
    DatabaseError,
    DatabaseConfigurationError,
)
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
        base_query = DBProject.find(
            Or(DBProject.contribution.organizationId == organization_id, DBProject.contribution.public == True)  # noqa: E712
        )

        # Apply filters if any
        if filter_by:
            base_query = filter_model_query(DBProject, filter_by, base_query)

        # Always fetch related links
        base_query = base_query.find({}, fetch_links=True)

        # Apply sorting if any
        if sort_by:
            base_query = sort_model_query(DBProject, sort_by, base_query)

            # If this is already an aggregation pipeline (e.g., for GWP intensity sorting)
            # we need to apply limit and offset differently
            if hasattr(base_query, '_aggregation_query'):
                # For aggregation queries, we add the skip and limit stages to the pipeline
                if offset:
                    base_query = base_query.skip(offset)
                if limit is not None:
                    base_query = base_query.limit(limit)

                # Return the aggregation result as a list
                return await base_query.to_list()

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

    except DocumentNotFound:
        raise EntityNotFound(message=f"No projects found for organization {organization_id}", name="Projects")
    except CollectionWasNotInitialized:
        raise DatabaseConfigurationError("Database collection was not properly initialized")
    except RevisionIdWasChanged:
        raise DatabaseError("Database revision ID was changed")
