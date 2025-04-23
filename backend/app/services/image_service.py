from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_, or_
from sqlalchemy.orm import selectinload
from app.models.image_node import ImageNode
from app.schemas import (
    ImageNodeCreate, 
    ImageLineage, 
    PCCaseAttributes, 
    TextToImageResponse
)
import json
import logging
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class ImageService:
    """Service for handling image generation and querying"""
    
    @staticmethod
    async def create_image(
        db: AsyncSession, 
        data: ImageNodeCreate, 
        image_base64: str
    ) -> ImageNode:
        """
        Create a new image node in the database
        """
        db_image = ImageNode(
            project_id=data.project_id,
            parent_id=data.parent_id,
            prompt=data.prompt,
            negative_prompt=data.negative_prompt,
            spec_json=data.spec_json,
            request_params=data.request_params,
            image_base64=image_base64,
            action_type=data.action_type
        )
        
        db.add(db_image)
        await db.commit()
        await db.refresh(db_image)
        return db_image
    
    @staticmethod
    async def get_image(db: AsyncSession, image_id: int) -> Optional[ImageNode]:
        """
        Get an image by ID
        """
        result = await db.execute(
            select(ImageNode).where(ImageNode.id == image_id)
        )
        return result.scalars().first()
    
    @staticmethod
    async def get_image_lineage(db: AsyncSession, image_id: int) -> ImageLineage:
        """
        Get the lineage (ancestors and descendants) of an image
        """
        # Get the target image with its parent relationship
        result = await db.execute(
            select(ImageNode)
            .where(ImageNode.id == image_id)
            .options(selectinload(ImageNode.parent))
        )
        image = result.scalars().first()
        
        if not image:
            return ImageLineage()
        
        # Get ancestors
        ancestors = []
        current = image.parent
        while current:
            ancestors.append(current)
            result = await db.execute(
                select(ImageNode)
                .where(ImageNode.id == current.parent_id)
                .options(selectinload(ImageNode.parent))
            )
            current = result.scalars().first()
        
        # Get descendants (all children)
        result = await db.execute(
            select(ImageNode)
            .where(ImageNode.parent_id == image_id)
            .options(selectinload(ImageNode.children))
        )
        descendants = result.scalars().all()
        
        # Collect all descendants recursively
        all_descendants = []
        all_descendants.extend(descendants)
        
        for descendant in descendants:
            child_result = await db.execute(
                select(ImageNode)
                .where(ImageNode.parent_id == descendant.id)
            )
            children = child_result.scalars().all()
            all_descendants.extend(children)
        
        return ImageLineage(
            ancestors=ancestors,
            descendants=all_descendants
        )
    
    @staticmethod
    async def get_project_images(
        db: AsyncSession, 
        project_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[ImageNode], int]:
        """
        Get all images for a project with pagination
        """
        # Get total count
        count_result = await db.execute(
            select(ImageNode)
            .where(ImageNode.project_id == project_id)
        )
        total = len(count_result.scalars().all())
        
        # Get paginated results
        result = await db.execute(
            select(ImageNode)
            .where(ImageNode.project_id == project_id)
            .order_by(desc(ImageNode.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        
        images = result.scalars().all()
        return images, total
        
    @staticmethod
    async def get_root_images(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[ImageNode], int]:
        """
        Get all root images (where parent_id is NULL)
        Optionally filter by project_id
        """
        # Build query conditions
        conditions = [ImageNode.parent_id == None]  # Root images have no parent
            
        # Get total count
        count_query = select(ImageNode).where(and_(*conditions))
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())
        
        # Get paginated results
        query = (
            select(ImageNode)
            .where(and_(*conditions))
            .order_by(desc(ImageNode.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        
        result = await db.execute(query)
        images = result.scalars().all()
        
        return images, total
        
    @staticmethod
    async def text_to_image_attributes(prompt: str) -> TextToImageResponse:
        """
        Convert free-form text to structured PC case design attributes using LLM
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
            # For development, use a mock response first
            # In production, replace with actual LLM API call
            
            # Mock implementation (in production, replace with actual LLM API call)
            # Check if we have LLM API access
            llm_api_key = os.environ.get("LLM_API_KEY")
            llm_api_url = os.environ.get("LLM_API_URL")
            
            if llm_api_key and llm_api_url:
                # Make actual API call to LLM
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        llm_api_url,
                        json={
                            "model": "gpt-4o", # or your preferred model
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.1,
                        },
                        headers={"Authorization": f"Bearer {llm_api_key}"},
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        content = result["choices"][0]["message"]["content"]
                        # Parse the JSON response from the LLM
                        attributes_dict = json.loads(content)
                    else:
                        logger.error(f"LLM API error: {response.status_code} - {response.text}")
                        # Fallback to empty attributes
                        attributes_dict = {}
            else:
                # Simple attribute extraction for development/fallback
                logger.warning("No LLM API credentials found, using mock extraction")
                attributes_dict = ImageService._mock_extract_attributes(prompt)
            
            # Convert the dictionary to our Pydantic model
            attributes = PCCaseAttributes(**attributes_dict)
            
            # Generate a structured prompt
            structured_prompt = ImageService._create_structured_prompt(prompt, attributes)
            
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
    def _mock_extract_attributes(prompt: str) -> dict:
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