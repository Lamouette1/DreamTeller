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
    Generate an image based on the provided prompt.
    
    Args:
        request: Contains the prompt and optional parameters for image generation
        
    Returns:
        The URL of the generated image
    """
    try:
        # Generate the image using the diffusion service
        image_url = await diffusion_service.generate_image(
            prompt=request.prompt,
            width=request.width,
            height=request.height,
            num_inference_steps=request.num_inference_steps,
            guidance_scale=request.guidance_scale,
            negative_prompt=request.negative_prompt
        )
        
        return ImageGenerationResponse(
            imageUrl=image_url,
            prompt=request.prompt
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate image: {str(e)}"
        )