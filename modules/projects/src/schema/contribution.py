from strawberry.types import Info

from core.context import get_user
from logic import get_contributions, create_contributions, check_fetch_projects
from models import GraphQLContribution, InputContribution, ContributionFilters, ContributionSort


async def contributions_query(
    info: Info, filters: ContributionFilters | None = None, sort_by: ContributionSort | None = None
) -> list[GraphQLContribution]:
    """Returns all contributions assigned to user"""

    user = get_user(info)

    contributions = await get_contributions(user.organization_id, filters, sort_by, check_fetch_projects(info))

    return contributions


async def add_contributions_mutation(info: Info, contributions: list[InputContribution]) -> list[GraphQLContribution]:
    """Creates new Contributions"""

    user = get_user(info)
    _contributions = await create_contributions(contributions, user)

    return _contributions
