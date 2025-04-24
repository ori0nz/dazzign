from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from app.schemas.node.base import NodeBase

# Schema for creating a new node
class NodeCreate(NodeBase):
    parent_id: Optional[int] = None
    request_params: Optional[Dict[str, Any]] = Field(default_factory=dict)
    image_base64: Optional[str] = None
    image_path: Optional[str] = None

# Schema for updating a node
class NodeUpdate(BaseModel):
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    spec_json: Optional[Dict[str, Any]] = None
    image_base64: Optional[str] = None
    image_path: Optional[str] = None

# Schema for query node lineage
class NodeLineage(BaseModel):
    ancestors: List[NodeBase] = Field(default_factory=list)
    descendants: List[NodeBase] = Field(default_factory=list)

# Schema for query root nodes
class RootNodes(BaseModel):
    nodes: List[NodeBase] = Field(default_factory=list)
    total: int
    page: int
    page_size: int 