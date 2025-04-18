# tests/unit/test_analysis_service.py

import pytest
from unittest.mock import MagicMock, call # call helps check multiple calls
from uuid import uuid4
from fastapi import HTTPException
from sqlmodel import Session # Type hint for mock session

# Assuming the service functions are importable
from backend.analysis_service import (
    save_speech_and_analysis,
    calculate_word_count,
    estimate_duration
)
# Assuming models and schemas are importable
from backend.database.models import Speech, SpeechAnalysis, SourceType
from backend.schemas.analysis_schema import AnalysisResponse

# --- Test Helper Functions First ---

def test_calculate_word_count():
    assert calculate_word_count("one two three") == 3
    assert calculate_word_count("  leading and trailing spaces  ") == 5
    assert calculate_word_count("") == 0
    assert calculate_word_count(None) == 0 # Adapt if None isn't expected

def test_estimate_duration():
    assert estimate_duration(150, wpm=150) == 1.0
    assert estimate_duration(300, wpm=150) == 2.0
    assert estimate_duration(75, wpm=150) == 0.5
    assert estimate_duration(0, wpm=150) == 0.0
    assert estimate_duration(150, wpm=0) == 0.0 # Prevent division by zero

# --- Test save_speech_and_analysis ---

@pytest.fixture
def mock_session():
    """Provides a mock Session."""
    return MagicMock(spec=Session)

@pytest.fixture
def mock_analyze_gpt():
    """Provides a mock analyze_text_with_gpt function."""
    return MagicMock()

# Mock data
test_user_id = uuid4()
test_content = "This is the speech content."
mock_speech_id = uuid4()
mock_analysis_id = uuid4()
mock_analysis_response = AnalysisResponse(
    clarity_score=8,
    structure_score=7,
    filler_words_rating=9,
    feedback="Mock feedback"
)

def test_save_speech_and_analysis_success(mocker, mock_session, mock_analyze_gpt):
    """Test the successful path of saving speech and analysis."""
    # Arrange
    # Patch the actual function used by the service
    mocker.patch('backend.analysis_service.analyze_text_with_gpt', return_value=mock_analysis_response)

    # Mock the Speech and SpeechAnalysis models being added/refreshed
    # Need to configure the mock session's behavior when add/commit/refresh is called
    # The actual objects added might be instances created inside the function, so capture them
    added_objects = []
    def mock_add(obj):
        added_objects.append(obj)
    mock_session.add.side_effect = mock_add
    mock_session.commit.return_value = None # Can be called multiple times
    # Simulate refresh by setting IDs on the captured objects
    def mock_refresh(obj):
        if isinstance(obj, Speech):
            obj.id = mock_speech_id
        elif isinstance(obj, SpeechAnalysis):
            obj.id = mock_analysis_id
    mock_session.refresh.side_effect = mock_refresh

    # Act
    result_analysis = save_speech_and_analysis(
        session=mock_session,
        user_id=test_user_id,
        content=test_content,
        source_type=SourceType.TEXT,
        prompt_type="default"
    )

    # Assert
    # Check database interactions
    assert mock_session.add.call_count == 2
    assert mock_session.commit.call_count == 2 # Commit for Speech, Commit for Analysis
    assert mock_session.refresh.call_count == 2

    # Verify the added objects (basic checks)
    assert len(added_objects) == 2
    assert isinstance(added_objects[0], Speech)
    assert added_objects[0].content == test_content
    assert added_objects[0].user_id == test_user_id
    assert isinstance(added_objects[1], SpeechAnalysis)
    assert added_objects[1].clarity_score == 8
    assert added_objects[1].speech_id == mock_speech_id # Check FK is set after refresh

    # Verify analyze_text_with_gpt was called
    mock_analyze_gpt_call = mocker.patch('backend.analysis_service.analyze_text_with_gpt') # Get the mock again
    mock_analyze_gpt_call.assert_called_once_with(test_content, "default")

    # Verify the returned object
    assert isinstance(result_analysis, SpeechAnalysis)
    assert result_analysis.id == mock_analysis_id
    assert result_analysis.feedback == "Mock feedback"

def test_save_speech_and_analysis_openai_fails(mocker, mock_session):
    """Test when analyze_text_with_gpt raises an HTTPException."""
    # Arrange
    # Mock analyze_text_with_gpt to raise an error
    mock_analyze_gpt = mocker.patch('backend.analysis_service.analyze_text_with_gpt', side_effect=HTTPException(status_code=502, detail="OpenAI Error"))

    # Mock session for the initial Speech save part
    added_objects = []
    mock_session.add.side_effect = lambda obj: added_objects.append(obj)
    mock_session.commit.return_value = None
    mock_session.refresh.side_effect = lambda obj: setattr(obj, 'id', mock_speech_id) if isinstance(obj, Speech) else None

    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        save_speech_and_analysis(
            session=mock_session,
            user_id=test_user_id,
            content=test_content,
            source_type=SourceType.TEXT
        )
    # Check that the specific HTTPException from the service was re-raised
    assert excinfo.value.status_code == 502
    assert excinfo.value.detail == "OpenAI Error"

    # Check that Speech was added and committed, but Analysis was not
    assert mock_session.add.call_count == 1 # Only Speech added
    assert mock_session.commit.call_count == 1 # Only Speech committed
    assert mock_session.refresh.call_count == 1 # Only Speech refreshed
    assert isinstance(added_objects[0], Speech)
    # Verify analyze_text_with_gpt was called
    mock_analyze_gpt.assert_called_once_with(test_content, "default")

def test_save_speech_and_analysis_analysis_commit_fails(mocker, mock_session):
    """Test when the commit for SpeechAnalysis fails."""
    # Arrange
    # Mock successful OpenAI call
    mocker.patch('backend.analysis_service.analyze_text_with_gpt', return_value=mock_analysis_response)

    # Configure session mocks
    added_objects = []
    def mock_add(obj):
        added_objects.append(obj)
    mock_session.add.side_effect = mock_add
    # First commit (Speech) succeeds, second (Analysis) fails
    mock_session.commit.side_effect = [None, Exception("DB Commit Error")]
    mock_session.refresh.side_effect = lambda obj: setattr(obj, 'id', mock_speech_id) if isinstance(obj, Speech) else None

    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        save_speech_and_analysis(
            session=mock_session,
            user_id=test_user_id,
            content=test_content,
            source_type=SourceType.TEXT
        )
    assert excinfo.value.status_code == 500
    assert "Failed to save analysis results" in excinfo.value.detail

    # Check calls
    assert mock_session.add.call_count == 2 # Speech and Analysis added
    assert mock_session.commit.call_count == 2 # Both commits attempted
    assert mock_session.refresh.call_count == 1 # Only Speech refresh happened before error