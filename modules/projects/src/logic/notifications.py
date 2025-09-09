import logging
from typing import Optional
from uuid import UUID

from models.database.db_model import DBProject, ProjectState
from models.user_role import UserRole

logger = logging.getLogger(__name__)


async def send_project_state_change_notification(
    project: DBProject, old_state: ProjectState, new_state: ProjectState, user_id: UUID
) -> None:
    """
    Send notification when project state changes.

    Args:
        project: Project that changed state
        old_state: Previous state of the project
        new_state: New state of the project
        user_id: ID of the user who triggered the state change
    """
    # This is a placeholder implementation that should fail until the real implementation is complete
    raise NotImplementedError("send_project_state_change_notification not implemented")


async def send_project_assignment_notification(project: DBProject, assigner_id: UUID, assignee_id: UUID) -> None:
    """
    Send notification when project is assigned to a user.

    Args:
        project: Project that was assigned
        assigner_id: ID of the user who assigned the project
        assignee_id: ID of the user who was assigned the project
    """
    # This is a placeholder implementation that should fail until the real implementation is complete
    raise NotImplementedError("send_project_assignment_notification not implemented")


async def send_project_submission_notification(project: DBProject, submitter_id: UUID) -> None:
    """
    Send notification when project is submitted for review.

    Args:
        project: Project that was submitted
        submitter_id: ID of the user who submitted the project
    """
    # This is a placeholder implementation that should fail until the real implementation is complete
    raise NotImplementedError("send_project_submission_notification not implemented")


async def send_project_approval_notification(project: DBProject, approver_id: UUID) -> None:
    """
    Send notification when project is approved.

    Args:
        project: Project that was approved
        approver_id: ID of the user who approved the project
    """
    # This is a placeholder implementation that should fail until the real implementation is complete
    raise NotImplementedError("send_project_approval_notification not implemented")


async def send_project_rejection_notification(
    project: DBProject, rejecter_id: UUID, reason: Optional[str] = None
) -> None:
    """
    Send notification when project is rejected.

    Args:
        project: Project that was rejected
        rejecter_id: ID of the user who rejected the project
        reason: Optional reason for rejection
    """
    # This is a placeholder implementation that should fail until the real implementation is complete
    raise NotImplementedError("send_project_rejection_notification not implemented")


async def send_project_publication_notification(project: DBProject, publisher_id: UUID) -> None:
    """
    Send notification when project is published.

    Args:
        project: Project that was published
        publisher_id: ID of the user who published the project
    """
    # This is a placeholder implementation that should fail until the real implementation is complete
    raise NotImplementedError("send_project_publication_notification not implemented")


async def send_project_unpublication_notification(project: DBProject, unpublisher_id: UUID) -> None:
    """
    Send notification when project is unpublished.

    Args:
        project: Project that was unpublished
        unpublisher_id: ID of the user who unpublished the project
    """
    # This is a placeholder implementation that should fail until the real implementation is complete
    raise NotImplementedError("send_project_unpublication_notification not implemented")


async def send_project_deletion_notification(project: DBProject, deleter_id: UUID) -> None:
    """
    Send notification when project is marked for deletion.

    Args:
        project: Project that was marked for deletion
        deleter_id: ID of the user who marked the project for deletion
    """
    # This is a placeholder implementation that should fail until the real implementation is complete
    raise NotImplementedError("send_project_deletion_notification not implemented")


async def send_project_lock_notification(project: DBProject, locker_id: UUID) -> None:
    """
    Send notification when project is locked.

    Args:
        project: Project that was locked
        locker_id: ID of the user who locked the project
    """
    # This is a placeholder implementation that should fail until the real implementation is complete
    raise NotImplementedError("send_project_lock_notification not implemented")


async def send_project_unlock_notification(project: DBProject, unlocker_id: UUID) -> None:
    """
    Send notification when project is unlocked.

    Args:
        project: Project that was unlocked
        unlocker_id: ID of the user who unlocked the project
    """
    # This is a placeholder implementation that should fail until the real implementation is complete
    raise NotImplementedError("send_project_unlock_notification not implemented")
