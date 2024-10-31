import dataclasses
import logging
from enum import Enum
from uuid import UUID

from beanie import WriteRules
from strawberry import Info

from models import DBContribution, InputContribution, DBProject, SuperTokensUser
from models.sort_filter import sort_model_query, filter_model_query, FilterBy, SortBy

logger = logging.getLogger("main")


async def get_contributions(
    organization_id: UUID,
    filter_by: FilterBy | None,
    sort_by: SortBy | None,
    limit: int | None,
    offset: int,
    fetch_links: bool = False,
) -> list[DBContribution]:
    query = DBContribution.find(DBContribution.organization_id == organization_id, fetch_links=fetch_links)

    query = filter_model_query(DBContribution, filter_by, query)
    query = sort_model_query(DBContribution, sort_by, query)

    if limit is not None:
        query = query.limit(limit)

    if offset:
        query = query.skip(offset)

    contributions = await query.to_list()
    logger.debug(f"Found {len(contributions)} projects for organization {organization_id}")
    return contributions


async def create_contributions(contributions: list[InputContribution], user: SuperTokensUser) -> list[DBContribution]:
    _contributions = []
    for _contribution in contributions:
        contribution = DBContribution(
            project=DBProject(**as_dict(_contribution.project)),
            user_id=user.id,
            organization_id=user.organization_id,
            public=_contribution.public,
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
