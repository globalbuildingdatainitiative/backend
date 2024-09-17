import logging
from uuid import UUID

from models import DBProject, FilterBy, SortBy, filter_model_query, sort_model_query

logger = logging.getLogger("main")


async def get_projects(organization_id: UUID, filter_by: FilterBy, sort_by: SortBy, limit: int, offset: int):
    project_query = DBProject.find(DBProject.contribution.organizationId == organization_id)
    project_query = filter_model_query(DBProject, filter_by, project_query)
    project_query = project_query.find({}, fetch_links=True)
    project_query = sort_model_query(DBProject, sort_by, project_query)
    project_query = project_query.limit(limit)

    if offset:
        project_query = project_query.skip(offset)

    projects = await project_query.to_list()
    logger.debug(f"Found {len(projects)} projects for organization {organization_id}")
    return projects
