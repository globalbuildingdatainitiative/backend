from uuid import UUID
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


async def create_organizations_mutation(organizations: list[InputOrganization]) -> list[DBOrganization]:
    _organizations = []
    for _organization in organizations:
        organization = DBOrganization(name=_organization.name)
        await organization.insert()
        _organizations.append(organization)

    return _organizations


async def update_organizations_mutation(organizations: list[InputOrganization]) -> list[GraphQLOrganization | None]:
    """Updates a list of existing Organizations"""

    updated_organizations = []
    for organization_data in organizations:
        organization_id = organization_data.__getattribute__("id")

        if not organization_id:
            # Handle case where no ID is provided for update
            return None  # Or raise an exception

        organization = await DBOrganization.get(document_id=organization_id)
        if organization:
            update_doc = {"$set": {"name": organization_data.__getattribute__("name")}}
            # organization.name = organization_data.__getattribute__("name")  # Update name if provided
            await organization.update(update_doc)
            updated_organizations.append(organization)
        else:
            # Handle case where organization with the provided ID is not found
            updated_organizations.append(None)  # Or raise an exception

    return updated_organizations


async def delete_organizations_mutation(ids: list[UUID]) -> list[UUID | None]:
    """Deletes a list of Organizations by their IDs and returns a list of deleted IDs"""

    deleted_ids = []
    for organization_id in ids:
        organization = await DBOrganization.get(document_id=organization_id)
        if organization:
            await organization.delete()
            deleted_ids.append(organization_id)

    return deleted_ids
