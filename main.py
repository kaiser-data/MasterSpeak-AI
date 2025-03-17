from fastapi import FastAPI, Depends
from sqlmodel import SQLModel
from database import init_db
from routes import router as speech_router

app = FastAPI(title="Speech Analysis API", version="1.0")

# Initialize Database on Startup
@app.on_event("startup")
def on_startup():
    init_db()

# Root Endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Speech Analysis API"}

# Personalized Hello
@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

# Include Speech Analysis Routes
app.include_router(speech_router, prefix="/speech", tags=["Speech Analysis"])
