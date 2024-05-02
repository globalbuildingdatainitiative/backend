from uuid import UUID

from beanie import WriteRules
from strawberry import Info

from ..models import DBOrganization, GraphQLOrganization,  OrganizationFilter


async def get_organization(
        filters: OrganizationFilter | None = None
        ) -> list[DBOrganization]:

    query = DBOrganization.find()
    if filters:
        if filters.id:
            if filters.id.equal:
                query = query.find(DBOrganization.id == filters.id.equal)
        if filters.name:
            if filters.name.equal:
                query = query.find(DBOrganization.name == filters.name.equal)
    return await query.to_list()


async def create_organization_mutation(info: Info, name: str) -> GraphQLOrganization:
    """Creates a new Organization"""

    organization = DBOrganization(name=name)
    await organization.insert(link_rule=WriteRules.WRITE)
    return organization


async def update_organization_mutation(info: Info, id: UUID, name: str) -> GraphQLOrganization | None:
    """Updates an existing Organization"""

    organization = await DBOrganization.get(id=id)
    if organization:
        organization.name = name
        await organization.update()
        return organization
    return None


async def delete_organization_mutation(info: Info, id: UUID) -> bool:
    """Deletes an existing Organization"""

    organization = await DBOrganization.get(id=id)
    if organization:
        await organization.delete()
        return True
    return False
