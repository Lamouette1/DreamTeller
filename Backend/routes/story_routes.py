# routes/story_routes.py
from fastapi import APIRouter, HTTPException, Response, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from typing import List
import uuid
from datetime import datetime
import os
import io
import zipfile
from loguru import logger

from models.story import (
    StoryPrompt,
    Story,
    RegenerateTextRequest,
    RegenerateTextResponse,
    StoryResponse
)
from services.fal_service import fal_service
from services.story_storage_service import story_storage_service
from utils.error_handling import handle_api_errors

# Create a simple in-memory database for stories
# In a production app, you would use a real database
stories_db = {}

router = APIRouter()

@router.post("/generate", response_model=StoryResponse)
@handle_api_errors
async def create_story(prompt: StoryPrompt):
    """
    Generate a new story based on the provided prompt using FAL AI.
    
    Args:
        prompt: The story prompt with genre, tone, and other details
        
    Returns:
        The complete generated story
    """
    logger.info(f"Received story prompt: {prompt.model_dump()}")
    logger.info(f"numScenes value: {prompt.numScenes}")
    # Generate the story using FAL AI
    story = await fal_service.generate_story(prompt)
    
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
    # Generate new text for the scene using FAL AI
    new_text = await fal_service.regenerate_scene_text(
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

# New endpoints for save/load functionality

@router.post("/{story_id}/save")
@handle_api_errors
async def save_story(story_id: str, filename: str = None):
    """
    Save a story to a file.
    
    Args:
        story_id: The ID of the story to save
        filename: Optional filename for the saved story
        
    Returns:
        The filename of the saved story
    """
    if story_id not in stories_db:
        raise HTTPException(status_code=404, detail="Story not found")
    
    story = stories_db[story_id]
    saved_filename = await story_storage_service.save_story(story, filename)
    
    return {"filename": saved_filename, "message": "Story saved successfully"}

@router.get("/saved/list")
@handle_api_errors
async def list_saved_stories():
    """
    List all saved stories.
    
    Returns:
        List of saved story metadata
    """
    stories = story_storage_service.list_saved_stories()
    return {"stories": stories, "count": len(stories)}

@router.post("/saved/load/{filename}", response_model=StoryResponse)
@handle_api_errors
async def load_saved_story(filename: str):
    """
    Load a saved story from file.
    
    Args:
        filename: The filename of the story to load
        
    Returns:
        The loaded story
    """
    try:
        story = await story_storage_service.load_story(filename)
        # Add to in-memory database
        stories_db[story.id] = story
        return story
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Story file not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/saved/download/{filename}")
@handle_api_errors
async def download_story(filename: str):
    """
    Download a saved story file.
    
    Args:
        filename: The filename of the story to download
        
    Returns:
        The story file as a download
    """
    try:
        filepath = story_storage_service.get_story_file_path(filename)
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="Story file not found")
        
        # Return the file as a download
        return FileResponse(
            path=filepath,
            media_type="application/zip",
            filename=filename if filename.endswith('.story') else f"{filename}.story"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/saved/{filename}")
@handle_api_errors
async def delete_saved_story(filename: str):
    """
    Delete a saved story file.
    
    Args:
        filename: The filename of the story to delete
        
    Returns:
        Confirmation of deletion
    """
    success = story_storage_service.delete_story(filename)
    if success:
        return {"message": "Story deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Story file not found")

@router.post("/saved/upload")
@handle_api_errors
async def upload_story(file: UploadFile = File(...)):
    """
    Upload a story file.
    
    Args:
        file: The story file to upload
        
    Returns:
        The uploaded story
    """
    try:
        # Validate file extension
        if not file.filename.endswith('.story'):
            raise HTTPException(status_code=400, detail="Invalid file type. Only .story files are accepted.")
        
        # Save the uploaded file temporarily
        temp_filename = f"temp_{uuid.uuid4()}.story"
        temp_filepath = os.path.join(story_storage_service.stories_dir, temp_filename)
        
        # Read and save file content
        content = await file.read()
        with open(temp_filepath, 'wb') as f:
            f.write(content)
        
        # Load the story
        story = await story_storage_service.load_story(temp_filename)
        
        # Rename to proper filename based on title
        safe_title = "".join(c for c in story.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        proper_filename = f"{safe_title}.story"
        proper_filepath = os.path.join(story_storage_service.stories_dir, proper_filename)
        
        # Check if file already exists
        counter = 1
        while os.path.exists(proper_filepath):
            proper_filename = f"{safe_title}_{counter}.story"
            proper_filepath = os.path.join(story_storage_service.stories_dir, proper_filename)
            counter += 1
        
        # Rename the file
        os.rename(temp_filepath, proper_filepath)
        
        # Add to in-memory database
        stories_db[story.id] = story
        
        return {"story": story, "filename": proper_filename}
        
    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_filepath' in locals() and os.path.exists(temp_filepath):
            os.remove(temp_filepath)
        raise HTTPException(status_code=400, detail=str(e))