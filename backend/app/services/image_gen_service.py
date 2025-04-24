import logging
import base64
import os
from typing import Optional
from app.schemas import NodeCreate

logger = logging.getLogger(__name__)

class ImageGenService:
    """Service for handling image generation using AI models"""
    
    @staticmethod
    async def generate_image(prompt: str, structured_prompt: Optional[str] = None) -> str:
        """
        Generate an image based on the provided prompt
        Returns base64 encoded image data
        
        In a real implementation, this would call a Stable Diffusion or similar model
        """
        # Use structured prompt if available, otherwise use original prompt
        generation_prompt = structured_prompt or prompt
        
        # For now, this is just a placeholder that returns a mock image
        # In a real implementation, this would call an AI model API
        
        # Check if we have image generation API credentials
        api_key = os.environ.get("IMAGE_GEN_API_KEY")
        
        if api_key:
            # In a real implementation, make API call to image generation service
            # For now, just log that we would call the API
            logger.info(f"Would call image generation API with prompt: {generation_prompt}")
            
            # Return mock image
            return ImageGenService._get_mock_image()
        else:
            # No API credentials, return mock image
            logger.warning("No image generation API credentials found, returning mock image")
            return ImageGenService._get_mock_image()
    
    @staticmethod
    async def prepare_generation_data(
        prompt: str, 
        negative_prompt: Optional[str] = None,
        structured_prompt: Optional[str] = None,
        parent_id: Optional[int] = None,
        project_id: int = 1
    ) -> NodeCreate:
        """
        Prepare data for image generation and database storage
        """
        # Create image data object
        spec_json = {}
        if structured_prompt:
            # If we have structured prompt, extract attributes to spec_json
            lines = structured_prompt.split("\n")
            for line in lines:
                if ":" in line and line.startswith(("Color:", "Style:", "Shape:", "Material:", "Ventilation:", "Lighting:", "Features:")):
                    key, value = line.split(":", 1)
                    spec_json[key.strip().lower()] = value.strip()
        
        image_data = ImageNodeCreate(
            project_id=project_id,
            parent_id=parent_id,
            prompt=prompt,
            negative_prompt=negative_prompt,
            spec_json=spec_json,
            request_params={
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "structured_prompt": structured_prompt
            },
            action_type="generate"
        )
        
        return image_data
    
    @staticmethod
    def _get_mock_image() -> str:
        """Return a mock image for development/testing"""
        # This is a tiny 1x1 transparent pixel in base64
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==" 