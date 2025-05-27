# routes/image_routes.py
from fastapi import APIRouter, HTTPException
from models.image import ImageGenerationRequest, ImageGenerationResponse
from services.diffusion_service import diffusion_service
from utils.error_handling import handle_api_errors

router = APIRouter()

@router.post("/generate", response_model=ImageGenerationResponse)
@handle_api_errors
async def generate_image(request: ImageGenerationRequest):
    """
    Generate an image based on the provided prompt using FAL AI.

    Args:
        request: Contains the prompt and optional parameters for image generation

    Returns:
        The URL of the generated image
    """
    try:
        # Generate the image using the FAL AI diffusion service
        image_url = await diffusion_service.generate_image(
            prompt=request.prompt,
            width=request.width,
            height=request.height,
            num_inference_steps=request.num_inference_steps,
            guidance_scale=request.guidance_scale,
            negative_prompt=request.negative_prompt
        )

        if not image_url:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate image - no URL returned"
            )

        return ImageGenerationResponse(
            imageUrl=image_url,
            prompt=request.prompt
        )

    except Exception as e:
        # Check for specific FAL AI errors
        error_message = str(e).lower()

        if "api key" in error_message or "authentication" in error_message:
            raise HTTPException(
                status_code=401,
                detail="FAL AI API authentication failed. Please check your API key."
            )
        elif "rate limit" in error_message:
            raise HTTPException(
                status_code=429,
                detail="FAL AI rate limit exceeded. Please try again later."
            )
        elif "invalid prompt" in error_message:
            raise HTTPException(
                status_code=400,
                detail="Invalid image prompt. Please check your input."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate image: {str(e)}"
            )

@router.post("/regenerate/{scene_index}", response_model=ImageGenerationResponse)
@handle_api_errors
async def regenerate_scene_image(scene_index: int, request: ImageGenerationRequest):
    """
    Regenerate an image for a specific scene.

    Args:
        scene_index: The index of the scene to regenerate
        request: Contains the prompt and optional parameters for image generation

    Returns:
        The URL of the regenerated image
    """
    try:
        # Add scene index to seed for variation
        seed_offset = 42 + scene_index

        # Generate the image with scene-specific seed
        image_url = await diffusion_service.generate_image(
            prompt=request.prompt,
            width=request.width,
            height=request.height,
            num_inference_steps=request.num_inference_steps,
            guidance_scale=request.guidance_scale,
            negative_prompt=request.negative_prompt
        )

        if not image_url:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to regenerate image for scene {scene_index + 1}"
            )

        return ImageGenerationResponse(
            imageUrl=image_url,
            prompt=request.prompt
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to regenerate scene image: {str(e)}"
        )