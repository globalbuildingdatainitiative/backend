from inspect import getdoc
from uuid import UUID

import strawberry

from models import GraphQLContribution, GraphQLResponse, GraphQLProject, GraphQLUser
from models.openbdf.types import GraphQLProjectState
from schema.contribution import add_contributions_mutation, delete_contributions_mutation, update_contributions_mutation
from schema.permisions import IsAuthenticated
from schema.resolvers.project_mutations import (
    submit_for_review_resolver,
    approve_project_resolver,
    reject_project_resolver,
    publish_project_resolver,
    unpublish_project_resolver,
    delete_project_resolver,
    lock_project_resolver,
    unlock_project_resolver,
    assign_project_resolver,
)
from schema.resolvers.project_queries import (
    projects_by_state_resolver,
    projects_for_review_resolver,
    projects_to_publish_resolver,
    projects_to_unpublish_resolver,
    projects_to_delete_resolver,
    my_projects_resolver,
    assigned_projects_resolver,
)
from schema.project_schema import (
    SubmitForReviewInput,
    ApproveProjectInput,
    RejectProjectInput,
    PublishProjectInput,
    UnpublishProjectInput,
    DeleteProjectInput,
    LockProjectInput,
    UnlockProjectInput,
    AssignProjectInput,
    ProjectsByStateInput,
)


@strawberry.type
class Query:
    @strawberry.field(permission_classes=[IsAuthenticated], description="Returns all projects of a user's organization")
    async def projects(self) -> GraphQLResponse[GraphQLProject]:
        return GraphQLResponse(GraphQLProject)

    @strawberry.field(
        permission_classes=[IsAuthenticated], description="Returns all contributions of a user's organization"
    )
    async def contributions(self) -> GraphQLResponse[GraphQLContribution]:
        return GraphQLResponse(GraphQLContribution)

    # New project query fields
    @strawberry.field(permission_classes=[IsAuthenticated], description="Get projects by state")
    async def projects_by_state(self, input: ProjectsByStateInput) -> list[GraphQLProject]:
        return await projects_by_state_resolver(self, input)

    @strawberry.field(
        permission_classes=[IsAuthenticated], description="Get projects that are in review (IN_REVIEW state)"
    )
    async def projects_for_review(self) -> list[GraphQLProject]:
        return await projects_for_review_resolver(self)

    @strawberry.field(
        permission_classes=[IsAuthenticated], description="Get projects that are ready to publish (TO_PUBLISH state)"
    )
    async def projects_to_publish(self) -> list[GraphQLProject]:
        return await projects_to_publish_resolver(self)

    @strawberry.field(
        permission_classes=[IsAuthenticated],
        description="Get projects that are marked for unpublishing (TO_UNPUBLISH state)",
    )
    async def projects_to_unpublish(self) -> list[GraphQLProject]:
        return await projects_to_unpublish_resolver(self)

    @strawberry.field(
        permission_classes=[IsAuthenticated], description="Get projects that are marked for deletion (TO_DELETE state)"
    )
    async def projects_to_delete(self) -> list[GraphQLProject]:
        return await projects_to_delete_resolver(self)

    @strawberry.field(permission_classes=[IsAuthenticated], description="Get projects created by the current user")
    async def my_projects(self) -> list[GraphQLProject]:
        return await my_projects_resolver(self)

    @strawberry.field(permission_classes=[IsAuthenticated], description="Get projects assigned to the current reviewer")
    async def assigned_projects(self) -> list[GraphQLProject]:
        return await assigned_projects_resolver(self)


@strawberry.type
class Mutation:
    add_contributions: list[GraphQLContribution] = strawberry.field(
        resolver=add_contributions_mutation,
        description=getdoc(add_contributions_mutation),
        permission_classes=[IsAuthenticated],
    )
    delete_contributions: list[UUID] = strawberry.field(
        resolver=delete_contributions_mutation,
        description=getdoc(delete_contributions_mutation),
        permission_classes=[IsAuthenticated],
    )
    update_contributions: list[GraphQLContribution] = strawberry.field(
        resolver=update_contributions_mutation,
        description=getdoc(update_contributions_mutation),
        permission_classes=[IsAuthenticated],
    )

    # New project mutation fields
    @strawberry.field(
        permission_classes=[IsAuthenticated],
        description="Submit a project for review (Contributor action)\nTransitions: DRAFT → IN_REVIEW",
    )
    async def submit_for_review(self, input: SubmitForReviewInput) -> GraphQLProject:
        return await submit_for_review_resolver(self, input)

    @strawberry.field(
        permission_classes=[IsAuthenticated],
        description="Approve a project for publication (Reviewer action)\nTransitions: IN_REVIEW → TO_PUBLISH",
    )
    async def approve_project(self, input: ApproveProjectInput) -> GraphQLProject:
        return await approve_project_resolver(self, input)

    @strawberry.field(
        permission_classes=[IsAuthenticated],
        description="Reject a project and send it back to draft (Reviewer action)\nTransitions: IN_REVIEW → DRAFT",
    )
    async def reject_project(self, input: RejectProjectInput) -> GraphQLProject:
        return await reject_project_resolver(self, input)

    @strawberry.field(
        permission_classes=[IsAuthenticated],
        description="Publish a project (Administrator action)\nTransitions: TO_PUBLISH → DRAFT (published)",
    )
    async def publish_project(self, input: PublishProjectInput) -> GraphQLProject:
        return await publish_project_resolver(self, input)

    @strawberry.field(
        permission_classes=[IsAuthenticated],
        description="Mark a project for unpublishing (Administrator action)\nTransitions: DRAFT → TO_UNPUBLISH",
    )
    async def unpublish_project(self, input: UnpublishProjectInput) -> GraphQLProject:
        return await unpublish_project_resolver(self, input)

    @strawberry.field(
        permission_classes=[IsAuthenticated],
        description="Delete a project (Administrator action)\nTransitions: TO_DELETE → deleted",
    )
    async def delete_project(self, input: DeleteProjectInput) -> bool:
        return await delete_project_resolver(self, input)

    @strawberry.field(
        permission_classes=[IsAuthenticated],
        description="Lock a project (Administrator action)\nTransitions: any state → LOCKED",
    )
    async def lock_project(self, input: LockProjectInput) -> GraphQLProject:
        return await lock_project_resolver(self, input)

    @strawberry.field(
        permission_classes=[IsAuthenticated],
        description="Unlock a project (Administrator action)\nTransitions: LOCKED → previous state",
    )
    async def unlock_project(self, input: UnlockProjectInput) -> GraphQLProject:
        return await unlock_project_resolver(self, input)

    @strawberry.field(
        permission_classes=[IsAuthenticated], description="Assign a project to a user (Administrator action)"
    )
    async def assign_project(self, input: AssignProjectInput) -> GraphQLProject:
        return await assign_project_resolver(self, input)


schema = strawberry.federation.Schema(query=Query, mutation=Mutation, types=[GraphQLUser], enable_federation_2=True)
