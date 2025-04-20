# tests/unit/test_prompts.py

import pytest
from backend.prompts import get_prompt, PROMPTS

def test_get_prompt_success():
    """Test retrieving a valid prompt type."""
    prompt_type = "default"
    expected_prompt = PROMPTS[prompt_type]
    actual_prompt = get_prompt(prompt_type)
    assert actual_prompt == expected_prompt

def test_get_prompt_detailed_success():
    """Test retrieving another valid prompt type."""
    prompt_type = "detailed"
    expected_prompt = PROMPTS[prompt_type]
    actual_prompt = get_prompt(prompt_type)
    assert actual_prompt == expected_prompt

def test_get_prompt_invalid_type():
    """Test retrieving an invalid prompt type raises ValueError."""
    invalid_prompt_type = "non_existent_prompt"
    with pytest.raises(ValueError) as excinfo:
        get_prompt(invalid_prompt_type)
    assert f"Unknown prompt type: {invalid_prompt_type}" in str(excinfo.value)

def test_get_prompt_case_sensitive():
    """Test that prompt types are case-sensitive (assuming they are)."""
    prompt_type_lower = "default"
    prompt_type_upper = "Default" # Assuming this is invalid
    # Check lowercase works
    assert get_prompt(prompt_type_lower) == PROMPTS[prompt_type_lower]
    # Check uppercase fails
    with pytest.raises(ValueError):
        get_prompt(prompt_type_upper)