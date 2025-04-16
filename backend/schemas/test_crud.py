# tests/unit/test_crud.py

import pytest
from unittest.mock import MagicMock, ANY
from sqlmodel import SQLModel, Field # Import base SQLModel for mock model creation

from backend.crud import CRUD # Assuming crud.py is in backend/
import logging

# Disable logging noise during tests if desired
# logging.disable(logging.CRITICAL)
# Or configure logging specifically for tests

# --- Mock Model ---
# Create a simple mock SQLModel class for testing the generic CRUD
class MockModel(SQLModel):
    id: int = Field(default=None, primary_key=True)
    name: str

# --- Test Fixture (Optional but can be useful) ---
@pytest.fixture
def crud_instance():
    """Provides a CRUD instance initialized with MockModel."""
    return CRUD(MockModel)

@pytest.fixture
def mock_session():
    """Provides a MagicMock instance simulating a SQLModel/SQLAlchemy Session."""
    return MagicMock()

# --- Tests ---

def test_crud_create(crud_instance: CRUD, mock_session: MagicMock):
    """Test the create method."""
    # Arrange
    input_data = MockModel(name="Test Item")
    # Configure mocks: session.add, commit, refresh don't return values but need to be callable
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None

    # Act
    created_obj = crud_instance.create(session=mock_session, obj_in=input_data)

    # Assert
    mock_session.add.assert_called_once_with(input_data)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(input_data)
    assert created_obj == input_data # Should return the input object after refresh

def test_crud_get_found(crud_instance: CRUD, mock_session: MagicMock):
    """Test the get method when the object is found."""
    # Arrange
    obj_id = 1
    expected_obj = MockModel(id=obj_id, name="Found Item")
    # Configure mock session.get to return the expected object
    mock_session.get.return_value = expected_obj

    # Act
    retrieved_obj = crud_instance.get(session=mock_session, id=obj_id)

    # Assert
    mock_session.get.assert_called_once_with(MockModel, obj_id)
    assert retrieved_obj == expected_obj

def test_crud_get_not_found(crud_instance: CRUD, mock_session: MagicMock):
    """Test the get method when the object is not found."""
    # Arrange
    obj_id = 99
    # Configure mock session.get to return None
    mock_session.get.return_value = None

    # Act
    retrieved_obj = crud_instance.get(session=mock_session, id=obj_id)

    # Assert
    mock_session.get.assert_called_once_with(MockModel, obj_id)
    assert retrieved_obj is None

def test_crud_get_all(crud_instance: CRUD, mock_session: MagicMock):
    """Test the get_all method."""
    # Arrange
    expected_list = [
        MockModel(id=1, name="Item 1"),
        MockModel(id=2, name="Item 2"),
    ]
    # Mock the chained call session.exec(...).all()
    mock_query_result = MagicMock()
    mock_query_result.all.return_value = expected_list
    mock_session.exec.return_value = mock_query_result

    # Act
    all_objs = crud_instance.get_all(session=mock_session)

    # Assert
    mock_session.exec.assert_called_once() # We might need more specific checks on the select statement passed if complex
    mock_query_result.all.assert_called_once()
    assert all_objs == expected_list

def test_crud_update_found(crud_instance: CRUD, mock_session: MagicMock):
    """Test the update method when the object exists."""
    # Arrange
    obj_id = 1
    existing_obj = MockModel(id=obj_id, name="Original Name")
    update_data = {"name": "Updated Name"}

    # Configure mocks
    mock_session.get.return_value = existing_obj
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None # Refresh is called on the updated object

    # Act
    updated_obj = crud_instance.update(session=mock_session, id=obj_id, obj_in=update_data)

    # Assert
    mock_session.get.assert_called_once_with(MockModel, obj_id)
    assert existing_obj.name == "Updated Name" # Check the object was modified in place
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(existing_obj)
    assert updated_obj == existing_obj # Should return the modified object

def test_crud_update_not_found(crud_instance: CRUD, mock_session: MagicMock):
    """Test the update method when the object does not exist."""
    # Arrange
    obj_id = 99
    update_data = {"name": "Updated Name"}
    mock_session.get.return_value = None # Simulate object not found

    # Act
    updated_obj = crud_instance.update(session=mock_session, id=obj_id, obj_in=update_data)

    # Assert
    mock_session.get.assert_called_once_with(MockModel, obj_id)
    mock_session.commit.assert_not_called() # Commit shouldn't be called if object not found
    mock_session.refresh.assert_not_called()
    assert updated_obj is None

def test_crud_delete_found(crud_instance: CRUD, mock_session: MagicMock):
    """Test the delete method when the object exists."""
    # Arrange
    obj_id = 1
    existing_obj = MockModel(id=obj_id, name="To Be Deleted")
    mock_session.get.return_value = existing_obj
    mock_session.delete.return_value = None
    mock_session.commit.return_value = None

    # Act
    deleted_obj = crud_instance.delete(session=mock_session, id=obj_id)

    # Assert
    mock_session.get.assert_called_once_with(MockModel, obj_id)
    mock_session.delete.assert_called_once_with(existing_obj)
    mock_session.commit.assert_called_once()
    assert deleted_obj == existing_obj # Should return the object that was deleted

def test_crud_delete_not_found(crud_instance: CRUD, mock_session: MagicMock):
    """Test the delete method when the object does not exist."""
    # Arrange
    obj_id = 99
    mock_session.get.return_value = None

    # Act
    deleted_obj = crud_instance.delete(session=mock_session, id=obj_id)

    # Assert
    mock_session.get.assert_called_once_with(MockModel, obj_id)
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()
    assert deleted_obj is None