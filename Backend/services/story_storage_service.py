# services/story_storage_service.py
import os
import json
import zipfile
import io
import datetime
import logging
import uuid
from typing import List, Dict, Any, Optional, Tuple
from models.story import Story, Scene, StoryPrompt
import httpx

logger = logging.getLogger(__name__)

class StoryStorageService:
    """Handles saving and loading story files that contain both text and images."""

    def __init__(self):
        # Create a stories directory with proper permissions
        self.stories_dir = os.path.abspath("stories")
        os.makedirs(self.stories_dir, exist_ok=True)
        logger.info(f"StoryStorage initialized. Stories directory: {os.path.abspath(self.stories_dir)}")

        # Verify write access with a test file
        try:
            test_file = os.path.join(self.stories_dir, ".write_test")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            logger.info("Write access to stories directory confirmed")
        except Exception as e:
            logger.error(f"CRITICAL: Cannot write to stories directory: {str(e)}")

    async def download_image(self, url: str) -> Optional[bytes]:
        """Download an image from a URL and return its bytes."""
        try:
            logger.info(f"Downloading image from: {url}")
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                logger.info(f"Image downloaded: {len(response.content)} bytes")
                return response.content
        except Exception as e:
            logger.error(f"Error downloading image from {url}: {str(e)}")
            # Try once more with a longer timeout
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    logger.info(f"Retrying image download from: {url}")
                    response = await client.get(url)
                    response.raise_for_status()
                    logger.info(f"Image downloaded on retry: {len(response.content)} bytes")
                    return response.content
            except Exception as retry_error:
                logger.error(f"Retry failed for image download: {str(retry_error)}")
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
            logger.info(f"Saving story to: {filepath}")

            # Create metadata with all required fields
            metadata = {
                "id": story.id,
                "title": story.title,
                "prompt": {
                    "idea": story.prompt.idea,
                    "genre": story.prompt.genre,
                    "tone": story.prompt.tone,
                    "mainCharacter": story.prompt.mainCharacter or "",
                    "setting": story.prompt.setting or "",
                    "artStyle": story.prompt.artStyle,
                    "numScenes": getattr(story.prompt, "numScenes", 5)
                },
                "num_scenes": len(story.scenes),
                "creation_date": story.created_at.isoformat() if story.created_at else datetime.datetime.now().isoformat(),
                "scenes": []
            }

            # Create the ZIP file
            with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Create images directory in the ZIP
                zip_file.writestr("images/.keep", "")

                # Process each scene
                for i, scene in enumerate(story.scenes):
                    scene_data = {
                        "index": i,
                        "text": scene.text,
                        "imageUrl": scene.imageUrl,
                        "imagePrompt": scene.imagePrompt or ""
                    }

                    # Download and save image if URL is available
                    if scene.imageUrl:
                        try:
                            image_data = await self.download_image(scene.imageUrl)
                            if image_data:
                                image_filename = f"images/scene_{i}.png"
                                zip_file.writestr(image_filename, image_data)
                                scene_data["image_file"] = image_filename
                                logger.info(f"Added image for scene {i} to ZIP")
                            else:
                                logger.warning(f"No image data for scene {i}")
                        except Exception as e:
                            logger.error(f"Error saving image for scene {i}: {str(e)}")

                    metadata["scenes"].append(scene_data)

                # Add metadata.json
                zip_file.writestr("metadata.json", json.dumps(metadata, indent=2))
                logger.info(f"Metadata added to ZIP: {len(json.dumps(metadata))} bytes")

            # Verify file was created
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                logger.info(f"Story saved successfully: {filepath} ({file_size} bytes)")
                return filename
            else:
                logger.error(f"Failed to create ZIP file: {filepath}")
                raise Exception("ZIP file was not created")

        except Exception as e:
            logger.error(f"Error saving story: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    def list_saved_stories(self) -> List[Dict[str, Any]]:
        """
        List all saved stories with their metadata.

        Returns:
            List of story metadata dictionaries
        """
        try:
            stories = []
            
            if not os.path.exists(self.stories_dir):
                logger.warning(f"Stories directory does not exist: {self.stories_dir}")
                return stories

            for filename in os.listdir(self.stories_dir):
                if filename.endswith('.story'):
                    try:
                        filepath = os.path.join(self.stories_dir, filename)
                        
                        # Extract metadata from the zip file
                        with zipfile.ZipFile(filepath, 'r') as zip_file:
                            if 'metadata.json' in zip_file.namelist():
                                metadata_content = zip_file.read('metadata.json')
                                metadata = json.loads(metadata_content.decode('utf-8'))
                                
                                # Add filename to metadata
                                metadata['filename'] = filename
                                stories.append(metadata)
                            else:
                                logger.warning(f"No metadata.json found in {filename}")
                                
                    except Exception as e:
                        logger.error(f"Error reading story file {filename}: {str(e)}")
                        continue

            # Sort stories by creation date (newest first)
            stories.sort(key=lambda x: x.get('creation_date', ''), reverse=True)
            logger.info(f"Found {len(stories)} saved stories")
            return stories

        except Exception as e:
            logger.error(f"Error listing saved stories: {str(e)}")
            return []

    async def load_story(self, filename: str) -> Story:
        """
        Load a story from a saved file.

        Args:
            filename: The filename of the story to load

        Returns:
            The loaded Story object
        """
        try:
            filepath = os.path.join(self.stories_dir, filename)
            
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Story file not found: {filename}")

            with zipfile.ZipFile(filepath, 'r') as zip_file:
                # Read metadata
                if 'metadata.json' not in zip_file.namelist():
                    raise ValueError(f"Invalid story file: missing metadata.json in {filename}")
                
                metadata_content = zip_file.read('metadata.json')
                metadata = json.loads(metadata_content.decode('utf-8'))

                # Reconstruct StoryPrompt
                prompt_data = metadata['prompt']
                story_prompt = StoryPrompt(
                    idea=prompt_data['idea'],
                    genre=prompt_data['genre'],
                    tone=prompt_data['tone'],
                    mainCharacter=prompt_data.get('mainCharacter', ''),
                    setting=prompt_data.get('setting', ''),
                    artStyle=prompt_data['artStyle'],
                    numScenes=prompt_data.get('numScenes', 5)
                )

                # Reconstruct scenes
                scenes = []
                for scene_data in metadata['scenes']:
                    # Check if there's a saved image file
                    image_url = scene_data.get('imageUrl')
                    if 'image_file' in scene_data:
                        # For now, we'll use the original URL since we can't serve local files easily
                        # In a production app, you'd want to serve these files via a static file endpoint
                        image_url = scene_data.get('imageUrl')
                    
                    scene = Scene(
                        text=scene_data['text'],
                        imageUrl=image_url,
                        imagePrompt=scene_data.get('imagePrompt', '')
                    )
                    scenes.append(scene)

                # Reconstruct Story
                story = Story(
                    id=metadata['id'],
                    title=metadata['title'],
                    prompt=story_prompt,
                    scenes=scenes,
                    created_at=datetime.datetime.fromisoformat(metadata['creation_date']) if metadata.get('creation_date') else datetime.datetime.now()
                )

                logger.info(f"Successfully loaded story: {story.title}")
                return story

        except Exception as e:
            logger.error(f"Error loading story {filename}: {str(e)}")
            raise

    def get_story_file_path(self, filename: str) -> str:
        """
        Get the full file path for a story filename.

        Args:
            filename: The story filename

        Returns:
            Full path to the story file
        """
        if not filename.endswith('.story'):
            filename = filename + '.story'
        return os.path.join(self.stories_dir, filename)

    def delete_story(self, filename: str) -> bool:
        """
        Delete a saved story file.

        Args:
            filename: The filename of the story to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            filepath = self.get_story_file_path(filename)
            
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Successfully deleted story: {filename}")
                return True
            else:
                logger.warning(f"Story file not found for deletion: {filename}")
                return False

        except Exception as e:
            logger.error(f"Error deleting story {filename}: {str(e)}")
            return False

# Create singleton instance
story_storage_service = StoryStorageService()