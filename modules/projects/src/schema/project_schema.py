from enum import Enum
import logging
from typing import Optional, List
from uuid import UUID

import strawberry
from strawberry.types import Info

from core.context import get_user
from models.project_state import ProjectState
from models.user_role import UserRole
from models.database.db_model import DBProject
from models.openbdf.types import GraphQLProject, GraphQLProjectState
from logic.project_service import ProjectService
from logic.permissions import (
    has_permission,
    can_submit_for_review,
    can_approve_project,
    can_reject_project,
    can_publish_project,
    can_unpublish_project,
    can_delete_project,
    can_lock_project,
    can_unlock_project,
    can_assign_project,
)

logger = logging.getLogger(__name__)


# Input types
@strawberry.input
class SubmitForReviewInput:
    project_id: UUID


@strawberry.input
class ApproveProjectInput:
    project_id: UUID


@strawberry.input
class RejectProjectInput:
    project_id: UUID


@strawberry.input
class PublishProjectInput:
    project_id: UUID


@strawberry.input
class UnpublishProjectInput:
    project_id: UUID


@strawberry.input
class DeleteProjectInput:
    project_id: UUID


@strawberry.input
class LockProjectInput:
    project_id: UUID


@strawberry.input
class UnlockProjectInput:
    project_id: UUID


@strawberry.input
class AssignProjectInput:
    project_id: UUID
    user_id: UUID


@strawberry.input
class ProjectsByStateInput:
    state: GraphQLProjectState


# Mutation resolvers
async def submit_for_review_resolver(info: Info, input: SubmitForReviewInput) -> GraphQLProject:
    """
    Submit a project for review (Contributor action)
    Transitions: DRAFT → IN_REVIEW
    """
    # This is a placeholder implementation that should fail until the real implementation is complete
    raise NotImplementedError("submit_for_review_resolver not implemented")


async def approve_project_resolver(info: Info, input: ApproveProjectInput) -> GraphQLProject:
    """
    Approve a project for publication (Reviewer action)
    Transitions: IN_REVIEW → TO_PUBLISH
    """
    # This is a placeholder implementation that should fail until the real implementation is complete
    raise NotImplementedError("approve_project_resolver not implemented")


async def reject_project_resolver(info: Info, input: RejectProjectInput) -> GraphQLProject:
    """
    Reject a project and send it back to draft (Reviewer action)
    Transitions: IN_REVIEW → DRAFT
    """
    # This is a placeholder implementation that should fail until the real implementation is complete
    raise NotImplementedError("reject_project_resolver not implemented")


async def publish_project_resolver(info: Info, input: PublishProjectInput) -> GraphQLProject:
    """
    Publish a project (Administrator action)
    Transitions: TO_PUBLISH → DRAFT (published)
    """
    # This is a placeholder implementation that should fail until the real implementation is complete
    raise NotImplementedError("publish_project_resolver not implemented")


async def unpublish_project_resolver(info: Info, input: UnpublishProjectInput) -> GraphQLProject:
    """
    Mark a project for unpublishing (Administrator action)
    Transitions: DRAFT → TO_UNPUBLISH
    """
    # This is a placeholder implementation that should fail until the real implementation is complete
    raise NotImplementedError("unpublish_project_resolver not implemented")


async def delete_project_resolver(info: Info, input: DeleteProjectInput) -> bool:
    """
    Delete a project (Administrator action)
    Transitions: TO_DELETE → deleted
    """
    # This is a placeholder implementation that should fail until the real implementation is complete
    raise NotImplementedError("delete_project_resolver not implemented")


async def lock_project_resolver(info: Info, input: LockProjectInput) -> GraphQLProject:
    """
    Lock a project (Administrator action)
    Transitions: any state → LOCKED
    """
    # This is a placeholder implementation that should fail until the real implementation is complete
    raise NotImplementedError("lock_project_resolver not implemented")


async def unlock_project_resolver(info: Info, input: UnlockProjectInput) -> GraphQLProject:
    """
    Unlock a project (Administrator action)
    Transitions: LOCKED → previous state
    """
    # This is a placeholder implementation that should fail until the real implementation is complete
    raise NotImplementedError("unlock_project_resolver not implemented")


async def assign_project_resolver(info: Info, input: AssignProjectInput) -> GraphQLProject:
    """
    Assign a project to a user (Administrator action)
    """
    # This is a placeholder implementation that should fail until the real implementation is complete
    raise NotImplementedError("assign_project_resolver not implemented")


# Query resolvers
async def projects_by_state_resolver(info: Info, input: ProjectsByStateInput) -> List[GraphQLProject]:
    """
    Get projects by state
    """
    # This is a placeholder implementation that should fail until the real implementation is complete
    raise NotImplementedError("projects_by_state_resolver not implemented")


async def projects_for_review_resolver(info: Info) -> List[GraphQLProject]:
    """
    Get projects that are in review (IN_REVIEW state)
    """
    # This is a placeholder implementation that should fail until the real implementation is complete
    raise NotImplementedError("projects_for_review_resolver not implemented")


async def projects_to_publish_resolver(info: Info) -> List[GraphQLProject]:
    """
    Get projects that are ready to publish (TO_PUBLISH state)
    """
    # This is a placeholder implementation that should fail until the real implementation is complete
    raise NotImplementedError("projects_to_publish_resolver not implemented")


async def projects_to_unpublish_resolver(info: Info) -> List[GraphQLProject]:
    """
    Get projects that are marked for unpublishing (TO_UNPUBLISH state)
    """
    # This is a placeholder implementation that should fail until the real implementation is complete
    raise NotImplementedError("projects_to_unpublish_resolver not implemented")


async def projects_to_delete_resolver(info: Info) -> List[GraphQLProject]:
    """
    Get projects that are marked for deletion (TO_DELETE state)
    """
    # This is a placeholder implementation that should fail until the real implementation is complete
    raise NotImplementedError("projects_to_delete_resolver not implemented")


async def my_projects_resolver(info: Info) -> List[GraphQLProject]:
    """
    Get projects created by the current user
    """
    # This is a placeholder implementation that should fail until the real implementation is complete
    raise NotImplementedError("my_projects_resolver not implemented")


async def assigned_projects_resolver(info: Info) -> List[GraphQLProject]:
    """
    Get projects assigned to the current reviewer
    """
    # This is a placeholder implementation that should fail until the real implementation is complete
    raise NotImplementedError("assigned_projects_resolver not implemented")
