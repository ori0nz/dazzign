from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from app.schemas.common.design_attributes import PCCaseAttributes


def to_camel(string: str) -> str:
    return ''.join(word.capitalize() if i else word for i, word in enumerate(string.split('_')))

# Schema for image generation request
class GenerateImageRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    spec_json: PCCaseAttributes
    parent_id: Optional[int] = None
    action_type: Optional[str] = None

    model_config = {
        "alias_generator": to_camel,
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "prompt": "A modern PC case with RGB lighting",
                "negativePrompt": "blurry, distorted",
                "specJson": {
                                "style":     ["Minimalist", "Cyberpunk",],
                                "material":  ["Carbon fiber", "Wood",],
                                "lighting":  ["Neon glow", "Soft ambient",],
                                "features":  ["Compact", "Cable management",]
                            },
                "parentId": None,
                "actionType": "generate"
            }
        }
    }