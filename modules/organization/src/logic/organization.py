from uuid import UUID
from models import DBOrganization, GraphQLOrganization, OrganizationFilter, InputOrganization, User
from exceptions.exceptions import EntityNotFound


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


async def add_organizations(
    names: list[str], addresses: list[str], cities: list[str], countries: list[str]
) -> list[DBOrganization]:
    organizations = []
    for name, address, city, country in zip(names, addresses, cities, countries):
        organization = DBOrganization(name=name, address=address, city=city, country=country)
        await organization.insert()
        organizations.append(organization)

    return organizations


async def add_organization(organization: InputOrganization, current_user: User) -> DBOrganization:
    new_organization = DBOrganization(
        name=organization.name, address=organization.address, city=organization.city, country=organization.country
    )
    await new_organization.insert()

    current_user._organization_id = new_organization.id
    await current_user.save()  # Assuming your User model has a save method
    return new_organization


async def edit_organizations(name: str, _id: UUID) -> DBOrganization:
    organization = await DBOrganization.get(document_id=_id)
    if organization:
        update_doc = {"$set": {"name": name}}
        await organization.update(update_doc)
    else:
        raise EntityNotFound("ERROR: Organization Not Found", name)
    return organization


async def remove_organizations(ids: list[UUID]) -> list[UUID]:
    deleted_ids = []
    for organization_id in ids:
        organization = await DBOrganization.get(document_id=organization_id)
        if organization:
            await organization.delete()
            deleted_ids.append(organization_id)
        else:
            raise EntityNotFound("ERROR: Organization Not Found", str(organization_id))
    return deleted_ids


async def create_organizations_mutation(organizations: list[InputOrganization]) -> list[DBOrganization]:
    _organizations = []
    for _organization in organizations:
        organization = DBOrganization(
            name=_organization.name,
            address=_organization.address,
            city=_organization.city,
            country=_organization.country,
        )

        await organization.insert()
        _organizations.append(organization)

    return _organizations


async def update_organizations_mutation(organizations: list[InputOrganization]) -> list[GraphQLOrganization]:
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
                    "country": organization_data.country,
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
