# models/image.py
from pydantic import BaseModel, Field
from typing import Optional

class ImageGenerationRequest(BaseModel):
    """Request model for generating an image."""
    prompt: str = Field(..., description="The image generation prompt")
    width: Optional[int] = Field(768, description="Width of the generated image")
    height: Optional[int] = Field(512, description="Height of the generated image")
    num_inference_steps: Optional[int] = Field(50, description="Number of diffusion steps")
    guidance_scale: Optional[float] = Field(7.5, description="Guidance scale for diffusion")
    negative_prompt: Optional[str] = Field("", description="Negative prompt for image generation")

class ImageGenerationResponse(BaseModel):
    """Response model for a generated image."""
    imageUrl: str
    prompt: str