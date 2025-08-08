# backend/mock_analysis_service.py
# Mock analysis service for testing when OpenAI is not available

import logging
import random
from backend.schemas.analysis_schema import OpenAIAnalysisResponse

logger = logging.getLogger(__name__)

async def analyze_text_with_gpt_mock(text: str, prompt_type: str = "default") -> OpenAIAnalysisResponse:
    """Mock analysis service that returns realistic fake data for testing."""
    
    logger.info(f"Using mock analysis service for text: {text[:50]}...")
    
    # Simulate some basic analysis
    word_count = len(text.split())
    
    # Generate realistic but fake scores based on simple heuristics
    clarity_score = min(10, max(1, 7 + random.randint(-2, 2)))
    structure_score = min(10, max(1, 6 + random.randint(-2, 3)))
    filler_words_rating = min(10, max(1, 8 + random.randint(-3, 2)))
    
    # Generate appropriate feedback
    feedback_parts = []
    
    if clarity_score >= 8:
        feedback_parts.append("Your speech is very clear and easy to understand.")
    elif clarity_score >= 6:
        feedback_parts.append("Your speech is generally clear with some minor areas for improvement.")
    else:
        feedback_parts.append("Consider speaking more clearly and using simpler language.")
    
    if structure_score >= 8:
        feedback_parts.append("The structure of your speech is well-organized.")
    elif structure_score >= 6:
        feedback_parts.append("Your speech has decent structure but could benefit from clearer organization.")
    else:
        feedback_parts.append("Try to organize your thoughts with a clear beginning, middle, and end.")
    
    if filler_words_rating >= 8:
        feedback_parts.append("Great job avoiding filler words!")
    elif filler_words_rating >= 6:
        feedback_parts.append("You use some filler words but it's not excessive.")
    else:
        feedback_parts.append("Try to reduce filler words like 'um', 'uh', and 'you know'.")
    
    feedback = " ".join(feedback_parts)
    
    return OpenAIAnalysisResponse(
        clarity_score=clarity_score,
        structure_score=structure_score,
        filler_words_rating=filler_words_rating,
        feedback=feedback
    )