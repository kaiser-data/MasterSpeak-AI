# tests/integration/test_analysis_routes.py

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool # Useful for in-memory SQLite testing
from uuid import uuid4
from unittest.mock import MagicMock

# Assuming your FastAPI app is created in backend.main and named 'app'
from backend.main import app
# Import dependencies that need overriding
from backend.database.database import get_session
# Import the function we want to mock within the endpoint's execution path
import backend.analysis_service # Or wherever save_speech_and_analysis/analyze_text_with_gpt live
# Import models and schemas
from backend.database.models import User, Speech, SpeechAnalysis, SourceType
from backend.schemas.analysis_schema import AnalysisResponse

# --- Test Setup Fixtures ---

@pytest.fixture(name="session")
def session_fixture():
    """Create a fresh SQLite memory database session for each test."""
    # Using StaticPool makes SQLite work reliably with TestClient across threads
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine) # Create tables
    with Session(engine) as session:
        yield session
    # Teardown: Tables are dropped implicitly with in-memory DB

@pytest.fixture(name="client")
def client_fixture(session: Session, mocker):
    """Provides a TestClient with overridden dependencies."""

    # Mock the function that calls OpenAI API *within* the service module
    # This prevents real API calls during integration testing
    mock_gpt_response = AnalysisResponse(clarity_score=9, structure_score=6, filler_words_rating=8, feedback="Test OK")
    mocker.patch(
        "backend.analysis_service.analyze_text_with_gpt", # Adjust path if needed
        return_value=mock_gpt_response
    )

    def get_session_override():
        return session # Use the test session

    # Create a test user directly in the test DB for authentication override
    test_user_id = uuid4()
    test_user_email = "testuser@example.com"
    test_user = User(id=test_user_id, email=test_user_email, hashed_password="fakepassword")
    session.add(test_user)
    session.commit()
    session.refresh(test_user)

    # Simple override for getting the current user (replace with your actual dependency name)
    # This bypasses actual token verification for this test
    async def get_current_active_user_override() -> User:
        return test_user

    # Override dependencies in the FastAPI app instance
    app.dependency_overrides[get_session] = get_session_override
    # Replace 'get_current_active_user' with the actual dependency used in your route
    # Assuming it's imported in main or the router from somewhere
    # You might need to find where the dependency is defined/used.
    # Example, if it's `from backend.auth import current_active_user`:
    # from backend.auth import current_active_user # Import the actual dependency object
    # app.dependency_overrides[current_active_user] = get_current_active_user_override
    # --- Placeholder: Adjust the actual dependency object below ---
    from backend.routes.analyze_routes import get_current_active_user # Example if defined there
    app.dependency_overrides[get_current_active_user] = get_current_active_user_override
    # --- End Placeholder ---


    yield TestClient(app) # Provide the client

    # Clean up overrides after test
    app.dependency_overrides.clear()


# --- Integration Test ---

def test_analyze_text_endpoint_success(client: TestClient, session: Session, mocker):
    """Test the POST /analysis/text endpoint successful path."""
    # Arrange
    test_speech_content = "This is my integration test speech."
    test_prompt = "default"

    # Act
    response = client.post(
        "/analysis/text", # Make sure prefix matches router definition
        data={"text": test_speech_content, "prompt_type": test_prompt}
        # Use 'data' for form data, 'json' for JSON body
    )

    # Assert Response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["clarity_score"] == 9 # From mock_gpt_response
    assert response_data["structure_score"] == 6
    assert response_data["word_count"] == 6 # Calculated in service
    assert response_data["prompt"] == test_prompt
    assert "id" in response_data
    assert "speech_id" in response_data

    # Assert Database State (Optional but good for integration tests)
    analysis_id = response_data["id"]
    db_analysis = session.get(SpeechAnalysis, analysis_id)
    assert db_analysis is not None
    assert db_analysis.clarity_score == 9
    assert db_analysis.prompt == test_prompt

    speech_id = response_data["speech_id"]
    db_speech = session.get(Speech, speech_id)
    assert db_speech is not None
    assert db_speech.content == test_speech_content
    assert db_speech.source_type == SourceType.TEXT
    # Check user association - need the test user's ID from the fixture setup
    test_user = session.query(User).filter(User.email == "testuser@example.com").first()
    assert db_speech.user_id == test_user.id

    # Verify the mocked GPT function was called (optional, confirms mock worked)
    mock_gpt_call = mocker.patch("backend.analysis_service.analyze_text_with_gpt")
    mock_gpt_call.assert_called_once_with(test_speech_content, test_prompt)

def test_analyze_text_endpoint_unauthenticated(client: TestClient):
    """Test that accessing the endpoint without auth fails (if auth override is removed/conditional)."""
    # Arrange: Need to configure client fixture *without* the auth override for this test
    # (This requires more advanced fixture setup, e.g., parameterizing the fixture
    # or creating a separate fixture for unauthenticated clients)
    # For now, assuming the endpoint IS protected and the override ISN'T active:

    # --- This part requires modifying the client fixture setup ---
    # --- to allow tests *without* the auth override ---
    # --- Skipping implementation detail for brevity ---
    # response = client_unauthenticated.post(...)
    # assert response.status_code == 401 # Or 403 depending on setup
    pytest.skip("Skipping unauthenticated test - requires fixture modification")

# Add more tests for:
# - File uploads (/analysis/upload)
# - Invalid input (e.g., missing form fields)
# - Cases where analyze_text_with_gpt *is mocked to raise an error*
# - Other endpoints (auth, getting speeches/analyses)