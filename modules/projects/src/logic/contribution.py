from uuid import UUID

from models import DBContribution, InputContribution, User, ContributionFilters, ContributionSort
from models.sort_filter import sort_model_query


async def get_contributions(organization_id: UUID, filters: ContributionFilters | None = None,
                            sort_by: ContributionSort | None = None) -> list[DBContribution]:
    query = DBContribution.find(DBContribution.organization_id == organization_id)
    if sort_by:
        query = sort_model_query(DBContribution, sort_by, query)
    return await query.to_list()


async def create_contributions(contributions: list[InputContribution], user: User) -> list[DBContribution]:
    _contributions = []
    for _contribution in contributions:
        contribution = DBContribution(
            **_contribution.dict(),
            user_id=user.id,
            organization_id=user.organization_id)
        await contribution.insert()
        _contributions.append(contribution)

    return _contributions
