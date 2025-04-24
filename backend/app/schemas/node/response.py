from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.schemas.node.base import NodeBase

# Schema for DB response
class NodeResponse(NodeBase):
    id: int
    is_root: bool
    parent_id: Optional[int] = None
    prompt: str
    negative_prompt: Optional[str] = None
    spec_json: Optional[Dict[str, Any]] = None
    request_params: Optional[Dict[str, Any]] = None
    image_base64: Optional[str] = None
    image_path: Optional[str] = None
    action_type: str
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }

# Schema for node with children (recursive tree structure)
class NodeWithChildren(NodeResponse):
    children: List["NodeWithChildren"] = Field(default_factory=list)
    
# Resolve forward reference
NodeWithChildren.model_rebuild()
    
# Schema for tree response
class NodeTreeResponse(BaseModel):
    tree: NodeWithChildren
    
# Schema for root response
class RootNodesResponse(BaseModel):
    nodes: List[NodeResponse] = Field(default_factory=list)
    total: int
    page: int
    page_size: int 