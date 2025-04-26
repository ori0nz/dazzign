from pydantic import BaseModel, Field
from typing import Optional, List
from app.schemas.common.design_attributes import PCCaseAttributes
# Schema for text-to-image response
class ToSpec(BaseModel):
    prompt: Optional[str] = None
    attributes: PCCaseAttributes
    structured_prompt: str = Field(..., description="Structured prompt suitable for image generation")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "prompt": "I want a sleek black PC case with RGB lighting and good airflow.",
                "attributes": {
                    "color": ["black"],
                    "style": ["sleek"],
                    "lighting": ["RGB"],
                    "ventilation": ["good airflow"]
                },
                "structured_prompt": "Color: Black\nStyle: Sleek\nLighting: RGB\nVentilation: Good airflow"
            }
        }
    }
