from uuid import UUID

from models import DBProject, FilterBy, SortBy, filter_model_query, sort_model_query


async def get_projects(organization_id: UUID, filter_by: FilterBy, sort_by: SortBy, limit: int, offset: int):
    project_query = DBProject.find_all(fetch_links=True)
    project_query = project_query.find(DBProject.contribution.organization_id == organization_id)
    project_query = filter_model_query(DBProject, filter_by, project_query)
    project_query = sort_model_query(DBProject, sort_by, project_query)
    project_query = project_query.limit(limit)

    if offset:
        project_query = project_query.skip(offset)

    return await project_query.to_list()
