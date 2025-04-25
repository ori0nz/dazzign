from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from app.db.session import get_db
from app.schemas.node.response import NodeResponse, RootNodesResponse, NodeTreeResponse
from app.schemas.node.request import RootNodesRequest, NodeCreateRequest
from app.services.node_service import NodeService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/root", response_model=RootNodesResponse)
async def list_root_nodes(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    List all root nodes (nodes with no parent)
    """
    
    try:
        nodes, total = await NodeService.get_root_nodes(
            db,
            page=page,
            page_size=page_size
        )
        
        return RootNodesResponse(
            nodes=nodes,
            total=total,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        logger.error(f"Error fetching root nodes: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch root nodes"
        )

@router.get("/{node_id}", response_model=NodeResponse)
async def get_node(
    node_id: int,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get a single node by ID
    """
    node = await NodeService.get_node(db, node_id)
    
    if not node:
        raise HTTPException(
            status_code=404,
            detail=f"node with ID {node_id} not found"
        )
        
    return node

@router.get("/{node_id}/tree", response_model=NodeTreeResponse)
async def get_node_tree(
    node_id: int,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get a node and all its descendants as a nested tree structure
    """
    # Get the tree
    tree = await NodeService.get_node_tree(db, node_id)
    
    if not tree:
        raise HTTPException(
            status_code=404,
            detail=f"node with ID {node_id} not found"
        )
    
    return tree

@router.post("/", response_model=NodeResponse)
async def create_node(
    node: NodeCreateRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Create a new node
    """
    try:
        new_node = await NodeService.create_node(db, node)
        return new_node
    except Exception as e:
        logger.error(f"Error creating node: {e}")
        raise HTTPException(status_code=500, detail="Failed to create node")