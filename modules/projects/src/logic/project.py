from models import DBProject, FilterBy, SortBy, filter_model_query, sort_model_query


async def get_projects(filter_by: FilterBy, sort_by: SortBy, limit: int, offset: int):
    project_query = filter_model_query(DBProject, filter_by)
    project_query = sort_model_query(DBProject, sort_by, project_query)
    project_query = project_query.limit(limit)

    if offset:
        project_query = project_query.skip(offset)

    return await project_query.to_list()
