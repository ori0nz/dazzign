from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from app.db.session import get_db
from app.schemas import GenerateImageRequest, GenerateImageResponse
from app.services import NodeService, ImageGenService
from app.services.image_gen_service import ImageProvider
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/generate", response_model=GenerateImageResponse, status_code=201)
async def generate_image(
    request: GenerateImageRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Generate a new image based on the provided prompt
    """
    try:

        negative_prompt = "text, logo, watermark, signature, blurry, lowres, noisy, grainy"
        
        # Prepare data for image generation
        image_data = await ImageGenService.prepare_generation_data(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            spec_json=request.spec_json,
            parent_id=request.parent_id,
            action_type=request.action_type,
        )

        
        
        # Generate the structured prompt
        structured_prompt = await ImageGenService.create_structured_prompt(request.spec_json)

        image_data.request_params = {
            "prompt": structured_prompt,
            "negative_prompt": negative_prompt,
        }
        # Generate the image
        image_service = ImageGenService()
        # Provider has 3 options: STABILITY_AI, AWS_NOVA, MOCK
        image_base64 = await image_service.generate_image(prompt=structured_prompt, 
                                                            negative_prompt=negative_prompt,
                                                            output_format="jpeg",
                                                            seed=202,
                                                            provider=ImageProvider.STABILITY_AI)
        image_data.image_base64 = image_base64

        # Create image in database
        db_image = await NodeService.create_node(
            db, 
            image_data,
        )
        
        return db_image
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate image"
        ) 