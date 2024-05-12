import dataclasses
from enum import Enum
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
        contribution = DBContribution(
            project=DBProject(**as_dict(_contribution.project)), user_id=user.id, organization_id=user.organization_id
        )
        await contribution.insert(link_rule=WriteRules.WRITE)
        _contributions.append(contribution)

    return _contributions


def check_fetch_projects(info: Info) -> bool:
    if contribution_field := [field for field in info.selected_fields if field.name == "contributions"]:
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
