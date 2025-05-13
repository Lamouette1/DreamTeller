# services/diffusion_service.py
import replicate
import httpx
import os
import base64
from typing import Optional
from config import settings

class DiffusionService:
    def __init__(self):
        """Initialize the diffusion service with API configuration."""
        # Configure Replicate if using it
        os.environ["REPLICATE_API_TOKEN"] = settings.STABILITY_API_KEY
        self.client = replicate.Client()
        
        # For direct Stability API calls
        self.stability_api_key = settings.STABILITY_API_KEY
        self.stability_api_url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        
    async def generate_image_replicate(
        self, 
        prompt: str, 
        width: int = 768, 
        height: int = 512,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
        negative_prompt: str = ""
    ) -> str:
        """
        Generate an image using Replicate's diffusion model API.
        
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
        # Use Replicate's Stable Diffusion model
        output = self.client.run(
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input={
                "prompt": prompt,
                "width": width,
                "height": height,
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale,
                "negative_prompt": negative_prompt,
            }
        )
        
        # Replicate returns a list of image URLs
        if output and len(output) > 0:
            return output[0]  # Return the first image URL
        
        raise Exception("Failed to generate image with Replicate")
        
    async def generate_image_stability(
        self, 
        prompt: str, 
        width: int = 1024, 
        height: int = 1024,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
        negative_prompt: str = ""
    ) -> str:
        """
        Generate an image using Stability AI's API directly.
        
        Args:
            prompt: Text description of the image to generate
            width: Width of the output image
            height: Height of the output image
            num_inference_steps: Number of denoising steps (steps parameter in Stability)
            guidance_scale: Scale for classifier-free guidance (cfg_scale in Stability)
            negative_prompt: What NOT to include in the image
            
        Returns:
            URL to the generated image
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.stability_api_key}"
        }
        
        payload = {
            "text_prompts": [
                {
                    "text": prompt,
                    "weight": 1.0
                }
            ],
            "cfg_scale": guidance_scale,
            "steps": num_inference_steps,
            "width": width,
            "height": height,
        }
        
        # Add negative prompt if provided
        if negative_prompt:
            payload["text_prompts"].append({
                "text": negative_prompt,
                "weight": -1.0
            })
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.stability_api_url,
                headers=headers,
                json=payload,
                timeout=60.0  # Image generation can take time
            )
            
            if response.status_code != 200:
                raise Exception(f"Error from Stability API: {response.text}")
                
            result = response.json()
            
            # Process the result - Stability returns base64 encoded images
            if "artifacts" in result and len(result["artifacts"]) > 0:
                # Here we would normally save the image or upload it to cloud storage
                # For this example, we'll return a placeholder URL
                # In a real application, return the actual URL to the saved image
                
                # Placeholder - in production, save the image and return its URL
                image_data = result["artifacts"][0]["base64"]
                
                # Save the image to a file or upload to cloud storage
                # Example: Save to local file (for demo purposes)
                image_id = os.urandom(8).hex()
                image_path = f"static/images/{image_id}.png"
                
                # Ensure directory exists
                os.makedirs("static/images", exist_ok=True)
                
                # Save the image
                with open(image_path, "wb") as f:
                    f.write(base64.b64decode(image_data))
                
                # Return the URL to the image
                # In production, this would be a proper URL to your storage
                return f"/static/images/{image_id}.png"
            
            raise Exception("No image was generated")
    
    async def generate_image(self, prompt: str, **kwargs) -> str:
        """
        Generate an image using the preferred API.
        This is the main method to call from routes.
        
        Args:
            prompt: Text description of the image to generate
            **kwargs: Additional parameters for image generation
            
        Returns:
            URL to the generated image
        """
        try:
            # Default to Replicate, but can be switched to Stability
            # You could add logic here to choose based on config or other factors
            return await self.generate_image_replicate(prompt, **kwargs)
        except Exception as e:
            # Fallback to another provider if one fails
            print(f"Error with primary image generation: {str(e)}")
            return await self.generate_image_stability(prompt, **kwargs)

# Create a singleton instance
diffusion_service = DiffusionService()