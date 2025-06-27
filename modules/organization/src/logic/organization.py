import logging
from uuid import UUID

from core.exceptions import EntityNotFound
from logic.roles import assign_role, Role
from models import (
    DBOrganization,
    InputOrganization,
    SuperTokensUser,
    OrganizationMetaDataModel,
)
from models.sort_filter import filter_model_query, FilterBy, SortBy, sort_model_query

logger = logging.getLogger("main")


async def get_organizations(
    filter_by: FilterBy | None = None,
    sort_by: SortBy | None = None,
    limit: int | None = None,
    offset: int = 0,
) -> list[DBOrganization]:
    query = DBOrganization.find()
    if filter_by:
        query = filter_model_query(DBOrganization, filter_by, query)

    if sort_by:
        query = sort_model_query(DBOrganization, sort_by, query)

    if limit is not None:
        query = query.limit(limit)

    if offset:
        query = query.skip(offset)

    organizations = await query.to_list()
    logger.debug(f"Found {len(organizations)} organizations")

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
            meta_data=OrganizationMetaDataModel(stakeholders=organization_data.meta_data.stakeholders),
        )
        await new_organization.insert()
        new_organizations.append(new_organization)
    await update_user_metadata(str(current_user.id), {"organization_id": str(new_organizations[0].id)})
    await assign_role(current_user.id, Role.OWNER)

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
                    "country": organization_data.country,
                    "meta_data": OrganizationMetaDataModel(
                        stakeholders=organization_data.meta_data.stakeholders
                    ).dict(),
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
