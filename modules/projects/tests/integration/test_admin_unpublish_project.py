import pytest
from uuid import uuid4

from models.database.db_model import DBProject, ProjectState
from models.user_role import UserRole
from logic.project_service import ProjectService


@pytest.mark.asyncio
async def test_admin_unpublish_project(projects, create_user):
    """
    Integration test for administrator unpublishing project.

    This test verifies the complete workflow of an administrator unpublishing a project.

    Expected behavior:
    - Administrator finds project in DRAFT state
    - Administrator marks project for unpublishing
    - Project state transitions from DRAFT to TO_UNPUBLISH
    """
    # Set project to DRAFT state
    project = projects[0]
    project.state = ProjectState.DRAFT
    await project.save()
    
    # Mark the project for unpublishing as an administrator
    result = await ProjectService.unpublish_project(project.id, create_user.id, UserRole.ADMINISTRATOR)
    
    # Verify the project state transitioned correctly
    assert result.state == ProjectState.TO_UNPUBLISH


@pytest.mark.asyncio
async def test_admin_unpublish_project_invalid_state(projects, create_user):
    """
    Integration test for administrator unpublishing project with invalid state.

    This test verifies that an administrator cannot unpublish a project if it's not in DRAFT state.
    """
    # Set project to IN_REVIEW state (invalid for unpublishing)
    project = projects[0]
    project.state = ProjectState.IN_REVIEW
    await project.save()
    
    # Try to unpublish the project as an administrator - this should raise an exception
    with pytest.raises(ValueError, match="User does not have permission to unpublish this project"):
        await ProjectService.unpublish_project(project.id, create_user.id, UserRole.ADMINISTRATOR)


@pytest.mark.asyncio
async def test_unauthorized_user_unpublish_project(projects, create_user):
    """
    Integration test for unauthorized user unpublishing project.

    This test verifies that users without ADMINISTRATOR role cannot unpublish projects.
    """
    # Set project to DRAFT state
    project = projects[0]
    project.state = ProjectState.DRAFT
    await project.save()
    
    # Try to unpublish the project as a CONTRIBUTOR - this should raise an exception
    with pytest.raises(ValueError, match="User does not have permission to unpublish this project"):
        await ProjectService.unpublish_project(project.id, create_user.id, UserRole.CONTRIBUTOR)
    
    # Try to unpublish the project as a REVIEWER - this should also raise an exception
    with pytest.raises(ValueError, match="User does not have permission to unpublish this project"):
        await ProjectService.unpublish_project(project.id, create_user.id, UserRole.REVIEWER)
