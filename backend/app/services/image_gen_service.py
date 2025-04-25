import logging
import base64
import os
from typing import Optional, Dict, Any, Literal
from app.schemas import NodeBase, PCCaseAttributes
import random
from enum import Enum

from app.services.stability_ai_service import StabilityAIService
from app.services.aws_nova_service import AWSNovaService

logger = logging.getLogger(__name__)

class ImageProvider(str, Enum):
    STABILITY_AI = "stability_ai"
    AWS_NOVA = "aws_nova"  # Placeholder for future implementation
    MOCK = "mock"

class ImageGenService:
    """Service for handling image generation using AI models"""
    
    def __init__(self):
        self.stability_service = StabilityAIService()
        self.nova_service = AWSNovaService()
    
    async def generate_image(self, prompt: str, 
                             negative_prompt: Optional[str] = None, 
                             seed: Optional[int] = 202,
                             output_format: Optional[Literal["webp", "jpeg", "png"]] = "jpeg",
                             provider: Optional[ImageProvider] = None,
                             model: Optional[str] = None) -> str:
        """
        Generate an image based on the provided prompt
        Returns base64 encoded image data
        
        Args:
            prompt: The main text prompt
            structured_prompt: Optional pre-structured prompt that overrides the main prompt
            negative_prompt: Text to guide what should not appear in the image
            seed: Random seed for reproducibility
            output_format: Image format (webp, jpeg, png)
            provider: Explicitly specify which provider to use
            model: The model to use for generation
        
        Returns:
            Base64 encoded image data
        """
        # Use structured prompt if available, otherwise use original prompt
        # generation_prompt = structured_prompt or prompt
        
        # Check if USE_FAKE_DATA is true - this overrides any provider setting
        use_fake_data = os.environ.get("USE_FAKE_DATA", "True").lower() == "true"
        if use_fake_data:
            logger.info("USE_FAKE_DATA is true, forcing mock provider")
            provider = ImageProvider.MOCK
        
        if provider == ImageProvider.STABILITY_AI:
            try:
                result = await self.stability_service.generate_image(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    aspect_ratio="1:1",
                    style_preset="3d-model",
                    seed=seed,
                    output_format=output_format,
                    model="core"
                )
                if result and "image" in result:
                    return result["image"]
                logger.error("Failed to generate image with Stability AI")
            except Exception as e:
                logger.error(f"Error generating image with Stability AI: {str(e)}")
                
        elif provider == ImageProvider.AWS_NOVA:
            try:
                result = await self.nova_service.generate_image(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    aspect_ratio="1:1",
                    style_preset="3d-model",
                    seed=seed,
                    output_format=output_format,
                    model=model
                )
                if result and "image" in result:
                    return result["image"]
                logger.error("Failed to generate image with AWS Nova")
            except Exception as e:
                logger.error(f"Error generating image with AWS Nova: {str(e)}")
                
        # Default to mock image if provider fails or is set to mock
        logger.warning("Using mock image for generation")
        return self._get_mock_image()
    
    @staticmethod
    async def prepare_generation_data(
        prompt: str, 
        negative_prompt: Optional[str] = None,
        spec_json: Optional[PCCaseAttributes] = None,
        parent_id: Optional[int] = None,
        action_type: Optional[str] = None,
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
            # Red
            "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAFUlEQVR42mP8z8BQz0AEYBxVSF+FABJADveWkH6oAAAAAElFTkSuQmCC"
            # Green
            "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAFUlEQVR42mNk+M9Qz0AEYBxVSF+FAAhKDveksOjmAAAAAElFTkSuQmCC",
            # Blue
            "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAFUlEQVR42mNkYPhfz0AEYBxVSF+FAP5FDvcfRYWgAAAAAElFTkSuQmCC"
        ]
        return random.choice(mock_images)