# app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from routes import story_routes, image_routes
from config import settings, CORS_ORIGINS

app = FastAPI(
    title="DreamTeller API",
    description="API for generating AI stories and illustrations using FAL AI",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create stories directory if it doesn't exist
os.makedirs(settings.STORIES_DIR, exist_ok=True)

# Mount static files for serving saved stories if needed
if os.path.exists(settings.STORIES_DIR):
    app.mount(f"/stories", StaticFiles(directory=settings.STORIES_DIR), name="stories")

# Include routers
app.include_router(story_routes.router, prefix="/api/stories", tags=["stories"])
app.include_router(image_routes.router, prefix="/api/images", tags=["images"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to DreamTeller API v2.0",
        "features": [
            "AI-powered story generation using FAL AI",
            "Dynamic scene illustration",
            "Story save/load functionality",
            "Scene regeneration"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "DreamTeller API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=settings.API_PORT, reload=True)