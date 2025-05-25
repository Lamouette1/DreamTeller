# services/story_storage_service.py
import os
import json
import zipfile
import io
import datetime
import logging
from typing import List, Dict, Any, Optional, Tuple
from models.story import Story, Scene, StoryPrompt
import httpx

logger = logging.getLogger(__name__)

class StoryStorageService:
    """Handles saving and loading story files that contain both text and images."""
    
    def __init__(self):
        # Create a stories directory if it doesn't exist
        self.stories_dir = "stories"
        os.makedirs(self.stories_dir, exist_ok=True)
        logger.debug(f"StoryStorage initialized. Stories directory: {self.stories_dir}")
    
    async def download_image(self, url: str) -> bytes:
        """Download an image from a URL and return its bytes."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0)
                response.raise_for_status()
                return response.content
        except Exception as e:
            logger.error(f"Error downloading image from {url}: {str(e)}")
            return None
    
    async def save_story(self, story: Story, filename: str = None) -> str:
        """
        Save a story to a zip file containing metadata and images.
        
        Args:
            story: The Story object to save
            filename: Optional filename (without extension)
            
        Returns:
            str: The filename of the saved story
        """
        try:
            # Generate filename if not provided
            if not filename:
                # Create filename from title and timestamp
                safe_title = "".join(c for c in story.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{safe_title}_{timestamp}"
            
            # Ensure filename has .story extension
            if not filename.endswith('.story'):
                filename = filename + '.story'
            
            filepath = os.path.join(self.stories_dir, filename)
            
            # Create metadata
            metadata = {
                "id": story.id,
                "title": story.title,
                "prompt": {
                    "idea": story.prompt.idea,
                    "genre": story.prompt.genre,
                    "tone": story.prompt.tone,
                    "mainCharacter": story.prompt.mainCharacter,
                    "setting": story.prompt.setting,
                    "artStyle": story.prompt.artStyle
                },
                "num_scenes": len(story.scenes),
                "creation_date": story.created_at.isoformat() if story.created_at else datetime.datetime.now().isoformat(),
                "scenes": []
            }
            
            # Create the ZIP file
            with zipfile.ZipFile(filepath, 'w') as zip_file:
                # Process each scene
                for i, scene in enumerate(story.scenes):
                    scene_data = {
                        "index": i,
                        "text": scene.text,
                        "imageUrl": scene.imageUrl,
                        "imagePrompt": scene.imagePrompt
                    }
                    
                    # Download and save image if URL is available
                    if scene.imageUrl:
                        try:
                            image_data = await self.download_image(scene.imageUrl)
                            if image_data:
                                zip_file.writestr(f"images/scene_{i}.png", image_data)
                                scene_data["image_file"] = f"images/scene_{i}.png"
                        except Exception as e:
                            logger.error(f"Error saving image for scene {i}: {str(e)}")
                    
                    metadata["scenes"].append(scene_data)
                
                # Add metadata.json
                zip_file.writestr("metadata.json", json.dumps(metadata, indent=2))
            
            logger.info(f"Story saved successfully to {filepath}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving story: {str(e)}")
            raise
    
    async def load_story(self, filename: str) -> Story:
        """
        Load a story from a zip file.
        
        Args:
            filename: The filename to load from (with or without extension)
            
        Returns:
            Story: The loaded story object
        """
        try:
            # Ensure filename has .story extension
            if not filename.endswith('.story'):
                filename = filename + '.story'
            filepath = os.path.join(self.stories_dir, filename)
            
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Story file not found: {filepath}")
            
            with zipfile.ZipFile(filepath, 'r') as zip_file:
                # Extract metadata
                if "metadata.json" not in zip_file.namelist():
                    raise ValueError(f"Invalid story file: metadata.json not found")
                
                metadata = json.loads(zip_file.read("metadata.json"))
                
                # Reconstruct the story prompt
                prompt = StoryPrompt(
                    idea=metadata["prompt"]["idea"],
                    genre=metadata["prompt"]["genre"],
                    tone=metadata["prompt"]["tone"],
                    mainCharacter=metadata["prompt"].get("mainCharacter"),
                    setting=metadata["prompt"].get("setting"),
                    artStyle=metadata["prompt"].get("artStyle", "Digital Painting")
                )
                
                # Reconstruct scenes
                scenes = []
                for scene_data in sorted(metadata["scenes"], key=lambda x: x["index"]):
                    scene = Scene(
                        text=scene_data["text"],
                        imageUrl=scene_data.get("imageUrl"),
                        imagePrompt=scene_data.get("imagePrompt")
                    )
                    scenes.append(scene)
                
                # Create the story object
                story = Story(
                    id=metadata.get("id"),
                    title=metadata["title"],
                    prompt=prompt,
                    scenes=scenes
                )
                
                # Set creation date if available
                if "creation_date" in metadata:
                    story.created_at = datetime.datetime.fromisoformat(metadata["creation_date"])
            
            logger.info(f"Story loaded successfully from {filepath}")
            return story
            
        except Exception as e:
            logger.error(f"Error loading story: {str(e)}")
            raise
    
    def list_saved_stories(self) -> List[Dict[str, Any]]:
        """
        List all saved stories with their metadata.
        
        Returns:
            List of dictionaries containing story metadata
        """
        stories = []
        
        for filename in os.listdir(self.stories_dir):
            if filename.endswith('.story'):
                try:
                    filepath = os.path.join(self.stories_dir, filename)
                    with zipfile.ZipFile(filepath, 'r') as zip_file:
                        if "metadata.json" in zip_file.namelist():
                            metadata = json.loads(zip_file.read("metadata.json"))
                            metadata["filename"] = filename
                            # Add file size
                            metadata["file_size"] = os.path.getsize(filepath)
                            stories.append(metadata)
                except Exception as e:
                    logger.error(f"Error reading story metadata from {filename}: {str(e)}")
        
        # Sort by creation date (newest first)
        stories.sort(key=lambda x: x.get("creation_date", ""), reverse=True)
        return stories
    
    def delete_story(self, filename: str) -> bool:
        """
        Delete a saved story.
        
        Args:
            filename: The filename to delete (with or without extension)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure filename has .story extension
            if not filename.endswith('.story'):
                filename = filename + '.story'
            filepath = os.path.join(self.stories_dir, filename)
            
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Story deleted: {filepath}")
                return True
            else:
                logger.warning(f"Story file not found for deletion: {filepath}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting story: {str(e)}")
            return False
    
    def get_story_file_path(self, filename: str) -> str:
        """Get the full path to a story file."""
        if not filename.endswith('.story'):
            filename = filename + '.story'
        return os.path.join(self.stories_dir, filename)

# Create singleton instance
story_storage_service = StoryStorageService()