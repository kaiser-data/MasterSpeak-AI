# backend/openai_service_backup.py
# Simple backup implementation without advanced features

import os
import json
import logging
import asyncio
from openai import OpenAI, APIError, AuthenticationError, RateLimitError, BadRequestError
from fastapi import HTTPException
from pydantic import ValidationError

from backend.config import settings
from backend.prompts import get_prompt
from backend.schemas.analysis_schema import OpenAIAnalysisResponse

logger = logging.getLogger(__name__)

# Initialize the client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

async def analyze_text_with_gpt_simple(text: str, prompt_type: str = "default") -> OpenAIAnalysisResponse:
    """Simple OpenAI analysis without advanced features for debugging."""
    try:
        # Get prompt template
        prompt_template = get_prompt(prompt_type)
        prompt = prompt_template.format(text=text)
        
        logger.info(f"Sending simple request to OpenAI (prompt type: {prompt_type})...")
        
        # Try without JSON format requirement first
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert speech analyst. Respond with valid JSON containing exactly these fields: clarity_score (1-10), structure_score (1-10), filler_words_rating (1-10), feedback (string)."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=400
        )
        
        analysis_content = response.choices[0].message.content.strip()
        logger.info(f"Raw OpenAI response: {analysis_content}")
        
        # Try to extract JSON from response
        try:
            # Find JSON in response
            start_idx = analysis_content.find('{')
            end_idx = analysis_content.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_content = analysis_content[start_idx:end_idx]
                analysis_dict = json.loads(json_content)
            else:
                analysis_dict = json.loads(analysis_content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            # Return default values if parsing fails
            analysis_dict = {
                "clarity_score": 5,
                "structure_score": 5,
                "filler_words_rating": 5,
                "feedback": f"Analysis completed but response format was unexpected: {analysis_content[:100]}..."
            }
        
        # Validate and create response
        analysis_data = OpenAIAnalysisResponse(**analysis_dict)
        logger.info("OpenAI analysis successful")
        return analysis_data
        
    except AuthenticationError as e:
        logger.error(f"OpenAI Authentication Error: {e}")
        raise HTTPException(status_code=500, detail="Analysis service authentication failed")
    
    except BadRequestError as e:
        logger.error(f"OpenAI Bad Request Error: {e}")
        raise HTTPException(status_code=500, detail="Analysis request format error")
    
    except RateLimitError as e:
        logger.error(f"OpenAI Rate Limit Error: {e}")
        raise HTTPException(status_code=429, detail="Analysis service rate limit exceeded")
    
    except Exception as e:
        logger.error(f"Unexpected error during OpenAI analysis: {e}")
        raise HTTPException(status_code=500, detail="Analysis service temporarily unavailable")