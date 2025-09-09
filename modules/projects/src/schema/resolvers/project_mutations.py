import logging
from typing import Optional
from uuid import UUID

import strawberry
from strawberry.types import Info

from core.context import get_user
from models.database.db_model import DBProject
from models.openbdf.types import GraphQLProject
from logic.project_service import ProjectService
from logic.permissions import (
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
from logic.notifications import (
    send_project_submission_notification,
    send_project_approval_notification,
    send_project_rejection_notification,
    send_project_publication_notification,
    send_project_unpublication_notification,
    send_project_deletion_notification,
    send_project_lock_notification,
    send_project_unlock_notification,
    send_project_assignment_notification,
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
)

logger = logging.getLogger(__name__)


async def submit_for_review_resolver(info: Info, input: SubmitForReviewInput) -> GraphQLProject:
    """
    Submit a project for review (Contributor action)
    Transitions: DRAFT → IN_REVIEW
    """
    user = get_user(info)
    project = await ProjectService.submit_for_review(input.project_id, user.id, user.roles)
    # Send notification
    await send_project_submission_notification(project, user)
    return GraphQLProject.from_pydantic(project)


async def approve_project_resolver(info: Info, input: ApproveProjectInput) -> GraphQLProject:
    """
    Approve a project for publication (Reviewer action)
    Transitions: IN_REVIEW → TO_PUBLISH
    """
    user = get_user(info)
    project = await ProjectService.approve_project(input.project_id, user.id, user.roles)
    # Send notification
    await send_project_approval_notification(project, user)
    return GraphQLProject.from_pydantic(project)


async def reject_project_resolver(info: Info, input: RejectProjectInput) -> GraphQLProject:
    """
    Reject a project and send it back to draft (Reviewer action)
    Transitions: IN_REVIEW → DRAFT
    """
    user = get_user(info)
    project = await ProjectService.reject_project(input.project_id, user.id, user.roles)
    # Send notification
    await send_project_rejection_notification(project, user)
    return GraphQLProject.from_pydantic(project)


async def publish_project_resolver(info: Info, input: PublishProjectInput) -> GraphQLProject:
    """
    Publish a project (Administrator action)
    Transitions: TO_PUBLISH → DRAFT (published)
    """
    user = get_user(info)
    project = await ProjectService.publish_project(input.project_id, user.id, user.roles)
    # Send notification
    await send_project_publication_notification(project, user)
    return GraphQLProject.from_pydantic(project)


async def unpublish_project_resolver(info: Info, input: UnpublishProjectInput) -> GraphQLProject:
    """
    Mark a project for unpublishing (Administrator action)
    Transitions: DRAFT → TO_UNPUBLISH
    """
    user = get_user(info)
    project = await ProjectService.unpublish_project(input.project_id, user.id, user.roles)
    # Send notification
    await send_project_unpublication_notification(project, user)
    return GraphQLProject.from_pydantic(project)


async def delete_project_resolver(info: Info, input: DeleteProjectInput) -> bool:
    """
    Delete a project (Administrator action)
    Transitions: TO_DELETE → deleted
    """
    user = get_user(info)
    result = await ProjectService.delete_project(input.project_id, user.id, user.roles)
    # Send notification
    # Note: We need to fetch the project before deletion to send notification
    project = await DBProject.get(input.project_id)
    if project:
        await send_project_deletion_notification(project, user)
    return result


async def lock_project_resolver(info: Info, input: LockProjectInput) -> GraphQLProject:
    """
    Lock a project (Administrator action)
    Transitions: any state → LOCKED
    """
    user = get_user(info)
    project = await ProjectService.lock_project(input.project_id, user.id, user.roles)
    # Send notification
    await send_project_lock_notification(project, user)
    return GraphQLProject.from_pydantic(project)


async def unlock_project_resolver(info: Info, input: UnlockProjectInput) -> GraphQLProject:
    """
    Unlock a project (Administrator action)
    Transitions: LOCKED → previous state
    """
    user = get_user(info)
    project = await ProjectService.unlock_project(input.project_id, user.id, user.roles)
    # Send notification
    await send_project_unlock_notification(project, user)
    return GraphQLProject.from_pydantic(project)


async def assign_project_resolver(info: Info, input: AssignProjectInput) -> GraphQLProject:
    """
    Assign a project to a user (Administrator action)
    """
    user = get_user(info)
    project = await ProjectService.assign_project(input.project_id, user.id, input.user_id, user.roles)
    # Send notification
    await send_project_assignment_notification(project, user)
    return GraphQLProject.from_pydantic(project)
