from pydantic import BaseModel, Field
from typing import Optional, List

# Schema for structured design attributes
class PCCaseAttributes(BaseModel):
    color: Optional[List[str]] = None
    style: Optional[List[str]] = None
    shape: Optional[List[str]] = None
    material: Optional[List[str]] = None
    ventilation: Optional[List[str]] = None
    lighting: Optional[List[str]] = None
    features: Optional[List[str]] = None

# Schema for text-to-image response
class ToSpec(BaseModel):
    prompt: str
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
