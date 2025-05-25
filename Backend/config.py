# config.py
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# FAL AI Settings
FAL_KEY = os.getenv("FAL_KEY", "")

# Image Generation Settings
IMAGE_WIDTH = int(os.getenv("IMAGE_WIDTH", "600"))
IMAGE_HEIGHT = int(os.getenv("IMAGE_HEIGHT", "600"))
DIFFUSION_STEPS = int(os.getenv("DIFFUSION_STEPS", "4"))

# Database Settings
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dreamteller.db")

# Server settings
API_PORT = int(os.getenv("API_PORT", "5000"))

# Number of scenes in a story
DEFAULT_SCENE_COUNT = int(os.getenv("DEFAULT_SCENE_COUNT", "5"))

# Story storage directory
STORIES_DIR = os.getenv("STORIES_DIR", "stories")

# CORS settings
def get_cors_origins() -> List[str]:
    """Get CORS origins from environment variable."""
    origins = os.getenv("CORS_ORIGINS", "*")
    if origins == "*":
        return ["*"]
    return origins.split(",")

CORS_ORIGINS = get_cors_origins()

# Create a settings object for compatibility with the rest of the code
class Settings:
    def __init__(self):
        self.FAL_KEY = FAL_KEY
        self.IMAGE_WIDTH = IMAGE_WIDTH
        self.IMAGE_HEIGHT = IMAGE_HEIGHT
        self.DIFFUSION_STEPS = DIFFUSION_STEPS
        self.DATABASE_URL = DATABASE_URL
        self.API_PORT = API_PORT
        self.DEFAULT_SCENE_COUNT = DEFAULT_SCENE_COUNT
        self.STORIES_DIR = STORIES_DIR

settings = Settings()