# utils/prompt_engineering.py
"""
Utility functions for crafting effective prompts for story and image generation.
These help ensure consistent, high-quality output from the AI models.
"""

def create_story_system_prompt(genre: str, tone: str) -> str:
    """
    Create a system prompt for the AI based on the genre and tone.

    Args:
        genre: The story genre (e.g., Fantasy, Sci-Fi, Mystery)
        tone: The desired tone (e.g., Lighthearted, Serious, Funny)

    Returns:
        A tailored system prompt for the AI
    """
    base_prompt = """You are an expert storyteller and novelist who specializes in creating engaging, well-structured stories. 
    Follow these guidelines when crafting the story:

    1. Create a cohesive narrative with a clear beginning, middle, and end
    2. Develop compelling characters with distinct personalities
    3. Use vivid imagery and sensory details to bring scenes to life
    4. Structure the story into distinct scenes that flow naturally
    5. Maintain a consistent narrative voice throughout
    6. Include meaningful dialog where appropriate
    7. Ensure the story resonates emotionally with readers
    8. Craft scenes that would translate well to visual illustrations

    Format your story into 5 separate scenes, each with its own narrative focus.
    """

    # Add genre-specific instructions
    genre_instructions = {
        "Fantasy": "Incorporate magical elements, mythical creatures, or supernatural abilities. Create a sense of wonder and possibility.",
        "Science Fiction": "Include futuristic technology, scientific concepts, or speculative elements. Consider how innovations impact society and individuals.",
        "Mystery": "Introduce an intriguing puzzle or problem to solve. Plant subtle clues and create tension through the unknown.",
        "Adventure": "Focus on journey, exploration, and facing challenges. Include elements of risk and discovery.",
        "Romance": "Center on the development of a relationship. Include emotional connection and meaningful interactions between characters.",
        "Horror": "Create an atmosphere of dread, suspense, or fear. Use psychological tension or supernatural elements to unsettle the reader."
    }

    # Add tone-specific instructions
    tone_instructions = {
        "Lighthearted": "Maintain an optimistic, upbeat mood. Include elements of humor and charm. Avoid overly dark or disturbing content.",
        "Serious": "Approach the narrative with gravity and earnestness. Explore deeper themes and complex emotional situations.",
        "Funny": "Incorporate humor through situations, dialogue, or character traits. Aim for moments that will make the reader smile or laugh.",
        "Dramatic": "Emphasize emotional intensity and significant conflicts. Create moments of high stakes and powerful feelings.",
        "Mysterious": "Cultivate an atmosphere of the unknown. Hold back information and reveal it gradually to create intrigue.",
        "Educational": "Weave informative content into the narrative naturally. Ensure facts are accurate while maintaining engaging storytelling.",
        "Inspirational": "Include themes of growth, overcoming obstacles, or finding meaning. Aim to evoke positive emotions and motivation."
    }

    # Add the specific instructions if they exist in our dictionaries
    if genre in genre_instructions:
        base_prompt += f"\nFor this {genre} story: {genre_instructions[genre]}"

    if tone in tone_instructions:
        base_prompt += f"\nMaintain a {tone} tone: {tone_instructions[tone]}"

    return base_prompt

def format_story_generation_prompt(
    idea: str, 
    genre: str, 
    tone: str, 
    character: str = None, 
    setting: str = None,
    scene_count: int = 5
) -> str:
    """
    Format a complete prompt for story generation.

    Args:
        idea: The main story concept
        genre: Story genre
        tone: Desired tone
        character: Optional character description
        setting: Optional setting description
        scene_count: Number of scenes to generate

    Returns:
        A formatted prompt for the AI
    """
    prompt = f"""Create a {genre} story with a {tone} tone based on the following idea:

    STORY IDEA:
    {idea}
    """

    if character:
        prompt += f"""

    MAIN CHARACTER:
    {character}
    """

    if setting:
        prompt += f"""

    SETTING:
    {setting}
    """

    prompt += f"""

    Please structure your story into exactly {scene_count} distinct scenes, each containing a logical segment of the narrative.
    Each scene should build upon the previous one to create a cohesive story with a beginning, middle, and end.
    Make each scene vivid and descriptive so it could be illustrated effectively.
    """

    return prompt

def format_scene_regeneration_prompt(
    idea: str,
    current_text: str,
    scene_index: int,
    genre: str,
    tone: str,
    character: str = None,
    setting: str = None
) -> str:
    """
    Format a prompt for regenerating a specific scene.

    Args:
        idea: The original story idea
        current_text: The current scene text to be regenerated
        scene_index: Which scene number is being regenerated
        genre, tone, character, setting: Original story parameters

    Returns:
        A formatted prompt for scene regeneration
    """
    prompt = f"""Rewrite Scene {scene_index + 1} for a {genre} story with a {tone} tone.

    ORIGINAL STORY IDEA:
    {idea}

    CURRENT SCENE TEXT:
    {current_text}
    """

    if character:
        prompt += f"""

    MAIN CHARACTER:
    {character}
    """

    if setting:
        prompt += f"""

    SETTING:
    {setting}
    """

    prompt += """

    Please create a completely new version of this scene that:
    1. Maintains the same narrative position in the overall story
    2. Keeps the same characters and setting
    3. Takes the story in a somewhat different direction
    4. Is vivid and descriptive enough to be illustrated effectively

    Write only the new scene text, without any introductory text or scene numbers.
    """

    return prompt

def format_title_generation_prompt(idea: str, story_text: str) -> str:
    """
    Format a prompt for generating a story title.

    Args:
        idea: The original story idea
        story_text: The complete generated story

    Returns:
        A prompt for title generation
    """
    # Extract the first 200 characters from the story to give context without too much detail
    story_preview = story_text[:200] + "..."

    prompt = f"""Create a compelling title for this story.

    STORY IDEA:
    {idea}

    STORY PREVIEW:
    {story_preview}

    The title should be:
    1. Catchy and memorable
    2. Relevant to the story content
    3. Between 2-7 words
    4. Evocative of the mood and theme

    Return only the title itself, without quotes or additional commentary.
    """

    return prompt