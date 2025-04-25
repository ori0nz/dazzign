import logging
import base64
import os
from typing import Optional
from app.schemas import NodeBase, PCCaseAttributes
import random

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
        use_fake_data = os.environ.get("USE_FAKE_DATA", "True").lower() == "true"
        
        if not use_fake_data:
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
        spec_json: Optional[PCCaseAttributes] = None,
        parent_id: Optional[int] = None,
    ) -> NodeBase:
        """
        Prepare data for image generation and database storage
        """
        # Create image data object

        image_data = NodeBase(
            parent_id=parent_id,
            prompt=prompt,
            negative_prompt=negative_prompt,
            spec_json=spec_json.model_dump() if spec_json else None,
            action_type="generate"
        )
        
        return image_data
    
    @staticmethod
    async def create_structured_prompt(attributes: PCCaseAttributes) -> str:
        """Create a natural-language prompt based on attribute template mapping."""

        parts = ["A high-resolution render of"]

        # Shape and Style
        if attributes.shape:
            shape_desc = f"a {' and '.join(attributes.shape)} PC case"
        else:
            shape_desc = "a PC case"

        if attributes.style:
            style_desc = f"with a {' and '.join(attributes.style)} aesthetic"
            parts.append(f"{shape_desc} {style_desc}")
        else:
            parts.append(shape_desc)

        # Materials
        if attributes.material:
            parts.append(f"made of {' and '.join(attributes.material)}")

        # Ventilation
        if attributes.ventilation:
            parts.append(f"featuring {' and '.join(attributes.ventilation)}")

        # Lighting
        if attributes.lighting:
            parts.append(f"illuminated by {' and '.join(attributes.lighting)}")

        # Features
        if attributes.features:
            parts.append(f"including {' and '.join(attributes.features)}")

        # Environment
        if attributes.environment:
            parts.append(f"set in {' and '.join(attributes.environment)}")

        # Final composition
        prompt = "; ".join(parts) + "."
        return prompt
    
    @staticmethod
    def _get_mock_image() -> str:
        """Return a mock image for development/testing"""
        mock_images = [
            # 1x1 transparent PNG
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==",
            # small JPG
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
            # ".
            "iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII",
            # Blue
            "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAFUlEQVR42mNkYPhfz0AEYBxVSF+FAP5FDvcfRYWgAAAAAElFTkSuQmCC"
        ]
        return random.choice(mock_images)