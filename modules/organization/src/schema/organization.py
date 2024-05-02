from uuid import UUID
from models import GraphQLOrganization, OrganizationFilter, DBOrganization
from strawberry.types import Info, ID
from logic import get_organizations, create_organizations_mutation, update_organizations_mutation, \
    delete_organizations_mutation


async def organizations_query(info: Info, filters: OrganizationFilter | None = None) -> list[GraphQLOrganization]:
    """Returns all Organizations"""

    organizations = await get_organizations(filters)
    return organizations


async def add_organizations_mutation(info: Info, names: list[str]) -> list[GraphQLOrganization]:
    """Creates a new Organization for each name in the provided list and returns them"""

    organizations = []
    for name in names:
        organization = DBOrganization(name=name)
        await create_organizations_mutation(organization)
        organizations.append(organization)

    return organizations


async def edit_organizations_mutation(info: Info, id: ID, name: str) -> list[GraphQLOrganization]:
    """Updates an existing Organization"""

    organization = await get_organizations(id=id)
    if organization:  # If organization exists, it will update else return None
        await update_organizations_mutation(id=id, name=name)
        return organization
    return None


async def remove_organizations_mutation(info: Info, ids: list[UUID]) -> list[UUID]:
    """Deletes a list of Organizations by their IDs and returns a list of deleted IDs"""

    deleted_ids = []
    for organization_id in ids:
        organization = await get_organizations(
            id=organization_id)  # Assuming get_organization fetches a single organization
        if organization:
            await delete_organizations_mutation(id=organization_id)
            deleted_ids.append(organization_id)

    return deleted_ids
