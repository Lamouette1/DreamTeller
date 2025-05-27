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
        negative_prompt: str = "",
        image_size: str = None,
        art_style: str = "Digital Painting"
    ) -> str:
        """
        Generate an image using FAL AI's Flux model.

        Args:
            prompt: Text description of the image to generate
            width: Width of the output image (deprecated, use image_size instead)
            height: Height of the output image (deprecated, use image_size instead)
            num_inference_steps: Number of denoising steps
            guidance_scale: Scale for classifier-free guidance (not used in FLUX schnell)
            negative_prompt: What NOT to include in the image (not used in FLUX schnell)
            image_size: FAL AI image size enum (preferred method)
            art_style: Art style to determine optimal image size

        Returns:
            URL to the generated image
        """
        try:
            # Determine image size
            if image_size and settings.validate_image_size(image_size):
                final_image_size = image_size
            elif art_style:
                final_image_size = settings.get_image_size_for_art_style(art_style)
            else:
                final_image_size = settings.DEFAULT_IMAGE_SIZE

            # Use defaults from settings if not provided
            num_inference_steps = num_inference_steps or settings.DIFFUSION_STEPS

            logger.info(f"Generating image with prompt: {prompt[:100]}...")
            logger.info(f"Using image size: {final_image_size}")

            # Call FAL AI Flux model
            result = fal_client.subscribe(
                "fal-ai/flux/schnell",
                arguments={
                    "prompt": prompt,
                    "image_size": final_image_size,
                    "num_inference_steps": num_inference_steps,
                    "seed": 42,  # Fixed seed for consistency
                    "num_images": 1,
                    "enable_safety_checker": True
                },
                with_logs=True
            )

            # Process the result
            if result and 'images' in result and len(result['images']) > 0:
                image_url = result['images'][0]['url']
                image_width = result['images'][0].get('width', 'unknown') 
                image_height = result['images'][0].get('height', 'unknown')
                logger.info(f"Successfully generated image: {image_url} ({image_width}x{image_height})")
                return image_url
            else:
                logger.error("No images returned from FAL AI")
                raise Exception("Failed to generate image with FAL AI")

        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            raise

    def get_supported_image_sizes(self) -> list:
        """Get list of supported image sizes."""
        return settings.AVAILABLE_IMAGE_SIZES.copy()

    def get_optimal_size_for_style(self, art_style: str) -> str:
        """Get optimal image size for a given art style."""
        return settings.get_image_size_for_art_style(art_style)

# Create a singleton instance
diffusion_service = DiffusionService()