from uuid import UUID

from strawberry.types import Info

from logic import (
    get_organizations,
    add_organizations,
    edit_organizations,
    remove_organizations,
    add_organization,
)
from models import GraphQLOrganization, OrganizationFilter, InputOrganization


async def organizations_query(info: Info, filters: OrganizationFilter | None = None) -> list[GraphQLOrganization]:
    """Returns all Organizations"""

    organizations = await get_organizations(filters)
    return organizations


async def add_organizations_mutation(
    info: Info, names: list[str], addresses: list[str], cities: list[str], countries: list[str]
) -> list[GraphQLOrganization]:
    """Creates a new Organization for each name in the provided list and returns them"""

    organizations = await add_organizations(names, addresses, cities, countries)
    return organizations


async def add_organization_mutation(info: Info, organization: InputOrganization) -> GraphQLOrganization:
    current_user = info.context["current_user"]
    new_organization = await add_organization(organization, current_user)  # assuming you have the user_id
    return new_organization


async def edit_organizations_mutation(info: Info, _id: UUID, name: str) -> list[GraphQLOrganization]:
    """Updates an existing Organization"""

    organizations = await edit_organizations(name, _id)
    return organizations


async def remove_organizations_mutation(info: Info, ids: list[UUID]) -> list[UUID]:
    """Deletes a list of Organizations by their IDs and returns a list of deleted IDs"""

    organizations = await remove_organizations(ids)
    return organizations
