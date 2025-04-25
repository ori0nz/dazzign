from pydantic import BaseModel, Field
from typing import Optional, List

# Schema for structured design attributes
class PCCaseAttributes(BaseModel):
    shape: List[str] = Field(default_factory=list)
    style: List[str] = Field(default_factory=list)
    color: List[str] = Field(default_factory=list)
    material: List[str] = Field(default_factory=list)
    ventilation: List[str] = Field(default_factory=list)
    lighting: List[str] = Field(default_factory=list)
    features: List[str] = Field(default_factory=list)
    environment: List[str] = Field(default_factory=list)