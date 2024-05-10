from uuid import UUID

from beanie import WriteRules
from strawberry import Info

from models import DBContribution, InputContribution, User, ContributionFilters, ContributionSort, DBProject
from models.sort_filter import sort_model_query


async def get_contributions(
    organization_id: UUID,
    filters: ContributionFilters | None = None,
    sort_by: ContributionSort | None = None,
    fetch_links: bool = False,
) -> list[DBContribution]:
    query = DBContribution.find(DBContribution.organization_id == organization_id, fetch_links=fetch_links)
    if sort_by:
        query = sort_model_query(DBContribution, sort_by, query)
    return await query.to_list()


async def create_contributions(contributions: list[InputContribution], user: User) -> list[DBContribution]:
    _contributions = []
    for _contribution in contributions:
        # TODO - Fix Me!
        contribution = DBContribution(
            project=DBProject(**_contribution.project.__dict__), user_id=user.id, organization_id=user.organization_id
        )
        await contribution.insert(link_rule=WriteRules.WRITE)
        _contributions.append(contribution)

    return _contributions


def check_fetch_projects(info: Info) -> bool:
    if contribution_field := [field for field in info.selected_fields if field.name == "contributions"]:
        if [_field for _field in contribution_field[0].selections if _field.name == "project"]:
            return True

    return False
