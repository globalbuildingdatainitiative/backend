from uuid import uuid4

from models import GraphQLUser
from models.user import get_user_organization


async def test_get_user_organization(organizations):
    organization = organizations[2]
    _user = GraphQLUser(id=uuid4(), organizationId=organization.id)

    _organization = await get_user_organization(_user)

    assert _organization.id == organization.id
