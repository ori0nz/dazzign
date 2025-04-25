from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from app.schemas.text_gen.design_attributes import PCCaseAttributes


def to_camel(string: str) -> str:
    return ''.join(word.capitalize() if i else word for i, word in enumerate(string.split('_')))

# Schema for text-to-image response
class ToSpecResponse(BaseModel):
    prompt: str
    attributes: PCCaseAttributes
    structured_prompt: str = Field(..., description="Structured prompt suitable for image generation")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "prompt": "I want a sleek black PC case with RGB lighting and good airflow.",
                "attributes": {
                    "style": ["Sleek"],
                    "color": ["Black"],
                    "ventilation": ["Airflow"],
                    "lighting": ["RGB lighting"],
                },
                "structured_prompt": "A high-resolution render of; a PC case with a Sleek aesthetic; featuring Airflow; illuminated by RGB lighting."
            }
        },
        from_attributes=True,          # orm object to pydantic model
        alias_generator=to_camel,      
        populate_by_name=True          # support snake_case to camelCase
    ) 