from uuid import UUID
from models import DBOrganization, OrganizationFilter, InputOrganization, SuperTokensUser
from exceptions.exceptions import EntityNotFound

# Define the allowed stakeholders list for validation
ALLOWED_STAKEHOLDERS = [
    "Building data owners",
    "Building design professionals (architects, engineers)",
    "Building design / LCA tool developers and providers",
    "Building LCA consultants and service providers",
    "Building users",
    "Civil society",
    "Clients / inventors / owners (of building data)",
    "Construction companies",
    "Construction product manufacturers",
    "Facility managers",
    "Financial service providers / insurance companies",
    "Funding (system) developers and providers",
    "Inter / National standardization bodies",
    "Media representatives",
    "Policy and law makers, regulators (national, local)",
    "Product LCA database developers",
    "Product LCA/EPD data developers",
    "Researchers (basic / applied building LCA research)",
    "Surveyors, valuation professionals",
    "Sustainability assessment system developers and providers",
    "Sustainability assessors/auditors",
    "Sustainability / ESG consultants and service providers",
]


async def get_organizations(filters: OrganizationFilter | None = None) -> list[DBOrganization]:
    query = DBOrganization.find()
    if filters:
        if filters.id:
            if filters.id.equal:
                if isinstance(filters.id.equal, UUID):
                    query = query.find(DBOrganization.id == filters.id.equal)
                else:
                    query = query.find(DBOrganization.id == UUID(filters.id.equal))
        if filters.name:
            if filters.name.equal:
                query = query.find(DBOrganization.name == filters.name.equal)
        if filters.stakeholders:
            if filters.stakeholders.equal:
                query = query.find(DBOrganization.stakeholders == filters.stakeholders.equal)
    organizations = await query.to_list()
    return organizations


async def create_organizations_mutation(
    organizations: list[InputOrganization], current_user: SuperTokensUser
) -> list[DBOrganization]:
    from supertokens_python.recipe.usermetadata.asyncio import update_user_metadata

    new_organizations = []
    for organization_data in organizations:
        new_organization = DBOrganization(
            name=organization_data.name,
            address=organization_data.address,
            city=organization_data.city,
            country=organization_data.country,
            stakeholders=organization_data.stakeholders,
        )
        await new_organization.insert()
        new_organizations.append(new_organization)
    await update_user_metadata(str(current_user.id), {"organization_id": str(new_organizations[0].id)})

    return new_organizations


async def update_organizations_mutation(organizations: list[InputOrganization]) -> list[DBOrganization]:
    """Updates a list of existing Organizations"""

    updated_organizations = []
    for organization_data in organizations:
        organization_id = organization_data.id
        organization = await DBOrganization.get(document_id=organization_id)
        if organization:
            # Validate stakeholders
            invalid_stakeholders = [s for s in organization_data.stakeholders if s not in ALLOWED_STAKEHOLDERS]
            if invalid_stakeholders:
                raise ValueError(f"Invalid stakeholders: {invalid_stakeholders}")
            update_doc = {
                "$set": {
                    "name": organization_data.name,
                    "address": organization_data.address,
                    "city": organization_data.city,
                    "country": organization_data.country,
                    "stakeholders": organization_data.stakeholders,
                }
            }
            await organization.update(update_doc)
            updated_organizations.append(organization)
        else:
            raise EntityNotFound("Organization Not Found", organization_data.name)

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
            raise EntityNotFound("Organization Not Found", str(organization_id))

    return deleted_ids
