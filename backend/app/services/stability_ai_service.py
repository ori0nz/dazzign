import requests
import base64
import json
import os
import logging
from typing import Optional, Dict, Any, Union, Literal
from datetime import datetime
from fastapi import HTTPException
from io import BytesIO

logger = logging.getLogger(__name__)

class StabilityAIService:
    """Service for handling image generation using Stability AI's API"""
    
    def __init__(self):
        self.api_key = os.environ.get("STABILITY_API_KEY")
        if not self.api_key:
            logger.warning("No Stability AI API key found in environment variables")
    
    async def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = "",
        aspect_ratio: Optional[str] = "1:1",
        style_preset: Optional[str] = None,
        seed: Optional[int] = 0,
        output_format: Optional[Literal["webp", "jpeg", "png"]] = "jpeg",
        model: Optional[Literal["ultra", "core", "sd3.5-large", "sd3.5-large-turbo", "sd3.5-medium"]] = "core"
    ) -> Dict[str, Any]:
        """Generate an image using the Stability AI API"""
        if not self.api_key:
            logger.warning("Stability AI API key not set, cannot generate image")
            return None
            
        # Determine which endpoint to use based on the model
        if model == "ultra":
            host = "https://api.stability.ai/v2beta/stable-image/generate/ultra"
        elif model == "core":
            host = "https://api.stability.ai/v2beta/stable-image/generate/core"
        elif model.startswith("sd3.5"):
            host = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
        else:
            raise ValueError("Invalid model specified")
        
        # Prepare parameters
        params = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "aspect_ratio": aspect_ratio,
            "seed": seed,
            "output_format": output_format
        }
        
        # Add style preset if provided
        if style_preset:
            params["style_preset"] = style_preset
        
        # Add model if using SD3.5
        if model.startswith("sd3.5"):
            params["model"] = model
            params["mode"] = "text-to-image"
        
        try:
            # Send the request
            response = await self._send_generation_request(host, params, self.api_key)
            
            # Process the response
            response_data = await self._process_response(response)
            return response_data
        except Exception as e:
            logger.error(f"Error generating image with Stability AI: {str(e)}")
            raise
    
    async def _send_generation_request(self, host: str, params: Dict[str, Any], api_key: str, files=None):
        """Send a generation request to the Stability AI API"""
        headers = {
            "Accept": "image/*",
            "Authorization": f"Bearer {api_key}"
        }

        if files is None:
            files = {}

        # Handle any image/mask files if provided
        image = params.pop("image", None)
        mask = params.pop("mask", None)
        if image is not None and image != '' and isinstance(image, str):
            files["image"] = open(image, 'rb')
        if mask is not None and mask != '' and isinstance(mask, str):
            files["mask"] = open(mask, 'rb')
        if len(files) == 0:
            files["none"] = ''

        # Send request
        logger.info(f"Sending request to {host}")
        response = requests.post(
            host,
            headers=headers,
            files=files,
            data=params
        )
        
        if not response.ok:
            logger.error(f"API request failed: {response.status_code} - {response.text}")
            raise HTTPException(status_code=response.status_code, detail=response.text)

        return response

    async def _process_response(self, response):
        """Process the response from the Stability API"""
        output_image = response.content
        finish_reason = response.headers.get("finish-reason")
        seed = int(response.headers.get("seed", 0))
        
        # Check for NSFW classification
        if finish_reason == 'CONTENT_FILTERED':
            raise HTTPException(status_code=400, detail="Generation failed NSFW classifier")
        
        # Encode the image as base64
        base64_image = base64.b64encode(output_image).decode("utf-8")
        
        # Create response object
        response_data = {
            "image": base64_image,
            "seed": seed,
            "timestamp": datetime.now().isoformat()
        }
        
        return response_data
