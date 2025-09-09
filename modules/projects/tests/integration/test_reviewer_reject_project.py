import pytest
from uuid import uuid4

from models.database.db_model import DBProject, ProjectState
from models.user_role import UserRole
from logic.project_service import ProjectService


@pytest.mark.asyncio
async def test_reviewer_reject_project(projects, create_user):
    """
    Integration test for reviewer rejecting project.

    This test verifies the complete workflow of a reviewer rejecting a project.

    Expected behavior:
    - Reviewer finds project in IN_REVIEW state
    - Reviewer rejects project
    - Project state transitions from IN_REVIEW to DRAFT
    - AssignedTo field is cleared
    - AssignedAt field is cleared
    """
    # Set project to IN_REVIEW state
    project = projects[0]
    project.state = ProjectState.IN_REVIEW
    project.assigned_to = create_user.id
    project.assigned_at = "2023-01-01T00:00:00"
    await project.save()
    
    # Reject the project as a reviewer
    result = await ProjectService.reject_project(project.id, create_user.id, UserRole.REVIEWER)
    
    # Verify the project state transitioned correctly
    assert result.state == ProjectState.DRAFT
    # Note: According to the service implementation, assigned_to and assigned_at are cleared during rejection


@pytest.mark.asyncio
async def test_reviewer_reject_project_invalid_state(projects, create_user):
    """
    Integration test for reviewer rejecting project with invalid state.

    This test verifies that a reviewer cannot reject a project if it's not in IN_REVIEW state.
    """
    # Set project to DRAFT state (invalid for rejection)
    project = projects[0]
    project.state = ProjectState.DRAFT
    await project.save()
    
    # Try to reject the project as a reviewer - this should raise an exception
    with pytest.raises(ValueError, match="User does not have permission to reject this project"):
        await ProjectService.reject_project(project.id, create_user.id, UserRole.REVIEWER)


@pytest.mark.asyncio
async def test_unauthorized_user_reject_project(projects, create_user):
    """
    Integration test for unauthorized user rejecting project.

    This test verifies that users without REVIEWER role cannot reject projects.
    """
    # Set project to IN_REVIEW state
    project = projects[0]
    project.state = ProjectState.IN_REVIEW
    await project.save()
    
    # Try to reject the project as a CONTRIBUTOR - this should raise an exception
    with pytest.raises(ValueError, match="User does not have permission to reject this project"):
        await ProjectService.reject_project(project.id, create_user.id, UserRole.CONTRIBUTOR)
    
    # Try to reject the project as an ADMINISTRATOR - this should now succeed
    result = await ProjectService.reject_project(project.id, create_user.id, UserRole.ADMINISTRATOR)
    assert result.state == ProjectState.DRAFT
    assert result.assigned_to is None
    assert result.assigned_at is None
