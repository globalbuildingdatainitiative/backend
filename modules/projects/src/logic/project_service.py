import logging
from typing import Optional, List
from uuid import UUID
import datetime

from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError

from models.database.db_model import DBProject, ProjectState
from models.user_role import UserRole

# Handle AuthRole import for tests
try:
    from backend.modules.auth.src.models.roles import Role as AuthRole
except ImportError:
    # Create a mock AuthRole for testing purposes
    from enum import Enum
    class AuthRole(str, Enum):
        OWNER = "OWNER"
        MEMBER = "MEMBER"
        ADMIN = "ADMIN"

from logic.permissions import (
    has_project_permission, 
    validate_project_ownership, 
    validate_project_assignment,
    can_submit_for_review,
    can_approve_project,
    can_reject_project,
    can_publish_project,
    can_unpublish_project,
    can_delete_project,
    can_lock_project,
    can_unlock_project,
    can_assign_project
)
from logic.role_mapping import get_highest_project_role

logger = logging.getLogger(__name__)


class ProjectService:
    """
    Service layer for managing project state transitions and business logic.
    """

    @staticmethod
    async def submit_for_review(project_id: UUID, user_id: UUID, user_roles: List[AuthRole]) -> DBProject:
        """
        Submit a project for review.

        Transitions: DRAFT → IN_REVIEW

        Args:
            project_id: ID of the project to submit
            user_id: ID of the user submitting the project
            user_roles: Roles of the user submitting the project

        Returns:
            Updated project

        Raises:
            ValueError: If project is not in DRAFT state or user doesn't have permission
            Exception: If database operation fails
        """
        # Fetch the project from database
        project = await DBProject.get(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        # Get the highest project role from auth roles
        user_role = get_highest_project_role(user_roles)
        
        # Check permissions
        if not can_submit_for_review(project, user_role, user_id):
            raise ValueError("User does not have permission to submit this project for review")
        
        # Update project state
        project.state = ProjectState.IN_REVIEW
        project.assigned_to = None  # Clear assignment when moving to review
        project.assigned_at = None
        
        # Save the updated project
        await project.save()
        return project

    @staticmethod
    async def approve_project(project_id: UUID, user_id: UUID, user_roles: List[AuthRole]) -> DBProject:
        """
        Approve a project for publication.

        Transitions: IN_REVIEW → TO_PUBLISH

        Args:
            project_id: ID of the project to approve
            user_id: ID of the user approving the project
            user_roles: Roles of the user approving the project

        Returns:
            Updated project

        Raises:
            ValueError: If project is not in IN_REVIEW state or user doesn't have permission
            Exception: If database operation fails
        """
        # Fetch the project from database
        project = await DBProject.get(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        # Get the highest project role from auth roles
        user_role = get_highest_project_role(user_roles)
        
        # Check permissions
        if not can_approve_project(project, user_role):
            raise ValueError("User does not have permission to approve this project")
        
        # Update project state
        project.state = ProjectState.TO_PUBLISH
        
        # Save the updated project
        await project.save()
        return project

    @staticmethod
    async def reject_project(project_id: UUID, user_id: UUID, user_roles: List[AuthRole]) -> DBProject:
        """
        Reject a project and send it back to draft.

        Transitions: IN_REVIEW → DRAFT

        Args:
            project_id: ID of the project to reject
            user_id: ID of the user rejecting the project
            user_roles: Roles of the user rejecting the project

        Returns:
            Updated project

        Raises:
            ValueError: If project is not in IN_REVIEW state or user doesn't have permission
            Exception: If database operation fails
        """
        # Fetch the project from database
        project = await DBProject.get(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        # Get the highest project role from auth roles
        user_role = get_highest_project_role(user_roles)
        
        # Check permissions
        if not can_reject_project(project, user_role):
            raise ValueError("User does not have permission to reject this project")
        
        # Update project state
        project.state = ProjectState.DRAFT
        project.assigned_to = None  # Clear assignment when moving back to draft
        project.assigned_at = None
        
        # Save the updated project
        await project.save()
        return project

    @staticmethod
    async def publish_project(project_id: UUID, user_id: UUID, user_roles: List[AuthRole]) -> DBProject:
        """
        Publish a project.

        Transitions: TO_PUBLISH → DRAFT (published)

        Args:
            project_id: ID of the project to publish
            user_id: ID of the user publishing the project
            user_roles: Roles of the user publishing the project

        Returns:
            Updated project

        Raises:
            ValueError: If project is not in TO_PUBLISH state or user doesn't have permission
            Exception: If database operation fails
        """
        # Fetch the project from database
        project = await DBProject.get(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        # Get the highest project role from auth roles
        user_role = get_highest_project_role(user_roles)
        
        # Check permissions
        if not can_publish_project(project, user_role):
            raise ValueError("User does not have permission to publish this project")
        
        # Update project state
        project.state = ProjectState.DRAFT  # Published projects go back to DRAFT state
        # Note: In a real implementation, you might want to add a PUBLISHED state
        
        # Save the updated project
        await project.save()
        return project

    @staticmethod
    async def unpublish_project(project_id: UUID, user_id: UUID, user_roles: List[AuthRole]) -> DBProject:
        """
        Mark a project for unpublishing.

        Transitions: DRAFT → TO_UNPUBLISH

        Args:
            project_id: ID of the project to unpublish
            user_id: ID of the user unpublishing the project
            user_roles: Roles of the user unpublishing the project

        Returns:
            Updated project

        Raises:
            ValueError: If project is not in DRAFT state or user doesn't have permission
            Exception: If database operation fails
        """
        # Fetch the project from database
        project = await DBProject.get(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        # Get the highest project role from auth roles
        user_role = get_highest_project_role(user_roles)
        
        # Check permissions
        if not can_unpublish_project(project, user_role):
            raise ValueError("User does not have permission to unpublish this project")
        
        # Update project state
        project.state = ProjectState.TO_UNPUBLISH
        
        # Save the updated project
        await project.save()
        return project

    @staticmethod
    async def delete_project(project_id: UUID, user_id: UUID, user_roles: List[AuthRole]) -> bool:
        """
        Mark a project for deletion.

        Transitions: any state → TO_DELETE

        Args:
            project_id: ID of the project to delete
            user_id: ID of the user deleting the project
            user_roles: Roles of the user deleting the project

        Returns:
            True if successful

        Raises:
            ValueError: If user doesn't have permission
            Exception: If database operation fails
        """
        # Fetch the project from database
        project = await DBProject.get(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        # Get the highest project role from auth roles
        user_role = get_highest_project_role(user_roles)
        
        # Check permissions
        if not can_delete_project(project, user_role, user_id):
            raise ValueError("User does not have permission to delete this project")
        
        # Update project state
        project.state = ProjectState.TO_DELETE
        
        # Save the updated project
        await project.save()
        return True

    @staticmethod
    async def lock_project(project_id: UUID, user_id: UUID, user_roles: List[AuthRole]) -> DBProject:
        """
        Lock a project.

        Transitions: any state → LOCKED

        Args:
            project_id: ID of the project to lock
            user_id: ID of the user locking the project
            user_roles: Roles of the user locking the project

        Returns:
            Updated project

        Raises:
            ValueError: If user doesn't have permission
            Exception: If database operation fails
        """
        # Fetch the project from database
        project = await DBProject.get(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        # Get the highest project role from auth roles
        user_role = get_highest_project_role(user_roles)
        
        # Check permissions
        if not can_lock_project(user_role):
            raise ValueError("User does not have permission to lock this project")
        
        # Store the previous state for potential unlock operation
        # In a real implementation, you might want to store this in a separate field
        project.previous_state = project.state.value if hasattr(project, 'previous_state') else project.state.value
        
        # Update project state
        project.state = ProjectState.LOCKED
        
        # Save the updated project
        await project.save()
        return project

    @staticmethod
    async def unlock_project(project_id: UUID, user_id: UUID, user_roles: List[AuthRole]) -> DBProject:
        """
        Unlock a project.

        Transitions: LOCKED → previous state

        Args:
            project_id: ID of the project to unlock
            user_id: ID of the user unlocking the project
            user_roles: Roles of the user unlocking the project

        Returns:
            Updated project

        Raises:
            ValueError: If project is not in LOCKED state or user doesn't have permission
            Exception: If database operation fails
        """
        # Fetch the project from database
        project = await DBProject.get(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        # Get the highest project role from auth roles
        user_role = get_highest_project_role(user_roles)
        
        # Check permissions
        if not can_unlock_project(project, user_role):
            raise ValueError("User does not have permission to unlock this project")
        
        # Restore previous state if available, otherwise default to DRAFT
        previous_state = getattr(project, 'previous_state', ProjectState.DRAFT.value)
        try:
            project.state = ProjectState(previous_state)
        except ValueError:
            # If previous state is invalid, default to DRAFT
            project.state = ProjectState.DRAFT
        
        # Save the updated project
        await project.save()
        return project

    @staticmethod
    async def assign_project(project_id: UUID, user_id: UUID, assignee_id: UUID, user_roles: List[AuthRole]) -> DBProject:
        """
        Assign a project to a user.

        Args:
            project_id: ID of the project to assign
            user_id: ID of the user assigning the project
            assignee_id: ID of the user to assign the project to
            user_roles: Roles of the user assigning the project

        Returns:
            Updated project

        Raises:
            ValueError: If user doesn't have permission or project is in invalid state
            Exception: If database operation fails
        """
        # Fetch the project from database
        project = await DBProject.get(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        # Get the highest project role from auth roles
        user_role = get_highest_project_role(user_roles)
        
        # Check permissions
        if not can_assign_project(user_role):
            raise ValueError("User does not have permission to assign this project")
        
        # Update project assignment
        project.assigned_to = assignee_id
        project.assigned_at = datetime.datetime.now()
        
        # Save the updated project
        await project.save()
        return project

    @staticmethod
    async def get_projects_by_state(state: ProjectState, user_id: UUID, user_role: UserRole) -> List[DBProject]:
        """
        Get projects by state with appropriate filtering based on user role.

        Args:
            state: Project state to filter by
            user_id: ID of the requesting user
            user_role: Role of the requesting user

        Returns:
            List of projects in the specified state that the user has access to
        """
        # For administrators, return all projects in the state
        if user_role == UserRole.ADMINISTRATOR:
            return await DBProject.find({"state": state}).to_list()
        
        # For reviewers, return projects in review-related states or assigned projects
        if user_role == UserRole.REVIEWER:
            if state in [ProjectState.IN_REVIEW, ProjectState.TO_PUBLISH, ProjectState.TO_UNPUBLISH, ProjectState.TO_DELETE]:
                return await DBProject.find({"state": state}).to_list()
            elif state == ProjectState.LOCKED:
                return await DBProject.find({"state": state}).to_list()
            else:
                # For other states, return projects assigned to the reviewer
                return await DBProject.find(
                    {"state": state, "assignedTo": user_id}
                ).to_list()
        
        # For contributors, only return their own projects
        return await DBProject.find(
            {"state": state, "createdBy": user_id}
        ).to_list()

    @staticmethod
    async def get_projects_for_review(user_id: UUID) -> List[DBProject]:
        """
        Get projects that are in review (IN_REVIEW state).

        Args:
            user_id: ID of the requesting user (reviewer)

        Returns:
            List of projects in IN_REVIEW state
        """
        return await DBProject.find({"state": ProjectState.IN_REVIEW}).to_list()

    @staticmethod
    async def get_projects_to_publish(user_id: UUID) -> List[DBProject]:
        """
        Get projects that are ready to publish (TO_PUBLISH state).

        Args:
            user_id: ID of the requesting user (administrator)

        Returns:
            List of projects in TO_PUBLISH state
        """
        return await DBProject.find({"state": ProjectState.TO_PUBLISH}).to_list()

    @staticmethod
    async def get_projects_to_unpublish(user_id: UUID) -> List[DBProject]:
        """
        Get projects that are marked for unpublishing (TO_UNPUBLISH state).

        Args:
            user_id: ID of the requesting user (administrator)

        Returns:
            List of projects in TO_UNPUBLISH state
        """
        return await DBProject.find({"state": ProjectState.TO_UNPUBLISH}).to_list()

    @staticmethod
    async def get_projects_to_delete(user_id: UUID) -> List[DBProject]:
        """
        Get projects that are marked for deletion (TO_DELETE state).

        Args:
            user_id: ID of the requesting user (administrator)

        Returns:
            List of projects in TO_DELETE state
        """
        return await DBProject.find({"state": ProjectState.TO_DELETE}).to_list()

    @staticmethod
    async def get_my_projects(user_id: UUID) -> List[DBProject]:
        """
        Get projects created by the current user.

        Args:
            user_id: ID of the requesting user

        Returns:
            List of projects created by the user
        """
        return await DBProject.find({"createdBy": user_id}).to_list()

    @staticmethod
    async def get_assigned_projects(user_id: UUID) -> List[DBProject]:
        """
        Get projects assigned to the current reviewer.

        Args:
            user_id: ID of the requesting user (reviewer)

        Returns:
            List of projects assigned to the reviewer
        """
        return await DBProject.find({"assignedTo": user_id}).to_list()
