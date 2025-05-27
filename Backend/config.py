# config.py
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# FAL AI Settings
FAL_KEY = os.getenv("FAL_KEY", "")

# Image Generation Settings - Using FAL AI optimal values
# Note: We now use FAL AI's predefined image_size enums instead of custom dimensions
DEFAULT_IMAGE_SIZE = os.getenv("DEFAULT_IMAGE_SIZE", "landscape_4_3")  # Good default for stories
DIFFUSION_STEPS = int(os.getenv("DIFFUSION_STEPS", "4"))  # Optimal for FLUX schnell

# Available image sizes for FAL AI FLUX model
AVAILABLE_IMAGE_SIZES = [
    "square_hd",      # 1024x1024 - High definition square
    "square",         # 512x512 - Standard square  
    "portrait_4_3",   # 768x1024 - Portrait 4:3 ratio
    "portrait_16_9",  # 576x1024 - Portrait 16:9 ratio
    "landscape_4_3",  # 1024x768 - Landscape 4:3 ratio (good for stories)
    "landscape_16_9"  # 1024x576 - Landscape 16:9 ratio (cinematic)
]

# Art style to optimal image size mapping
ART_STYLE_IMAGE_SIZE_MAP = {
    "Digital Painting": "landscape_4_3",      # Detailed scenes work well in 4:3
    "Watercolor": "landscape_4_3",            # Natural, flowing compositions
    "Pixel Art": "square_hd",                 # Pixel art looks great in square
    "Comic Book": "landscape_16_9",           # Wide panels like comics
    "3D Rendered": "landscape_4_3",           # 3D scenes benefit from 4:3
    "Children's Book Illustration": "landscape_4_3",  # Traditional book format
    "Concept Art": "landscape_16_9"           # Wide, dramatic compositions
}

# Database Settings
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dreamteller.db")

# Server settings
API_PORT = int(os.getenv("API_PORT", "5000"))

# Number of scenes in a story
DEFAULT_SCENE_COUNT = int(os.getenv("DEFAULT_SCENE_COUNT", "5"))
MIN_SCENE_COUNT = 3
MAX_SCENE_COUNT = 10

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

# Image quality settings
IMAGE_QUALITY = float(os.getenv("IMAGE_QUALITY", "0.95"))  # JPEG quality for saved images
IMAGE_TIMEOUT = int(os.getenv("IMAGE_TIMEOUT", "60"))      # Timeout for image downloads

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "dreamteller.log")

# Create a settings object for compatibility with the rest of the code
class Settings:
    def __init__(self):
        self.FAL_KEY = FAL_KEY
        self.DEFAULT_IMAGE_SIZE = DEFAULT_IMAGE_SIZE
        self.DIFFUSION_STEPS = DIFFUSION_STEPS
        self.AVAILABLE_IMAGE_SIZES = AVAILABLE_IMAGE_SIZES
        self.ART_STYLE_IMAGE_SIZE_MAP = ART_STYLE_IMAGE_SIZE_MAP
        self.DATABASE_URL = DATABASE_URL
        self.API_PORT = API_PORT
        self.DEFAULT_SCENE_COUNT = DEFAULT_SCENE_COUNT
        self.MIN_SCENE_COUNT = MIN_SCENE_COUNT
        self.MAX_SCENE_COUNT = MAX_SCENE_COUNT
        self.STORIES_DIR = STORIES_DIR
        self.IMAGE_QUALITY = IMAGE_QUALITY
        self.IMAGE_TIMEOUT = IMAGE_TIMEOUT
        self.LOG_LEVEL = LOG_LEVEL
        self.LOG_FILE = LOG_FILE
        
        # Backward compatibility - these are no longer used but kept for any legacy code
        self.IMAGE_WIDTH = 1024   # Default landscape_4_3 width
        self.IMAGE_HEIGHT = 768   # Default landscape_4_3 height

settings = Settings()

# Validation functions
def validate_image_size(image_size: str) -> bool:
    """Validate that the image size is supported by FAL AI."""
    return image_size in AVAILABLE_IMAGE_SIZES

def get_image_size_for_art_style(art_style: str) -> str:
    """Get the optimal image size for a given art style."""
    return ART_STYLE_IMAGE_SIZE_MAP.get(art_style, DEFAULT_IMAGE_SIZE)

def validate_scene_count(scene_count: int) -> bool:
    """Validate that the scene count is within acceptable limits."""
    return MIN_SCENE_COUNT <= scene_count <= MAX_SCENE_COUNT