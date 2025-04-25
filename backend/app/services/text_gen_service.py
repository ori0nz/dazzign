from typing import Dict, Any
import json
import logging
import os
import httpx
from dotenv import load_dotenv
from app.schemas.text_gen.domain import PCCaseAttributes, ToSpec

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class TextGenService:
    """Service for handling text-to-image conversions using LLM"""
    
    # OpenAI API credentials
    USE_FAKE_DATA = os.environ.get("USE_FAKE_DATA", "True").lower() == "true"
    API_KEY = os.environ.get("OPENAI_API_KEY")
    API_URL = "https://api.openai.com/v1/chat/completions"
    MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")
    
    @staticmethod
    async def text_to_image_attributes(prompt: str) -> ToSpec:
        """
        Convert free-form text to structured PC case design attributes using OpenAI
        """
        # LLM system prompt for attribute extraction
        system_prompt = """You are an AI assistant whose job is to extract structured PC case design attributes from a free-form user prompt.

                        Please extract the following attributes **as arrays of English strings**:

                        - color: Main and accent colors (e.g., "Black", "Red", "Navy Blue", "Gold").
                        - style: Design style or theme (e.g., "Minimalist", "Futuristic", "Steampunk", "Cthulhu-Ghibli").
                        - shape: Form factor or silhouette (e.g., "Mid-Tower", "Cube", "Spherical", "Open-Frame").
                        - material: Construction materials (e.g., "Aluminum", "Tempered Glass", "Wood", "Acrylic").
                        - ventilation: Vent and airflow features (e.g., "Mesh Front", "Side Vents", "Open-Air Design").
                        - lighting: Lighting setup (e.g., "ARGB Fans", "LED Strips", "Ambient Glow", "No Lighting").
                        - features: Functional features (e.g., "Water Cooling", "Vertical GPU Mount", "Cable Management", "LCD Display").
                        - environment: Visual setting or background (e.g., "Dark Room", "On a Gaming Desk", "Futuristic Lab").

                        You MUST follow these rules:
                        1. Return a **single JSON object** containing only the keys that were confidently extracted.
                        2. Each attribute must be represented as an **array** of strings, even if only one value is extracted.
                        3. All extracted values must be in **English**, even if the user input is in another language.
                        4. If no attribute can be extracted, return an **empty JSON object**: `{}`.
                        5. Do NOT add any explanations or extra text—output ONLY the JSON object.

                        Below are a few examples:"""
        
        few_shot_examples = """
                        User Prompt: "我想要一個木頭風格的中塔機殼，有RGB燈條和側邊透氣孔，內建水冷，整體走日系極簡風，擺在書桌上很好看"
                        Output:
                        {
                        "material": ["Wood"],
                        "shape": ["Mid-Tower"],
                        "lighting": ["RGB Lighting"],
                        "ventilation": ["Side Vents"],
                        "features": ["Water Cooling"],
                        "style": ["Minimalist", "Japanese"],
                        "environment": ["On a Desk"]
                        }

                        ---

                        User Prompt: "A cyberpunk cube case with open sides, neon ARGB glow, and vertical GPU mount. It should be small and look good in a dark gaming room."
                        Output:
                        {
                        "style": ["Cyberpunk"],
                        "shape": ["Cube", "Compact"],
                        "ventilation": ["Open-Air Design"],
                        "lighting": ["ARGB Lighting", "Neon"],
                        "features": ["Vertical GPU Mount"],
                        "environment": ["Dark Room", "Gaming Setup"]
                        }
                        """
        final_prompt = f"{system_prompt}\n\n{few_shot_examples}"

        try:
            # Check if we have OpenAI API access
            if not TextGenService.USE_FAKE_DATA:
                # Make API call to OpenAI
                attributes_dict = await TextGenService._call_openai_api(prompt, final_prompt)
            else:
                # Fallback to mock extraction if no API key
                logger.warning("No OpenAI API key found, using mock extraction")
                attributes_dict = TextGenService._mock_extract_attributes(prompt)
            
            # Convert the dictionary to our Pydantic model
            attributes = PCCaseAttributes(**attributes_dict)
            logger.info(f"Attributes: {attributes}")
            
            # Generate a structured prompt
            structured_prompt = TextGenService._create_structured_prompt(prompt, attributes)
            
            return ToSpec(
                prompt=prompt,
                attributes=attributes,
                structured_prompt=structured_prompt
            )
            
        except Exception as e:
            logger.error(f"Error in text_to_image conversion: {e}")
            # Return empty attributes in case of failure
            attributes = PCCaseAttributes()
            return ToSpec(
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
                    TextGenService.API_URL,
                    json={
                        "model": TextGenService.MODEL,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.1,
                    },
                    headers={"Authorization": f"Bearer {TextGenService.API_KEY}"},
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
        """Mock: Extract design attributes from prompt using keyword scanning."""
        attributes = {}
        prompt_lower = prompt.lower()

        # Keyword dictionaries
        shape_keywords = ["mid-tower", "cube", "spherical", "slim", "open-frame", "compact", "ultra-tower"]
        style_keywords = ["futuristic", "steampunk", "minimalist", "modern", "sleek", "industrial", "cthulhu", "ghibli"]
        color_keywords = ["black", "white", "red", "blue", "green", "silver", "gray", "gold", "brown", "navy"]
        material_keywords = ["aluminum", "tempered glass", "wood", "acrylic", "steel", "carbon fiber", "glass"]
        ventilation_keywords = ["mesh", "side vents", "open-air", "airflow", "intake", "cooling"]
        lighting_keywords = ["argb", "rgb", "led", "ambient glow", "neon", "illuminated", "no lighting"]
        feature_keywords = ["lcd", "handle", "psu shroud", "decorative", "water cooling", "cable management", "vertical gpu"]
        environment_keywords = [
            "dark room", "spotlight", "studio", "on a desk", "with peripherals", "in a showcase", "in a gaming setup",
            "cyberpunk city", "nature background", "futuristic lab"
        ]

        def match_and_append(attr, keywords, format_fn=lambda x: x.title()):
            for keyword in keywords:
                if keyword in prompt_lower:
                    attributes.setdefault(attr, []).append(format_fn(keyword))

        match_and_append("shape", shape_keywords)
        match_and_append("style", style_keywords)
        match_and_append("color", color_keywords)
        match_and_append("material", material_keywords)
        match_and_append("ventilation", ventilation_keywords)
        match_and_append("lighting", lighting_keywords, lambda x: x.upper() + " lighting" if x in ["rgb", "argb", "led"] else x.title())
        match_and_append("features", feature_keywords)
        match_and_append("environment", environment_keywords)

        return attributes


    @staticmethod
    def _create_structured_prompt(original_prompt: str, attributes: PCCaseAttributes) -> str:
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
