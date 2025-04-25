from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

def to_camel(string: str) -> str:
    return ''.join(word.capitalize() if i else word for i, word in enumerate(string.split('_')))

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

    model_config = ConfigDict(
        from_attributes=True, 
        alias_generator=to_camel,
        populate_by_name=True,
    )