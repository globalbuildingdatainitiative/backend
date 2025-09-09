import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import UUID

from models.database.db_model import DBProject, ProjectState
from models.user_role import UserRole
from logic.project_service import ProjectService

# Mock UUIDs for testing
MOCK_PROJECT_ID = UUID("12345678-1234-5678-1234-567812345678")
MOCK_USER_ID = UUID("87654321-4321-8765-4321-876543218765")
MOCK_ASSIGNEE_ID = UUID("11111111-2222-3333-4444-555555555555")


@pytest.fixture
def mock_db_project():
    """Create a mock DBProject for testing"""
    project = MagicMock(spec=DBProject)
    project.id = MOCK_PROJECT_ID
    project.state = ProjectState.DRAFT
    project.created_by = MOCK_USER_ID
    project.assigned_to = None
    project.assigned_at = None
    return project


@pytest.mark.asyncio
async def test_submit_for_review():
    """Test submit_for_review method"""
    # Create a mock project in DRAFT state
    mock_project = MagicMock(spec=DBProject)
    mock_project.id = MOCK_PROJECT_ID
    mock_project.state = ProjectState.DRAFT
    mock_project.created_by = MOCK_USER_ID
    mock_project.assigned_to = None
    mock_project.assigned_at = None
    
    # Mock the DBProject.get method to return our mock project
    with patch('logic.project_service.DBProject.get', new=AsyncMock(return_value=mock_project)):
        # Mock the save method
        mock_project.save = AsyncMock()
        
        # Call the method
        result = await ProjectService.submit_for_review(MOCK_PROJECT_ID, MOCK_USER_ID, UserRole.CONTRIBUTOR)
        
        # Assertions
        assert result.state == ProjectState.IN_REVIEW
        assert result.assigned_to is None
        assert result.assigned_at is None
        mock_project.save.assert_called_once()


@pytest.mark.asyncio
async def test_approve_project():
    """Test approve_project method"""
    # Create a mock project in IN_REVIEW state
    mock_project = MagicMock(spec=DBProject)
    mock_project.id = MOCK_PROJECT_ID
    mock_project.state = ProjectState.IN_REVIEW
    
    # Mock the DBProject.get method to return our mock project
    with patch('logic.project_service.DBProject.get', new=AsyncMock(return_value=mock_project)):
        # Mock the save method
        mock_project.save = AsyncMock()
        
        # Call the method
        result = await ProjectService.approve_project(MOCK_PROJECT_ID, MOCK_USER_ID, UserRole.REVIEWER)
        
        # Assertions
        assert result.state == ProjectState.TO_PUBLISH
        mock_project.save.assert_called_once()


@pytest.mark.asyncio
async def test_reject_project():
    """Test reject_project method"""
    # Create a mock project in IN_REVIEW state
    mock_project = MagicMock(spec=DBProject)
    mock_project.id = MOCK_PROJECT_ID
    mock_project.state = ProjectState.IN_REVIEW
    mock_project.assigned_to = MOCK_ASSIGNEE_ID
    mock_project.assigned_at = MagicMock()
    
    # Mock the DBProject.get method to return our mock project
    with patch('logic.project_service.DBProject.get', new=AsyncMock(return_value=mock_project)):
        # Mock the save method
        mock_project.save = AsyncMock()
        
        # Call the method
        result = await ProjectService.reject_project(MOCK_PROJECT_ID, MOCK_USER_ID, UserRole.REVIEWER)
        
        # Assertions
        assert result.state == ProjectState.DRAFT
        assert result.assigned_to is None
        assert result.assigned_at is None
        mock_project.save.assert_called_once()


@pytest.mark.asyncio
async def test_publish_project():
    """Test publish_project method"""
    # Create a mock project in TO_PUBLISH state
    mock_project = MagicMock(spec=DBProject)
    mock_project.id = MOCK_PROJECT_ID
    mock_project.state = ProjectState.TO_PUBLISH
    
    # Mock the DBProject.get method to return our mock project
    with patch('logic.project_service.DBProject.get', new=AsyncMock(return_value=mock_project)):
        # Mock the save method
        mock_project.save = AsyncMock()
        
        # Call the method
        result = await ProjectService.publish_project(MOCK_PROJECT_ID, MOCK_USER_ID, UserRole.ADMINISTRATOR)
        
        # Assertions
        assert result.state == ProjectState.DRAFT
        mock_project.save.assert_called_once()


@pytest.mark.asyncio
async def test_unpublish_project():
    """Test unpublish_project method"""
    # Create a mock project in DRAFT state
    mock_project = MagicMock(spec=DBProject)
    mock_project.id = MOCK_PROJECT_ID
    mock_project.state = ProjectState.DRAFT
    
    # Mock the DBProject.get method to return our mock project
    with patch('logic.project_service.DBProject.get', new=AsyncMock(return_value=mock_project)):
        # Mock the save method
        mock_project.save = AsyncMock()
        
        # Call the method
        result = await ProjectService.unpublish_project(MOCK_PROJECT_ID, MOCK_USER_ID, UserRole.ADMINISTRATOR)
        
        # Assertions
        assert result.state == ProjectState.TO_UNPUBLISH
        mock_project.save.assert_called_once()


@pytest.mark.asyncio
async def test_delete_project():
    """Test delete_project method"""
    # Create a mock project in DRAFT state
    mock_project = MagicMock(spec=DBProject)
    mock_project.id = MOCK_PROJECT_ID
    mock_project.state = ProjectState.DRAFT
    mock_project.created_by = MOCK_USER_ID
    
    # Mock the DBProject.get method to return our mock project
    with patch('logic.project_service.DBProject.get', new=AsyncMock(return_value=mock_project)):
        # Mock the save method
        mock_project.save = AsyncMock()
        
        # Call the method
        result = await ProjectService.delete_project(MOCK_PROJECT_ID, MOCK_USER_ID, UserRole.CONTRIBUTOR)
        
        # Assertions
        assert result is True
        assert mock_project.state == ProjectState.TO_DELETE
        mock_project.save.assert_called_once()


@pytest.mark.asyncio
async def test_lock_project():
    """Test lock_project method"""
    # Create a mock project in DRAFT state
    mock_project = MagicMock(spec=DBProject)
    mock_project.id = MOCK_PROJECT_ID
    mock_project.state = ProjectState.DRAFT
    mock_project.previous_state = None
    
    # Mock the DBProject.get method to return our mock project
    with patch('logic.project_service.DBProject.get', new=AsyncMock(return_value=mock_project)):
        # Mock the save method
        mock_project.save = AsyncMock()
        
        # Call the method
        result = await ProjectService.lock_project(MOCK_PROJECT_ID, MOCK_USER_ID, UserRole.ADMINISTRATOR)
        
        # Assertions
        assert result.state == ProjectState.LOCKED
        mock_project.save.assert_called_once()


@pytest.mark.asyncio
async def test_unlock_project():
    """Test unlock_project method"""
    # Create a mock project in LOCKED state
    mock_project = MagicMock(spec=DBProject)
    mock_project.id = MOCK_PROJECT_ID
    mock_project.state = ProjectState.LOCKED
    mock_project.previous_state = ProjectState.DRAFT.value
    
    # Mock the DBProject.get method to return our mock project
    with patch('logic.project_service.DBProject.get', new=AsyncMock(return_value=mock_project)):
        # Mock the save method
        mock_project.save = AsyncMock()
        
        # Call the method
        result = await ProjectService.unlock_project(MOCK_PROJECT_ID, MOCK_USER_ID, UserRole.ADMINISTRATOR)
        
        # Assertions
        assert result.state == ProjectState.DRAFT
        mock_project.save.assert_called_once()


@pytest.mark.asyncio
async def test_assign_project():
    """Test assign_project method"""
    # Create a mock project
    mock_project = MagicMock(spec=DBProject)
    mock_project.id = MOCK_PROJECT_ID
    mock_project.assigned_to = None
    mock_project.assigned_at = None
    
    # Mock the DBProject.get method to return our mock project
    with patch('logic.project_service.DBProject.get', new=AsyncMock(return_value=mock_project)):
        # Mock the save method
        mock_project.save = AsyncMock()
        
        # Call the method
        result = await ProjectService.assign_project(MOCK_PROJECT_ID, MOCK_USER_ID, MOCK_ASSIGNEE_ID, UserRole.ADMINISTRATOR)
        
        # Assertions
        assert result.assigned_to == MOCK_ASSIGNEE_ID
        assert result.assigned_at is not None
        mock_project.save.assert_called_once()


@pytest.mark.asyncio
async def test_get_projects_by_state():
    """Test get_projects_by_state method"""
    # Create mock projects
    mock_projects = [MagicMock(spec=DBProject), MagicMock(spec=DBProject)]
    
    # Mock the DBProject.find method to return a mock query object
    mock_query = MagicMock()
    mock_query.to_list = AsyncMock(return_value=mock_projects)
    
    with patch('logic.project_service.DBProject.find', return_value=mock_query):
        # Test for administrator
        result = await ProjectService.get_projects_by_state(ProjectState.DRAFT, MOCK_USER_ID, UserRole.ADMINISTRATOR)
        assert result == mock_projects


@pytest.mark.asyncio
async def test_get_projects_for_review():
    """Test get_projects_for_review method"""
    # Create mock projects
    mock_projects = [MagicMock(spec=DBProject), MagicMock(spec=DBProject)]
    
    # Mock the DBProject.find method to return a mock query object
    mock_query = MagicMock()
    mock_query.to_list = AsyncMock(return_value=mock_projects)
    
    with patch('logic.project_service.DBProject.find', return_value=mock_query):
        result = await ProjectService.get_projects_for_review(MOCK_USER_ID)
        assert result == mock_projects


@pytest.mark.asyncio
async def test_get_projects_to_publish():
    """Test get_projects_to_publish method"""
    # Create mock projects
    mock_projects = [MagicMock(spec=DBProject), MagicMock(spec=DBProject)]
    
    # Mock the DBProject.find method to return a mock query object
    mock_query = MagicMock()
    mock_query.to_list = AsyncMock(return_value=mock_projects)
    
    with patch('logic.project_service.DBProject.find', return_value=mock_query):
        result = await ProjectService.get_projects_to_publish(MOCK_USER_ID)
        assert result == mock_projects


@pytest.mark.asyncio
async def test_get_projects_to_unpublish():
    """Test get_projects_to_unpublish method"""
    # Create mock projects
    mock_projects = [MagicMock(spec=DBProject), MagicMock(spec=DBProject)]
    
    # Mock the DBProject.find method to return a mock query object
    mock_query = MagicMock()
    mock_query.to_list = AsyncMock(return_value=mock_projects)
    
    with patch('logic.project_service.DBProject.find', return_value=mock_query):
        result = await ProjectService.get_projects_to_unpublish(MOCK_USER_ID)
        assert result == mock_projects


@pytest.mark.asyncio
async def test_get_projects_to_delete():
    """Test get_projects_to_delete method"""
    # Create mock projects
    mock_projects = [MagicMock(spec=DBProject), MagicMock(spec=DBProject)]
    
    # Mock the DBProject.find method to return a mock query object
    mock_query = MagicMock()
    mock_query.to_list = AsyncMock(return_value=mock_projects)
    
    with patch('logic.project_service.DBProject.find', return_value=mock_query):
        result = await ProjectService.get_projects_to_delete(MOCK_USER_ID)
        assert result == mock_projects


@pytest.mark.asyncio
async def test_get_my_projects():
    """Test get_my_projects method"""
    # Create mock projects
    mock_projects = [MagicMock(spec=DBProject), MagicMock(spec=DBProject)]
    
    # Mock the DBProject.find method to return a mock query object
    mock_query = MagicMock()
    mock_query.to_list = AsyncMock(return_value=mock_projects)
    
    with patch('logic.project_service.DBProject.find', return_value=mock_query):
        result = await ProjectService.get_my_projects(MOCK_USER_ID)
        assert result == mock_projects


@pytest.mark.asyncio
async def test_get_assigned_projects():
    """Test get_assigned_projects method"""
    # Create mock projects
    mock_projects = [MagicMock(spec=DBProject), MagicMock(spec=DBProject)]
    
    # Mock the DBProject.find method to return a mock query object
    mock_query = MagicMock()
    mock_query.to_list = AsyncMock(return_value=mock_projects)
    
    with patch('logic.project_service.DBProject.find', return_value=mock_query):
        result = await ProjectService.get_assigned_projects(MOCK_USER_ID)
        assert result == mock_projects
