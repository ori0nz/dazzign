from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_, text
from sqlalchemy.orm import selectinload
from app.models.node import Node
from app.schemas.node.domain import NodeCreate, NodeLineage, RootNodes
from app.schemas.node.response import NodeTreeResponse
import logging

logger = logging.getLogger(__name__)

class NodeService:
    """Service for node operations (create, get, list)"""
    
    @staticmethod
    async def create_node(
        db: AsyncSession, 
        data: NodeCreate, 
    ) -> Node:
        """
        Create a new node in the database
        """
        if data.parent_id is None:
            data.is_root = True
            
        db_node = Node(
            is_root=data.is_root,
            parent_id=data.parent_id,
            prompt=data.prompt,
            negative_prompt=data.negative_prompt,
            spec_json=data.spec_json,
            request_params=data.request_params,
            image_base64=data.image_base64,
            action_type=data.action_type
        )
        
        db.add(db_node)
        await db.commit()
        await db.refresh(db_node)
        return db_node
    
    @staticmethod
    async def get_node(db: AsyncSession, node_id: int) -> Optional[Node]:
        """
        Get a node by ID
        """
        result = await db.execute(
            select(Node).where(Node.id == node_id)
        )
        return result.scalars().first()
    
    @staticmethod
    async def get_node_tree(db: AsyncSession, node_id: int) -> Optional[NodeTreeResponse]:
        """
        Get a node and all its descendants as a tree structure
        """
        # First check if the node exists
        node = await NodeService.get_node(db, node_id)
        if not node:
            return None
            
        # Get all descendants using recursive CTE
        sql = text("""
                    WITH RECURSIVE descendants AS (
                        SELECT * FROM nodes WHERE id = :node_id
                        UNION ALL
                        SELECT n.* FROM nodes n
                        JOIN descendants d ON n.parent_id = d.id
                    )
                    SELECT * FROM descendants;
                """)
        
        result = await db.execute(sql, {"node_id": node_id})
        rows = result.mappings().all()  
        # logger.info(f"rows: {rows}")

        return rows
    
    @staticmethod
    async def get_root_nodes(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Node], int]:
        """
        Get all root nodes (where parent_id is NULL or is_root is True)
        """
        # Build query conditions - either parent_id is NULL or is_root is True
        conditions = [Node.is_root == True]
            
        # Get total count
        count_query = select(Node).where(and_(*conditions))
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())
        
        # Get paginated results
        query = (
            select(Node)
            .where(and_(*conditions))
            .order_by(desc(Node.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        
        result = await db.execute(query)
        nodes = result.scalars().all()
        
        return nodes, total 