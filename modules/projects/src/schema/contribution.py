from strawberry.types import Info

from core.context import get_user
from logic import create_contributions
from models import GraphQLContribution, InputContribution


async def add_contributions_mutation(info: Info, contributions: list[InputContribution]) -> list[GraphQLContribution]:
    """Creates new Contributions"""

    user = get_user(info)
    _contributions = await create_contributions(contributions, user)

    return _contributions
