# models/story.py
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class StoryPrompt(BaseModel):
    """Story prompt model for generating a new story."""
    idea: str = Field(..., description="The main story idea or concept")
    genre: str = Field(..., description="The genre of the story")
    tone: str = Field(..., description="The tone or mood of the story")
    mainCharacter: Optional[str] = Field(None, description="Description of the main character")
    setting: Optional[str] = Field(None, description="The setting of the story")
    artStyle: str = Field(..., description="The art style for illustrations")
    numScenes: int = Field(5, ge=3, le=10, description="Number of scenes in the story (3-10)")

class Scene(BaseModel):
    """Scene model representing a part of the story with text and image."""
    text: str
    imageUrl: Optional[str] = None
    imagePrompt: Optional[str] = None

class Story(BaseModel):
    """Complete story model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    prompt: StoryPrompt
    scenes: List[Scene]
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

class StoryResponse(BaseModel):
    """API response model for stories."""
    id: str
    title: str
    prompt: StoryPrompt
    scenes: List[Scene]

class RegenerateTextRequest(BaseModel):
    """Request model for regenerating scene text."""
    prompt: StoryPrompt
    currentText: str
    sceneIndex: int

class RegenerateTextResponse(BaseModel):
    """Response model for regenerated text."""
    text: str