from uuid import UUID

from beanie import WriteRules
from strawberry import Info

from models import DBOrganization, GraphQLOrganization, OrganizationFilter, InputOrganization


async def get_organizations(filters: OrganizationFilter | None = None) -> list[DBOrganization]:
    query = DBOrganization.find()
    if filters:
        if filters.id:
            if filters.id.equal:
                query = query.find(DBOrganization.id == filters.id.equal)
        if filters.name:
            if filters.name.equal:
                query = query.find(DBOrganization.name == filters.name.equal)
    return await query.to_list()


async def create_organizations_mutation(info: Info, organizations: list[InputOrganization]) -> list[DBOrganization]:
    _organizations = []
    for _organization in organizations:
        organization = DBOrganization(**_organization.dict())
        await organization.insert(link_rule=WriteRules.WRITE)
        _organizations.append(organization)

    return _organizations


async def update_organizations_mutation(info: Info, organizations: list[InputOrganization]) -> list[
    GraphQLOrganization | None]:
    """Updates a list of existing Organizations"""

    updated_organizations = []
    for organization_data in organizations:
        organization_id = organization_data.get("id")

        if not organization_id:
            # Handle case where no ID is provided for update
            return None  # Or raise an exception

        organization = await DBOrganization.get(id=organization_id)
        if organization:
            organization.name = organization_data.get("name", organization.name)  # Update name if provided
            await organization.update()
            updated_organizations.append(organization)
        else:
            # Handle case where organization with the provided ID is not found
            updated_organizations.append(None)  # Or raise an exception

    return updated_organizations


async def delete_organizations_mutation(info: Info, ids: list[UUID]) -> list[UUID | None]:
    """Deletes a list of Organizations by their IDs and returns a list of deleted IDs"""

    deleted_ids = []
    for organization_id in ids:
        organization = await DBOrganization.get(id=organization_id)
        if organization:
            await organization.delete()
            deleted_ids.append(organization_id)

    return deleted_ids
