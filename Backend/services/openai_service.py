# services/openai_service.py
import openai
from typing import List, Dict, Any, Optional
from config import settings
from models.story import StoryPrompt, Scene, Story
from utils.prompt_engineering import (
    create_story_system_prompt,
    format_story_generation_prompt,
    format_scene_regeneration_prompt,
    format_title_generation_prompt
)

# Configure OpenAI API
openai.api_key = settings.OPENAI_API_KEY

async def generate_story(prompt: StoryPrompt) -> Story:
    """
    Generate a story using OpenAI's GPT model based on the provided prompt.
    
    Args:
        prompt: The story prompt with genre, tone, and other details
        
    Returns:
        A complete story with title and scenes
    """
    # Create system prompt
    system_prompt = create_story_system_prompt(prompt.genre, prompt.tone)
    
    # Format user prompt
    user_prompt = format_story_generation_prompt(
        idea=prompt.idea,
        genre=prompt.genre,
        tone=prompt.tone,
        character=prompt.mainCharacter,
        setting=prompt.setting,
        scene_count=settings.DEFAULT_SCENE_COUNT
    )
    
    # Make API call to OpenAI
    response = await openai.ChatCompletion.acreate(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=settings.OPENAI_TEMPERATURE,
        max_tokens=settings.OPENAI_MAX_TOKENS
    )
    
    # Parse the response to extract scenes
    story_text = response.choices[0].message.content
    
    # Generate a title for the story
    title = await generate_title(prompt, story_text)
    
    # Split the story into scenes
    scenes = parse_story_into_scenes(story_text)
    
    # Create image prompts for each scene
    scenes_with_prompts = await generate_image_prompts(prompt, scenes)
    
    # Create and return the story
    return Story(
        title=title,
        prompt=prompt,
        scenes=scenes_with_prompts
    )

async def generate_title(prompt: StoryPrompt, story_text: str) -> str:
    """Generate a title for the story."""
    title_prompt = format_title_generation_prompt(prompt.idea, story_text)
    
    response = await openai.ChatCompletion.acreate(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a creative title generator for stories."},
            {"role": "user", "content": title_prompt}
        ],
        temperature=0.7,
        max_tokens=50
    )
    
    return response.choices[0].message.content.strip().replace('"', '')

async def regenerate_scene_text(prompt: StoryPrompt, current_text: str, scene_index: int) -> str:
    """Regenerate text for a specific scene."""
    system_prompt = create_story_system_prompt(prompt.genre, prompt.tone)
    
    user_prompt = format_scene_regeneration_prompt(
        idea=prompt.idea,
        current_text=current_text,
        scene_index=scene_index,
        genre=prompt.genre,
        tone=prompt.tone,
        character=prompt.mainCharacter,
        setting=prompt.setting
    )
    
    response = await openai.ChatCompletion.acreate(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=settings.OPENAI_TEMPERATURE + 0.1,  # Slightly higher for variation
        max_tokens=settings.OPENAI_MAX_TOKENS // 2  # Smaller token count for single scene
    )
    
    return response.choices[0].message.content.strip()

async def generate_image_prompts(prompt: StoryPrompt, scenes: List[Scene]) -> List[Scene]:
    """Generate image prompts for each scene."""
    art_style = prompt.artStyle
    setting = prompt.setting if prompt.setting else ""
    
    # Create a single prompt to generate image prompts for all scenes
    system_prompt = "You are an expert at creating detailed image prompts for AI image generation."
    
    scenes_with_prompts = []
    
    for i, scene in enumerate(scenes):
        image_prompt_text = f"""
        Create a detailed image prompt for scene {i+1} of this story.
        
        SCENE TEXT:
        {scene.text}
        
        SETTING:
        {setting}
        
        ART STYLE:
        {art_style}
        
        The prompt should be descriptive, detailed, and capture the essence of the scene. 
        Focus on what should be visible in the image, the environment, lighting, mood, and characters.
        Keep the prompt under 100 words.
        """
        
        response = await openai.ChatCompletion.acreate(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": image_prompt_text}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        image_prompt = response.choices[0].message.content.strip()
        
        scenes_with_prompts.append(Scene(
            text=scene.text,
            imagePrompt=image_prompt
        ))
    
    return scenes_with_prompts

def parse_story_into_scenes(story_text: str) -> List[Scene]:
    """
    Parse the generated story text into separate scenes.
    
    This function looks for scene markers or splits the text into roughly equal parts
    if no explicit markers are found.
    """
    # Look for scene markers like "Scene 1:", "Scene One:", etc.
    import re
    scene_pattern = re.compile(r'(?:Scene|SCENE|Part|PART)\s*(?:\d+|[A-Za-z]+)[:.-]?\s*', re.IGNORECASE)
    
    # Split by scene markers
    scene_splits = scene_pattern.split(story_text)
    
    # Remove empty scenes and any introduction text before first scene marker
    scene_texts = [s.strip() for s in scene_splits if s.strip()]
    
    # If we didn't find any scene markers or only found one scene, 
    # try to split the text into roughly equal parts
    if len(scene_texts) <= 1:
        # Count paragraphs
        paragraphs = [p for p in story_text.split("\n\n") if p.strip()]
        
        # If we have enough paragraphs, distribute them into scenes
        if len(paragraphs) >= settings.DEFAULT_SCENE_COUNT:
            scene_texts = []
            paragraphs_per_scene = len(paragraphs) // settings.DEFAULT_SCENE_COUNT
            
            # Distribute paragraphs into scenes
            for i in range(settings.DEFAULT_SCENE_COUNT):
                start_idx = i * paragraphs_per_scene
                end_idx = start_idx + paragraphs_per_scene if i < settings.DEFAULT_SCENE_COUNT - 1 else len(paragraphs)
                scene_content = "\n\n".join(paragraphs[start_idx:end_idx])
                scene_texts.append(scene_content)
        else:
            # If not enough paragraphs, just create one scene per paragraph
            scene_texts = paragraphs[:settings.DEFAULT_SCENE_COUNT]
            
            # If we still don't have enough scenes, duplicate the last one
            while len(scene_texts) < settings.DEFAULT_SCENE_COUNT:
                scene_texts.append(scene_texts[-1])
    
    # Create Scene objects
    scenes = [Scene(text=text) for text in scene_texts[:settings.DEFAULT_SCENE_COUNT]]
    
    return scenes