from inspect import getdoc

import strawberry

from models import GraphQLUser, InviteResult
from schema.permissions import IsAuthenticated, IsAdmin
from schema.user import (
    users_query,
    update_user_mutation,
    invite_users_mutation,
    accept_invitation_mutation,
    reject_invitation_mutation,
    resend_invitation_mutation,
    impersonate_mutation
)


@strawberry.type
class Query:
    users: list[GraphQLUser] = strawberry.field(
        resolver=users_query, description=getdoc(users_query), permission_classes=[IsAuthenticated]
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


schema = strawberry.federation.Schema(query=Query, mutation=Mutation, enable_federation_2=True)
