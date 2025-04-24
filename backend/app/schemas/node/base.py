from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

# Base schema with common attributes
class NodeBase(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    spec_json: Optional[Dict[str, Any]] = Field(default_factory=dict)
    action_type: str = "generate"
    is_root: bool = False
    parent_id: Optional[int] = None
    request_params: Optional[Dict[str, Any]] = Field(default_factory=dict)
    image_base64: Optional[str] = None
    image_path: Optional[str] = None
