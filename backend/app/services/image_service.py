from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_, or_
from sqlalchemy.orm import selectinload
from app.models.image_node import ImageNode
from app.schemas import (
    ImageNodeCreate, 
    ImageNode,
    ImageLineage,
    PCCaseAttributes,
    TextToImageResponse
)
from app.services.text_to_image_service import TextToImageService
from app.services.node_service import NodeService
from app.services.generation_service import GenerationService
import json
import logging
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class ImageService:
    """Facade service that coordinates other specialized services"""
    
    @staticmethod
    async def create_image(
        db: AsyncSession, 
        data: ImageNodeCreate, 
        image_base64: str
    ) -> ImageNode:
        """Create a new image node in the database"""
        return await NodeService.create_image(db, data, image_base64)
    
    @staticmethod
    async def get_image(db: AsyncSession, image_id: int) -> Optional[ImageNode]:
        """Get an image by ID"""
        return await NodeService.get_image(db, image_id)
    
    @staticmethod
    async def get_image_lineage(db: AsyncSession, image_id: int) -> ImageLineage:
        """Get the lineage (ancestors and descendants) of an image"""
        return await NodeService.get_image_lineage(db, image_id)
    
    @staticmethod
    async def get_project_images(db: AsyncSession, project_id: int, page: int = 1, page_size: int = 20):
        """Get all images for a project with pagination"""
        return await NodeService.get_project_images(db, project_id, page, page_size)
    
    @staticmethod
    async def get_root_images(db: AsyncSession, page: int = 1, page_size: int = 20):
        """Get all root images (with no parent)"""
        return await NodeService.get_root_images(db, page, page_size)
    
    @staticmethod
    async def text_to_image_attributes(prompt: str) -> TextToImageResponse:
        """Convert free-form text to structured PC case design attributes using LLM"""
        return await TextToImageService.text_to_image_attributes(prompt)
    
    @staticmethod
    async def generate_image(prompt: str, structured_prompt: Optional[str] = None) -> str:
        """Generate an image from a prompt"""
        return await GenerationService.generate_image(prompt, structured_prompt)
    
    @staticmethod
    async def prepare_generation_data(
        prompt: str, 
        negative_prompt: Optional[str] = None,
        structured_prompt: Optional[str] = None,
        parent_id: Optional[int] = None,
        project_id: int = 1
    ) -> ImageNodeCreate:
        """Prepare data for image generation"""
        return await GenerationService.prepare_generation_data(
            prompt, 
            negative_prompt, 
            structured_prompt, 
            parent_id, 
            project_id
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