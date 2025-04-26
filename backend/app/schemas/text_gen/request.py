from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

# Schema for text-to-image request
class ToSpecRequest(BaseModel):
    prompt: Optional[str] = Field(..., description="Free-form text description of the desired PC case design")
    negative_prompt: Optional[str] = None
    parent_id: Optional[int] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "prompt": "I want a sleek black PC case with RGB lighting and good airflow."
            }
        }
    }