from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import (
    ImageNodeCreate, 
    ImageNode,
    ImageLineage,
    TextToImageResponse
)
from app.services.text_service import TextService
from app.services.node_service import NodeService
from app.services.image_generation_service import ImageGenerationService
import logging

logger = logging.getLogger(__name__)

class ImageService:
    """Facade service that coordinates other specialized services (DEPRECATED: Use FacadeService instead)"""
    
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
        return await TextService.text_to_image_attributes(prompt)
    
    @staticmethod
    async def generate_image(prompt: str, structured_prompt: Optional[str] = None) -> str:
        """Generate an image from a prompt"""
        return await ImageGenerationService.generate_image(prompt, structured_prompt)
    
    @staticmethod
    async def prepare_generation_data(
        prompt: str, 
        negative_prompt: Optional[str] = None,
        structured_prompt: Optional[str] = None,
        parent_id: Optional[int] = None,
        project_id: int = 1
    ) -> ImageNodeCreate:
        """Prepare data for image generation"""
        return await ImageGenerationService.prepare_generation_data(
            prompt, 
            negative_prompt, 
            structured_prompt, 
            parent_id, 
            project_id
        ) 