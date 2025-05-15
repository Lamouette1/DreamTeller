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
dotenv.load_dotenv()
import fal_client
import ollama

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

    def on_queue_update(self, update, scene_index):
        """Callback function for FAL API queue updates"""
        if hasattr(update, 'logs') and update.logs:
            for log in update.logs:
                logging.debug(f"FAL API (Scene {scene_index+1}) update: {log.get('message', '')}")

    def generate_story_prompt(self, prompt, num_scenes=None):
        """
        Generate just the story text based on a prompt
        Returns a list of scene descriptions
        """
        if num_scenes is None:
            num_scenes = self.default_num_scenes

        try:
            self.status_callback(f"Asking Llama 3 to create a {num_scenes}-scene story...")

            logging.debug(f"=== STARTING STORY TEXT GENERATION ===")
            logging.debug(f"User prompt: '{prompt}'")
            logging.debug(f"Requested scenes: {num_scenes}")

            # Generate story with Ollama Llama 3 - dynamic scene prompt construction
            story_prompt = f"Create a {num_scenes}-scene picture story based on this prompt: \"{prompt}\"\n\n"
            story_prompt += "Format your response as follows:\n"

            # Dynamically add examples for each scene
            for i in range(1, min(num_scenes + 1, 4)):  # Show up to 3 examples
                if i == num_scenes:
                    story_prompt += f"SCENE {i}: [Final scene text, describing the culminating moment that would make a good image]\n\n"
                else:
                    story_prompt += f"SCENE {i}: [Scene {i} text, describing a moment that would make a good image]\n\n"

            # If more than 3 scenes, add indication for middle scenes
            if num_scenes > 3:
                story_prompt += "... (continue with scenes 4 through " + str(num_scenes-1) + ")\n\n"
                story_prompt += f"SCENE {num_scenes}: [Final scene text, describing the culminating moment that would make a good image]\n\n"

            story_prompt += "Keep each scene description under 150 words. Make the scenes visual and descriptive."

            logging.debug(f"Sending prompt to Llama 3: {story_prompt[:100]}...")

            response = ollama.chat(model="llama3", messages=[
                {"role": "user", "content": story_prompt}
            ])

            story_text = response['message']['content']
            logging.debug(f"=== RAW STORY RESPONSE ===\n{story_text}\n=== END RAW RESPONSE ===")

            # Parse scenes
            scenes = []
            current_scene = ""
            scene_started = False

            logging.debug(f"Starting to parse scenes from response...")
            for line in story_text.split('\n'):
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
            logging.error(f"Error generating story text: {str(e)}")
            self.status_callback(f"Error generating story text: {str(e)}")
            return []

    def generate_image(self, scene_text, scene_index):
        """
        Generate an image for a single scene
        Returns the raw image data
        """
        try:
            self.status_callback(f"Generating image {scene_index+1}...")
            self.image_status_callback(scene_index, True)  # Mark as loading

            logging.debug(f"=== STARTING IMAGE GENERATION FOR SCENE {scene_index+1} ===")
            logging.debug(f"Scene text: {scene_text}")

            # Create image prompt
            image_prompt_creation = f"""
            Convert this scene description into a clear, detailed prompt for image generation.
            Focus on visual elements like lighting, perspective, colors, and key objects.
            Keep it concise (under 100 words) but detailed enough for good image generation.

            Scene: {scene_text}

            Image prompt:
            """

            logging.debug(f"Creating optimized image prompt using Llama 3")

            # Use Llama 3 to create a better image prompt
            try:
                prompt_response = ollama.chat(model="llama3", messages=[
                    {"role": "user", "content": image_prompt_creation}
                ])

                image_prompt = prompt_response['message']['content']
                # Clean up the response if needed
                if "Image prompt:" in image_prompt:
                    image_prompt = image_prompt.split("Image prompt:", 1)[1].strip()

                logging.debug(f"Generated image prompt: {image_prompt}")
            except Exception as e:
                logging.error(f"Error creating optimized image prompt: {str(e)}")
                # Fallback to using the scene directly
                image_prompt = scene_text
                logging.debug(f"Falling back to using scene text directly")

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

                # Download image
                if result and 'images' in result and len(result['images']) > 0:
                    image_url = result['images'][0]['url']
                    logging.debug(f"Image URL: {image_url}")

                    # Download image
                    logging.debug(f"Downloading image...")
                    with urllib.request.urlopen(image_url) as response:
                        image_data = response.read()

                    # Return the raw image data
                    logging.debug(f"Image {scene_index+1} successfully downloaded")
                    return image_data
                else:
                    logging.error(f"No images returned in the FAL AI response")
                    return None

            except Exception as e:
                logging.error(f"Error generating image {scene_index+1}: {str(e)}")
                self.status_callback(f"Error generating image {scene_index+1}: {str(e)}")
                return None

        except Exception as e:
            logging.error(f"Error in generate_image: {str(e)}")
            return None
        finally:
            self.image_status_callback(scene_index, False)  # Mark as done loading
            logging.debug(f"=== COMPLETED IMAGE GENERATION FOR SCENE {scene_index+1} ===")

    def generate_complete_story(self, prompt, num_scenes=None):
        """
        Generate a full story with images
        Returns (story_scenes, image_data_list)
        """
        if num_scenes is None:
            num_scenes = self.default_num_scenes

        try:
            # First generate the story text
            story_scenes = self.generate_story_prompt(prompt, num_scenes)

            if not story_scenes:
                return [], []

            # Then generate images for each scene
            image_data_list = [None] * len(story_scenes)

            for i, scene in enumerate(story_scenes):
                image_data = self.generate_image(scene, i)
                image_data_list[i] = image_data

            logging.debug(f"=== STORY AND IMAGE GENERATION COMPLETE ===")
            self.status_callback("Story and images generated successfully!")

            return story_scenes, image_data_list

        except Exception as e:
            logging.error(f"Error generating complete story: {str(e)}")
            self.status_callback(f"Error generating story: {str(e)}")
            return [], []

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

        # Fonts
        self.title_font = pygame.font.SysFont('Arial', 42, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 22)
        self.input_font = pygame.font.SysFont('Arial', 24)

        # Initial number of scenes
        self.num_scenes = num_scenes

        # Story data
        self.story_prompt = ""
        self.story_scenes = []
        self.generated_images = []
        self.current_page = 0

        # State tracking
        self.state = "input"  # States: input, generating, viewing
        self.input_text = ""
        self.status_message = ""
        self.image_loading = []

        # Input boxes
        self.input_box = pygame.Rect((SCREEN_WIDTH - 800)//2, 400, 800, 60)
        self.scenes_input_box = pygame.Rect((SCREEN_WIDTH - 200)//2, 470, 200, 40)
        self.active_input = "prompt"  # Which input is active: "prompt" or "scenes"

        # Button
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

    def update_status(self, message):
        """Callback to update status message from AI generator"""
        with self.lock:
            self.status_message = message

    def update_image_status(self, index, is_loading):
        """Callback to update image loading status from AI generator"""
        with self.lock:
            # Ensure image_loading list is long enough
            while len(self.image_loading) <= index:
                self.image_loading.append(False)
            self.image_loading[index] = is_loading

    def draw_input_screen(self):
        self.screen.fill(WHITE)

        # Title
        title_surface = self.title_font.render("Picture Story Generator", True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, 120))
        self.screen.blit(title_surface, title_rect)

        # Instructions
        instructions = [
            "Enter a prompt to generate a picture story.",
            "Example: 'make me a picture story about a sci-fi ninja in space'",
            f"The app will generate a {self.num_scenes}-scene story with images.",
            "You can change the number of scenes below."
        ]

        for i, instruction in enumerate(instructions):
            text_surface = self.text_font.render(instruction, True, BLACK)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, 220 + i*35))
            self.screen.blit(text_surface, text_rect)

        # Prompt Input box
        pygame.draw.rect(self.screen, GRAY if self.active_input == "prompt" else DARK_GRAY, self.input_box, 2)
        text_surface = self.input_font.render(self.input_text, True, BLACK)
        # Center the text vertically in the input box
        text_rect = text_surface.get_rect(midleft=(self.input_box.x + 10, self.input_box.y + self.input_box.height//2))
        self.screen.blit(text_surface, text_rect)

        # Scenes Input label
        scenes_label = self.text_font.render("Number of scenes:", True, BLACK)
        scenes_label_rect = scenes_label.get_rect(midright=(self.scenes_input_box.x - 10, self.scenes_input_box.y + self.scenes_input_box.height//2))
        self.screen.blit(scenes_label, scenes_label_rect)

        # Scenes Input box
        pygame.draw.rect(self.screen, GRAY if self.active_input == "scenes" else DARK_GRAY, self.scenes_input_box, 2)
        scenes_text = self.text_font.render(str(self.num_scenes), True, BLACK)
        scenes_text_rect = scenes_text.get_rect(center=self.scenes_input_box.center)
        self.screen.blit(scenes_text, scenes_text_rect)

        # Generate button
        pygame.draw.rect(self.screen, BLUE, self.generate_button)
        button_text = self.text_font.render("Generate Story", True, WHITE)
        button_rect = button_text.get_rect(center=self.generate_button.center)
        self.screen.blit(button_text, button_rect)

        # Status message
        if self.status_message:
            status_surface = self.text_font.render(self.status_message, True, BLACK)
            status_rect = status_surface.get_rect(center=(SCREEN_WIDTH//2, 600))
            self.screen.blit(status_surface, status_rect)

    def draw_generating_screen(self):
        self.screen.fill(WHITE)

        # Title
        title_surface = self.title_font.render("Generating Your Story...", True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(title_surface, title_rect)

        # Status message
        if self.status_message:
            status_surface = self.text_font.render(self.status_message, True, BLACK)
            status_rect = status_surface.get_rect(center=(SCREEN_WIDTH//2, 250))
            self.screen.blit(status_surface, status_rect)

        # Loading indicators for images
        for i in range(len(self.image_loading)):
            color = BLUE if i < len(self.image_loading) and self.image_loading[i] else GRAY
            indicator_x = SCREEN_WIDTH//2 - ((len(self.image_loading) * 120) // 2) + i*120
            indicator_rect = pygame.Rect(indicator_x, 350, 80, 80)
            pygame.draw.rect(self.screen, color, indicator_rect)
            text = self.text_font.render(f"Image {i+1}", True, BLACK)
            text_rect = text.get_rect(center=(indicator_x + 40, 460))
            self.screen.blit(text, text_rect)

    def draw_story_page(self):
        self.screen.fill(WHITE)

        if 0 <= self.current_page < len(self.story_scenes):
            # Display image
            if self.current_page < len(self.generated_images) and self.generated_images[self.current_page]:
                image_rect = self.generated_images[self.current_page].get_rect()
                image_rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//3)
                self.screen.blit(self.generated_images[self.current_page], image_rect)
            else:
                # Placeholder for image
                pygame.draw.rect(self.screen, GRAY, (SCREEN_WIDTH//2 - IMG_DIM["width"]//2, 
                                                   SCREEN_HEIGHT//3 - IMG_DIM["height"]//2, 
                                                   IMG_DIM["width"], IMG_DIM["height"]))

            # Display scene text
            scene_text = self.story_scenes[self.current_page]

            # Display scene number
            scene_label = self.title_font.render(f"Scene {self.current_page + 1}", True, TITLE_BLUE)
            scene_label_rect = scene_label.get_rect(center=(120, SCREEN_HEIGHT//2 + 100))
            self.screen.blit(scene_label, scene_label_rect)

            # Calculate text area
            text_area_width = SCREEN_WIDTH - 100
            text_area_height = SCREEN_HEIGHT//2 - 150
            text_area_top = SCREEN_HEIGHT//2 + 150

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

            # Render wrapped text
            text_y_start = text_area_top
            for i, line in enumerate(wrapped_text):
                text_surface = self.text_font.render(line, True, BLACK)
                text_rect = text_surface.get_rect()
                text_rect.left = 50
                text_rect.top = text_y_start + i * 32  # Increased line spacing
                self.screen.blit(text_surface, text_rect)

        # Navigation controls
        button_y = SCREEN_HEIGHT - 80

        # Previous button
        prev_button = pygame.Rect(80, button_y, 130, 50)
        pygame.draw.rect(self.screen, BLUE if self.current_page > 0 else DARK_GRAY, prev_button)
        prev_text = self.text_font.render("Previous", True, WHITE)
        prev_text_rect = prev_text.get_rect(center=prev_button.center)
        self.screen.blit(prev_text, prev_text_rect)

        # Next button
        next_button = pygame.Rect(SCREEN_WIDTH - 210, button_y, 130, 50)
        pygame.draw.rect(self.screen, BLUE if self.current_page < len(self.story_scenes) - 1 else DARK_GRAY, next_button)
        next_text = self.text_font.render("Next", True, WHITE)
        next_text_rect = next_text.get_rect(center=next_button.center)
        self.screen.blit(next_text, next_text_rect)

        # Page indicator
        page_text = self.text_font.render(f"Page {self.current_page + 1} of {len(self.story_scenes)}", True, BLACK)
        page_text_rect = page_text.get_rect(center=(SCREEN_WIDTH//2, button_y - 30))
        self.screen.blit(page_text, page_text_rect)

        # New story button
        new_story_button = pygame.Rect(SCREEN_WIDTH//2 - 100, button_y, 200, 50)
        pygame.draw.rect(self.screen, GRAY, new_story_button)
        new_story_text = self.text_font.render("New Story", True, BLACK)
        new_story_text_rect = new_story_text.get_rect(center=new_story_button.center)
        self.screen.blit(new_story_text, new_story_text_rect)

    def start_generation(self):
        """Start the story generation process in a separate thread"""
        self.story_prompt = self.input_text
        logging.debug(f"=== GENERATION STARTED ===")
        logging.debug(f"User prompt: '{self.story_prompt}'")
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
            story_scenes, image_data_list = self.ai_generator.generate_complete_story(
                self.story_prompt, 
                self.num_scenes
            )

            # Process the results
            with self.lock:
                self.story_scenes = story_scenes

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

                self.state = "viewing"
                self.current_page = 0
                self.status_message = ""

        except Exception as e:
            logging.error(f"Error in generate_story_thread: {str(e)}")
            with self.lock:
                self.status_message = f"Error generating story: {str(e)}"
                self.state = "input"

    def handle_input_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the prompt input box is clicked
            if self.input_box.collidepoint(event.pos):
                self.active_input = "prompt"

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
                    self.active_input = "scenes"
                else:
                    self.input_text += event.unicode

            elif self.active_input == "scenes":
                if event.key == pygame.K_RETURN and self.input_text.strip():
                    self.start_generation()
                elif event.key == pygame.K_BACKSPACE:
                    self.num_scenes = str(self.num_scenes)[:-1] or "3"  # Default to 3 if empty
                elif event.key == pygame.K_TAB:
                    self.active_input = "prompt"
                elif event.unicode.isdigit():
                    new_value = str(self.num_scenes) + event.unicode
                    try:
                        num = int(new_value)
                        if 1 <= num <= 10:  # Set a reasonable range
                            self.num_scenes = num
                    except ValueError:
                        pass  # Ignore if not a valid number

    def handle_viewing_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Previous button
            prev_button = pygame.Rect(80, SCREEN_HEIGHT - 80, 130, 50)
            if prev_button.collidepoint(event.pos) and self.current_page > 0:
                self.current_page -= 1
                logging.debug(f"Navigation: Moving to page {self.current_page + 1}")

            # Next button
            next_button = pygame.Rect(SCREEN_WIDTH - 210, SCREEN_HEIGHT - 80, 130, 50)
            if next_button.collidepoint(event.pos) and self.current_page < len(self.story_scenes) - 1:
                self.current_page += 1
                logging.debug(f"Navigation: Moving to page {self.current_page + 1}")

            # New story button
            new_story_button = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 80, 200, 50)
            if new_story_button.collidepoint(event.pos):
                logging.debug(f"=== STARTING NEW STORY ===")
                self.state = "input"
                self.input_text = ""
                self.story_scenes = []
                self.generated_images = []
                self.current_page = 0
                self.status_message = ""
                self.image_loading = []

    def run(self):
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

                # Handle events based on state
                if self.state == "input":
                    self.handle_input_events(event)
                elif self.state == "viewing":
                    self.handle_viewing_events(event)

            # Draw based on state
            with self.lock:
                if self.state == "input":
                    self.draw_input_screen()
                elif self.state == "generating":
                    self.draw_generating_screen()
                elif self.state == "viewing":
                    self.draw_story_page()

                    # Log current page info
                    if event.type == pygame.MOUSEBUTTONDOWN and (
                        pygame.Rect(50, SCREEN_HEIGHT - 100, 100, 50).collidepoint(event.pos) or  # Prev button
                        pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 100, 100, 50).collidepoint(event.pos)  # Next button
                    ):
                        logging.debug(f"=== VIEWING PAGE {self.current_page + 1} ===")
                        if 0 <= self.current_page < len(self.story_scenes):
                            logging.debug(f"Scene text: {self.story_scenes[self.current_page][:100]}...")

            pygame.display.flip()
            clock.tick(30)

        pygame.quit()

if __name__ == "__main__":
    app = UI(num_scenes=3)  # Default to 3 scenes, but it's configurable
    app.run()