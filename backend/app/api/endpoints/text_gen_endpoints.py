from fastapi import APIRouter, HTTPException, Form, File, UploadFile
from typing import Any, Optional
from typing import Any
from app.schemas import ToSpecRequest, ToSpecResponse
from app.services import TextGenService
import logging
from pydantic import ValidationError
import base64
logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/to-spec", response_model=ToSpecResponse)
async def text_to_image(
    prompt: Optional[str] = Form(None),
    negative_prompt: Optional[str] = Form(None),
    parent_id: Optional[int] = Form(None),
    image_file: UploadFile = File(None)
) -> Any:
    """
    Convert free-form text to structured PC case design attributes
    """
    logger.info(f"prompt: {prompt}")
    logger.info(f"image_file: {image_file}")
    
    if not prompt and not image_file:
        raise HTTPException(status_code=422, detail="At least one of 'prompt' or 'image_file' must be provided.")

    try:
        spec_request = ToSpecRequest(
            prompt=prompt,
            negative_prompt=negative_prompt,
            parent_id=parent_id
        )
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    
    image_attributes = None
    text_attributes = None
    
    if image_file:
        # todo: mpv stage handle here but need to move to image gen service

        try:
            image_base64 = await image_file.read()
            image_base64 = base64.b64encode(image_base64).decode('utf-8')
            logger.info(f"starting image-to-attributes conversion")
            image_attributes = await TextGenService.text_to_image_attributes(prompt=spec_request.prompt, image_base64=image_base64, provider="claude", model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0")
            logger.info(f"image-to-attributes conversion complete")
        except Exception as e:
            logger.error(f"Error in image-to-attributes conversion: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to process image-to-attributes conversion"
            )

    if prompt:
        try:
            # Process the prompt through LLM to extract attributes
            text_attributes = await TextGenService.text_to_image_attributes(spec_request.prompt, provider="nova", model_id="us.amazon.nova-pro-v1:0")
            
        except Exception as e:
            logger.error(f"Error in text-to-image conversion: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to process text-to-image conversion"
            ) 
    
    logger.info(f"text_attributes: {text_attributes}")
    logger.info(f"image_attributes: {image_attributes}")
        
    if image_attributes and text_attributes:
        merged_attributes = await TextGenService.merge_attributes(text_attributes, image_attributes)
        return merged_attributes
    
    elif image_attributes:
        return image_attributes
    
    else:
        return text_attributes