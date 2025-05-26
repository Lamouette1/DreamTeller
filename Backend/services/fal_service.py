# services/fal_service.py
import os
import logging
import re
import fal_client
from typing import List, Dict, Any, Optional, Tuple
from config import settings
from models.story import StoryPrompt, Scene, Story

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set FAL API key
os.environ["FAL_KEY"] = settings.FAL_KEY

class FALService:
    def __init__(self):
        self.default_num_scenes = settings.DEFAULT_SCENE_COUNT
        
    def on_queue_update(self, update, scene_index=None):
        """Callback function for FAL API queue updates"""
        if hasattr(update, 'logs') and update.logs:
            for log in update.logs:
                if scene_index is not None:
                    logger.debug(f"FAL API (Scene {scene_index+1}) update: {log.get('message', '')}")
                else:
                    logger.debug(f"FAL API update: {log.get('message', '')}")

    async def generate_story_rough_sketch(self, user_prompt: str, genre: str, tone: str, num_scenes: int, 
                                        user_character_desc: Optional[str] = None, 
                                        user_setting_desc: Optional[str] = None) -> str:
        """Generate a rough sketch of the overall story based on user preferences"""
        try:
            logger.info(f"Creating a {num_scenes}-scene {genre} story sketch...")
            
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
            logger.debug(f"Story sketch generated: {story_sketch[:300]}...")
            
            return story_sketch
            
        except Exception as e:
            logger.error(f"Error generating story sketch: {str(e)}")
            raise

    async def generate_character_description(self, story_sketch: str, user_character_desc: Optional[str] = None) -> str:
        """Generate a detailed character description based on the story sketch and user input"""
        try:
            logger.info("Creating detailed character profile...")
            
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
            logger.debug(f"Character description generated: {character_description[:300]}...")
            
            return character_description
            
        except Exception as e:
            logger.error(f"Error generating character description: {str(e)}")
            raise

    async def generate_story_scenes(self, story_sketch: str, character_description: str, num_scenes: int) -> List[str]:
        """Generate detailed scenes based on the story sketch, character description, and number of scenes"""
        try:
            logger.info(f"Developing {num_scenes} detailed story scenes...")
            
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
            logger.debug(f"Raw scene response: {scene_text[:500]}...")
            
            # Parse scenes
            scenes = []
            current_scene = ""
            scene_started = False
            
            for line in scene_text.split('\n'):
                line = line.strip()
                
                # Check for scene markers like "SCENE 1:" or "SCENE 1"
                if re.search(r'SCENE\s+\d+:?', line):
                    if scene_started and current_scene:
                        scenes.append(current_scene.strip())
                    current_scene = line.split(':', 1)[1].strip() if ':' in line else ""
                    scene_started = True
                # If we're in a scene and this isn't a new scene marker, add the line to the current scene
                elif scene_started and line:
                    current_scene += " " + line
            
            # Add the last scene if there is one
            if scene_started and current_scene:
                scenes.append(current_scene.strip())
            
            # Ensure we have the requested number of scenes
            while len(scenes) < num_scenes:
                scenes.append(f"Scene {len(scenes)+1} description not available.")
            
            return scenes[:num_scenes]  # Limit to requested number of scenes
            
        except Exception as e:
            logger.error(f"Error generating story scenes: {str(e)}")
            raise

    async def generate_image_prompt(self, scene_text: str, scene_index: int, character_description: str) -> str:
        """Use the video prompt generator to create an enhanced image prompt that includes character details"""
        try:
            logger.debug(f"Enhancing image prompt for scene {scene_index+1}")
            
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
                    "style": "Cinematic",
                    "camera_style": "Steadicam flow",
                    "special_effects": "Practical effects",
                    "prompt_length": "Medium",
                    "model": "google/gemini-flash-1.5"
                },
                with_logs=True,
                on_queue_update=on_queue_update_for_video_prompt
            )
            
            enhanced_prompt = result["prompt"]
            logger.debug(f"Enhanced image prompt: {enhanced_prompt}")
            return enhanced_prompt
            
        except Exception as e:
            logger.error(f"Error enhancing image prompt, falling back to original: {str(e)}")
            return scene_text  # Fallback to original scene text

    async def generate_image(self, scene_text: str, scene_index: int, character_description: str, art_style: str) -> str:
        """Generate an image for a scene incorporating character details. Returns image URL."""
        try:
            logger.info(f"Generating image {scene_index+1}...")
            
            # Generate enhanced image prompt with character details
            image_prompt = await self.generate_image_prompt(scene_text, scene_index, character_description)
            
            # Add art style to the prompt
            if art_style and art_style != "Digital Painting":
                image_prompt = f"{image_prompt} in {art_style} style"
            
            # Call FAL API to generate image
            def on_queue_update_for_scene(update):
                self.on_queue_update(update, scene_index)
            
            result = fal_client.subscribe(
                "fal-ai/flux/schnell",
                arguments={
                    "prompt": image_prompt,
                    "image_size": {
                        "width": settings.IMAGE_WIDTH,
                        "height": settings.IMAGE_HEIGHT
                    },
                    "num_inference_steps": settings.DIFFUSION_STEPS,
                    "seed": 42 + scene_index  # Use different seeds for variation
                },
                with_logs=True,
                on_queue_update=on_queue_update_for_scene
            )
            
            # Process image
            if result and 'images' in result and len(result['images']) > 0:
                image_url = result['images'][0]['url']
                logger.debug(f"Image URL: {image_url}")
                return image_url
            else:
                logger.error(f"No images returned in the FAL AI response")
                return None
                
        except Exception as e:
            logger.error(f"Error generating image {scene_index+1}: {str(e)}")
            return None

    async def generate_story(self, prompt: StoryPrompt) -> Story:
        """Generate a full story with images using the four-step process"""
        try:
            num_scenes = prompt.numScenes if hasattr(prompt, 'numScenes') else self.default_num_scenes
            logger.info(f"Generating story with {prompt.numScenes} scenes")
            # Step 1: Generate the story rough sketch
            story_sketch = await self.generate_story_rough_sketch(
                prompt.idea,
                prompt.genre,
                prompt.tone,
                num_scenes,
                prompt.mainCharacter,
                prompt.setting
            )
            
            if not story_sketch:
                raise ValueError("Failed to generate story sketch")
            
            # Step 2: Generate detailed character description
            character_description = await self.generate_character_description(
                story_sketch,
                prompt.mainCharacter
            )
            
            if not character_description:
                raise ValueError("Failed to generate character description")
            
            # Step 3: Generate story scenes
            story_scenes = await self.generate_story_scenes(
                story_sketch,
                character_description,
                num_scenes
            )
            
            if not story_scenes:
                raise ValueError("Failed to generate story scenes")
            
            # Step 4: Generate images for each scene
            scenes = []
            for i, scene_text in enumerate(story_scenes):
                image_url = await self.generate_image(
                    scene_text,
                    i,
                    character_description,
                    prompt.artStyle
                )
                
                # Create scene with text and image
                scene = Scene(
                    text=scene_text,
                    imageUrl=image_url,
                    imagePrompt=scene_text[:100] + "..."  # Store abbreviated prompt
                )
                scenes.append(scene)
            
            # Generate title
            title = await self.generate_title(prompt.idea, story_sketch)
            
            # Create and return the story
            return Story(
                title=title,
                prompt=prompt,
                scenes=scenes
            )
            
        except Exception as e:
            logger.error(f"Error generating complete story: {str(e)}")
            raise

    async def generate_title(self, idea: str, story_sketch: str) -> str:
        """Generate a title for the story"""
        try:
            title_prompt = f"""
            Create a compelling title for this story.
            
            STORY IDEA:
            {idea}
            
            STORY SKETCH:
            {story_sketch[:200]}...
            
            The title should be:
            1. Catchy and memorable
            2. Relevant to the story content
            3. Between 2-7 words
            4. Evocative of the mood and theme
            
            Return only the title itself, without quotes or additional commentary.
            """
            
            result = fal_client.subscribe(
                "fal-ai/any-llm",
                arguments={
                    "model": "openai/gpt-4o",
                    "prompt": title_prompt
                },
                with_logs=True,
                on_queue_update=self.on_queue_update
            )
            
            return result["output"].strip().replace('"', '')
            
        except Exception as e:
            logger.error(f"Error generating title: {str(e)}")
            return "Untitled Story"

    async def regenerate_scene_text(self, prompt: StoryPrompt, current_text: str, scene_index: int) -> str:
        """Regenerate text for a specific scene"""
        try:
            regenerate_prompt = f"""
            Rewrite Scene {scene_index + 1} for a {prompt.genre} story with a {prompt.tone} tone.
            
            ORIGINAL STORY IDEA:
            {prompt.idea}
            
            CURRENT SCENE TEXT:
            {current_text}
            """
            
            if prompt.mainCharacter:
                regenerate_prompt += f"""
                
                MAIN CHARACTER:
                {prompt.mainCharacter}
                """
            
            if prompt.setting:
                regenerate_prompt += f"""
                
                SETTING:
                {prompt.setting}
                """
            
            regenerate_prompt += """
            
            Please create a completely new version of this scene that:
            1. Maintains the same narrative position in the overall story
            2. Keeps the same characters and setting
            3. Takes the story in a somewhat different direction
            4. Is vivid and descriptive enough to be illustrated effectively
            
            Write only the new scene text, without any introductory text or scene numbers.
            """
            
            result = fal_client.subscribe(
                "fal-ai/any-llm",
                arguments={
                    "model": "openai/gpt-4o",
                    "prompt": regenerate_prompt
                },
                with_logs=True,
                on_queue_update=self.on_queue_update
            )
            
            return result["output"].strip()
            
        except Exception as e:
            logger.error(f"Error regenerating scene text: {str(e)}")
            raise

# Create singleton instance
fal_service = FALService()