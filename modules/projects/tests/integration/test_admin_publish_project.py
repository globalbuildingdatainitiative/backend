import pytest
from uuid import uuid4

from models.database.db_model import DBProject, ProjectState
from models.user_role import UserRole
from logic.project_service import ProjectService


@pytest.mark.asyncio
async def test_admin_publish_project(projects, create_user):
    """
    Integration test for administrator publishing project.

    This test verifies the complete workflow of an administrator publishing a project.

    Expected behavior:
    - Administrator finds project in TO_PUBLISH state
    - Administrator publishes project
    - Project state transitions from TO_PUBLISH to DRAFT (published)
    """
    # Set project to TO_PUBLISH state
    project = projects[0]
    project.state = ProjectState.TO_PUBLISH
    await project.save()
    
    # Publish the project as an administrator
    result = await ProjectService.publish_project(project.id, create_user.id, UserRole.ADMINISTRATOR)
    
    # Verify the project state transitioned correctly
    assert result.state == ProjectState.DRAFT
    # Note: According to the service implementation, published projects go back to DRAFT state


@pytest.mark.asyncio
async def test_admin_publish_project_invalid_state(projects, create_user):
    """
    Integration test for administrator publishing project with invalid state.

    This test verifies that an administrator cannot publish a project if it's not in TO_PUBLISH state.
    """
    # Set project to IN_REVIEW state (invalid for publishing)
    project = projects[0]
    project.state = ProjectState.IN_REVIEW
    await project.save()
    
    # Try to publish the project as an administrator - this should raise an exception
    with pytest.raises(ValueError, match="User does not have permission to publish this project"):
        await ProjectService.publish_project(project.id, create_user.id, UserRole.ADMINISTRATOR)


@pytest.mark.asyncio
async def test_unauthorized_user_publish_project(projects, create_user):
    """
    Integration test for unauthorized user publishing project.

    This test verifies that users without ADMINISTRATOR role cannot publish projects.
    """
    # Set project to TO_PUBLISH state
    project = projects[0]
    project.state = ProjectState.TO_PUBLISH
    await project.save()
    
    # Try to publish the project as a CONTRIBUTOR - this should raise an exception
    with pytest.raises(ValueError, match="User does not have permission to publish this project"):
        await ProjectService.publish_project(project.id, create_user.id, UserRole.CONTRIBUTOR)
    
    # Try to publish the project as a REVIEWER - this should also raise an exception
    with pytest.raises(ValueError, match="User does not have permission to publish this project"):
        await ProjectService.publish_project(project.id, create_user.id, UserRole.REVIEWER)
