# routes/story_routes.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import uuid
from datetime import datetime

from models.story import (
    StoryPrompt,
    Story,
    RegenerateTextRequest,
    RegenerateTextResponse,
    StoryResponse
)
from services.openai_service import generate_story, regenerate_scene_text
from utils.error_handling import handle_api_errors

# Create a simple in-memory database for stories
# In a production app, you would use a real database
stories_db = {}

router = APIRouter()

@router.post("/generate", response_model=StoryResponse)
@handle_api_errors
async def create_story(prompt: StoryPrompt):
    """
    Generate a new story based on the provided prompt.
    
    Args:
        prompt: The story prompt with genre, tone, and other details
        
    Returns:
        The complete generated story
    """
    # Generate the story using OpenAI
    story = await generate_story(prompt)
    
    # Store the story in our "database"
    stories_db[story.id] = story
    
    return story

@router.post("/regenerate-text", response_model=RegenerateTextResponse)
@handle_api_errors
async def regenerate_scene(request: RegenerateTextRequest):
    """
    Regenerate text for a specific scene in a story.
    
    Args:
        request: Contains the original prompt, current text, and scene index
        
    Returns:
        The regenerated text for the scene
    """
    # Generate new text for the scene
    new_text = await regenerate_scene_text(
        prompt=request.prompt,
        current_text=request.currentText,
        scene_index=request.sceneIndex
    )
    
    return RegenerateTextResponse(text=new_text)

@router.get("", response_model=List[StoryResponse])
@handle_api_errors
async def get_all_stories():
    """
    Get all stored stories.
    
    Returns:
        List of all stories
    """
    return list(stories_db.values())

@router.get("/{story_id}", response_model=StoryResponse)
@handle_api_errors
async def get_story(story_id: str):
    """
    Get a specific story by ID.
    
    Args:
        story_id: The ID of the story to retrieve
        
    Returns:
        The requested story
    """
    if story_id not in stories_db:
        raise HTTPException(status_code=404, detail="Story not found")
    
    return stories_db[story_id]

@router.delete("/{story_id}")
@handle_api_errors
async def delete_story(story_id: str):
    """
    Delete a story by ID.
    
    Args:
        story_id: The ID of the story to delete
        
    Returns:
        Confirmation of deletion
    """
    if story_id not in stories_db:
        raise HTTPException(status_code=404, detail="Story not found")
    
    del stories_db[story_id]
    
    return {"message": "Story deleted successfully"}