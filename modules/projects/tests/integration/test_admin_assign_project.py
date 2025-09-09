import pytest
from uuid import uuid4
from supertokens_python.recipe.emailpassword.asyncio import sign_up

from models.database.db_model import DBProject, ProjectState
from models.user_role import UserRole
from logic.project_service import ProjectService


@pytest.mark.asyncio
async def test_admin_assign_project(metadata_project, create_user):
    """
    Integration test for administrator assigning project.

    This test verifies the complete workflow of an administrator assigning a project to a reviewer.

    Expected behavior:
    - Administrator finds project
    - Administrator assigns project to reviewer
    - Project assignedTo field is updated with reviewer's ID
    - Project assignedAt field is updated with current timestamp
    """
    # Create a reviewer user
    reviewer_response = await sign_up("public", "reviewer@email.com", "currentPassword123")
    reviewer_id = reviewer_response.user.id
    
    # Assign the project to the reviewer as an administrator
    result = await ProjectService.assign_project(metadata_project.id, create_user.id, reviewer_id, UserRole.ADMINISTRATOR)
    
    # Verify the project was assigned correctly
    assert str(result.assigned_to) == reviewer_id
    assert result.assigned_at is not None
    assert result.id == metadata_project.id


@pytest.mark.asyncio
async def test_unauthorized_user_assign_project(metadata_project, create_user):
    """
    Integration test for unauthorized user assigning project.

    This test verifies that users without ADMINISTRATOR role cannot assign projects.
    """
    # Create a reviewer user
    reviewer_response = await sign_up("public", "reviewer2@email.com", "currentPassword123")
    reviewer_id = reviewer_response.user.id
    
    # Try to assign the project as a CONTRIBUTOR - this should raise an exception
    with pytest.raises(ValueError, match="User does not have permission to assign this project"):
        await ProjectService.assign_project(metadata_project.id, create_user.id, reviewer_id, UserRole.CONTRIBUTOR)
    
    # Try to assign the project as a REVIEWER - this should also raise an exception
    with pytest.raises(ValueError, match="User does not have permission to assign this project"):
        await ProjectService.assign_project(metadata_project.id, create_user.id, reviewer_id, UserRole.REVIEWER)


@pytest.mark.asyncio
async def test_admin_assign_project_locked_state(projects, create_user):
    """
    Integration test for administrator assigning project in invalid state.

    This test verifies that administrators can assign projects even in LOCKED state.
    Note: Assignment is allowed in any state according to the permissions logic.
    """
    # Create a reviewer user
    reviewer_response = await sign_up("public", "reviewer3@email.com", "currentPassword123")
    reviewer_id = reviewer_response.user.id
    
    # Set project to LOCKED state
    project = projects[0]
    project.state = ProjectState.LOCKED
    await project.save()
    
    # Assign the project as an administrator - this should work even in LOCKED state
    result = await ProjectService.assign_project(project.id, create_user.id, reviewer_id, UserRole.ADMINISTRATOR)
    
    # Verify the project was assigned correctly
    assert str(result.assigned_to) == reviewer_id
    assert result.assigned_at is not None
    assert result.id == project.id
