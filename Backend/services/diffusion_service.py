# services/diffusion_service.py
import os
import logging
import fal_client
from typing import Optional
from config import settings

logger = logging.getLogger(__name__)

# Set FAL API key
os.environ["FAL_KEY"] = settings.FAL_KEY

class DiffusionService:
    def __init__(self):
        """Initialize the diffusion service with FAL AI configuration."""
        pass

    async def generate_image(
        self, 
        prompt: str, 
        width: int = None, 
        height: int = None,
        num_inference_steps: int = None,
        guidance_scale: float = 7.5,
        negative_prompt: str = ""
    ) -> str:
        """
        Generate an image using FAL AI's Flux model.

        Args:
            prompt: Text description of the image to generate
            width: Width of the output image
            height: Height of the output image
            num_inference_steps: Number of denoising steps
            guidance_scale: Scale for classifier-free guidance
            negative_prompt: What NOT to include in the image

        Returns:
            URL to the generated image
        """
        try:
            # Use defaults from settings if not provided
            width = width or settings.IMAGE_WIDTH
            height = height or settings.IMAGE_HEIGHT
            num_inference_steps = num_inference_steps or settings.DIFFUSION_STEPS

            logger.info(f"Generating image with prompt: {prompt[:100]}...")

            # Call FAL AI Flux model
            result = fal_client.subscribe(
                "fal-ai/flux/schnell",
                arguments={
                    "prompt": prompt,
                    "image_size": {
                        "width": width,
                        "height": height
                    },
                    "num_inference_steps": num_inference_steps,
                    "seed": 42  # Fixed seed for consistency
                },
                with_logs=True
            )

            # Process the result
            if result and 'images' in result and len(result['images']) > 0:
                image_url = result['images'][0]['url']
                logger.info(f"Successfully generated image: {image_url}")
                return image_url
            else:
                logger.error("No images returned from FAL AI")
                raise Exception("Failed to generate image with FAL AI")

        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            raise

# Create a singleton instance
diffusion_service = DiffusionService()