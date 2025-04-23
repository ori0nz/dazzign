from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from app.db.session import get_db
from app.schemas import (
    ImageGenerateRequest, 
    ImageNode, 
    ImageLineage, 
    RootImages, 
    TextToImageRequest, 
    TextToImageResponse
)
from app.services.image_service import ImageService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Mock image generation for MVP (in real app, this would call an AI model)
async def mock_generate_image(prompt: str) -> str:
    """
    Mock function to simulate image generation
    Returns a base64 encoded placeholder image
    """
    # This is a tiny 1x1 transparent pixel in base64
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

@router.post("/generate", response_model=ImageNode, status_code=201)
async def generate_image(
    request: ImageGenerateRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Generate a new image based on the provided prompt
    """
    try:
        # Prepare data for image generation
        image_data = await ImageService.prepare_generation_data(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            parent_id=request.parent_id,
            project_id=1  # Default project ID for now
        )
        
        # Generate the image
        image_base64 = await ImageService.generate_image(request.prompt)
        
        # Create image in database
        db_image = await ImageService.create_image(
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

@router.post("/text-to-image", response_model=TextToImageResponse)
async def text_to_image(
    request: TextToImageRequest
) -> Any:
    """
    Convert free-form text to structured PC case design attributes
    """
    try:
        # Process the prompt through LLM to extract attributes
        result = await ImageService.text_to_image_attributes(request.prompt)
        return result
        
    except Exception as e:
        logger.error(f"Error in text-to-image conversion: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process text-to-image conversion"
        )

@router.get("/{image_id}", response_model=ImageNode)
async def get_image(
    image_id: int,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get a single image by ID
    """
    image = await ImageService.get_image(db, image_id)
    
    if not image:
        raise HTTPException(
            status_code=404,
            detail=f"Image with ID {image_id} not found"
        )
        
    return image

@router.get("/{image_id}/lineage", response_model=ImageLineage)
async def get_image_lineage(
    image_id: int,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get the lineage (ancestors and descendants) of an image
    """
    # Check if image exists
    image = await ImageService.get_image(db, image_id)
    
    if not image:
        raise HTTPException(
            status_code=404,
            detail=f"Image with ID {image_id} not found"
        )
    
    # Get lineage
    lineage = await ImageService.get_image_lineage(db, image_id)
    return lineage

@router.get("/root/list", response_model=RootImages)
async def list_root_images(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    List all root images (images with no parent)
    """
    try:
        images, total = await ImageService.get_root_images(
            db,
            page=page,
            page_size=page_size
        )
        
        return RootImages(
            images=images,
            total=total,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        logger.error(f"Error fetching root images: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch root images"
        ) 