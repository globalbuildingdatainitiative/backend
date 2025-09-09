import pytest
from backend.modules.auth.src.models.roles import Role as AuthRole

from models.database.db_model import DBProject, ProjectState
from models.user_role import UserRole
from logic.project_service import ProjectService
from logic.permissions import (
    can_submit_for_review,
    can_approve_project,
    can_reject_project,
    can_publish_project,
    can_unpublish_project,
    can_delete_project,
    can_lock_project,
    can_unlock_project,
    can_assign_project,
)


@pytest.mark.asyncio
async def test_contributor_role_permissions(projects, create_user):
    """
    Integration test for contributor role permissions.

    This test verifies that users with CONTRIBUTOR role have appropriate permissions.

    Expected behavior:
    - Contributors can submit their own projects for review
    - Contributors cannot approve/reject projects
    - Contributors cannot publish/unpublish projects
    - Contributors cannot lock/unlock projects
    - Contributors cannot assign projects
    """
    # Set project to DRAFT state and owned by the user
    project = projects[0]
    project.state = ProjectState.DRAFT
    project.created_by = create_user.id
    await project.save()
    
    # Test that contributor can submit their own project for review
    result = await ProjectService.submit_for_review(project.id, create_user.id, [AuthRole.MEMBER])
    assert result.state == ProjectState.IN_REVIEW
    
    # Reset project to DRAFT for further tests
    project.state = ProjectState.DRAFT
    await project.save()
    
    # Test that contributor cannot approve projects (requires REVIEWER role)
    with pytest.raises(ValueError, match="User does not have permission to approve this project"):
        await ProjectService.approve_project(project.id, create_user.id, [AuthRole.MEMBER])
    
    # Test that contributor cannot reject projects (requires REVIEWER role)
    with pytest.raises(ValueError, match="User does not have permission to reject this project"):
        await ProjectService.reject_project(project.id, create_user.id, [AuthRole.MEMBER])
    
    # Test that contributor cannot publish projects (requires ADMINISTRATOR role)
    project.state = ProjectState.TO_PUBLISH
    await project.save()
    with pytest.raises(ValueError, match="User does not have permission to publish this project"):
        await ProjectService.publish_project(project.id, create_user.id, [AuthRole.MEMBER])
    
    # Test that contributor cannot unpublish projects (requires ADMINISTRATOR role)
    project.state = ProjectState.DRAFT
    await project.save()
    with pytest.raises(ValueError, match="User does not have permission to unpublish this project"):
        await ProjectService.unpublish_project(project.id, create_user.id, [AuthRole.MEMBER])
    
    # Test that contributor cannot lock projects (requires ADMINISTRATOR role)
    with pytest.raises(ValueError, match="User does not have permission to lock this project"):
        await ProjectService.lock_project(project.id, create_user.id, [AuthRole.MEMBER])
    
    # Test that contributor cannot unlock projects (requires ADMINISTRATOR role)
    project.state = ProjectState.LOCKED
    await project.save()
    with pytest.raises(ValueError, match="User does not have permission to unlock this project"):
        await ProjectService.unlock_project(project.id, create_user.id, [AuthRole.MEMBER])
    
    # Test that contributor cannot assign projects (requires ADMINISTRATOR role)
    with pytest.raises(ValueError, match="User does not have permission to assign this project"):
        await ProjectService.assign_project(project.id, create_user.id, create_user.id, [AuthRole.MEMBER])


@pytest.mark.asyncio
async def test_reviewer_role_permissions(projects, create_user):
    """
    Integration test for reviewer role permissions.

    This test verifies that users with REVIEWER role have appropriate permissions.

    Expected behavior:
    - Reviewers can approve/reject projects in IN_REVIEW state
    - Reviewers cannot publish/unpublish projects
    - Reviewers cannot lock/unlock projects
    - Reviewers cannot assign projects
    - Reviewers cannot submit projects for review (unless they're also contributors)
    """
    # Set project to IN_REVIEW state
    project = projects[0]
    project.state = ProjectState.IN_REVIEW
    await project.save()
    
    # Test that reviewer can approve projects in IN_REVIEW state
    result = await ProjectService.approve_project(project.id, create_user.id, [AuthRole.MEMBER])
    assert result.state == ProjectState.TO_PUBLISH
    
    # Reset project to IN_REVIEW for further tests
    project.state = ProjectState.IN_REVIEW
    await project.save()
    
    # Test that reviewer can reject projects in IN_REVIEW state
    result = await ProjectService.reject_project(project.id, create_user.id, [AuthRole.MEMBER])
    assert result.state == ProjectState.DRAFT
    
    # Test that reviewer cannot submit projects for review (requires CONTRIBUTOR role)
    project.state = ProjectState.DRAFT
    project.created_by = create_user.id
    await project.save()
    with pytest.raises(ValueError, match="User does not have permission to submit this project for review"):
        await ProjectService.submit_for_review(project.id, create_user.id, [AuthRole.MEMBER])
    
    # Test that reviewer cannot publish projects (requires ADMINISTRATOR role)
    project.state = ProjectState.TO_PUBLISH
    await project.save()
    with pytest.raises(ValueError, match="User does not have permission to publish this project"):
        await ProjectService.publish_project(project.id, create_user.id, [AuthRole.MEMBER])
    
    # Test that reviewer cannot unpublish projects (requires ADMINISTRATOR role)
    project.state = ProjectState.DRAFT
    await project.save()
    with pytest.raises(ValueError, match="User does not have permission to unpublish this project"):
        await ProjectService.unpublish_project(project.id, create_user.id, [AuthRole.MEMBER])
    
    # Test that reviewer cannot lock projects (requires ADMINISTRATOR role)
    with pytest.raises(ValueError, match="User does not have permission to lock this project"):
        await ProjectService.lock_project(project.id, create_user.id, [AuthRole.MEMBER])
    
    # Test that reviewer cannot unlock projects (requires ADMINISTRATOR role)
    project.state = ProjectState.LOCKED
    await project.save()
    with pytest.raises(ValueError, match="User does not have permission to unlock this project"):
        await ProjectService.unlock_project(project.id, create_user.id, [AuthRole.MEMBER])
    
    # Test that reviewer cannot assign projects (requires ADMINISTRATOR role)
    project.state = ProjectState.DRAFT
    await project.save()
    with pytest.raises(ValueError, match="User does not have permission to assign this project"):
        await ProjectService.assign_project(project.id, create_user.id, create_user.id, [AuthRole.MEMBER])


@pytest.mark.asyncio
async def test_administrator_role_permissions(projects, create_user):
    """
    Integration test for administrator role permissions.

    This test verifies that users with ADMINISTRATOR role have appropriate permissions.

    Expected behavior:
    - Administrators can publish/unpublish projects
    - Administrators can lock/unlock projects
    - Administrators can assign projects
    - Administrators can delete projects
    - Administrators can perform all other operations
    """
    # Test that administrator can publish projects in TO_PUBLISH state
    project = projects[0]
    project.state = ProjectState.TO_PUBLISH
    await project.save()
    result = await ProjectService.publish_project(project.id, create_user.id, [AuthRole.ADMIN])
    assert result.state == ProjectState.DRAFT
    
    # Test that administrator can unpublish projects in DRAFT state
    project.state = ProjectState.DRAFT
    await project.save()
    result = await ProjectService.unpublish_project(project.id, create_user.id, [AuthRole.ADMIN])
    assert result.state == ProjectState.TO_UNPUBLISH
    
    # Test that administrator can lock projects in any state
    project.state = ProjectState.DRAFT
    await project.save()
    result = await ProjectService.lock_project(project.id, create_user.id, [AuthRole.ADMIN])
    assert result.state == ProjectState.LOCKED
    
    # Test that administrator can unlock projects in LOCKED state
    result = await ProjectService.unlock_project(project.id, create_user.id, [AuthRole.ADMIN])
    assert result.state == ProjectState.DRAFT
    
    # Test that administrator can assign projects
    result = await ProjectService.assign_project(project.id, create_user.id, create_user.id, [AuthRole.ADMIN])
    assert result.assigned_to == create_user.id
    
    # Test that administrator can delete projects
    project.state = ProjectState.TO_DELETE
    await project.save()
    result = await ProjectService.delete_project(project.id, create_user.id, [AuthRole.ADMIN])
    assert result == True
    
    # Test that administrator can also perform reviewer operations
    project = projects[1]  # Use a different project
    project.state = ProjectState.IN_REVIEW
    await project.save()
    result = await ProjectService.approve_project(project.id, create_user.id, [AuthRole.ADMIN])
    assert result.state == ProjectState.TO_PUBLISH
    
    # Test that administrator can also perform contributor operations
    project = projects[2]  # Use another different project
    project.state = ProjectState.DRAFT
    project.created_by = create_user.id
    await project.save()
    result = await ProjectService.submit_for_review(project.id, create_user.id, [AuthRole.ADMIN])
    assert result.state == ProjectState.IN_REVIEW
