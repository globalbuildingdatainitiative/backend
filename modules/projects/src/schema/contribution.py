from uuid import UUID

from strawberry.types import Info

from core.context import get_user
from logic import create_contributions, delete_contributions, update_contributions
from models import GraphQLContribution, InputContribution, UpdateContribution


async def add_contributions_mutation(info: Info, contributions: list[InputContribution]) -> list[GraphQLContribution]:
    """Creates new Contributions"""

    user = get_user(info)
    _contributions = await create_contributions(contributions, user)

    return _contributions


async def delete_contributions_mutation(info: Info, contributions: list[UUID]) -> list[UUID]:
    """Deletes Contributions"""

    user = get_user(info)
    _contributions = await delete_contributions(contributions, user)

    return _contributions


async def update_contributions_mutation(
    info: Info, contributions: list[UpdateContribution]
) -> list[GraphQLContribution]:
    """Updates Contributions"""

    user = get_user(info)
    _contributions = await update_contributions(contributions, user)

    return _contributions
