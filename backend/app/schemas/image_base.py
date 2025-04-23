from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

# Base schema with common attributes
class ImageNodeBase(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    spec_json: Optional[Dict[str, Any]] = Field(default_factory=dict)
    action_type: str = "generate"
    
# Schema for creating a new image
class ImageNodeCreate(ImageNodeBase):
    parent_id: Optional[int] = None
    request_params: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
# Schema for DB response
class ImageNode(ImageNodeBase):
    id: int
    parent_id: Optional[int] = None
    image_base64: str
    image_path: Optional[str] = None
    request_params: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True 