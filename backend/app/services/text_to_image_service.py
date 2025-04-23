from typing import Dict, Any
import json
import logging
import os
import httpx
from dotenv import load_dotenv
from app.schemas import PCCaseAttributes, TextToImageResponse

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class TextToImageService:
    """Service for handling text-to-image conversions using LLM"""
    
    # OpenAI API credentials
    API_KEY = os.environ.get("OPENAI_API_KEY")
    API_URL = "https://api.openai.com/v1/chat/completions"
    MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")
    
    @staticmethod
    async def text_to_image_attributes(prompt: str) -> TextToImageResponse:
        """
        Convert free-form text to structured PC case design attributes using OpenAI
        """
        # LLM system prompt for attribute extraction
        system_prompt = """You are an AI assistant whose job is to extract structured PC case design attributes from a free‑form user description.

                        Define each attribute as follows:
                        - color: The primary and accent colors the user wants for the case.
                        - style: The overall design style, such as "Minimalist," "Futuristic," "Retro," "Industrial," "Gaming," etc.
                        - shape: The silhouette or contour of the case, e.g. "Rectangular," "Curved," "Angled," "Rounded," "Asymmetric."
                        - material: The main construction material, such as "Aluminum," "Tempered Glass," "Steel," "Plastic," "Carbon Fiber."
                        - ventilation: The cooling or airflow features, e.g. "Mesh Front," "Side Vents," "Top Vent."
                        - lighting: Any lighting elements, for example "ARGB Fans," "LED Strips," "Underglow."
                        - features: Additional functional features like "Tool‑less Design," "Vertical GPU Mount," "Cable Management," "Modular Panels," "Dust Filters," "Silent Operation."

                        When you receive a user prompt, you MUST:
                        1. Map any mentioned design details to the above attributes.
                        2. Always output each extracted attribute as an **array** of strings, even if there is only one value.
                        3. Output a single JSON object containing only the keys for attributes you successfully extracted.
                        4.Omit any attribute entirely if it is not mentioned or cannot be extracted.
                        5. If you cannot extract any attribute, return an empty JSON object: `{}`.
                        6.Always represent extracted attribute values in English in the JSON output, regardless of whether the user wrote them in any language.
                        7. Do NOT output any extra text or explanation—only the JSON object."""

        try:
            # Check if we have OpenAI API access
            if TextToImageService.API_KEY:
                # Make API call to OpenAI
                attributes_dict = await TextToImageService._call_openai_api(prompt, system_prompt)
            else:
                # Fallback to mock extraction if no API key
                logger.warning("No OpenAI API key found, using mock extraction")
                attributes_dict = TextToImageService._mock_extract_attributes(prompt)
            
            # Convert the dictionary to our Pydantic model
            attributes = PCCaseAttributes(**attributes_dict)
            
            # Generate a structured prompt
            structured_prompt = TextToImageService._create_structured_prompt(prompt, attributes)
            
            return TextToImageResponse(
                prompt=prompt,
                attributes=attributes,
                structured_prompt=structured_prompt
            )
            
        except Exception as e:
            logger.error(f"Error in text_to_image conversion: {e}")
            # Return empty attributes in case of failure
            attributes = PCCaseAttributes()
            return TextToImageResponse(
                prompt=prompt,
                attributes=attributes,
                structured_prompt=prompt
            )
    
    @staticmethod
    async def _call_openai_api(prompt: str, system_prompt: str) -> Dict[str, Any]:
        """Call OpenAI API to extract attributes from text"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    TextToImageService.API_URL,
                    json={
                        "model": TextToImageService.MODEL,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.1,
                    },
                    headers={"Authorization": f"Bearer {TextToImageService.API_KEY}"},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    # Parse the JSON response from the LLM
                    return json.loads(content)
                else:
                    logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                    # Return empty dict on error
                    return {}
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return {}
    
    @staticmethod
    def _mock_extract_attributes(prompt: str) -> Dict[str, Any]:
        """Simple attribute extraction for development/testing"""
        attributes = {}
        
        prompt_lower = prompt.lower()
        
        # Simple keyword matching for mock extraction
        color_keywords = ["black", "white", "red", "blue", "green", "silver", "gray", "grey", "purple", "pink", "orange"]
        style_keywords = ["minimalist", "futuristic", "retro", "industrial", "gaming", "modern", "sleek"]
        material_keywords = ["glass", "aluminum", "steel", "plastic", "carbon fiber", "wood", "tempered glass"]
        shape_keywords = ["rectangular", "curved", "angled", "rounded", "square", "compact"]
        lighting_keywords = ["rgb", "argb", "led", "light", "glow", "illuminated"]
        ventilation_keywords = ["mesh", "vent", "airflow", "cooling", "fan"]
        feature_keywords = ["cable management", "tool-less", "dust filter", "silent", "modular", "vertical gpu"]
        
        # Extract attributes using simple keyword matching
        for keyword in color_keywords:
            if keyword in prompt_lower:
                if "color" not in attributes:
                    attributes["color"] = []
                attributes["color"].append(keyword.title())
                
        for keyword in style_keywords:
            if keyword in prompt_lower:
                if "style" not in attributes:
                    attributes["style"] = []
                attributes["style"].append(keyword.title())
                
        for keyword in material_keywords:
            if keyword in prompt_lower:
                if "material" not in attributes:
                    attributes["material"] = []
                attributes["material"].append(keyword.title().replace("Tempered Glass", "Tempered Glass"))
                
        for keyword in shape_keywords:
            if keyword in prompt_lower:
                if "shape" not in attributes:
                    attributes["shape"] = []
                attributes["shape"].append(keyword.title())
                
        for keyword in lighting_keywords:
            if keyword in prompt_lower:
                if "lighting" not in attributes:
                    attributes["lighting"] = []
                if keyword.upper() in ["RGB", "ARGB", "LED"]:
                    attributes["lighting"].append(keyword.upper() + " Lighting")
                else:
                    attributes["lighting"].append(keyword.title())
                
        for keyword in ventilation_keywords:
            if keyword in prompt_lower:
                if "ventilation" not in attributes:
                    attributes["ventilation"] = []
                attributes["ventilation"].append(keyword.title())
                
        for keyword in feature_keywords:
            if keyword in prompt_lower:
                if "features" not in attributes:
                    attributes["features"] = []
                attributes["features"].append(keyword.title())
                
        return attributes
    
    @staticmethod
    def _create_structured_prompt(original_prompt: str, attributes: PCCaseAttributes) -> str:
        """Create a structured prompt for the image generation model"""
        prompt_parts = [original_prompt, "Details:"]
        
        if attributes.color:
            prompt_parts.append(f"Color: {', '.join(attributes.color)}")
            
        if attributes.style:
            prompt_parts.append(f"Style: {', '.join(attributes.style)}")
            
        if attributes.shape:
            prompt_parts.append(f"Shape: {', '.join(attributes.shape)}")
            
        if attributes.material:
            prompt_parts.append(f"Material: {', '.join(attributes.material)}")
            
        if attributes.ventilation:
            prompt_parts.append(f"Ventilation: {', '.join(attributes.ventilation)}")
            
        if attributes.lighting:
            prompt_parts.append(f"Lighting: {', '.join(attributes.lighting)}")
            
        if attributes.features:
            prompt_parts.append(f"Features: {', '.join(attributes.features)}")
            
        return "\n".join(prompt_parts) 