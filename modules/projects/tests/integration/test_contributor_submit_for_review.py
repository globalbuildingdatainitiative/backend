import pytest

from models.database.db_model import DBProject, ProjectState
from models.user_role import UserRole
from logic.project_service import ProjectService


@pytest.mark.asyncio
async def test_contributor_submit_for_review(projects, create_user):
    """
    Integration test for contributor submitting project for review.

    This test verifies the complete workflow of a contributor submitting a project for review.

    Expected behavior:
    - Contributor finds project in DRAFT state
    - Contributor submits project for review
    - Project state transitions from DRAFT to IN_REVIEW
    - AssignedTo field is cleared
    - AssignedAt field is cleared
    """
    # Set project to DRAFT state and owned by the user
    project = projects[0]
    project.state = ProjectState.DRAFT
    project.created_by = create_user.id
    await project.save()
    
    # Submit the project for review as a contributor
    result = await ProjectService.submit_for_review(project.id, create_user.id, UserRole.CONTRIBUTOR)
    
    # Verify the project state transitioned correctly
    assert result.state == ProjectState.IN_REVIEW
    assert result.assigned_to is None
    assert result.assigned_at is None


@pytest.mark.asyncio
async def test_contributor_submit_for_review_invalid_state(projects, create_user):
    """
    Integration test for contributor submitting project for review with invalid state.

    This test verifies that a contributor cannot submit a project for review if it's not in DRAFT state.
    """
    # Set project to IN_REVIEW state (invalid for submission)
    project = projects[0]
    project.state = ProjectState.IN_REVIEW
    project.created_by = create_user.id
    await project.save()
    
    # Try to submit the project for review - this should raise an exception
    with pytest.raises(ValueError, match="User does not have permission to submit this project for review"):
        await ProjectService.submit_for_review(project.id, create_user.id, UserRole.CONTRIBUTOR)


@pytest.mark.asyncio
async def test_unauthorized_user_submit_for_review(projects, create_user):
    """
    Integration test for unauthorized user submitting project for review.

    This test verifies that users without CONTRIBUTOR role cannot submit projects for review.
    """
    # Set project to DRAFT state
    project = projects[0]
    project.state = ProjectState.DRAFT
    project.created_by = create_user.id
    await project.save()
    
    # Try to submit the project for review as a REVIEWER - this should raise an exception
    with pytest.raises(ValueError, match="User does not have permission to submit this project for review"):
        await ProjectService.submit_for_review(project.id, create_user.id, UserRole.REVIEWER)
    
    # Try to submit the project for review as an ADMINISTRATOR - this should now succeed
    result = await ProjectService.submit_for_review(project.id, create_user.id, UserRole.ADMINISTRATOR)
    assert result.state == ProjectState.IN_REVIEW
