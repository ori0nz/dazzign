from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.node.base import NodeBase
from app.schemas.node.domain import NodeCreate, NodeLineage, RootNodes
from app.schemas.text_gen.reponse import ToSpecResponse
from app.models.node import Node
from app.services.image_gen_service import ImageGenService
from app.services.node_service import NodeService
from app.services.text_gen_service import TextGenService
import logging

logger = logging.getLogger(__name__)

class FacadeService:
    """Facade service that coordinates other specialized services"""
    
    @staticmethod
    async def create_node(
        db: AsyncSession, 
        data: NodeCreate, 
        image_base64: str
    ) -> Node:
        """Create a new node in the database"""
        return await NodeService.create_node(db, data, image_base64)
    
    @staticmethod
    async def get_node(db: AsyncSession, node_id: int) -> Optional[Node]:
        """Get a node by ID"""
        return await NodeService.get_node(db, node_id)
    
    @staticmethod
    async def get_node_lineage(db: AsyncSession, node_id: int) -> NodeLineage:
        """Get the lineage (ancestors and descendants) of a node"""
        return await NodeService.get_node_lineage(db, node_id)
    
    @staticmethod
    async def get_root_nodes(db: AsyncSession, page: int = 1, page_size: int = 20):
        """Get all root nodes (with is_root=True)"""
        return await NodeService.get_root_nodes(db, page, page_size)
    
    @staticmethod
    async def text_to_image_attributes(prompt: str) -> ToSpecResponse:
        """Convert free-form text to structured PC case design attributes using LLM"""
        return await TextGenService.text_to_image_attributes(prompt)
    
    @staticmethod
    async def generate_image(prompt: str, structured_prompt: Optional[str] = None) -> str:
        """Generate an image from a prompt"""
        return await ImageGenService.generate_image(prompt, structured_prompt)
    
    @staticmethod
    async def prepare_generation_data(
        prompt: str, 
        negative_prompt: Optional[str] = None,
        structured_prompt: Optional[str] = None,
        parent_id: Optional[int] = None,
        is_root: bool = False
    ) -> NodeCreate:
        """Prepare data for node creation with image generation"""
        return await ImageGenService.prepare_generation_data(
            prompt, 
            negative_prompt, 
            structured_prompt, 
            parent_id,
            is_root
        ) 