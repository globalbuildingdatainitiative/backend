from inspect import getdoc

import strawberry

from models import GraphQLUser, InviteResult, RolePermission
from models.user_response import UserResponse
from schema.permissions import IsAuthenticated, IsAdmin
from schema.roles import make_admin_mutation, unmake_admin_mutation, roles_query
from schema.user import (
    update_user_mutation,
    invite_users_mutation,
    accept_invitation_mutation,
    reject_invitation_mutation,
    resend_invitation_mutation,
    impersonate_mutation,
)


@strawberry.type
class Query:
    @strawberry.field(permission_classes=[IsAuthenticated], description="Returns all Users")
    async def users(self) -> UserResponse:
        return UserResponse()

    roles: list[RolePermission] = strawberry.field(
        resolver=roles_query, description=getdoc(roles_query), permission_classes=[IsAuthenticated]
    )


@strawberry.type
class Mutation:
    update_user: GraphQLUser = strawberry.field(
        resolver=update_user_mutation, description=getdoc(update_user_mutation), permission_classes=[IsAuthenticated]
    )
    invite_users: list[InviteResult] = strawberry.field(
        resolver=invite_users_mutation, description=getdoc(invite_users_mutation), permission_classes=[IsAuthenticated]
    )
    accept_invitation: bool = strawberry.field(
        resolver=accept_invitation_mutation, description=getdoc(accept_invitation_mutation)
    )
    reject_invitation: bool = strawberry.field(
        resolver=reject_invitation_mutation, description=getdoc(reject_invitation_mutation)
    )
    resend_invitation: InviteResult = strawberry.field(
        resolver=resend_invitation_mutation,
        description=getdoc(resend_invitation_mutation),
        permission_classes=[IsAuthenticated],
    )
    impersonate: bool = strawberry.field(
        resolver=impersonate_mutation, description=getdoc(impersonate_mutation), permission_classes=[IsAdmin]
    )
    make_admin: bool = strawberry.field(
        resolver=make_admin_mutation, description=getdoc(make_admin_mutation), permission_classes=[IsAdmin]
    )
    # unmake admin mutation can be added here similarly
    unmake_admin: bool = strawberry.field(
        resolver=unmake_admin_mutation, description=getdoc(unmake_admin_mutation), permission_classes=[IsAdmin]
    )


schema = strawberry.federation.Schema(query=Query, mutation=Mutation, enable_federation_2=True)
