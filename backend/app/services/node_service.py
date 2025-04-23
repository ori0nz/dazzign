from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from sqlalchemy.orm import selectinload
from app.models.image_node import ImageNode
from app.schemas import ImageNodeCreate, ImageLineage
import logging

logger = logging.getLogger(__name__)

class NodeService:
    """Service for handling image node operations (create, get, list)"""
    
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