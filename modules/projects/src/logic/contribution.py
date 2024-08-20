import dataclasses
from enum import Enum
from uuid import UUID
from datetime import datetime
from beanie import WriteRules
from strawberry import Info

from models import DBContribution, InputContribution, User, DBProject, ContributionHeaderData
from models.sort_filter import sort_model_query, filter_model_query, FilterBy, SortBy


async def get_contributions(
    organization_id: UUID,
    filter_by: FilterBy | None,
    sort_by: SortBy | None,
    limit: int,
    offset: int,
    fetch_links: bool = False,
) -> list[DBContribution]:
    query = DBContribution.find(DBContribution.organization_id == organization_id, fetch_links=fetch_links)

    query = filter_model_query(DBContribution, filter_by, query)
    query = sort_model_query(DBContribution, sort_by, query)
    query = query.limit(limit)

    if offset:
        query = query.skip(offset)

    contributions = await query.to_list()
    return contributions


async def get_contributions_for_header(organization_id: UUID) -> ContributionHeaderData:
    total_contributions = await DBContribution.find(DBContribution.organization_id == organization_id).count()
    contributions = await get_contributions(
        organization_id=organization_id,
        filter_by=None,
        sort_by=SortBy(dsc="uploaded_at"),
        limit=1,
        offset=0,
    )

    last_contribution_date = contributions[0].uploaded_at if contributions else None

    if last_contribution_date:
        days_since_last_contribution = (datetime.now() - last_contribution_date).days
    else:
        days_since_last_contribution = 0  # Default to 0 if there are no contributions

    return ContributionHeaderData(
        total_contributions=total_contributions,
        days_since_last_contribution=days_since_last_contribution,
    )


async def create_contributions(contributions: list[InputContribution], user: User) -> list[DBContribution]:
    _contributions = []
    for _contribution in contributions:
        contribution = DBContribution(
            project=DBProject(**as_dict(_contribution.project)), user_id=user.id, organization_id=user.organization_id
        )
        await contribution.insert(link_rule=WriteRules.WRITE)
        _contributions.append(contribution)

    return _contributions


def check_fetch_projects(info: Info) -> bool:
    if contribution_field := [field for field in info.selected_fields if field.name == "items"]:
        if [_field for _field in contribution_field[0].selections if _field.name == "project"]:
            return True

    return False


def as_dict(obj):
    def asdict_factory(data):
        def convert_value(obj):
            if isinstance(obj, Enum):
                return obj.name
            elif isinstance(obj, list):
                return [convert_value(v) for v in obj]
            return obj

        return dict((k, convert_value(v)) for k, v in data)

    data = dataclasses.asdict(obj, dict_factory=asdict_factory)

    return data
