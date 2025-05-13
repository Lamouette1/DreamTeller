# app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import story_routes, image_routes
from config import settings, CORS_ORIGINS

app = FastAPI(
    title="DreamTeller API",
    description="API for generating AI stories and illustrations",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(story_routes.router, prefix="/api/stories", tags=["stories"])
app.include_router(image_routes.router, prefix="/api/images", tags=["images"])

@app.get("/")
async def root():
    return {"message": "Welcome to DreamTeller API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=settings.API_PORT, reload=True)