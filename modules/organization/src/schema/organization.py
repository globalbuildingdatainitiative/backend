from uuid import UUID

from strawberry.types import Info

from logic import (
    get_organizations,
    create_organizations_mutation,
    update_organizations_mutation,
    delete_organizations_mutation,
)
from models import OrganizationFilter, InputOrganization, DBOrganization


async def organizations_query(info: Info, filters: OrganizationFilter | None = None) -> list[DBOrganization]:
    """Returns all Organizations"""

    organizations = await get_organizations(filters)
    return organizations


async def add_organizations_mutation(info: Info, organizations: list[InputOrganization]) -> list[DBOrganization]:
    """Creates multiple organizations and associates them with the current user"""
    current_user = info.context.get("user")
    new_organization = await create_organizations_mutation(organizations, current_user)
    return new_organization


async def edit_organizations_mutation(info: Info, organizations: list[InputOrganization]) -> list[DBOrganization]:
    """Updates an existing Organization"""

    organizations = await update_organizations_mutation(organizations)
    return organizations


async def remove_organizations_mutation(info: Info, ids: list[UUID]) -> list[UUID]:
    """Deletes a list of Organizations by their IDs and returns a list of deleted IDs"""

    organizations = await delete_organizations_mutation(ids)
    return organizations
