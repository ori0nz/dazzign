from fastapi import APIRouter, HTTPException
from typing import Any
from app.schemas import TextToImageRequest, TextToImageResponse
from app.services import TextGenService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/text-to-image", response_model=TextToImageResponse)
async def text_to_image(
    request: TextToImageRequest
) -> Any:
    """
    Convert free-form text to structured PC case design attributes
    """
    try:
        # Process the prompt through LLM to extract attributes
        result = await TextGenService.text_to_image_attributes(request.prompt)
        return result
        
    except Exception as e:
        logger.error(f"Error in text-to-image conversion: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process text-to-image conversion"
        ) 