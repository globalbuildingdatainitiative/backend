import pytest
from backend.modules.auth.src.models.roles import Role as AuthRole

from models.database.db_model import DBProject, ProjectState
from models.user_role import UserRole
from logic.project_service import ProjectService


@pytest.mark.asyncio
async def test_complete_project_lifecycle(projects, create_user):
    """
    Integration test for complete project lifecycle.

    This test verifies the complete workflow of a project through all states.

    Expected behavior:
    - Project starts in DRAFT state
    - Contributor submits for review → IN_REVIEW
    - Reviewer approves → TO_PUBLISH
    - Administrator publishes → DRAFT (published)
    - Administrator unpublishes → TO_UNPUBLISH
    - Administrator deletes → TO_DELETE
    """
    # Start with a DRAFT project owned by the user
    project = projects[0]
    project.state = ProjectState.DRAFT
    project.created_by = create_user.id
    await project.save()
    
    # Step 1: Contributor submits for review (DRAFT → IN_REVIEW)
    result = await ProjectService.submit_for_review(project.id, create_user.id, [AuthRole.MEMBER])
    assert result.state == ProjectState.IN_REVIEW
    
    # Step 2: Reviewer approves (IN_REVIEW → TO_PUBLISH)
    result = await ProjectService.approve_project(project.id, create_user.id, [AuthRole.MEMBER])
    assert result.state == ProjectState.TO_PUBLISH
    
    # Step 3: Administrator publishes (TO_PUBLISH → DRAFT)
    result = await ProjectService.publish_project(project.id, create_user.id, [AuthRole.ADMIN])
    assert result.state == ProjectState.DRAFT
    
    # Step 4: Administrator unpublishes (DRAFT → TO_UNPUBLISH)
    result = await ProjectService.unpublish_project(project.id, create_user.id, [AuthRole.ADMIN])
    assert result.state == ProjectState.TO_UNPUBLISH
    
    # Step 5: Administrator marks for deletion (TO_UNPUBLISH → TO_DELETE)
    result = await ProjectService.delete_project(project.id, create_user.id, [AuthRole.ADMIN])
    assert result == True
    
    # Verify the project is now in TO_DELETE state
    updated_project = await DBProject.get(project.id)
    assert updated_project.state == ProjectState.TO_DELETE


@pytest.mark.asyncio
async def test_project_rejection_workflow(projects, create_user):
    """
    Integration test for project rejection workflow.

    This test verifies the workflow when a project is rejected and resubmitted.

    Expected behavior:
    - Project in IN_REVIEW state gets rejected → DRAFT
    - Contributor can resubmit from DRAFT → IN_REVIEW
    - Process continues normally
    """
    # Start with a DRAFT project owned by the user
    project = projects[0]
    project.state = ProjectState.DRAFT
    project.created_by = create_user.id
    await project.save()
    
    # Submit for review (DRAFT → IN_REVIEW)
    result = await ProjectService.submit_for_review(project.id, create_user.id, [AuthRole.MEMBER])
    assert result.state == ProjectState.IN_REVIEW
    
    # Reject the project (IN_REVIEW → DRAFT)
    result = await ProjectService.reject_project(project.id, create_user.id, [AuthRole.MEMBER])
    assert result.state == ProjectState.DRAFT
    assert result.assigned_to is None
    assert result.assigned_at is None
    
    # Resubmit for review (DRAFT → IN_REVIEW)
    result = await ProjectService.submit_for_review(project.id, create_user.id, [AuthRole.MEMBER])
    assert result.state == ProjectState.IN_REVIEW


@pytest.mark.asyncio
async def test_project_locking_workflow(projects, create_user):
    """
    Integration test for project locking workflow.

    This test verifies the workflow when a project is locked and unlocked.

    Expected behavior:
    - Project in any state can be locked → LOCKED
    - Locked project can be unlocked → previous state
    """
    # Start with a DRAFT project
    project = projects[0]
    project.state = ProjectState.DRAFT
    project.created_by = create_user.id
    # Store the previous state for verification
    project.previous_state = ProjectState.DRAFT.value
    await project.save()
    
    # Lock the project (DRAFT → LOCKED)
    result = await ProjectService.lock_project(project.id, create_user.id, [AuthRole.ADMIN])
    assert result.state == ProjectState.LOCKED
    
    # Unlock the project (LOCKED → DRAFT)
    result = await ProjectService.unlock_project(project.id, create_user.id, [AuthRole.ADMIN])
    assert result.state == ProjectState.DRAFT


@pytest.mark.asyncio
async def test_invalid_state_transitions(projects, create_user):
    """
    Integration test for invalid state transitions.

    This test verifies that invalid state transitions raise appropriate exceptions.
    """
    # Test submitting a project that's already in IN_REVIEW state
    project = projects[0]
    project.state = ProjectState.IN_REVIEW
    project.created_by = create_user.id
    await project.save()
    
    with pytest.raises(ValueError, match="User does not have permission to submit this project for review"):
        await ProjectService.submit_for_review(project.id, create_user.id, [AuthRole.MEMBER])
    
    # Test approving a project that's in DRAFT state
    project.state = ProjectState.DRAFT
    await project.save()
    
    with pytest.raises(ValueError, match="User does not have permission to approve this project"):
        await ProjectService.approve_project(project.id, create_user.id, [AuthRole.MEMBER])
    
    # Test rejecting a project that's in DRAFT state
    with pytest.raises(ValueError, match="User does not have permission to reject this project"):
        await ProjectService.reject_project(project.id, create_user.id, [AuthRole.MEMBER])
    
    # Test publishing a project that's in IN_REVIEW state
    project.state = ProjectState.IN_REVIEW
    await project.save()
    
    with pytest.raises(ValueError, match="User does not have permission to publish this project"):
        await ProjectService.publish_project(project.id, create_user.id, [AuthRole.ADMIN])
    
    # Test unpublishing a project that's in IN_REVIEW state
    with pytest.raises(ValueError, match="User does not have permission to unpublish this project"):
        await ProjectService.unpublish_project(project.id, create_user.id, [AuthRole.ADMIN])
