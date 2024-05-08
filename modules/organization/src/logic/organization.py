from uuid import UUID
from models import DBOrganization, OrganizationFilter, InputOrganization, User
from exceptions.exceptions import EntityNotFound
from models.country_codes import get_country_codes_by_name


def get_country_code(country_name: str) -> str:
    return get_country_codes_by_name(country_name=country_name)


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


async def create_organizations_mutation(
    organizations: list[InputOrganization], current_user: User
) -> list[DBOrganization]:
    new_organizations = []
    for organization_data in organizations:
        new_organization = DBOrganization(
            name=organization_data.name,
            address=organization_data.address,
            city=organization_data.city,
            country=get_country_code(organization_data.country),
        )
        await new_organization.insert()
        new_organizations.append(new_organization)

        current_user.organization_id = new_organization.id

    return new_organizations


async def update_organizations_mutation(organizations: list[InputOrganization]) -> list[DBOrganization]:
    """Updates a list of existing Organizations"""

    updated_organizations = []
    for organization_data in organizations:
        organization_id = organization_data.id
        organization = await DBOrganization.get(document_id=organization_id)
        if organization:
            update_doc = {
                "$set": {
                    "name": organization_data.name,
                    "address": organization_data.address,
                    "city": organization_data.city,
                    "country": get_country_code(organization_data.country),
                }
            }
            await organization.update(update_doc)
            updated_organizations.append(organization)
        else:
            raise EntityNotFound("ERROR: Organization Not Found", organization_data.name)

    return updated_organizations


async def delete_organizations_mutation(ids: list[UUID]) -> list[UUID]:
    """Deletes a list of Organizations by their IDs and returns a list of deleted IDs"""

    deleted_ids = []
    for organization_id in ids:
        organization = await DBOrganization.get(document_id=organization_id)
        if organization:
            await organization.delete()
            deleted_ids.append(organization_id)
        else:
            raise EntityNotFound("ERROR: Organization Not Found", str(organization_id))

    return deleted_ids
