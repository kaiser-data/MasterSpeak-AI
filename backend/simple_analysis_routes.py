# backend/simple_analysis_routes.py
# Simple analysis endpoint that always works for testing

from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import JSONResponse
import logging
import uuid
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/api/simple-analyze/text")
async def simple_analyze_text(
    text: str = Form(...),
    title: str = Form("Simple Analysis")
):
    """Simple analysis endpoint that always works."""
    try:
        # Generate realistic mock analysis
        word_count = len(text.split())
        
        # Simple scoring based on text length and structure
        clarity_score = min(10, max(3, 5 + (word_count // 5)))
        structure_score = min(10, max(3, 6 + (len(text.split('.')) // 2)))
        filler_count = text.lower().count('um') + text.lower().count('uh') + text.lower().count('like')
        
        feedback = f"Analysis complete! Your speech has {word_count} words. "
        if clarity_score >= 7:
            feedback += "Good clarity. "
        if structure_score >= 7:
            feedback += "Well structured. "
        if filler_count == 0:
            feedback += "No filler words detected - excellent!"
        elif filler_count <= 2:
            feedback += "Minimal filler words - good job!"
        else:
            feedback += f"Try to reduce {filler_count} filler words."
        
        speech_id = str(uuid.uuid4())
        
        return JSONResponse(content={
            "success": True,
            "speech_id": speech_id,
            "analysis": {
                "word_count": word_count,
                "clarity_score": clarity_score,
                "structure_score": structure_score,
                "filler_word_count": filler_count,
                "feedback": feedback,
                "created_at": datetime.utcnow().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error in simple analysis: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Simple analysis failed: {str(e)}"}
        )