# backend/openai_service.py
import os
import json
import logging
from openai import OpenAI, APIError, AuthenticationError, RateLimitError, BadRequestError
from fastapi import HTTPException
from pydantic import ValidationError

from backend.config import settings # Import settings
from backend.prompts import get_prompt
from backend.schemas.analysis_schema import AnalysisResponse # Import schema

logger = logging.getLogger(__name__)

# Initialize the client using the API key from settings
# Consider using AsyncOpenAI for async routes
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def analyze_text_with_gpt(text: str, prompt_type: str = "default") -> AnalysisResponse:
    """
    Analyze text using OpenAI GPT, handle errors, and validate the response.

    Args:
        text (str): The text to analyze.
        prompt_type (str): The type of prompt to use.

    Returns:
        AnalysisResponse: Validated analysis data.

    Raises:
        HTTPException: If analysis fails or response is invalid.
    """
    try:
        prompt_template = get_prompt(prompt_type)
        prompt = prompt_template.format(text=text)

        logger.info(f"Sending request to OpenAI (prompt type: {prompt_type})...")
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Or your preferred model
            messages=[
                {"role": "system", "content": "You are an expert speech analyst. Respond ONLY with valid JSON matching the requested structure."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5, # Adjust temperature as needed
            max_tokens=300, # Adjust based on expected response size
            response_format={"type": "json_object"} # Use JSON mode if available
        )

        analysis_content = response.choices[0].message.content.strip()
        logger.debug(f"Raw OpenAI response content: {analysis_content}")

        # Parse and validate the JSON response using Pydantic schema
        analysis_data = AnalysisResponse.parse_raw(analysis_content)
        logger.info("OpenAI analysis successful and response validated.")
        return analysis_data

    except (APIError, RateLimitError) as e:
        logger.error(f"OpenAI API Error: {e}", exc_info=True)
        raise HTTPException(status_code=502, detail=f"Analysis service communication error: {type(e).__name__}")
    except AuthenticationError as e:
        logger.error(f"OpenAI Authentication Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis service authentication failed. Check API key configuration.")
    except BadRequestError as e:
         logger.error(f"OpenAI Bad Request Error (possibly prompt issue): {e}", exc_info=True)
         raise HTTPException(status_code=400, detail=f"Invalid request sent to analysis service: {e}")
    except ValidationError as e:
        logger.error(f"Invalid JSON structure or data types received from OpenAI:\n{analysis_content}\nValidation Errors: {e.errors()}", exc_info=True)
        raise HTTPException(status_code=500, detail="Received invalid analysis data format from service.")
    except ValueError as e: # Catch errors from get_prompt
         logger.error(f"Value error (e.g., unknown prompt type): {e}", exc_info=True)
         raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during OpenAI analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred during analysis.")

# Remove the __main__ test block or update it to use the new structure/schema