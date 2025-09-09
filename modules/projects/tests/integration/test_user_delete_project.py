import pytest

from models.database.db_model import DBProject, ProjectState
from models.user_role import UserRole
from logic.project_service import ProjectService


@pytest.mark.asyncio
async def test_user_delete_project(projects, create_user):
    """
    Integration test for user deleting project.

    This test verifies the complete workflow of a user marking a project for deletion.

    Expected behavior:
    - User finds their project
    - User marks project for deletion
    - Project state transitions to TO_DELETE
    """
    # Set project to DRAFT state and owned by the user
    project = projects[0]
    project.state = ProjectState.DRAFT
    project.created_by = create_user.id
    await project.save()
    
    # Mark the project for deletion as the owner
    result = await ProjectService.delete_project(project.id, create_user.id, UserRole.CONTRIBUTOR)
    
    # Verify the project was marked for deletion
    assert result == True
    updated_project = await DBProject.get(project.id)
    assert updated_project.state == ProjectState.TO_DELETE


@pytest.mark.asyncio
async def test_user_delete_project_invalid_state(projects, create_user):
    """
    Integration test for user deleting project with invalid state.

    This test verifies that a user cannot delete a project if it's in LOCKED state.
    """
    # Set project to LOCKED state
    project = projects[0]
    project.state = ProjectState.LOCKED
    project.created_by = create_user.id
    await project.save()
    
    # Try to delete the project - this should raise an exception
    with pytest.raises(ValueError, match="User does not have permission to delete this project"):
        await ProjectService.delete_project(project.id, create_user.id, UserRole.CONTRIBUTOR)


@pytest.mark.asyncio
async def test_unauthorized_user_delete_project(projects, create_user):
    """
    Integration test for unauthorized user deleting project.

    This test verifies that users cannot delete projects they don't own.
    """
    # Set project to DRAFT state but owned by someone else
    project = projects[0]
    project.state = ProjectState.DRAFT
    project.created_by = "00000000-0000-0000-0000-000000000000"  # Different user ID
    await project.save()
    
    # Try to delete the project as a different user - this should raise an exception
    with pytest.raises(ValueError, match="User does not have permission to delete this project"):
        await ProjectService.delete_project(project.id, create_user.id, UserRole.CONTRIBUTOR)
