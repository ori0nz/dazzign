from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

# Schema for image generation request
class ImageGenerateRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    spec_json: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    parent_id: Optional[int] = None

# Schema for text-to-image request
class TextToImageRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    parent_id: Optional[int] = None 