import logging
from typing import Optional
from uuid import UUID

from models.database.db_model import DBProject, ProjectState
from models.user_role import UserRole

logger = logging.getLogger(__name__)


def has_permission(user_role: UserRole, required_role: UserRole) -> bool:
    """
    Check if a user has the required role or higher permissions.

    Args:
        user_role: Role of the user
        required_role: Minimum required role

    Returns:
        True if user has required permissions, False otherwise
    """
    # Define role hierarchy: CONTRIBUTOR < REVIEWER < ADMINISTRATOR
    role_hierarchy = {
        UserRole.CONTRIBUTOR: 1,
        UserRole.REVIEWER: 2,
        UserRole.ADMINISTRATOR: 3
    }
    
    return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)


def validate_project_ownership(project: DBProject, user_id: UUID) -> bool:
    """
    Validate that a user owns a project.

    Args:
        project: Project to check
        user_id: ID of the user

    Returns:
        True if user owns the project, False otherwise
    """
    return project.created_by == user_id


def validate_project_assignment(project: DBProject, user_id: UUID) -> bool:
    """
    Validate that a user is assigned to a project.

    Args:
        project: Project to check
        user_id: ID of the user

    Returns:
        True if user is assigned to the project, False otherwise
    """
    return project.assigned_to == user_id


def can_submit_for_review(project: DBProject, user_role: UserRole, user_id: UUID) -> bool:
    """
    Check if a user can submit a project for review.

    Rules:
    - User must be a CONTRIBUTOR or ADMINISTRATOR
    - Project must be in DRAFT state
    - User must own the project (for CONTRIBUTORS) or can be any ADMINISTRATOR

    Args:
        project: Project to check
        user_role: Role of the user
        user_id: ID of the user

    Returns:
        True if user can submit project for review, False otherwise
    """
    # For contributors, they must own the project
    if user_role == UserRole.CONTRIBUTOR:
        return (
            project.state == ProjectState.DRAFT and
            validate_project_ownership(project, user_id)
        )
    # For administrators, they can submit any project
    elif user_role == UserRole.ADMINISTRATOR:
        return project.state == ProjectState.DRAFT
    # Reviewers cannot submit projects for review
    else:
        return False


def can_approve_project(project: DBProject, user_role: UserRole) -> bool:
    """
    Check if a user can approve a project.

    Rules:
    - User must be a REVIEWER or ADMINISTRATOR
    - Project must be in IN_REVIEW state

    Args:
        project: Project to check
        user_role: Role of the user

    Returns:
        True if user can approve project, False otherwise
    """
    return (
        user_role in [UserRole.REVIEWER, UserRole.ADMINISTRATOR] and
        project.state == ProjectState.IN_REVIEW
    )


def can_reject_project(project: DBProject, user_role: UserRole) -> bool:
    """
    Check if a user can reject a project.

    Rules:
    - User must be a REVIEWER or ADMINISTRATOR
    - Project must be in IN_REVIEW state

    Args:
        project: Project to check
        user_role: Role of the user

    Returns:
        True if user can reject project, False otherwise
    """
    return (
        user_role in [UserRole.REVIEWER, UserRole.ADMINISTRATOR] and
        project.state == ProjectState.IN_REVIEW
    )


def can_publish_project(project: DBProject, user_role: UserRole) -> bool:
    """
    Check if a user can publish a project.

    Rules:
    - User must be an ADMINISTRATOR
    - Project must be in TO_PUBLISH state

    Args:
        project: Project to check
        user_role: Role of the user

    Returns:
        True if user can publish project, False otherwise
    """
    return (
        user_role == UserRole.ADMINISTRATOR and
        project.state == ProjectState.TO_PUBLISH
    )


def can_unpublish_project(project: DBProject, user_role: UserRole) -> bool:
    """
    Check if a user can unpublish a project.

    Rules:
    - User must be an ADMINISTRATOR
    - Project must be in DRAFT state

    Args:
        project: Project to check
        user_role: Role of the user

    Returns:
        True if user can unpublish project, False otherwise
    """
    return (
        user_role == UserRole.ADMINISTRATOR and
        project.state == ProjectState.DRAFT
    )


def can_delete_project(project: DBProject, user_role: UserRole, user_id: UUID) -> bool:
    """
    Check if a user can delete a project.

    Rules:
    - User must own the project OR be an ADMINISTRATOR
    - Project must not be in LOCKED state

    Args:
        project: Project to check
        user_role: Role of the user
        user_id: ID of the user

    Returns:
        True if user can delete project, False otherwise
    """
    return (
        project.state != ProjectState.LOCKED and
        (validate_project_ownership(project, user_id) or user_role == UserRole.ADMINISTRATOR)
    )


def can_lock_project(user_role: UserRole) -> bool:
    """
    Check if a user can lock a project.

    Rules:
    - User must be an ADMINISTRATOR

    Args:
        user_role: Role of the user

    Returns:
        True if user can lock project, False otherwise
    """
    return user_role == UserRole.ADMINISTRATOR


def can_unlock_project(project: DBProject, user_role: UserRole) -> bool:
    """
    Check if a user can unlock a project.

    Rules:
    - User must be an ADMINISTRATOR
    - Project must be in LOCKED state

    Args:
        project: Project to check
        user_role: Role of the user

    Returns:
        True if user can unlock project, False otherwise
    """
    return (
        user_role == UserRole.ADMINISTRATOR and
        project.state == ProjectState.LOCKED
    )


def can_assign_project(user_role: UserRole) -> bool:
    """
    Check if a user can assign a project.

    Rules:
    - User must be an ADMINISTRATOR

    Args:
        user_role: Role of the user

    Returns:
        True if user can assign project, False otherwise
    """
    return user_role == UserRole.ADMINISTRATOR
