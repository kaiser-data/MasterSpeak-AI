# backend/debug_routes.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import logging
from backend.config import settings
from backend.openai_service import client
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/debug/openai-test")
async def test_openai():
    """Debug endpoint to test OpenAI API connectivity"""
    try:
        # Check if API key is configured
        if not settings.OPENAI_API_KEY:
            return JSONResponse({
                "status": "error",
                "message": "OpenAI API key not configured"
            })
        
        # Mask API key for logging
        masked_key = f"{settings.OPENAI_API_KEY[:8]}..." if len(settings.OPENAI_API_KEY) > 8 else "***"
        logger.info(f"Testing OpenAI with key: {masked_key}")
        
        # Test basic OpenAI connectivity with specific model version
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "user", "content": "Say 'API connection successful'"}
            ],
            max_tokens=10
        )
        
        return JSONResponse({
            "status": "success",
            "message": "OpenAI API connection successful",
            "response": response.choices[0].message.content.strip()
        })
        
    except Exception as e:
        logger.error(f"OpenAI test failed: {e}")
        return JSONResponse({
            "status": "error", 
            "message": f"OpenAI test failed: {str(e)}"
        })

@router.get("/debug/analysis-test")
async def test_analysis():
    """Debug endpoint to test the analysis pipeline"""
    try:
        from backend.openai_service import analyze_text_with_gpt
        
        test_text = "Hello, this is a test speech for analysis."
        result = await analyze_text_with_gpt(test_text, "default")
        
        return JSONResponse({
            "status": "success",
            "message": "Analysis pipeline working",
            "result": result.dict()
        })
        
    except Exception as e:
        logger.error(f"Analysis test failed: {e}")
        return JSONResponse({
            "status": "error",
            "message": f"Analysis test failed: {str(e)}"
        })