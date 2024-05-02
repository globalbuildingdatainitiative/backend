from ..models import DBOrganization, GraphQLOrganization, OrganizationFilter
from strawberry.types import Info, ID
from ..logic import get_organization, create_organization_mutation, update_organization_mutation, \
    delete_organization_mutation


async def organization_query(info: Info, filters: OrganizationFilter | None = None) -> list[GraphQLOrganization]:
    """Returns all Organizations"""

    organizations = await get_organization(filters)
    return organizations


async def create_organization_mutation(info: Info, name: str) -> list[GraphQLOrganization]:
    """Creates a new Organization"""

    organization = DBOrganization(name=name)
    await organization.insert()
    return organization


async def update_organization_mutation(info: Info, id: ID, name: str) -> list[GraphQLOrganization]:
    """Updates an existing Organization"""

    organization = await DBOrganization.get(id=id)
    if organization:  # If organization exists, it will update else return None
        organization.name = name
        await organization.update()
        return organization
    return None


async def delete_organization_mutation(info: Info, id: ID) -> list[GraphQLOrganization]:
    """Deletes an existing Organization"""

    organization = await DBOrganization.get(id=id)
    if organization:
        await organization.delete()
        return True
    return False
