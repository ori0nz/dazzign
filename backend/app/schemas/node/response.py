from pydantic import BaseModel, Field, ConfigDict, RootModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.schemas.node.base import NodeBase


def to_camel(string: str) -> str:
    return ''.join(word.capitalize() if i else word for i, word in enumerate(string.split('_')))

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
    
    model_config = ConfigDict(
        from_attributes=True,          # orm object to pydantic model
        alias_generator=to_camel,      
        populate_by_name=True          # support snake_case to camelCase
    )

    
# Schema for tree response
class NodeTreeResponse(RootModel):
    root: List[NodeResponse]
    
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True
    )
    
# Schema for root response
class RootNodesResponse(BaseModel):
    nodes: List[NodeResponse] = Field(default_factory=list)
    total: int
    page: int
    page_size: int 