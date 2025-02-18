import dataclasses
import logging
from enum import Enum
from uuid import UUID

from beanie import WriteRules
from beanie.odm.operators.find.logical import Or
from beanie.operators import In
from strawberry import Info, UNSET

from models import DBContribution, InputContribution, DBProject, SuperTokensUser, UpdateContribution
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
    query = DBContribution.find(Or(DBContribution.organization_id == organization_id, DBContribution.public == True))  # noqa: E712

    query = filter_model_query(DBContribution, filter_by, query)
    query = sort_model_query(DBContribution, sort_by, query)

    if limit is not None:
        query = query.limit(limit)

    if offset:
        query = query.skip(offset)
    if fetch_links:
        query = query.find({}, fetch_links=True)
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


async def delete_contributions(contributions: list[UUID], user: SuperTokensUser) -> list[UUID]:
    _contributions = DBContribution.find(In(DBContribution.id, contributions)).find(
        DBContribution.organization_id == user.organization_id
    )
    logger.debug(f"Deleting {len(contributions)} contributions for organization {user.organization_id}")
    await _contributions.delete()

    return contributions


async def update_contributions(contributions: list[UpdateContribution], user: SuperTokensUser) -> list[DBContribution]:
    _contributions = []
    for _contribution in contributions:
        contribution = await DBContribution.find(
            DBContribution.id == _contribution.id, DBContribution.organization_id == user.organization_id
        ).first_or_none()
        if not contribution:
            logger.debug(
                f"Couldn't find Contribution with id {_contribution.id} and organization_id {user.organization_id}"
            )
            continue
        for field, value in as_dict(_contribution).items():
            if field == "id" or value is UNSET:
                continue
            setattr(contribution, field, value)

        await contribution.save()
        logger.debug(f"Updated Contribution with id {_contribution.id} and organization_id {user.organization_id}")
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
