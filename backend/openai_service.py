# backend/openai_service.py
import os
import json
import logging
import time
from openai import OpenAI, APIError, AuthenticationError, RateLimitError, BadRequestError
from fastapi import HTTPException
from pydantic import ValidationError
from typing import Optional, Dict
import asyncio
from datetime import datetime, timedelta
from functools import lru_cache
import hashlib

from backend.config import settings # Import settings
from backend.prompts import get_prompt
from backend.schemas.analysis_schema import OpenAIAnalysisResponse, AnalysisResponse # Import schema

logger = logging.getLogger(__name__)

# Initialize the client using the API key from settings
# Consider using AsyncOpenAI for async routes
client = OpenAI(api_key=settings.OPENAI_API_KEY)

class RateLimiter:
    def __init__(self, tokens_per_minute: int = 40):  # Increased from 20 to 40
        self.tokens_per_minute = tokens_per_minute
        self.tokens = tokens_per_minute
        self.last_refill = datetime.now()
        self.lock = asyncio.Lock()
        self.requests_in_progress = 0
        self.max_concurrent_requests = 5

    async def acquire(self):
        async with self.lock:
            # Check concurrent requests
            if self.requests_in_progress >= self.max_concurrent_requests:
                await asyncio.sleep(1)
                return await self.acquire()

            now = datetime.now()
            time_passed = (now - self.last_refill).total_seconds()
            
            # Refill tokens based on time passed
            if time_passed >= 60:
                self.tokens = self.tokens_per_minute
                self.last_refill = now
            else:
                # Add tokens proportionally to time passed
                self.tokens = min(
                    self.tokens_per_minute,
                    self.tokens + (self.tokens_per_minute * time_passed / 60)
                )
            
            if self.tokens < 1:
                # Calculate wait time
                wait_time = 60 - time_passed
                await asyncio.sleep(wait_time)
                self.tokens = self.tokens_per_minute
                self.last_refill = datetime.now()
            
            self.tokens -= 1
            self.requests_in_progress += 1

    async def release(self):
        async with self.lock:
            self.requests_in_progress -= 1

# Initialize rate limiter with increased rate
rate_limiter = RateLimiter(tokens_per_minute=40)

# Cache for storing analysis results
analysis_cache: Dict[str, OpenAIAnalysisResponse] = {}

def get_cache_key(text: str, prompt_type: str) -> str:
    """Generate a cache key for the analysis request."""
    return hashlib.md5(f"{text}:{prompt_type}".encode()).hexdigest()

@lru_cache(maxsize=100)
def get_cached_prompt(prompt_type: str) -> str:
    """Cache the prompt templates to avoid repeated string formatting."""
    return get_prompt(prompt_type)

async def analyze_text_with_gpt(text: str, prompt_type: str = "default", max_retries: int = 3) -> OpenAIAnalysisResponse:
    """
    Analyze text using OpenAI GPT with rate limiting, caching, and retry logic.

    Args:
        text (str): The text to analyze.
        prompt_type (str): The type of prompt to use.
        max_retries (int): Maximum number of retry attempts.

    Returns:
        OpenAIAnalysisResponse: Validated analysis data.

    Raises:
        HTTPException: If analysis fails or response is invalid.
    """
    # Check cache first
    cache_key = get_cache_key(text, prompt_type)
    if cache_key in analysis_cache:
        logger.info("Returning cached analysis result")
        return analysis_cache[cache_key]

    retry_count = 0
    last_error = None

    while retry_count < max_retries:
        try:
            # Wait for rate limit token
            await rate_limiter.acquire()
            
            try:
                # Get cached prompt template
                prompt_template = get_cached_prompt(prompt_type)
                prompt = prompt_template.format(text=text)

                logger.info(f"Sending request to OpenAI (prompt type: {prompt_type})...")
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",  # Changed from gpt-4 to more reliable model
                    messages=[
                        {"role": "system", "content": "You are an expert speech analyst. Respond ONLY with valid JSON matching the requested structure. The feedback field should be a single string, not a dictionary."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.5,
                    max_tokens=500,  # Increased token limit
                    response_format={"type": "json_object"}
                )

                analysis_content = response.choices[0].message.content.strip()
                logger.debug(f"Raw OpenAI response content: {analysis_content}")

                # Parse and validate the JSON response
                analysis_data = OpenAIAnalysisResponse.parse_raw(analysis_content)
                
                # Cache the result
                analysis_cache[cache_key] = analysis_data
                
                logger.info("OpenAI analysis successful and response validated.")
                return analysis_data

            finally:
                await rate_limiter.release()

        except RateLimitError as e:
            last_error = e
            retry_count += 1
            if retry_count < max_retries:
                # Exponential backoff with longer initial delay
                wait_time = min(2 ** (retry_count + 2), 60)  # Start with 8 seconds
                logger.warning(f"Rate limit hit, retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            continue

        except AuthenticationError as e:
            logger.error(f"OpenAI Authentication Error - check API key: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Analysis service authentication failed")
        
        except (APIError, BadRequestError) as e:
            logger.error(f"OpenAI API Error: {e}", exc_info=True)
            raise HTTPException(
                status_code=502 if isinstance(e, APIError) else 500,
                detail=f"Analysis service error: {type(e).__name__}"
            )

        except ValidationError as e:
            logger.error(f"Invalid JSON structure or data types received from OpenAI:\n{analysis_content}\nValidation Errors: {e.errors()}", exc_info=True)
            raise HTTPException(status_code=500, detail="Received invalid analysis data format from service.")

        except ValueError as e:
            logger.error(f"Value error (e.g., unknown prompt type): {e}", exc_info=True)
            raise HTTPException(status_code=400, detail=str(e))

        except Exception as e:
            logger.error(f"Unexpected error during OpenAI analysis: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="An unexpected error occurred during analysis.")

    # If we've exhausted all retries
    if last_error:
        logger.error(f"Failed after {max_retries} retries. Last error: {last_error}")
        raise HTTPException(
            status_code=429,
            detail="Analysis service is currently overloaded. Please try again later."
        )

# Remove the __main__ test block or update it to use the new structure/schema