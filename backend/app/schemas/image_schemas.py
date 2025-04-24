from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

# Schema for image generation request
class ImageGenerateRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    spec_json: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    parent_id: Optional[int] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "prompt": "A modern PC case with RGB lighting",
                "negative_prompt": "blurry, distorted",
                "spec_json": {"width": 512, "height": 512},
                "parent_id": None
            }
        }
    } 