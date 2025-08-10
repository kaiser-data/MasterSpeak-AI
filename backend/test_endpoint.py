# Simple test endpoint to debug frontend issues
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/test-analysis-response")
async def test_analysis_response():
    """Return exactly the format our frontend expects"""
    return JSONResponse({
        "success": True,
        "speech_id": "test-speech-id-12345",
        "analysis": {
            "clarity_score": 8,
            "structure_score": 7,
            "filler_word_count": 3,
            "feedback": "This is a test feedback message to verify the frontend display is working correctly."
        }
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)