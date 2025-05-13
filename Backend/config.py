# config.py
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define settings as simple variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY", "")

# OpenAI Settings
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))

# Image Generation Settings
IMAGE_WIDTH = int(os.getenv("IMAGE_WIDTH", "768"))
IMAGE_HEIGHT = int(os.getenv("IMAGE_HEIGHT", "512"))
DIFFUSION_STEPS = int(os.getenv("DIFFUSION_STEPS", "50"))
GUIDANCE_SCALE = float(os.getenv("GUIDANCE_SCALE", "7.5"))

# Database Settings
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dreamteller.db")

# Server settings
API_PORT = int(os.getenv("API_PORT", "5000"))

# Number of scenes in a story
DEFAULT_SCENE_COUNT = int(os.getenv("DEFAULT_SCENE_COUNT", "5"))

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
        self.OPENAI_API_KEY = OPENAI_API_KEY
        self.STABILITY_API_KEY = STABILITY_API_KEY
        self.OPENAI_MODEL = OPENAI_MODEL
        self.OPENAI_TEMPERATURE = OPENAI_TEMPERATURE
        self.OPENAI_MAX_TOKENS = OPENAI_MAX_TOKENS
        self.IMAGE_WIDTH = IMAGE_WIDTH
        self.IMAGE_HEIGHT = IMAGE_HEIGHT
        self.DIFFUSION_STEPS = DIFFUSION_STEPS
        self.GUIDANCE_SCALE = GUIDANCE_SCALE
        self.DATABASE_URL = DATABASE_URL
        self.API_PORT = API_PORT
        self.DEFAULT_SCENE_COUNT = DEFAULT_SCENE_COUNT

settings = Settings()