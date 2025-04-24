from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from app.db.session import get_db
from app.schemas import ImageGenerateRequest, NodeBase
from app.services import NodeService, ImageGenService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/generate", response_model=NodeBase, status_code=201)
async def generate_image(
    request: ImageGenerateRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Generate a new image based on the provided prompt
    """
    try:
        # Prepare data for image generation
        image_data = await ImageGenService.prepare_generation_data(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            parent_id=request.parent_id,
            project_id=1  # Default project ID for now
        )
        
        # Generate the image
        image_base64 = await ImageGenService.generate_image(request.prompt)
        
        # Create image in database
        db_image = await NodeService.create_image(
            db, 
            image_data, 
            image_base64
        )
        
        return db_image
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate image"
        ) 