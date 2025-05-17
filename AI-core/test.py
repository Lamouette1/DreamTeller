import os
import sys
import time
import pygame
import threading
import dotenv
import json
import logging
import re
import urllib.request
import io
import zipfile
import datetime
from typing import List, Tuple, Dict, Any, Optional

dotenv.load_dotenv()
import fal_client

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900
IMG_DIM = {
    "width": 600,
    "height": 600
}
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
BLUE = (0, 0, 255)
TITLE_BLUE = (0, 0, 180)

# Debug variables
DEBUG_MODE = True  # Set to True to enable additional console logging

# Check for required environment variables
if not os.getenv("FAL_KEY"):
    logging.error("Error: FAL_KEY environment variable not set")
    logging.error("Please create a .env file with your FAL_KEY")
    sys.exit(1)

# Create a log file in addition to console output
if DEBUG_MODE:
    file_handler = logging.FileHandler('story_generator_debug.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(file_handler)
    logging.debug("Debug mode enabled - Writing logs to story_generator_debug.log")

class StoryStorage:
    """
    Handles saving and loading story files that contain both text and images.
    Uses a zip-based file format with a .story extension.
    """
    def __init__(self):
        # Create a stories directory if it doesn't exist
        self.stories_dir = "stories"
        os.makedirs(self.stories_dir, exist_ok=True)
        logging.debug(f"StoryStorage initialized. Stories directory: {self.stories_dir}")
        
    def save_story(self, 
                   filename: str,
                   story_scenes: List[str],
                   generated_images: List[Optional[pygame.Surface]],
                   image_urls: List[Optional[str]],
                   prompt: str,
                   genre: str,
                   tone: str,
                   character_desc: str = "",
                   setting_desc: str = "",
                   art_style: str = "Digital Painting",
                   title: str = None) -> bool:
        """
        Save a story to a zip file containing metadata, images, and image URLs.
        
        Args:
            filename: The filename to save to (without extension)
            story_scenes: List of text scenes
            generated_images: List of pygame Surface objects containing the images
            image_urls: List of image URLs from the API
            prompt: Original user prompt
            genre: Story genre
            tone: Story tone
            character_desc: Character description (optional)
            setting_desc: Setting description (optional)
            art_style: Art style (optional)
            title: Story title (optional, defaults to prompt)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create full path with .story extension
            if not filename.endswith('.story'):
                filename = filename + '.story'
            filepath = os.path.join(self.stories_dir, filename)
            
            # Create metadata
            metadata = {
                "title": title if title else (prompt[:30] + "..." if len(prompt) > 30 else prompt),
                "prompt": prompt,
                "genre": genre,
                "tone": tone,
                "character_desc": character_desc,
                "setting_desc": setting_desc,
                "art_style": art_style,
                "num_scenes": len(story_scenes),
                "creation_date": datetime.datetime.now().isoformat(),
                "scenes": []
            }
            
            # Create scenes metadata
            for i, (scene_text, image, image_url) in enumerate(zip(story_scenes, generated_images, image_urls)):
                scene_data = {
                    "index": i,
                    "text": scene_text,
                    "image_file": f"images/scene_{i}.png" if image else None,
                    "image_url": image_url  # Store the image URL
                }
                metadata["scenes"].append(scene_data)
            
            # Create the ZIP file
            with zipfile.ZipFile(filepath, 'w') as zip_file:
                # Add metadata.json
                zip_file.writestr("metadata.json", json.dumps(metadata, indent=2))
                
                # Create images directory
                zip_file.writestr("images/", "")
                
                # Add images
                for i, image in enumerate(generated_images):
                    if image:
                        # Create an in-memory bytes buffer for the image
                        img_bytes = io.BytesIO()
                        # Save the pygame surface as PNG to the buffer
                        pygame.image.save(image, img_bytes)
                        img_bytes.seek(0)  # Reset buffer position
                        
                        # Add to zip
                        zip_file.writestr(f"images/scene_{i}.png", img_bytes.read())
            
            logging.debug(f"Story saved successfully to {filepath}")
            return True
            
        except Exception as e:
            logging.error(f"Error saving story: {str(e)}")
            return False
    
    def load_story(self, filename: str) -> Tuple[Dict[str, Any], List[str], List[Optional[pygame.Surface]]]:
        """
        Load a story from a zip file.
        
        Args:
            filename: The filename to load from (with or without extension)
            
        Returns:
            Tuple containing:
            - metadata (dict): Story metadata
            - story_scenes (list): List of scene texts
            - generated_images (list): List of pygame Surface objects
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file format is invalid
        """
        try:
            # Ensure filename has .story extension
            if not filename.endswith('.story'):
                filename = filename + '.story'
            filepath = os.path.join(self.stories_dir, filename)
            
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Story file not found: {filepath}")
            
            story_scenes = []
            generated_images = []
            metadata = {}
            
            with zipfile.ZipFile(filepath, 'r') as zip_file:
                # Extract metadata
                if "metadata.json" not in zip_file.namelist():
                    raise ValueError(f"Invalid story file: metadata.json not found")
                
                metadata = json.loads(zip_file.read("metadata.json"))
                
                # Extract scenes in order
                for scene in sorted(metadata["scenes"], key=lambda x: x["index"]):
                    # Add scene text
                    story_scenes.append(scene["text"])
                    
                    # Try to load the image - first from URL if available, then from file
                    image_url = scene.get("image_url")
                    image_file = scene.get("image_file")
                    image = None
                    
                    # Try to load from URL first
                    if image_url:
                        try:
                            logging.debug(f"Loading image from URL: {image_url}")
                            with urllib.request.urlopen(image_url) as response:
                                img_data = response.read()
                                img_stream = io.BytesIO(img_data)
                                image = pygame.image.load(img_stream)
                        except Exception as e:
                            logging.error(f"Error loading image from URL: {str(e)}")
                            # Fall back to local file
                    
                    # If URL failed or wasn't available, try local file
                    if image is None and image_file and image_file in zip_file.namelist():
                        try:
                            img_data = zip_file.read(image_file)
                            img_stream = io.BytesIO(img_data)
                            image = pygame.image.load(img_stream)
                        except Exception as e:
                            logging.error(f"Error loading image from file: {str(e)}")
                    
                    generated_images.append(image)
            
            logging.debug(f"Story loaded successfully from {filepath}")
            return metadata, story_scenes, generated_images
            
        except Exception as e:
            logging.error(f"Error loading story: {str(e)}")
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
                            stories.append(metadata)
                except Exception as e:
                    logging.error(f"Error reading story metadata from {filename}: {str(e)}")
        
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
                logging.debug(f"Story deleted: {filepath}")
                return True
            else:
                logging.warning(f"Story file not found for deletion: {filepath}")
                return False
                
        except Exception as e:
            logging.error(f"Error deleting story: {str(e)}")
            return False


class AI_Generation:
    """
    Handles all AI generation functionality - story text and images
    """
    def __init__(self, default_num_scenes=3):
        self.default_num_scenes = default_num_scenes
        self.status_callback = lambda msg: None  # Default empty callback
        self.image_status_callback = lambda idx, status: None  # Default empty callback

    def set_callbacks(self, status_callback, image_status_callback):
        """Set callbacks for status updates"""
        self.status_callback = status_callback
        self.image_status_callback = image_status_callback

    def on_queue_update(self, update, scene_index=None):
        """Callback function for FAL API queue updates"""
        if hasattr(update, 'logs') and update.logs:
            for log in update.logs:
                if scene_index is not None:
                    logging.debug(f"FAL API (Scene {scene_index+1}) update: {log.get('message', '')}")
                else:
                    logging.debug(f"FAL API update: {log.get('message', '')}")

    def generate_story_rough_sketch(self, user_prompt, genre, tone, num_scenes, user_character_desc=None, user_setting_desc=None):
        """
        PROMPT TYPE ONE:
        Generate a rough sketch of the overall story based on user preferences
        """
        try:
            self.status_callback(f"Creating a {num_scenes}-scene {genre} story sketch...")
            
            logging.debug(f"=== GENERATING STORY ROUGH SKETCH ===")
            logging.debug(f"User prompt: '{user_prompt}'")
            logging.debug(f"Genre: {genre}, Tone: {tone}, Scenes: {num_scenes}")
            
            # Construct the prompt for story sketch generation
            sketch_prompt = f"""
            Create a rough sketch for a {num_scenes}-scene {genre} story with a {tone.lower()} tone based on this idea: 
            "{user_prompt}"
            
            """
            
            # Add optional character/setting info if provided
            if user_character_desc:
                sketch_prompt += f"\nThe main character is described as: {user_character_desc}\n"
            
            if user_setting_desc:
                sketch_prompt += f"\nThe story is set in: {user_setting_desc}\n"
            
            sketch_prompt += f"""
            Your response should include:
            1. A brief story synopsis (2-3 sentences)
            2. Main plot points for a {num_scenes}-scene structure
            3. Key themes or motifs
            4. Critical story elements (items, places, events)
            
            Format your response in clear sections with headers. Keep the entire response under 400 words.
            """
            
            # Call FAL AI any-llm API with GPT-4o model
            result = fal_client.subscribe(
                "fal-ai/any-llm",
                arguments={
                    "model": "openai/gpt-4o",
                    "prompt": sketch_prompt
                },
                with_logs=True,
                on_queue_update=self.on_queue_update
            )
            
            story_sketch = result["output"]
            logging.debug(f"=== STORY SKETCH GENERATED ===\n{story_sketch[:300]}...\n")
            
            return story_sketch
            
        except Exception as e:
            logging.error(f"Error generating story sketch: {str(e)}")
            self.status_callback(f"Error generating story sketch: {str(e)}")
            return ""

    def generate_character_description(self, story_sketch, user_character_desc=None):
        """
        PROMPT TYPE TWO:
        Generate a detailed character description based on the story sketch and user input
        """
        try:
            self.status_callback("Creating detailed character profile...")
            
            logging.debug(f"=== GENERATING CHARACTER DESCRIPTION ===")
            
            # Construct the prompt for character generation
            character_prompt = f"""
            Based on the following story sketch, create a detailed description of the main character.
            
            STORY SKETCH:
            {story_sketch}
            """
            
            # Add user's character description if provided
            if user_character_desc:
                character_prompt += f"""
                ADDITIONAL CHARACTER INFORMATION FROM USER:
                {user_character_desc}
                
                Incorporate these details into your character profile.
                """
            
            character_prompt += """
            Create a comprehensive character profile including:
            
            1. PHYSICAL APPEARANCE: Age, gender, distinguishing features, style of dress, and other visual characteristics that would be important for illustration.
            
            2. PERSONALITY: Key personality traits, values, fears, desires, and quirks that define this character.
            
            3. BACKGROUND: Brief relevant backstory elements that influence the character's actions in this story.
            
            4. RELATIONSHIPS: Important connections to other characters or entities in the story.
            
            5. GROWTH ARC: How this character might change throughout the story.
            
            Format this as a clear profile that can be referenced when creating story scenes and illustrations. Be specific and visual where possible.
            """
            
            # Call FAL AI any-llm API with GPT-4o model
            result = fal_client.subscribe(
                "fal-ai/any-llm",
                arguments={
                    "model": "openai/gpt-4o",
                    "prompt": character_prompt
                },
                with_logs=True,
                on_queue_update=self.on_queue_update
            )
            
            character_description = result["output"]
            logging.debug(f"=== CHARACTER DESCRIPTION GENERATED ===\n{character_description[:300]}...\n")
            
            return character_description
            
        except Exception as e:
            logging.error(f"Error generating character description: {str(e)}")
            self.status_callback(f"Error generating character description: {str(e)}")
            return ""

    def generate_story_scenes(self, story_sketch, character_description, num_scenes):
        """
        PROMPT TYPE THREE:
        Generate detailed scenes based on the story sketch, character description, and number of scenes
        """
        try:
            self.status_callback(f"Developing {num_scenes} detailed story scenes...")
            
            logging.debug(f"=== GENERATING STORY SCENES ===")
            logging.debug(f"Number of scenes: {num_scenes}")
            
            # Construct the prompt for scene generation
            scene_prompt = f"""
            Create {num_scenes} detailed, coherent scenes for a story based on the following story sketch and character profile:
            
            STORY SKETCH:
            {story_sketch}
            
            CHARACTER PROFILE:
            {character_description}
            
            Format your response exactly as follows:
            
            SCENE 1: [Vivid, detailed description of the first scene. Make it highly visual and descriptive, focusing on the character's experience.]
            
            SCENE 2: [Vivid, detailed description of the second scene that builds from the first. Again, make it visual and incorporate character details.]
            """
            
            # Add placeholders for the remaining scenes
            for i in range(3, num_scenes + 1):
                scene_prompt += f"""
                
                SCENE {i}: [Vivid, detailed description of scene {i} that advances the story. Make it visual and ensure character continuity.]
                """
            
            scene_prompt += """
            
            Keep each scene description between 100-150 words. Make each scene visually distinctive and memorable, perfect for illustration. Ensure the character remains consistent throughout all scenes, and that the narrative builds logically from one scene to the next.
            """
            
            # Call FAL AI any-llm API with GPT-4o model
            result = fal_client.subscribe(
                "fal-ai/any-llm",
                arguments={
                    "model": "openai/gpt-4o",
                    "prompt": scene_prompt
                },
                with_logs=True,
                on_queue_update=self.on_queue_update
            )
            
            scene_text = result["output"]
            logging.debug(f"=== RAW SCENE RESPONSE ===\n{scene_text[:500]}...\n=== END RAW RESPONSE ===")
            
            # Parse scenes
            scenes = []
            current_scene = ""
            scene_started = False
            
            logging.debug(f"Starting to parse scenes from response...")
            for line in scene_text.split('\n'):
                line = line.strip()
                logging.debug(f"Parsing line: '{line[:50]}...' if longer")
                
                # Check for scene markers like "SCENE 1:" or "SCENE 1"
                if re.search(r'SCENE\s+\d+:?', line):
                    logging.debug(f"Found scene marker: '{line}'")
                    if scene_started and current_scene:
                        logging.debug(f"Adding previous scene: '{current_scene[:50]}...'")
                        scenes.append(current_scene.strip())
                    current_scene = line.split(':', 1)[1].strip() if ':' in line else ""
                    scene_started = True
                # If we're in a scene and this isn't a new scene marker, add the line to the current scene
                elif scene_started and line:
                    current_scene += " " + line
            
            # Add the last scene if there is one
            if scene_started and current_scene:
                logging.debug(f"Adding final scene: '{current_scene[:50]}...'")
                scenes.append(current_scene.strip())
            
            # Ensure we have the requested number of scenes
            while len(scenes) < num_scenes:
                logging.warning(f"Not enough scenes parsed, adding placeholder for scene {len(scenes)+1}")
                scenes.append(f"Scene {len(scenes)+1} description not available.")
            
            logging.debug(f"=== PARSED SCENES ===")
            for i, scene in enumerate(scenes[:num_scenes]):
                logging.debug(f"Scene {i+1}: {scene[:100]}...")
            
            return scenes[:num_scenes]  # Limit to requested number of scenes
            
        except Exception as e:
            logging.error(f"Error generating story scenes: {str(e)}")
            self.status_callback(f"Error generating story scenes: {str(e)}")
            return []

    def generate_image_prompt(self, scene_text, scene_index, character_description):
        """
        Use the video prompt generator to create an enhanced image prompt that includes character details
        """
        try:
            logging.debug(f"=== ENHANCING IMAGE PROMPT FOR SCENE {scene_index+1} ===")
            logging.debug(f"Scene text: {scene_text[:100]}...")
            
            # Extract key physical details from character description
            character_physical = ""
            char_desc_lines = character_description.split('\n')
            in_physical_section = False
            
            for line in char_desc_lines:
                if "PHYSICAL APPEARANCE" in line:
                    in_physical_section = True
                    continue
                elif any(section in line for section in ["PERSONALITY", "BACKGROUND", "RELATIONSHIPS", "GROWTH"]):
                    in_physical_section = False
                elif in_physical_section and line.strip():
                    character_physical += line.strip() + " "
            
            # Create a scene-specific queue update callback
            def on_queue_update_for_video_prompt(update):
                self.on_queue_update(update, scene_index)
            
            # Prepare the input concept combining scene and character details
            input_concept = f"""
            Scene description: {scene_text}
            
            Main character appearance: {character_physical}
            """
            
            # Call FAL AI video prompt generator
            result = fal_client.subscribe(
                "fal-ai/video-prompt-generator",
                arguments={
                    "input_concept": input_concept,
                    "style": "Cinematic",  # Using Cinematic style for more visual details
                    "camera_style": "Steadicam flow",  # Add camera style for more visual variety
                    "special_effects": "Practical effects",  # Add special effects for visual interest
                    "prompt_length": "Medium",  # Medium length for balance between detail and conciseness
                    "model": "google/gemini-flash-1.5"  # Using default model for speed
                },
                with_logs=True,
                on_queue_update=on_queue_update_for_video_prompt
            )
            
            enhanced_prompt = result["prompt"]
            logging.debug(f"Enhanced image prompt: {enhanced_prompt}")
            return enhanced_prompt
            
        except Exception as e:
            logging.error(f"Error enhancing image prompt, falling back to original: {str(e)}")
            return scene_text  # Fallback to original scene text

    def generate_image(self, scene_text, scene_index, character_description):
        """
        PROMPT TYPE FOUR:
        Generate an image for a scene incorporating character details
        Returns a tuple of (image_data, image_url)
        """
        try:
            self.status_callback(f"Generating image {scene_index+1}...")
            self.image_status_callback(scene_index, True)  # Mark as loading
            
            logging.debug(f"=== STARTING IMAGE GENERATION FOR SCENE {scene_index+1} ===")
            
            # Generate enhanced image prompt with character details
            image_prompt = self.generate_image_prompt(scene_text, scene_index, character_description)
            
            # Call FAL API to generate image
            try:
                logging.debug(f"Calling FAL AI FLUX with prompt: {image_prompt[:100]}...")
                logging.debug(f"Image dimensions: {IMG_DIM}")
                
                # Create a scene-specific queue update callback
                def on_queue_update_for_scene(update):
                    self.on_queue_update(update, scene_index)
                
                result = fal_client.subscribe(
                    "fal-ai/flux/schnell",
                    arguments={
                        "prompt": image_prompt,
                        "image_size": IMG_DIM,
                        "num_inference_steps": 4,
                        "seed": 42 + scene_index  # Use different seeds for variation
                    },
                    with_logs=True,
                    on_queue_update=on_queue_update_for_scene
                )
                
                logging.debug(f"FAL AI response received:")
                logging.debug(json.dumps(result, indent=2, default=str)[:500] + "...")
                
                # Process image
                if result and 'images' in result and len(result['images']) > 0:
                    image_url = result['images'][0]['url']
                    logging.debug(f"Image URL: {image_url}")
                    
                    # Download image for immediate display
                    logging.debug(f"Downloading image...")
                    with urllib.request.urlopen(image_url) as response:
                        image_data = response.read()
                    
                    # Return both the image data and the URL
                    logging.debug(f"Image {scene_index+1} successfully downloaded")
                    return (image_data, image_url)
                else:
                    logging.error(f"No images returned in the FAL AI response")
                    return (None, None)
                
            except Exception as e:
                logging.error(f"Error generating image {scene_index+1}: {str(e)}")
                self.status_callback(f"Error generating image {scene_index+1}: {str(e)}")
                return (None, None)
            
        except Exception as e:
            logging.error(f"Error in generate_image: {str(e)}")
            return (None, None)
        finally:
            self.image_status_callback(scene_index, False)  # Mark as done loading
            logging.debug(f"=== COMPLETED IMAGE GENERATION FOR SCENE {scene_index+1} ===")

    def generate_complete_story(self, user_prompt, genre, tone, num_scenes=None, user_character_desc=None, user_setting_desc=None, art_style=None):
        """
        Generate a full story with images using the four-step process
        """
        if num_scenes is None:
            num_scenes = self.default_num_scenes
        
        try:
            # Step 1: Generate the story rough sketch
            self.status_callback("Step 1/4: Creating story outline...")
            story_sketch = self.generate_story_rough_sketch(
                user_prompt, 
                genre, 
                tone, 
                num_scenes, 
                user_character_desc, 
                user_setting_desc
            )
            
            if not story_sketch:
                return [], [], []
            
            # Step 2: Generate detailed character description
            self.status_callback("Step 2/4: Developing character profile...")
            character_description = self.generate_character_description(
                story_sketch, 
                user_character_desc
            )
            
            if not character_description:
                return [], [], []
            
            # Step 3: Generate story scenes
            self.status_callback("Step 3/4: Creating story scenes...")
            story_scenes = self.generate_story_scenes(
                story_sketch, 
                character_description, 
                num_scenes
            )
            
            if not story_scenes:
                return [], [], []
            
            # Step 4: Generate images for each scene
            self.status_callback("Step 4/4: Illustrating scenes...")
            image_data_list = [None] * len(story_scenes)
            image_url_list = [None] * len(story_scenes)
            
            for i, scene in enumerate(story_scenes):
                image_result = self.generate_image(scene, i, character_description)
                if image_result:
                    image_data, image_url = image_result
                    image_data_list[i] = image_data
                    image_url_list[i] = image_url
            
            logging.debug(f"=== STORY AND IMAGE GENERATION COMPLETE ===")
            self.status_callback("Story and images generated successfully!")
            
            return story_scenes, image_data_list, image_url_list
            
        except Exception as e:
            logging.error(f"Error generating complete story: {str(e)}")
            self.status_callback(f"Error generating story: {str(e)}")
            return [], [], []

class UI:
    """Handles all UI components and user interaction"""
    def __init__(self, num_scenes=3):
        # Initialize pygame
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Picture Story Generator")
        
        # Set window icon if available
        try:
            icon = pygame.Surface((32, 32))
            icon.fill((0, 120, 255))
            pygame.display.set_icon(icon)
        except:
            logging.debug("Could not set window icon")
        
        # Fonts - reduced sizes for better fit
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 18)
        self.input_font = pygame.font.SysFont('Arial', 20)
        
        # Initial number of scenes
        self.num_scenes = num_scenes
        
        # Story data
        self.story_prompt = ""
        self.genre = "Fantasy"
        self.tone = "Lighthearted"
        self.character_desc = ""
        self.setting_desc = ""
        self.art_style = "Digital Painting"
        self.story_scenes = []
        self.generated_images = []
        self.image_url_list = []  # Store the image URLs
        self.current_page = 0
        
        # State tracking
        self.state = "start_menu"  # States: start_menu, input, generating, viewing
        self.input_text = ""
        self.status_message = ""
        self.image_loading = []
        
        # Input boxes
        self.input_box = pygame.Rect((SCREEN_WIDTH - 800)//2, 200, 800, 60)
        self.character_box = pygame.Rect((SCREEN_WIDTH - 800)//2, 300, 800, 60)
        self.setting_box = pygame.Rect((SCREEN_WIDTH - 800)//2, 400, 800, 60)
        self.scenes_input_box = pygame.Rect((SCREEN_WIDTH - 200)//2, 470, 200, 40)
        self.active_input = "prompt"  # Which input is active: "prompt", "character", "setting", "scenes"
        
        # Genre buttons (placeholder - would need to be implemented for full UI)
        self.genre_buttons = {
            "Fantasy": pygame.Rect(100, 250, 150, 40),
            "Sci-Fi": pygame.Rect(260, 250, 150, 40),
            "Mystery": pygame.Rect(420, 250, 150, 40),
            "Adventure": pygame.Rect(580, 250, 150, 40),
            "Romance": pygame.Rect(740, 250, 150, 40),
            "Horror": pygame.Rect(900, 250, 150, 40)
        }
        self.selected_genre = "Fantasy"
        
        # Generate button
        self.generate_button = pygame.Rect(SCREEN_WIDTH//2 - 150, 520, 300, 60)
        
        # For threading
        self.thread = None
        self.lock = threading.Lock()
        
        # Create the AI generation manager
        self.ai_generator = AI_Generation(default_num_scenes=num_scenes)
        
        # Set up callbacks
        self.ai_generator.set_callbacks(
            status_callback=self.update_status,
            image_status_callback=self.update_image_status
        )
        
        # Add story storage
        self.story_storage = StoryStorage()
        
        # State tracking for file operations
        self.show_file_dialog = False
        self.file_dialog_mode = None  # "save" or "load"
        self.file_input = ""
        self.file_list = []
        self.selected_file_index = -1
        
        # Start menu buttons
        self.new_story_button = pygame.Rect(SCREEN_WIDTH//2 - 200, 350, 400, 80)
        self.load_story_button = pygame.Rect(SCREEN_WIDTH//2 - 200, 450, 400, 80)

    # ----- Callback Methods -----
    
    def update_status(self, message):
        """Callback method to update the status message from AI generation"""
        with self.lock:
            self.status_message = message
            logging.debug(f"Status update: {message}")

    def update_image_status(self, index, is_loading):
        """Callback method to update image loading status"""
        with self.lock:
            # Make sure the image_loading list is long enough
            while len(self.image_loading) <= index:
                self.image_loading.append(False)
            self.image_loading[index] = is_loading
            logging.debug(f"Image {index+1} loading status: {is_loading}")
    
    # ----- Drawing Methods -----
    
    def draw_start_menu(self):
        """Draw the initial start menu with options to create new story or load existing one"""
        self.screen.fill(WHITE)
        
        # Title
        title_surface = self.title_font.render("Picture Story Generator", True, TITLE_BLUE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(title_surface, title_rect)
        
        # Subtitle
        subtitle_surface = self.text_font.render("Create illustrated stories with AI", True, BLACK)
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(subtitle_surface, subtitle_rect)
        
        # New Story button
        pygame.draw.rect(self.screen, BLUE, self.new_story_button)
        new_story_text = self.title_font.render("Create New Story", True, WHITE)
        new_story_rect = new_story_text.get_rect(center=self.new_story_button.center)
        self.screen.blit(new_story_text, new_story_rect)
        
        # Load Story button
        pygame.draw.rect(self.screen, BLUE, self.load_story_button)
        load_story_text = self.title_font.render("Load Existing Story", True, WHITE)
        load_story_rect = load_story_text.get_rect(center=self.load_story_button.center)
        self.screen.blit(load_story_text, load_story_rect)
        
        # Version info
        version_text = self.text_font.render("v1.0", True, DARK_GRAY)
        version_rect = version_text.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))
        self.screen.blit(version_text, version_rect)
        
        # Check if there are any saved stories
        num_stories = len(self.story_storage.list_saved_stories())
        if num_stories > 0:
            saved_stories_text = self.text_font.render(f"{num_stories} saved stories available", True, DARK_GRAY)
            saved_stories_rect = saved_stories_text.get_rect(center=(SCREEN_WIDTH//2, self.load_story_button.bottom + 30))
            self.screen.blit(saved_stories_text, saved_stories_rect)

    def draw_input_screen(self):
        """Draw the initial input screen for story parameters"""
        self.screen.fill(WHITE)
        
        # Title - moved up
        title_surface = self.title_font.render("Picture Story Generator", True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, 60))
        self.screen.blit(title_surface, title_rect)
        
        # Instructions - more compact
        instructions = [
            "Enter your story idea below",
            f"The app will generate a {self.num_scenes}-scene story with images."
        ]
        
        for i, instruction in enumerate(instructions):
            text_surface = self.text_font.render(instruction, True, BLACK)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, 100 + i*25))
            self.screen.blit(text_surface, text_rect)
        
        # Vertical starting position - moved up
        start_y = 150
        spacing = 70  # Reduced spacing between elements
        
        # Prompt input - repositioned
        prompt_y = start_y
        prompt_label = self.text_font.render("Story Idea:", True, BLACK)
        self.input_box = pygame.Rect((SCREEN_WIDTH - 800)//2, prompt_y, 800, 50)
        prompt_label_rect = prompt_label.get_rect(midright=(self.input_box.x - 10, self.input_box.y + self.input_box.height//2))
        self.screen.blit(prompt_label, prompt_label_rect)
        
        pygame.draw.rect(self.screen, GRAY if self.active_input == "prompt" else DARK_GRAY, self.input_box, 2)
        text_surface = self.input_font.render(self.input_text, True, BLACK)
        text_rect = text_surface.get_rect(midleft=(self.input_box.x + 10, self.input_box.y + self.input_box.height//2))
        self.screen.blit(text_surface, text_rect)
        
        # Character input - repositioned
        char_y = prompt_y + spacing
        char_label = self.text_font.render("Character (Optional):", True, BLACK)
        self.character_box = pygame.Rect((SCREEN_WIDTH - 800)//2, char_y, 800, 50)
        char_label_rect = char_label.get_rect(midright=(self.character_box.x - 10, self.character_box.y + self.character_box.height//2))
        self.screen.blit(char_label, char_label_rect)
        
        pygame.draw.rect(self.screen, GRAY if self.active_input == "character" else DARK_GRAY, self.character_box, 2)
        char_surface = self.input_font.render(self.character_desc, True, BLACK)
        char_rect = char_surface.get_rect(midleft=(self.character_box.x + 10, self.character_box.y + self.character_box.height//2))
        self.screen.blit(char_surface, char_rect)
        
        # Setting input - repositioned (moved before genre/tone/style)
        setting_y = char_y + spacing
        setting_label = self.text_font.render("Setting (Optional):", True, BLACK)
        self.setting_box = pygame.Rect((SCREEN_WIDTH - 800)//2, setting_y, 800, 50)
        setting_label_rect = setting_label.get_rect(midright=(self.setting_box.x - 10, self.setting_box.y + self.setting_box.height//2))
        self.screen.blit(setting_label, setting_label_rect)
        
        pygame.draw.rect(self.screen, GRAY if self.active_input == "setting" else DARK_GRAY, self.setting_box, 2)
        setting_surface = self.input_font.render(self.setting_desc, True, BLACK)
        setting_rect = setting_surface.get_rect(midleft=(self.setting_box.x + 10, self.setting_box.y + self.setting_box.height//2))
        self.screen.blit(setting_surface, setting_rect)
        
        # Genre, Tone, Art Style - moved after Setting and better aligned
        info_y = setting_y + spacing
        info_x = (SCREEN_WIDTH - 800)//2  # Left-aligned with the input boxes
        label_width = 120  # Fixed width for labels
        value_x = info_x + label_width + 10  # Position for the values
        
        # Genre selection - left-aligned with input boxes
        genre_label = self.text_font.render("Selected Genre:", True, BLACK)
        genre_label_rect = genre_label.get_rect(left=info_x, centery=info_y)
        self.screen.blit(genre_label, genre_label_rect)
        
        genre_value = self.text_font.render(self.genre, True, BLUE)
        genre_value_rect = genre_value.get_rect(left=value_x, centery=info_y)
        self.screen.blit(genre_value, genre_value_rect)
        
        # Tone selection - left-aligned with input boxes
        tone_y = info_y + 30
        tone_label = self.text_font.render("Story Tone:", True, BLACK)
        tone_label_rect = tone_label.get_rect(left=info_x, centery=tone_y)
        self.screen.blit(tone_label, tone_label_rect)
        
        tone_value = self.text_font.render(self.tone, True, BLUE)
        tone_value_rect = tone_value.get_rect(left=value_x, centery=tone_y)
        self.screen.blit(tone_value, tone_value_rect)
        
        # Art style selection - left-aligned with input boxes
        art_y = tone_y + 30
        art_label = self.text_font.render("Art Style:", True, BLACK)
        art_label_rect = art_label.get_rect(left=info_x, centery=art_y)
        self.screen.blit(art_label, art_label_rect)
        
        art_value = self.text_font.render(self.art_style, True, BLUE)
        art_value_rect = art_value.get_rect(left=value_x, centery=art_y)
        self.screen.blit(art_value, art_value_rect)
        
        # Scenes Input - repositioned
        scenes_y = art_y + 50
        scenes_label = self.text_font.render("Number of scenes:", True, BLACK)
        self.scenes_input_box = pygame.Rect(value_x, scenes_y - 20, 100, 40)
        scenes_label_rect = scenes_label.get_rect(left=info_x, centery=scenes_y)
        self.screen.blit(scenes_label, scenes_label_rect)
        
        pygame.draw.rect(self.screen, GRAY if self.active_input == "scenes" else DARK_GRAY, self.scenes_input_box, 2)
        scenes_text = self.text_font.render(str(self.num_scenes), True, BLACK)
        scenes_text_rect = scenes_text.get_rect(center=self.scenes_input_box.center)
        self.screen.blit(scenes_text, scenes_text_rect)
        
        # Generate button - moved down
        button_y = scenes_y + 70
        self.generate_button = pygame.Rect(SCREEN_WIDTH//2 - 150, button_y, 300, 50)
        pygame.draw.rect(self.screen, BLUE, self.generate_button)
        button_text = self.text_font.render("Generate Story", True, WHITE)
        button_rect = button_text.get_rect(center=self.generate_button.center)
        self.screen.blit(button_text, button_rect)
        
        # Back button (to return to start menu)
        back_button = pygame.Rect(50, 50, 100, 40)
        pygame.draw.rect(self.screen, GRAY, back_button)
        back_text = self.text_font.render("Back", True, BLACK)
        back_text_rect = back_text.get_rect(center=back_button.center)
        self.screen.blit(back_text, back_text_rect)
        
        # Status message
        if self.status_message:
            status_surface = self.text_font.render(self.status_message, True, BLACK)
            status_rect = status_surface.get_rect(center=(SCREEN_WIDTH//2, button_y + 70))
            self.screen.blit(status_surface, status_rect)

    def draw_generating_screen(self):
        """Draw the loading screen while generating the story"""
        self.screen.fill(WHITE)
        
        # Title
        title_surface = self.title_font.render("Generating Your Story...", True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(title_surface, title_rect)
        
        # Status message
        if self.status_message:
            status_surface = self.text_font.render(self.status_message, True, BLACK)
            status_rect = status_surface.get_rect(center=(SCREEN_WIDTH//2, 180))
            self.screen.blit(status_surface, status_rect)
        
        # Loading indicators for images - more compact layout
        indicator_width = 60
        indicator_height = 60
        indicator_spacing = 90
        
        # Calculate total width needed for all indicators
        total_width = len(self.image_loading) * indicator_spacing
        start_x = (SCREEN_WIDTH - total_width) // 2 + indicator_spacing // 2
        
        for i in range(len(self.image_loading)):
            color = BLUE if i < len(self.image_loading) and self.image_loading[i] else GRAY
            indicator_x = start_x + i * indicator_spacing
            indicator_rect = pygame.Rect(indicator_x - indicator_width//2, 300, indicator_width, indicator_height)
            pygame.draw.rect(self.screen, color, indicator_rect)
            text = self.text_font.render(f"Image {i+1}", True, BLACK)
            text_rect = text.get_rect(center=(indicator_x, 380))
            self.screen.blit(text, text_rect)

    def draw_story_page(self):
        """Draw the story viewing screen"""
        self.screen.fill(WHITE)
        
        if 0 <= self.current_page < len(self.story_scenes):
            # Display image - slightly smaller
            img_display_width = IMG_DIM["width"] - 50
            img_display_height = IMG_DIM["height"] - 50
            
            if self.current_page < len(self.generated_images) and self.generated_images[self.current_page]:
                image = self.generated_images[self.current_page]
                # Scale to display size
                image = pygame.transform.scale(image, (img_display_width, img_display_height))
                image_rect = image.get_rect()
                image_rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//3 - 30)  # Moved up
                self.screen.blit(image, image_rect)
            else:
                # Placeholder for image - smaller and moved up
                pygame.draw.rect(self.screen, GRAY, (SCREEN_WIDTH//2 - img_display_width//2, 
                                                   SCREEN_HEIGHT//3 - 30 - img_display_height//2, 
                                                   img_display_width, img_display_height))
            
            # Display scene text
            scene_text = self.story_scenes[self.current_page]
            
            # Display scene number - moved to top
            scene_label = self.title_font.render(f"Scene {self.current_page + 1}", True, TITLE_BLUE)
            scene_label_rect = scene_label.get_rect(center=(SCREEN_WIDTH//2, 20))
            self.screen.blit(scene_label, scene_label_rect)
            
            # Calculate text area - moved up and expanded
            text_area_width = SCREEN_WIDTH - 100
            text_area_top = SCREEN_HEIGHT//2 + 70  # Moved up
            
            # Wrap text
            wrapped_text = []
            words = scene_text.split()
            line = ""
            for word in words:
                test_line = line + word + " "
                text_width = self.text_font.size(test_line)[0]
                if text_width < text_area_width:
                    line = test_line
                else:
                    wrapped_text.append(line)
                    line = word + " "
            wrapped_text.append(line)
            
            # Render wrapped text - smaller line spacing
            text_y_start = text_area_top
            line_spacing = 25  # Reduced from 32
            for i, line in enumerate(wrapped_text):
                text_surface = self.text_font.render(line, True, BLACK)
                text_rect = text_surface.get_rect()
                text_rect.left = 50
                text_rect.top = text_y_start + i * line_spacing
                self.screen.blit(text_surface, text_rect)
        
        # Navigation controls - moved up
        button_y = SCREEN_HEIGHT - 60
        
        # Save button
        save_button = pygame.Rect(80, button_y - 50, 130, 40)
        pygame.draw.rect(self.screen, BLUE, save_button)
        save_text = self.text_font.render("Save Story", True, WHITE)
        save_text_rect = save_text.get_rect(center=save_button.center)
        self.screen.blit(save_text, save_text_rect)
        
        # Load button
        load_button = pygame.Rect(SCREEN_WIDTH - 210, button_y - 50, 130, 40)
        pygame.draw.rect(self.screen, BLUE, load_button)
        load_text = self.text_font.render("Load Story", True, WHITE)
        load_text_rect = load_text.get_rect(center=load_button.center)
        self.screen.blit(load_text, load_text_rect)
        
        # Previous button
        prev_button = pygame.Rect(80, button_y, 130, 40)
        pygame.draw.rect(self.screen, BLUE if self.current_page > 0 else DARK_GRAY, prev_button)
        prev_text = self.text_font.render("Previous", True, WHITE)
        prev_text_rect = prev_text.get_rect(center=prev_button.center)
        self.screen.blit(prev_text, prev_text_rect)
        
        # Next button
        next_button = pygame.Rect(SCREEN_WIDTH - 210, button_y, 130, 40)
        pygame.draw.rect(self.screen, BLUE if self.current_page < len(self.story_scenes) - 1 else DARK_GRAY, next_button)
        next_text = self.text_font.render("Next", True, WHITE)
        next_text_rect = next_text.get_rect(center=next_button.center)
        self.screen.blit(next_text, next_text_rect)
        
        # Page indicator
        page_text = self.text_font.render(f"Page {self.current_page + 1} of {len(self.story_scenes)}", True, BLACK)
        page_text_rect = page_text.get_rect(center=(SCREEN_WIDTH//2, button_y - 25))
        self.screen.blit(page_text, page_text_rect)
        
        # New story button
        new_story_button = pygame.Rect(SCREEN_WIDTH//2 - 100, button_y, 200, 40)
        pygame.draw.rect(self.screen, GRAY, new_story_button)
        new_story_text = self.text_font.render("New Story", True, BLACK)
        new_story_text_rect = new_story_text.get_rect(center=new_story_button.center)
        self.screen.blit(new_story_text, new_story_text_rect)
        
        # Back to main menu button
        main_menu_button = pygame.Rect(SCREEN_WIDTH//2 - 100, button_y - 100, 200, 40)
        pygame.draw.rect(self.screen, GRAY, main_menu_button)
        main_menu_text = self.text_font.render("Main Menu", True, BLACK)
        main_menu_text_rect = main_menu_text.get_rect(center=main_menu_button.center)
        self.screen.blit(main_menu_text, main_menu_text_rect)

    def draw_file_dialog(self):
        """Draw a dialog for saving/loading files"""
        # Darken the background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # Dialog box
        dialog_width = 600
        dialog_height = 500
        dialog_x = (SCREEN_WIDTH - dialog_width) // 2
        dialog_y = (SCREEN_HEIGHT - dialog_height) // 2
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        pygame.draw.rect(self.screen, WHITE, dialog_rect)
        pygame.draw.rect(self.screen, BLACK, dialog_rect, 2)
        
        # Title
        title_text = "Save Story" if self.file_dialog_mode == "save" else "Load Story"
        title_surface = self.title_font.render(title_text, True, BLACK)
        title_rect = title_surface.get_rect(centerx=dialog_x + dialog_width//2, top=dialog_y + 20)
        self.screen.blit(title_surface, title_rect)
        
        if self.file_dialog_mode == "save":
            # Input field for filename
            input_label = self.text_font.render("Enter filename:", True, BLACK)
            input_label_rect = input_label.get_rect(left=dialog_x + 30, top=dialog_y + 80)
            self.screen.blit(input_label, input_label_rect)
            
            input_box = pygame.Rect(dialog_x + 30, dialog_y + 110, dialog_width - 60, 40)
            pygame.draw.rect(self.screen, GRAY, input_box, 2)
            input_text = self.input_font.render(self.file_input, True, BLACK)
            self.screen.blit(input_text, (input_box.x + 10, input_box.y + 10))
        
        # File list (for both save and load)
        list_label = self.text_font.render("Saved Stories:", True, BLACK)
        list_label_rect = list_label.get_rect(left=dialog_x + 30, top=dialog_y + (170 if self.file_dialog_mode == "save" else 80))
        self.screen.blit(list_label, list_label_rect)
        
        list_box = pygame.Rect(dialog_x + 30, list_label_rect.bottom + 10, dialog_width - 60, 250)
        pygame.draw.rect(self.screen, GRAY, list_box, 1)
        
        # Draw file items
        item_height = 30
        for i, file_info in enumerate(self.file_list):
            item_rect = pygame.Rect(list_box.left, list_box.top + i*item_height, list_box.width, item_height)
            
            # Highlight selected item
            if i == self.selected_file_index:
                pygame.draw.rect(self.screen, (200, 220, 255), item_rect)
            
            # Draw separator line
            pygame.draw.line(self.screen, GRAY, (item_rect.left, item_rect.bottom), (item_rect.right, item_rect.bottom), 1)
            
            # Draw file info
            title = file_info.get("title", "Untitled")
            date = file_info.get("creation_date", "").split("T")[0] if "creation_date" in file_info else ""
            scenes = file_info.get("num_scenes", 0)
            file_text = f"{title} - {date} ({scenes} scenes)"
            
            text_surface = self.text_font.render(file_text, True, BLACK)
            self.screen.blit(text_surface, (item_rect.left + 10, item_rect.top + 5))
        
        # Action buttons
        button_y = dialog_y + dialog_height - 60
        
        # Cancel button
        cancel_button = pygame.Rect(dialog_x + 30, button_y, 150, 40)
        pygame.draw.rect(self.screen, GRAY, cancel_button)
        cancel_text = self.text_font.render("Cancel", True, BLACK)
        cancel_text_rect = cancel_text.get_rect(center=cancel_button.center)
        self.screen.blit(cancel_text, cancel_text_rect)
        
        # Save/Load button
        action_button = pygame.Rect(dialog_x + dialog_width - 180, button_y, 150, 40)
        action_text = "Save" if self.file_dialog_mode == "save" else "Load"
        
        # Determine if button should be active
        button_active = (self.file_dialog_mode == "save" and self.file_input.strip()) or \
                        (self.file_dialog_mode == "load" and self.selected_file_index >= 0)
        
        pygame.draw.rect(self.screen, BLUE if button_active else DARK_GRAY, action_button)
        action_text_surface = self.text_font.render(action_text, True, WHITE)
        action_text_rect = action_text_surface.get_rect(center=action_button.center)
        self.screen.blit(action_text_surface, action_text_rect)
        
        # Delete button (only for load dialog)
        if self.file_dialog_mode == "load" and self.selected_file_index >= 0:
            delete_button = pygame.Rect(dialog_x + dialog_width//2 - 75, button_y, 150, 40)
            pygame.draw.rect(self.screen, (200, 0, 0), delete_button)
            delete_text = self.text_font.render("Delete", True, WHITE)
            delete_text_rect = delete_text.get_rect(center=delete_button.center)
            self.screen.blit(delete_text, delete_text_rect)

    # ----- Event Handling Methods -----
    
    def handle_start_menu_events(self, event):
        """Handle events for the start menu screen"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the "Create New Story" button is clicked
            if self.new_story_button.collidepoint(event.pos):
                self.state = "input"
                self.input_text = ""
                self.character_desc = ""
                self.setting_desc = ""
                self.num_scenes = 3
                logging.debug("Starting new story from main menu")
            
            # Check if the "Load Existing Story" button is clicked
            elif self.load_story_button.collidepoint(event.pos):
                self.show_load_dialog()
                logging.debug("Opening load dialog from main menu")
    
    def handle_input_events(self, event):
        """Handle events for the input screen"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if back button was clicked
            back_button = pygame.Rect(50, 50, 100, 40)
            if back_button.collidepoint(event.pos):
                self.state = "start_menu"
                return
            
            # Check if the prompt input box is clicked
            if self.input_box.collidepoint(event.pos):
                self.active_input = "prompt"
            
            # Check if the character input box is clicked
            elif self.character_box.collidepoint(event.pos):
                self.active_input = "character"
            
            # Check if the setting input box is clicked
            elif self.setting_box.collidepoint(event.pos):
                self.active_input = "setting"
            
            # Check if the scenes input box is clicked
            elif self.scenes_input_box.collidepoint(event.pos):
                self.active_input = "scenes"
            
            # Check if generate button is clicked
            elif self.generate_button.collidepoint(event.pos) and self.input_text.strip():
                try:
                    # Make sure num_scenes is a valid number
                    num = int(self.num_scenes)
                    if num < 1:
                        self.num_scenes = 1
                    elif num > 10:  # Set a reasonable maximum
                        self.num_scenes = 10
                except ValueError:
                    self.num_scenes = 3  # Default to 3 if invalid
                
                self.start_generation()
        
        elif event.type == pygame.KEYDOWN:
            if self.active_input == "prompt":
                if event.key == pygame.K_RETURN and self.input_text.strip():
                    self.start_generation()
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                elif event.key == pygame.K_TAB:
                    self.active_input = "character"
                else:
                    self.input_text += event.unicode
            
            elif self.active_input == "character":
                if event.key == pygame.K_RETURN and self.input_text.strip():
                    self.start_generation()
                elif event.key == pygame.K_BACKSPACE:
                    self.character_desc = self.character_desc[:-1]
                elif event.key == pygame.K_TAB:
                    self.active_input = "setting"
                else:
                    self.character_desc += event.unicode
            
            elif self.active_input == "setting":
                if event.key == pygame.K_RETURN and self.input_text.strip():
                    self.start_generation()
                elif event.key == pygame.K_BACKSPACE:
                    self.setting_desc = self.setting_desc[:-1]
                elif event.key == pygame.K_TAB:
                    self.active_input = "scenes"
                else:
                    self.setting_desc += event.unicode
            
            elif self.active_input == "scenes":
                if event.key == pygame.K_RETURN and self.input_text.strip():
                    self.start_generation()
                elif event.key == pygame.K_BACKSPACE:
                    self.num_scenes = str(self.num_scenes)[:-1] or "3"  # Default to 3 if empty
                elif event.key == pygame.K_TAB:
                    self.active_input = "prompt"
                elif event.unicode.isdigit():
                    new_value = str(self.num_scenes) + event.unicode if isinstance(self.num_scenes, int) else event.unicode
                    try:
                        num = int(new_value)
                        if 1 <= num <= 10:  # Set a reasonable range
                            self.num_scenes = num
                    except ValueError:
                        pass  # Ignore if not a valid number

    def handle_viewing_events(self, event):
        """Handle events for the story viewing screen"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Previous button - updated coordinates
            prev_button = pygame.Rect(80, SCREEN_HEIGHT - 60, 130, 40)
            if prev_button.collidepoint(event.pos) and self.current_page > 0:
                self.current_page -= 1
                logging.debug(f"Navigation: Moving to page {self.current_page + 1}")
            
            # Next button - updated coordinates
            next_button = pygame.Rect(SCREEN_WIDTH - 210, SCREEN_HEIGHT - 60, 130, 40)
            if next_button.collidepoint(event.pos) and self.current_page < len(self.story_scenes) - 1:
                self.current_page += 1
                logging.debug(f"Navigation: Moving to page {self.current_page + 1}")
            
            # New story button - updated coordinates
            new_story_button = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 60, 200, 40)
            if new_story_button.collidepoint(event.pos):
                logging.debug(f"=== STARTING NEW STORY ===")
                self.state = "input"
                self.input_text = ""
                self.character_desc = ""
                self.setting_desc = ""
                self.story_scenes = []
                self.generated_images = []
                self.current_page = 0
                self.status_message = ""
                self.image_loading = []
            
            # Main menu button
            main_menu_button = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 110, 200, 40)
            if main_menu_button.collidepoint(event.pos):
                logging.debug("Returning to main menu")
                self.state = "start_menu"
                return
            
            # Save button
            save_button = pygame.Rect(80, SCREEN_HEIGHT - 110, 130, 40)
            if save_button.collidepoint(event.pos):
                self.show_save_dialog()
                return
            
            # Load button
            load_button = pygame.Rect(SCREEN_WIDTH - 210, SCREEN_HEIGHT - 110, 130, 40)
            if load_button.collidepoint(event.pos):
                self.show_load_dialog()
                return

    def handle_file_dialog_events(self, event):
        """Handle events for the file dialog"""
        dialog_width = 600
        dialog_height = 500
        dialog_x = (SCREEN_WIDTH - dialog_width) // 2
        dialog_y = (SCREEN_HEIGHT - dialog_height) // 2
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if clicked outside the dialog (close it)
            dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
            if not dialog_rect.collidepoint(event.pos):
                self.show_file_dialog = False
                return
            
            # Check for input box click (save mode)
            if self.file_dialog_mode == "save":
                input_box = pygame.Rect(dialog_x + 30, dialog_y + 110, dialog_width - 60, 40)
                if input_box.collidepoint(event.pos):
                    # Activate input box
                    self.active_input = "file"
                    return
            
            # Check for file list click
            list_box = pygame.Rect(dialog_x + 30, 
                                  dialog_y + (190 if self.file_dialog_mode == "save" else 100), 
                                  dialog_width - 60, 250)
            if list_box.collidepoint(event.pos) and self.file_list:
                # Calculate which item was clicked
                item_height = 30
                item_index = (event.pos[1] - list_box.top) // item_height
                if 0 <= item_index < len(self.file_list):
                    self.selected_file_index = item_index
                    # In save mode, also set the filename
                    if self.file_dialog_mode == "save":
                        self.file_input = self.file_list[item_index].get("filename", "").replace(".story", "")
                return
            
            # Check for cancel button
            cancel_button = pygame.Rect(dialog_x + 30, dialog_y + dialog_height - 60, 150, 40)
            if cancel_button.collidepoint(event.pos):
                self.show_file_dialog = False
                return
            
            # Check for action button (save/load)
            action_button = pygame.Rect(dialog_x + dialog_width - 180, dialog_y + dialog_height - 60, 150, 40)
            button_active = (self.file_dialog_mode == "save" and self.file_input.strip()) or \
                            (self.file_dialog_mode == "load" and self.selected_file_index >= 0)
            
            if action_button.collidepoint(event.pos) and button_active:
                if self.file_dialog_mode == "save":
                    self.save_current_story()
                else:  # load
                    self.load_selected_story()
                self.show_file_dialog = False
                return
            
            # Check for delete button (load mode)
            if self.file_dialog_mode == "load" and self.selected_file_index >= 0:
                delete_button = pygame.Rect(dialog_x + dialog_width//2 - 75, dialog_y + dialog_height - 60, 150, 40)
                if delete_button.collidepoint(event.pos):
                    self.delete_selected_story()
                    return
        
        elif event.type == pygame.KEYDOWN:
            if self.file_dialog_mode == "save" and self.active_input == "file":
                if event.key == pygame.K_RETURN and self.file_input.strip():
                    self.save_current_story()
                    self.show_file_dialog = False
                elif event.key == pygame.K_BACKSPACE:
                    self.file_input = self.file_input[:-1]
                elif event.key == pygame.K_ESCAPE:
                    self.show_file_dialog = False
                else:
                    # Filter for valid filename characters
                    valid_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_ "
                    if event.unicode in valid_chars:
                        self.file_input += event.unicode
            elif event.key == pygame.K_ESCAPE:
                self.show_file_dialog = False

    # ----- File Operation Methods -----
    
    def show_save_dialog(self):
        """Show the save dialog"""
        self.show_file_dialog = True
        self.file_dialog_mode = "save"
        self.file_input = ""
        self.file_list = self.story_storage.list_saved_stories()
        self.selected_file_index = -1
        self.active_input = "file"  # Set active input to file input
    
    def show_load_dialog(self):
        """Show the load dialog"""
        self.show_file_dialog = True
        self.file_dialog_mode = "load"
        self.file_input = ""
        self.file_list = self.story_storage.list_saved_stories()
        self.selected_file_index = -1
    
    def save_current_story(self):
        """Save the current story"""
        try:
            if not self.story_scenes:
                self.status_message = "No story to save!"
                return False
            
            filename = self.file_input.strip()
            if not filename:
                filename = "Untitled Story"
            
            success = self.story_storage.save_story(
                filename=filename,
                story_scenes=self.story_scenes,
                generated_images=self.generated_images,
                image_urls=self.image_url_list,  # Include the image URLs
                prompt=self.story_prompt,
                genre=self.genre,
                tone=self.tone,
                character_desc=self.character_desc,
                setting_desc=self.setting_desc,
                art_style=self.art_style
            )
            
            if success:
                self.status_message = f"Story saved as '{filename}'"
                logging.debug(f"Story saved: {filename}")
                return True
            else:
                self.status_message = "Error saving story!"
                return False
                
        except Exception as e:
            self.status_message = f"Error saving: {str(e)}"
            logging.error(f"Error in save_current_story: {str(e)}")
            return False
    
    def load_selected_story(self):
        """Load the selected story"""
        try:
            if self.selected_file_index < 0 or self.selected_file_index >= len(self.file_list):
                self.status_message = "No story selected!"
                return False
            
            filename = self.file_list[self.selected_file_index].get("filename")
            if not filename:
                self.status_message = "Invalid story file!"
                return False
            
            try:
                metadata, story_scenes, generated_images = self.story_storage.load_story(filename)
                
                # Update UI with loaded story
                self.story_scenes = story_scenes
                self.generated_images = generated_images
                self.story_prompt = metadata.get("prompt", "")
                self.genre = metadata.get("genre", "Fantasy")
                self.tone = metadata.get("tone", "Lighthearted")
                self.character_desc = metadata.get("character_desc", "")
                self.setting_desc = metadata.get("setting_desc", "")
                self.art_style = metadata.get("art_style", "Digital Painting")
                self.num_scenes = len(story_scenes)
                
                # Extract image URLs if available
                self.image_url_list = []
                for scene in metadata.get("scenes", []):
                    self.image_url_list.append(scene.get("image_url"))
                
                # Make sure we have the right number of URL slots
                while len(self.image_url_list) < len(story_scenes):
                    self.image_url_list.append(None)
                
                self.state = "viewing"
                self.current_page = 0
                self.status_message = f"Story '{metadata.get('title', 'Untitled')}' loaded!"
                
                logging.debug(f"Story loaded: {filename}")
                return True
                
            except Exception as e:
                self.status_message = f"Error loading story: {str(e)}"
                logging.error(f"Error loading story: {str(e)}")
                return False
                
        except Exception as e:
            self.status_message = f"Error: {str(e)}"
            logging.error(f"Error in load_selected_story: {str(e)}")
            return False
    
    def delete_selected_story(self):
        """Delete the selected story"""
        try:
            if self.selected_file_index < 0 or self.selected_file_index >= len(self.file_list):
                return
            
            filename = self.file_list[self.selected_file_index].get("filename")
            if not filename:
                return
            
            success = self.story_storage.delete_story(filename)
            if success:
                # Refresh the file list
                self.file_list = self.story_storage.list_saved_stories()
                self.selected_file_index = -1
                
        except Exception as e:
            logging.error(f"Error in delete_selected_story: {str(e)}")

    # ----- Story Generation Methods -----
    
    def start_generation(self):
        """Start the story generation process in a separate thread"""
        self.story_prompt = self.input_text
        logging.debug(f"=== GENERATION STARTED ===")
        logging.debug(f"User prompt: '{self.story_prompt}'")
        logging.debug(f"Genre: {self.genre}, Tone: {self.tone}")
        logging.debug(f"Character: '{self.character_desc}'")
        logging.debug(f"Setting: '{self.setting_desc}'")
        logging.debug(f"Number of scenes: {self.num_scenes}")
        
        self.state = "generating"
        self.status_message = "Starting generation..."
        self.image_loading = [False] * self.num_scenes
        
        # Start generation in a separate thread
        self.thread = threading.Thread(target=self.generate_story_thread)
        self.thread.daemon = True
        self.thread.start()

    def generate_story_thread(self):
        """Thread function to generate story and images"""
        try:
            # Call the AI generator to generate the complete story
            story_scenes, image_data_list, image_url_list = self.ai_generator.generate_complete_story(
                self.story_prompt,
                self.genre,
                self.tone,
                self.num_scenes,
                self.character_desc,
                self.setting_desc,
                self.art_style
            )
            
            # Process the results
            with self.lock:
                self.story_scenes = story_scenes
                self.image_url_list = image_url_list  # Store the image URLs
                
                # Convert image data to pygame surfaces
                self.generated_images = []
                for img_data in image_data_list:
                    if img_data:
                        try:
                            # Convert to pygame surface
                            image = pygame.image.load(io.BytesIO(img_data))
                            
                            # Scale to fit if needed
                            if image.get_width() != IMG_DIM["width"] or image.get_height() != IMG_DIM["height"]:
                                image = pygame.transform.scale(image, (IMG_DIM["width"], IMG_DIM["height"]))
                            
                            self.generated_images.append(image)
                        except Exception as e:
                            logging.error(f"Error converting image: {str(e)}")
                            self.generated_images.append(None)
                    else:
                        self.generated_images.append(None)
                
                # Ensure we have placeholders for all scenes
                while len(self.generated_images) < len(self.story_scenes):
                    self.generated_images.append(None)
                
                # Ensure we have placeholders for all image URLs
                while len(self.image_url_list) < len(self.story_scenes):
                    self.image_url_list.append(None)
                
                self.state = "viewing"
                self.current_page = 0
                self.status_message = ""
        
        except Exception as e:
            logging.error(f"Error in generate_story_thread: {str(e)}")
            with self.lock:
                self.status_message = f"Error generating story: {str(e)}"
                self.state = "input"
    
    # ----- Main Loop -----
    
    def run(self):
        """Main application loop"""
        running = True
        clock = pygame.time.Clock()
        
        logging.debug(f"=== APPLICATION STARTED ===")
        logging.debug(f"Screen dimensions: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        logging.debug(f"Image dimensions: {IMG_DIM}")
        logging.debug(f"Default number of scenes: {self.num_scenes}")
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    logging.debug(f"=== APPLICATION CLOSING ===")
                    running = False
                
                # Handle file dialog events first
                if self.show_file_dialog:
                    self.handle_file_dialog_events(event)
                    continue
                
                # Handle events based on state
                if self.state == "start_menu":
                    self.handle_start_menu_events(event)
                elif self.state == "input":
                    self.handle_input_events(event)
                elif self.state == "viewing":
                    self.handle_viewing_events(event)
            
            # Draw based on state
            with self.lock:
                if self.state == "start_menu":
                    self.draw_start_menu()
                elif self.state == "input":
                    self.draw_input_screen()
                elif self.state == "generating":
                    self.draw_generating_screen()
                elif self.state == "viewing":
                    self.draw_story_page()
                
                # Draw file dialog on top if needed
                if self.show_file_dialog:
                    self.draw_file_dialog()
            
            pygame.display.flip()
            clock.tick(30)
        
        pygame.quit()

if __name__ == "__main__":
    app = UI(num_scenes=3)  # Default to 3 scenes, but it's configurable
    app.run()