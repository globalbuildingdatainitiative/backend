from strawberry.types import Info

from core.context import get_user
from logic import create_contributions, get_contributions_for_header
from models import GraphQLContribution, InputContribution, ContributionHeaderData


async def add_contributions_mutation(info: Info, contributions: list[InputContribution]) -> list[GraphQLContribution]:
    """Creates new Contributions"""

    user = get_user(info)
    _contributions = await create_contributions(contributions, user)

    return _contributions


async def get_contributions_for_header_resolver(info: Info) -> ContributionHeaderData:
    user = get_user(info)
    organization_id = user.organization_id

    return await get_contributions_for_header(organization_id)
