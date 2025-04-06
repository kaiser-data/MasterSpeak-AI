# main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes import all_routers

app = FastAPI()

# Mount static files directory
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")

# Include all routers
for router in all_routers:
    app.include_router(router)